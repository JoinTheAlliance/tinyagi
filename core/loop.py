# core/loop.py
# Handles the main execution loop, which repeats at a fixed internal

import os
import time
from datetime import datetime

from easycompletion import compose_function, openai_function_call, compose_prompt
from core.action import get_action, use_action, search_actions
from core.events import get_events, create_event, increment_event_epoch


orient_prompt = """\
The current time is {{current_time}} on {{current_date}}.

Here are some things I know:
{{knowledge}}

This is my event stream. These are the events that happened in previous epochs:
{{events_earlier_epochs}}

These are the most recent events from last epoch:
{{events_this_epoch}}

Please summarize, from the most recent events, how it's going, what I learned this epoch and what I should do next.
"""


orient_function = compose_function(
    "summarize_recent_events",
    properties={
        "summary": {
            "type": "string",
            "description": "A summary of the most recent events from the last epoch and how it's going.",
        },
        "next": {
            "type": "string",
            "description": "What should I do next? The next action to take. Continue what I was working on until completion, start something new, or something entirely different?",
        },
    },
    description="Summarize the most recent events and decide what to do next.",
    required_property_names=["summary", "next"],
)


decision_prompt = """\
The current time is {{current_time}} on {{current_date}}.

Here are some things I know:
{{knowledge}}

This is my event stream. These are the latest events that have happened:
{{events}}

These are the actions available for me to take:
{{available_actions}}

Which action should I take next?
Your task: Please decide which of the actions that you think is the best next step for me.
Respond with the name of the action.
I will do the action and let you know how it went.
Do not ask if you can help. Do not ask how you can assist. Just tell me the action that is the best next step for me. You are the decision maker.
"""


decision_function = compose_function(
    name="decide_action",
    description="Decide which action to take next.",
    properties={
        "action_name": {
            "type": "string",
            "description": "The name of the action to take. Should be one of the available actions, and should not include quotes or any punctuation",
        },
        "reasoning": {
            "type": "string",
            "description": "The reasoning behind the decision. Why did you choose this action?",
        }
    },
    required_property_names=["action_name", "reasoning"],
)




def loop():
    """
    Main execution loop. This is modeled on the OODA loop -- https://en.wikipedia.org/wiki/OODA_loop
    """
    print("Loop started.")

    increment_event_epoch()

    ### OBSERVE ###
    # Collect inputs and summarize the current world state - what is currently going on and what actions might we take next?
    # TODO: Get events, knowledge, events per epoch, available actions
    # TODO: add events, events for last epoch, events for current epoch, knowledge, available actions

    events = get_events() or "I have awaken."
    knowledge
    available_actions

    observation = {
        "current_time": datetime.now().strftime("%H:%M"),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }

    ### ORIENT ###
    # Create a decision prompt based on the observation to decide on, find most relevant actions to take next
    composed_orient_prompt = compose_prompt(orient_prompt, observation)
    response = openai_function_call(text=composed_orient_prompt, functions=orient_function)
    observation["summary"] = response["arguments"]["summary"]
    observation["next"] = response["arguments"]["next"]

    ### DECIDE ###
    # Based on observations, decide which action to take next
    composed_decision_prompt = compose_prompt(decision_prompt, observation)
    response = openai_function_call(text=composed_decision_prompt, functions=decision_function)

    # Extract response message and remove the agent's name from it
    content = response["content"]
    if(content is not None):
        print(content)

    arguments = response["arguments"]

    ### ACT ###
    # Execute the action that was decided on
    # openai returns a "function_call" object
    # parse the name and arguments from it to call an action

    action = get_action(arguments["action_name"])

    action_prompt = action["prompt"]

    action_function = action["function"]

    composed_action_prompt = compose_prompt(action_prompt, observation)

    response = openai_function_call(text=composed_action_prompt, functions=action_function)

    use_action(response["function_name"], response["arguments"])

    print("loop end")


def start():
    while True:
        interval = os.getenv("UPDATE_INTERVAL") or 3
        interval = int(interval)
        loop()
        time.sleep(interval)
