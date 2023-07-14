# core/loop.py
# Handles the main execution loop, which repeats at a fixed internal

import json
import time
import os
import sys
from datetime import datetime

from easycompletion import (
    openai_function_call,
    compose_prompt,
    compose_function,
    count_tokens,
    trim_prompt,
)

from tinyagi.core.constants import (
    DEBUG,
    UPDATE_INTERVAL,
    EVENT_COUNT_DISPLAY_LIMIT,
    TOKEN_DISPLAY_LIMIT,
    ENTRY_TOKEN_DISPLAY_LIMIT,
)

from .system import check_log_dirs, debug_log, increment_epoch, get_epoch

from .actions import (
    get_action,
    get_formatted_available_actions,
    use_action,
)
from .events import create_event, get_events, get_events, event_to_string

from .knowledge import (
    add_knowledge,
    formatted_search_knowledge,
    get_knowledge_from_epoch,
)


### START ###
def start():
    while True:
        print("looping")
        loop()
        time.sleep(UPDATE_INTERVAL)


### MAIN LOOP ###
def loop():
    """
    Main execution loop. This is modeled on the OODA loop -- https://en.wikipedia.org/wiki/OODA_loop
    # The steps are observe, oriented, decide, act
    # Observe - collect inputs and summarize the current world state - what is currently going on and what actions might we take next?
    # Orient - summarize the last epoch and think about what to do next, then augment the observation
    # Decide - based on the orientation and observation, decide which relevant action to take
    # Act - execute the action that was decided on
    """

    # Each run of the loop is an epoch
    increment_epoch()
    epoch = get_epoch()

    if epoch == 1:
        create_event("I have just woken up.", type="system", subtype="intialized")

    epoch = get_epoch()

    ### OBSERVE ###
    # Collect inputs and summarize the current world state - what is currently going on and what actions might we take next?
    observation = observe()

    ### ORIENT ###
    # Summarize the last epoch and think about what to do next

    observation = orient(observation)

    ### DECIDE ###
    # Based on the orientation, decide which relevant action to take
    observation = decide(observation)

    ### ACT ###
    # Execute the action that was decided on
    # parse the name and arguments from the response object to call an action
    observation = act(observation)

    write_observation_to_log(observation, "loop_end")
    

def write_observation_to_log(observation, step="loop"):
    # if debug is not true, skip this
    if os.environ.get("TINYAGI_DEBUG") not in ["1", "true", "True"]:
        return

    check_log_dirs()

    print("observation is", observation)

    text = ""
    # observation is a key value store
    for key, value in observation.items():
        text += f"{key}: {value}\n"
    debug_log(f"observation:{text}")
    filename = "observation"
    # write the prompt, functions and response to a file
    with open(f"./logs/loop/{filename}_{step}_{time.time()}.txt", "w") as f:
        f.write(text)



### OBSERVE ###


def observe():
    events = get_events(n_results=EVENT_COUNT_DISPLAY_LIMIT)

    # reverse events
    events = events[::-1]

    # annotated events
    annotated_events = "\n".join([event_to_string(event) for event in events])

    # trim any individual events, just in case
    for i in range(len(events)):
        document = events[i]["document"]
        if count_tokens(document) > ENTRY_TOKEN_DISPLAY_LIMIT:
            events[i]["document"] = (
                trim_prompt(document, ENTRY_TOKEN_DISPLAY_LIMIT - 5) + " ..."
            )

    while count_tokens(annotated_events) > TOKEN_DISPLAY_LIMIT:
        # remove the first event
        events = events[1:]
        annotated_events = "\n".join([event_to_string(event) for event in events])

    recent_knowledge = get_knowledge_from_epoch(get_epoch() - 1)

    # trim any individual knowledge, just in case
    for i in range(len(recent_knowledge)):
        document = recent_knowledge[i]["document"]
        if count_tokens(document) > ENTRY_TOKEN_DISPLAY_LIMIT:
            recent_knowledge[i]["document"] = (
                trim_prompt(document, ENTRY_TOKEN_DISPLAY_LIMIT - 5) + " ..."
            )

    formatted_knowledge = "\n".join([k["document"] for k in recent_knowledge])

    while count_tokens(formatted_knowledge) > TOKEN_DISPLAY_LIMIT:
        if len(recent_knowledge) == 1:
            raise Exception(
                "Single knowledge length is greater than token limit, should not happen"
            )
        # remove the first event
        recent_knowledge = recent_knowledge[1:]
        formatted_knowledge = "\n".join([k["document"] for k in recent_knowledge])

    observation = {
        "epoch": get_epoch(),
        "last_epoch": str(get_epoch() - 1),
        "current_time": datetime.now().strftime("%H:%M"),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "platform": sys.platform,
        "cwd": os.getcwd(),
        "events": annotated_events,
        "recent_knowledge": formatted_knowledge,
        "knowledge": None,  # populated in loop
        "summary": None,  # populated in loop from orient function
        "available_actions": None,  # populated in the loop by the orient function
        "reasoning": None,  # populated in the loop by the decision function
    }
    write_observation_to_log(observation, "loop_end")
    return observation


