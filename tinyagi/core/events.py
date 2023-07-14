from agentmemory import create_memory, search_memory, get_memories

from .system import get_epoch, write_to_log, debug_log


def create_event(content, type=None, subtype=None, creator=None, metadata={}):
    """
    Create event, then save it to the event log file and print it
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
    Get the last n events from the 'events' collection.
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


def search_events(search_text, n_results=None):
    """
    Search the 'events' collection by search text
    """
    memories = search_memory("events", search_text, n_results=n_results)
    debug_log(f"Searching events: {memories}")
    return memories


def event_to_string(event):
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