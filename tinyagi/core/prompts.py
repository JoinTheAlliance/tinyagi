# core/prompts.py
# Built-in prompt data and functions used in the loop

import json
import os
import sys
from datetime import datetime

from easycompletion import (
    compose_function,
    count_tokens,
)

from .events import (
    get_epoch,
    get_events,
    get_events,
)

from easycompletion import (
    compose_function,
)

orient_prompt = """\
The current time is {{current_time}} on {{current_date}}.

Here are some things I know:
{{knowledge}}

This is my event stream. These are the events that happened in previous epochs:
{{events_from_previous_epochs}}

These are the most recent events from last epoch:
{{events_from_last_epoch}}

Please summarize, from the most recent events, how it's going, what I learned this epoch and what I should do next.
First, summarize as yourself (the assistant), then summarize as if you were me, the user, in the first person from my perspective.
Lastly, include any new knowledge that I learned this epoch as an array of knowledge items.
Each knowledge item should be a factual statement that I learned, and should include the source, the content and the relationship.
If there is no new knowledge, use an empty array [].
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
        "assistant_reasoning": {
            "type": "string",
            "description": "The reasoning behind the decision. Why did you choose this action? Should be written from your perspective, as the assistant, telling the user why you chose this action.",
        },
        "user_reasoning": {
            "type": "string",
            "description": "The reasoning behind the decision, from the perspective of the user. Why did I, the user choose this action? Should be written as if you were the user, in the first person.",
        },
    },
    required_properties=["action_name", "assistant_reasoning", "user_reasoning"],
)


def compose_observation(token_limit=1536, short=False):
    limits = {
        "events": 50,
        "events_from_previous_epochs": 25,
        "events_from_last_epoch": 25,
        "summaries": 3,
        "knowledge": 10,
        "available_actions": 10,
    }
    if short is True:
        limits = {
            "events": 10,
            "events_from_previous_epochs": 10,
            "events_from_last_epoch": 10,
            "summaries": 2,
            "knowledge": 5,
            "available_actions": 5,
        }

    events = get_events(n_results=limits["events"])

    events_from_last_epoch = get_events(
        n_results=limits["events_from_last_epoch"],
        filter_metadata={"epoch": get_epoch() - 1},
    )
    events_from_previous_epochs = get_events(
        n_results=limits["events_from_previous_epochs"],
        filter_metadata={"epoch": {"$gte": get_epoch() - 2}},
    )

    # each event is a dictionary with keys: id, document, metadata
    # Inside the metadata is the epoch number
    # Join the documents together into a single string

    formatted_events = "\n".join([event["document"] for event in events])

    formatted_events_from_last_epoch = "\n".join(
        [event["document"] for event in events_from_last_epoch]
    )

    formatted_events_from_previous_epochs = "\n".join(
        [event["document"] for event in events_from_previous_epochs]
    )

    summaries = get_events(type="summary", n_results=limits["summaries"])
    formatted_summaries = "\n".join([s["document"] for s in summaries])

    observation_data = {
        "current_time": datetime.now().strftime("%H:%M"),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "current_working_directory": os.getcwd(),
        "current_playform": sys.platform,
        "events": formatted_events,
        "events_from_previous_epochs": formatted_events_from_previous_epochs,
        "events_from_last_epoch": formatted_events_from_last_epoch,
        "previous_summaries": formatted_summaries,
        "knowledge": None,  # populated in loop
        "summary": None,  # populated in loop from orient function
        "available_actions": None,  # populated in the loop by the orient function
        "action_reasoning": None,  # populated in the loop by the decision function
    }

    if short is True:
        return observation_data

    prompt_string = json.dumps(observation_data, indent=None)
    token_count = count_tokens(prompt_string)
    # if the observation is too big, shorten it
    if token_count > token_limit:
        return compose_observation(short=True)
    return observation_data
