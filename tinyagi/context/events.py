import json
from agentmemory import get_memories
from tinyagi.constants import (
    MAX_PROMPT_LIST_ITEMS,
    MAX_PROMPT_LIST_TOKENS,
    MAX_PROMPT_TOKENS,
)

from easycompletion import (
    count_tokens,
    trim_prompt,
)


def event_to_string(event):
    """
    Converts an event document into a formatted string.

    Parameters:
    - event (dict): The event document to be formatted.

    Returns: str - The formatted event string.
    """
    # Create an event with a formatted string and annotations
    e_m = event["metadata"]
    # check if e_m['epoch'] is none, set it to 0 if it is
    if e_m.get("epoch") is None:
        e_m["epoch"] = 0
    if e_m.get("type") is None:
        e_m["type"] = "unknown"
    new_event = f"{e_m['epoch']} | {e_m['type']}"
    if e_m.get("subtype") is not None:
        new_event += f"::{e_m['subtype']}"
    if e_m.get("creator") is not None:
        new_event += f" ({e_m['creator']})"
    new_event += f": {event['document']}"
    return new_event


def build_events_context(context={}):
    """
    Retrieve and format recent events

    Parameters: None

    Returns: str - A string representing a list of formatted events
    """
    events_header = """\
Recent Events are formatted as follows:
Epoch # | <Type>::<Subtype> (Creator): <Event>
============================================"""

    events = get_memories("events", n_results=MAX_PROMPT_LIST_ITEMS)

    # get the 'document' from all events and make an array
    event_documents = [{ "document": event["document"], "metadata": event["metadata"] } for event in events]

    # format events with pretty json to view
    events_to_print = json.dumps(event_documents, indent=4, sort_keys=True)
    print(events_to_print)

    # reverse events

    # sort the events by event["metadata"]["epoch"]
    events = sorted(events, key=lambda k: k["metadata"]["epoch"])

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
    if annotated_events is not None and annotated_events != "":
        context["events"] = events_header + "\n" + annotated_events + "\n"
    else:
        context["events"] = ""
    return context


def get_context_builders():
    """
    Returns a list of functions that build context dictionaries

    Returns:
        context_builders: a list of functions that build context dictionaries
    """
    return [build_events_context]
