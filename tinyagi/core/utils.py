import os
import time

from easycompletion import count_tokens, openai_function_call, trim_prompt

from agentevents import create_event, get_events, event_to_string

from actionflow import get_available_actions

from tinyagi.core.constants import (
    MAX_PROMPT_LIST_ITEMS,
    MAX_PROMPT_LIST_TOKENS,
    MAX_PROMPT_TOKENS,
    TYPE_COLORS,
)


def debuggable_create_event(
    event_type, event_subtype, document, metadata={}, type_colors=TYPE_COLORS
):
    return create_event(
        event_type, event_subtype, document, metadata=metadata, type_colors=type_colors
    )


def debuggable_function_call(text, functions, name="prompt"):
    """
    Wraps openai_function_call in debug logging.
    Arguments:
    - text: String containing the prompt text for the function call.
    - functions: List of functions to be called.
    - name: Name of the prompt.
    Return: Response from the openai_function_call.
    """
    response = openai_function_call(text=text, functions=functions)
    if os.environ.get("DEBUG") in ["1", "true", "True"]:
        with open(f"./logs/{name}_{time.time()}.txt", "w") as f:
            f.write(text)

    return response


def get_formatted_events(n_results=MAX_PROMPT_LIST_ITEMS):
    """
    Retrieve and format recent events

    Parameters: None

    Returns: str - A string representing a list of formatted events
    """
    events_header = """Recent Events are formatted as follows:
Epoch # | <Type>::<Subtype> (Creator): <Event>
============================================"""

    events = get_events(n_results=n_results)

    # reverse events
    events = events[::-1]

    # annotated events
    annotated_events = "\n".join([event_to_string(event) for event in events])

    # trim any individual events, just in case
    for i in range(len(events)):
        document = events[i]["document"]
        if count_tokens(document) > MAX_PROMPT_LIST_TOKENS:
            events[i]["document"] = (
                trim_prompt(document, MAX_PROMPT_LIST_TOKENS - 5) + " ..."
            )

    while count_tokens(annotated_events) > MAX_PROMPT_TOKENS:
        # remove the first event
        events = events[1:]
        event_strings = [event_to_string(event) for event in events]
        annotated_events = "\n".join(event_strings)

    return events_header + "\n" + annotated_events + "\n"


def get_formatted_available_actions(search_text):
    """
    Retrieve a formatted string of the available actions based on search text

    Args:
        search_text: Find most revelant actions whith are available.

    Returns:
        A string representing the available actions.
    """
    header_text = "Available actions for me to choose from:"
    available_actions = get_available_actions(search_text)
    formatted_available_actions = "\n".join(available_actions)
    while count_tokens(formatted_available_actions) > MAX_PROMPT_TOKENS:
        if len(available_actions) == 1:
            raise Exception("Single knowledge length greater than token limit")
        available_actions = available_actions[:-1]
        formatted_available_actions = "\n".join(
            [k["document"] for k in available_actions]
        )
    return header_text + "\n" + formatted_available_actions + "\n"
