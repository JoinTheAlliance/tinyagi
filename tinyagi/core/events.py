from agentmemory import create_memory, search_memory, get_memories
from easycompletion import count_tokens, trim_prompt

from tinyagi.core.constants import MAX_PROMPT_LIST_ITEMS, MAX_PROMPT_LIST_TOKENS, MAX_PROMPT_TOKENS

from .system import get_epoch, write_to_log, debug_log


def create_event(content, type=None, subtype=None, creator=None, metadata={}):
    """
    Creates an event with provided metadata and saves it to the event log file.
    
    Parameters:
    - content (str): Content of the event
    - type (str, optional): Type of the event. Defaults to None.
    - subtype (str, optional): Subtype of the event. Defaults to None.
    - creator (str, optional): Creator of the event. Defaults to None.
    - metadata (dict, optional): Additional metadata for the event. Defaults to empty dictionary.
    
    Returns: None
    """
    metadata["type"] = type
    metadata["subtype"] = subtype
    metadata["creator"] = creator
    metadata["epoch"] = get_epoch()

    # if any keys are None, delete them
    metadata = {k: v for k, v in metadata.items() if v is not None}

    event = {
        "document": content,
        "metadata": metadata,
    }

    event_string = event_to_string(event)

    create_memory("events", content, metadata=metadata)
    print(f"{event_string}")
    write_to_log(f"{event_string}")
    debug_log(f"{event_string}")


def get_events(type=None, n_results=None, filter_metadata=None):
    """
    Retrieves the last n events from the 'events' collection based on the specified filter metadata.
    
    Parameters:
    - type (str, optional): The type of events to retrieve. Defaults to None.
    - n_results (int, optional): The number of results to return. Defaults to None.
    - filter_metadata (dict, optional): A dictionary used to filter the results. Defaults to None.
    
    Returns: list of event documents
    """
    if filter_metadata is None:
        filter_metadata = {}
    if type is not None:
        filter_metadata = {"type": type}
    memories = get_memories(
        "events", filter_metadata=filter_metadata, n_results=n_results
    )
    debug_log(f"Getting events: {memories}")
    return memories


def get_formatted_events():
    """
    Retrieves and formats a specified number of recent events from the 'events' collection.
    
    Parameters: None

    Returns: str - A string representing a list of formatted events
    """
    events_header = """Recent Events are formatted as follows:
Epoch # | <Type>::<Subtype> (Creator): <Event>
============================================"""

    events = get_events(n_results=MAX_PROMPT_LIST_ITEMS)

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
        annotated_events = "\n".join([event_to_string(event) for event in events])

    return events_header + "\n" + annotated_events + "\n"



def search_events(search_text, n_results=None):
    """
    Searches the 'events' collection for events that match the provided search text.
    
    Parameters:
    - search_text (str): The text to search for.
    - n_results (int, optional): The number of results to return. Defaults to None.
    
    Returns: list of event documents that match the search criteria
    """
    memories = search_memory("events", search_text, n_results=n_results)
    debug_log(f"Searching events: {memories}")
    return memories


def event_to_string(event):
    """
    Converts an event document into a formatted string.
    
    Parameters:
    - event (dict): The event document to be formatted.
    
    Returns: str - The formatted event string.
    """
    # Create an event with a formatted string and annotations
    e_m = event['metadata']
    # check if e_m['epoch'] is none, set it to 0 if it is
    if e_m.get('epoch') is None:
        e_m['epoch'] = 0
    if e_m.get('type') is None:
        e_m['type'] = 'unknown'
    new_event = f"{e_m['epoch']} | {e_m['type']}"
    if e_m.get('subtype') is not None:
        new_event += f"::{e_m['subtype']}"
    if e_m.get('creator') is not None:
        new_event += f" ({e_m['creator']})"
    new_event += f": {event['document']}"
    return new_event