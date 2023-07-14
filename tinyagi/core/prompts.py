# core/prompts.py
# Built-in prompt data and functions used in the loop

import json
import os
import sys
from datetime import datetime
import time

from easycompletion import (
    compose_function,
    count_tokens,
)

from tinyagi.core.system import check_log_dirs, debug_log, get_epoch

from .events import (
    get_events,
    get_events,
)

from easycompletion import (
    compose_function,
)

orient_prompt = """The current time is {{current_time}} on {{current_date}}.
Recent Events are formatted as follows:
Epoch # | <Type> [Subtype] (Creator): <Event>
============================================
{{annotated_events}}

# Assistant Task
- Summarize what happened in Epoch {{epoch}} and reason about what I should do next to move forward.
- First, summarize as yourself (the assistant). Include any relevant information for me, the user, for the next step.
- Next summarize as if you were me, the user, in the first person from my perspective. Use "I" instead of "You".
- Lastly, include any new knowledge that I learned this epoch as an array of knowledge items.
- Your summary should include what I learned, what you think I should do next and why. You should argue for why you think this is the best next step.
- I am worried about getting stuck in a loop or make new progress. Your reasoning should be novel and interesting and helpful me to make progress towards my goals.
- Each knowledge array item should be a factual statement that I learned, and should include the source, the content and the relationship.
- ONLY extract knowledge from this epoch, which is #{{epoch}}. Do not extract knowledge from previous epochs.
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


decision_prompt = """The current time is {{current_time}} on {{current_date}}.

Here are some things I know:
{{knowledge}}

This is my event stream. These are the latest events that have happened:
{{annotated_events}}

These are the actions available for me to take:
{{available_actions}}

Assistant Notes:
- Do not ask if you can help. Do not ask how you can assist. Do not gather more information.
- I will not repeat the same action unless it achieves some additional goal. I don't like getting stuck in loops or repeating myself.
- I prefer to act in a way that is novel and interesting.
- I only want to gather additional knowledge when I have to. I like to try things first.

Your task: 
- Decide which of the actions that you think is the best next step to progress towards my goals.
- Based on the information provided, write a summary from your perspective of what action I should take next and why (assistant_reasoning)
- Respond with the name of the action (action_name)
- Rewrite the summary as if you were me, the user, in the first person (user_reasoning)
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
            "description": "The reasoning behind the decision, from the perspective of the user. Why did I, the user choose this action? Should be written as if you were the user, in the first person.",
        },
    },
    required_properties=["action_name", "assistant_reasoning", "user_reasoning"],
)

def write_observation_to_log(observation_data):
    check_log_dirs()
    # if debug is not true, skip this
    if os.environ.get("TINYAGI_DEBUG") not in ["1", "true", "True"]:
        return
    
    text = ""
    # observation is a key value store
    for key, value in observation_data.items():
        text += f"{key}: {value}\n"
    debug_log(f"observation:{text}")
    # write the prompt, functions and response to a file
    with open(f"./logs/loop/observation_{time.time()}.txt", "w") as f:
        f.write(text)
            

def compose_observation(token_limit=1536, short=False):
    limits = {
        "events": 50,
        "summaries": 3,
        "knowledge": 10,
        "available_actions": 10,
    }
    if short is True:
        limits = {
            "events": 10,
            "summaries": 2,
            "knowledge": 5,
            "available_actions": 5,
        }

    events = get_events(n_results=limits["events"])

    # reverse events
    events = events[::-1]

    formatted_events = "\n".join([event["document"] for event in events])

    # annotated events
    annotated_events = ""
    # iterate through events and print f"{event['metadata']['epoch']} | 
    for event in events:
        if(annotated_events != ""):
            annotated_events += "\n"
        e_m = event['metadata']
        print("event document")
        print(event['document'])
        print("e_m")
        print(e_m)
        # check if e_m['epoch'] is none, set it to 0 if it is
        if e_m.get('epoch') is None:
            e_m['epoch'] = 0
        annotated_events += f"{e_m['epoch']} | {e_m['type']}"
        if e_m.get('subtype') is not None:
            annotated_events += f"::{e_m['subtype']}"
        if e_m.get('creator') != 'Me' and e_m.get('creator') is not None:
            annotated_events += f" ({e_m['creator']})"
        annotated_events += f": {event['document']}"

    summaries = get_events(type="summary", n_results=limits["summaries"])
    formatted_summaries = "\n".join([s["document"] for s in summaries])

    print('************************************************')
    print('****** SUMMARIES')
    print(formatted_summaries)
    if formatted_summaries == "":
        formatted_summaries = "(No summaries yet)"

    observation_data = {
        "epoch": get_epoch(),
        "current_time": datetime.now().strftime("%H:%M"),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "platform": sys.platform,
        "cwd": os.getcwd(),
        "events": formatted_events,
        "annotated_events": annotated_events,
        "previous_summaries": formatted_summaries,
        "knowledge": None,  # populated in loop
        "summary": None,  # populated in loop from orient function
        "available_actions": None,  # populated in the loop by the orient function
        "reasoning": None,  # populated in the loop by the decision function
    }

    if short is True:
        return observation_data

    prompt_string = json.dumps(observation_data, indent=None)
    token_count = count_tokens(prompt_string)
    


    # if the observation is too big, shorten it
    if token_count > token_limit:
        return compose_observation(short=True)
    write_observation_to_log(observation_data)
    return observation_data