### ORIENT ###

orient_prompt = """Current Epoch: {{epoch}}
The current time is {{current_time}} on {{current_date}}.

I learned the following knowledge last epoch:
{{recent_knowledge}}

Recent Events are formatted as follows:
Epoch # | <Type> [Subtype] (Creator): <Event>
============================================
{{events}}

# Assistant Task
- Summarize what happened in Epoch {{last_epoch}} and reason about what I should do next to move forward.
- First, summarize as yourself (the assistant). Include any relevant information for me, the user, for the next step.
- Next summarize as if you were me, the user, in the first person from my perspective. Use "I" instead of "You".
- Lastly, include any new knowledge that I learned this epoch as an array of knowledge items.
- Your summary should include what I learned, what you think I should do next and why. You should argue for why you think this is the best next step.
- I am worried about getting stuck in a loop or make new progress. Your reasoning should be novel and interesting and helpful me to make progress towards my goals.
- Each knowledge array item should be a factual statement that I learned, and should include the source, the content and the relationship.
- For the "content" of each knowledge item, please be extremely detailed. Include as much information as possible, including who or where you learned it from, what it means, how it relates to my goals, etc.
- ONLY extract knowledge from the last epoch, which is #{{last_epoch}}. Do not extract knowledge from previous epochs.
- If there is no new knowledge, respond with an empty array [].
"""


orient_function = compose_function(
    "summarize_recent_events",
    properties={
        "summary_as_assistant": {
            "type": "string",
            "description": "Respond to the me, the user, as yourself, the assistant. Summarize what has happened recently, what you learned from it and what you'd like to do next. Use 'You' instead of 'I'.",
        },
        "summary_as_user": {
            "type": "string",
            "description": "Resphrase your response as if you were me, the user, from the user's perspective in the first person. Use 'I' instead of 'You'.",
        },
        "knowledge": {
            "type": "array",
            "description": "An array of knowledge items that are extracted from my last epoch of events and the summary of those events. Only include knowledge that has not been learned before. Knowledge can be about anything that would help me. If none, use an empty array.",
            "items": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Where did I learn this? From a connector, the internet, a user or from my own reasoning? Use first person, e.g. 'I learned this from the internet.', from the user's perspective",
                    },
                    "content": {
                        "type": "string",
                        "description": "The actual knowledge I learned. Please format it as a sentence, e.g. 'The sky is blue.' from the user's perspective, in the first person, e.g. 'I can write shell scripts by running a shell command, calling cat and piping out.'",
                    },
                    "relationship": {
                        "type": "string",
                        "description": "What is useful, interesting or important about this information to me and my goals? How does it relate to what I'm doing? Use first person, e.g. 'I can use X to do Y.' from the user's perspective",
                    },
                },
            },
        },
    },
    description="Summarize the most recent events and decide what to do next.",
    required_properties=["summary_as_assistant", "summary_as_user", "knowledge"],
)


