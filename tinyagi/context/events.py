import os
import sys
import time
from datetime import datetime

from easycompletion import (
    count_tokens,
    trim_prompt,
)


from agentevents import (
    get_events,
    event_to_string,
)


MAX_PROMPT_LIST_ITEMS = 30  # maximum number of events to display
MAX_PROMPT_LIST_TOKENS = 1536  # 2048 - 512
MAX_PROMPT_TOKENS = 3072  # 4096 - 1024

TYPE_COLORS = {
    "error": "red",
    "summary": "cyan",
    "reasoning": "blue",
    "action": "green",
    "system": "magenta",
}

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