from agentmemory import create_memory, search_memory, get_memories

from .system import get_epoch, write_to_log, debug_log


def create_event(content, type=None, subtype=None, creator="Me", metadata={}):
    """
    Create event, then save it to the event log file and print it
    """
    metadata["type"] = type
    metadata["subtype"] = subtype
    metadata["creator"] = creator
    metadata["epoch"] = get_epoch()

    # if any keys are None, delete them
    metadata = {k: v for k, v in metadata.items() if v is not None}

    create_memory("events", content, metadata=metadata)
    print(f"{content}")
    write_to_log(f"{content}")
    debug_log(f"Created event: {content}")


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