def orient(observation):
    composed_orient_prompt = compose_prompt(orient_prompt, observation)
    response = debuggable_function_call(
        text=composed_orient_prompt, functions=orient_function, name="orient"
    )

    arguments = response["arguments"]
    if arguments is None:
        arguments = {}
        print("No arguments returned from orient_function")

    # Create new knowledge and add to the knowledge base
    knowledge = arguments.get("knowledge", [])
    if len(knowledge) > 0:
        for k in knowledge:
            # each item in knowledge contains content, source and relationship
            metadata = {
                "source": k["source"],
                "relationship": k["relationship"],
            }
            add_knowledge(k["content"], metadata=metadata)

    # Get the summary and add to the observation object
    summary = response["arguments"]["summary_as_user"]
    observation["summary"] = summary

    # Search for knowledge based on the summary and add to the observation object
    observation["knowledge"] = formatted_search_knowledge(
        search_text=summary, n_results=10
    )

    # Search for the most relevant available actions based on the summary
    observation["available_actions"] = get_formatted_available_actions(summary)

    # Add observation summary to event stream
    create_event(summary, type="summary")
    write_observation_to_log(observation, "orient")
    return observation


### DECIDE ###

decision_prompt = """Current Epoch: {{epoch}}
The current time is {{current_time}} on {{current_date}}.

Here are some relevant things I know:
{{knowledge}}

Recent Events are formatted as follows:
Epoch # | <Type>::<Subtype> (Creator): <Event>
============================================
{{events}}

Available actions for me to choose from:
{{available_actions}}

Assistant Notes:
- Do not ask if you can help. Do not ask how you can assist. Do not gather more information.
- I will not repeat the same action unless it achieves some additional goal. I don't like getting stuck in loops or repeating myself.
- I prefer to act in a way that is novel and interesting.
- I only want to gather additional knowledge when I have to. I like to try things first.

Your task: 
- Based on recent events, which of the actions that you think is the best next action for me to progress towards my goals.
- Based on the information provided, write a summary from your perspective of what action I should take next and why (assistant_reasoning)
- Respond with the name of the action (action_name)
- Rewrite the summary as if you were me, the user, in the first person (user_reasoning)
- I can only choose from the available actions. You must choose one of the available actions.
"""


decision_function = compose_function(
    name="decide_action",
    description="Decide which action to take next.",
    properties={
        "assistant_reasoning": {
            "type": "string",
            "description": "The reasoning behind the decision. Why did you choose this action? Should be written from your perspective, as the assistant, telling the user why you chose this action.",
        },
        "action_name": {
            "type": "string",
            "description": "The name of the action to take. Should be one of the available actions, and should not include quotes or any punctuation",
        },
        "user_reasoning": {
            "type": "string",
            "description": "Rewrite the assistant_reasoning from the perspective of the user. Rewrite your reasoning from my perspective, using 'I' instead of 'You'.",
        },
    },
    required_properties=["action_name", "assistant_reasoning", "user_reasoning"],
)


def decide(observation):
    composed_decision_prompt = compose_prompt(decision_prompt, observation)
    response = debuggable_function_call(
        text=composed_decision_prompt, functions=decision_function, name="decision"
    )

    # Add the action reasoning to the observation object
    reasoning = response["arguments"]["user_reasoning"]
    observation["reasoning"] = reasoning
    observation["action_name"] = response["arguments"]["action_name"]
    create_event(reasoning, type="reasoning")
    write_observation_to_log(observation, "decide")
    return observation

def act(observation):
    action_name = observation["action_name"]
    action = get_action(action_name)

    if action is None:
        create_event(
            f"I tried to use the action `{action_name}`, but it was not found.",
            type="error",
            subtype="action_not_found",
        )
        return

    composed_action_prompt = compose_prompt(action["prompt"], observation)

    response = debuggable_function_call(
        text=composed_action_prompt,
        functions=action["function"],
        name=f"action_{action_name}",
    )

    # TODO: check if the action is the last as last time

    use_action(response["function_name"], response["arguments"])
    write_observation_to_log(observation, "act")
    return observation

### UTILS ###


def debuggable_function_call(text, functions, name="prompt"):
    # Wraps openai_function_call in debug logging
    response = openai_function_call(text=text, functions=functions)
    if DEBUG:
        debug_log(
            f"openai_function_call\nprompt:\n{text}\nfunctions:\n{functions}\nresponse:\n{response}"
        )
        check_log_dirs()
        # write the prompt, functions and response to a file
        with open(f"./logs/loop/{name}_{time.time()}.txt", "w") as f:
            f.write(text)

    return response
