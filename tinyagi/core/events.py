from datetime import datetime
import os

from agentmemory import count_memories, create_memory, search_memory, get_memories


# Get the current event epoch
def get_epoch():
    # returns current event epoch
    # or initializes event epoch to 0
    return count_memories("epoch")


# Each loop is an epoch
def increment_epoch():
    new_epoch_index = get_epoch() + 1

    # if length of current_epoch is 0, then epoch is not set
    document = f"Epoch {new_epoch_index} started at {str(datetime.utcnow())}"
    create_memory("epoch", document, id=new_epoch_index)
    return new_epoch_index


def write_to_log(content, filename="logs/events.txt"):
    """
    Write to the event log file
    """
    # first, check that all directories in filename exist
    # if not, create them

    for i in range(len(filename.split("/")) - 1):
        # if the current directory doesn't exist, create it
        if not os.path.exists("/".join(filename.split("/")[: i + 1])):
            os.mkdir("/".join(filename.split("/")[: i + 1]))

    # then, write to the file
    with open(filename, "a") as f:
        f.write(f"{content}\n")


def create_event(content, type=None, subtype=None, event_creator="Me", metadata={}):
    """
    Create event, then save it to the event log file and print it
    """
    metadata["type"] = type
    metadata["subtype"] = subtype
    metadata["event_creator"] = event_creator
    metadata["epoch"] = get_epoch()

    # if any keys are None, delete them
    metadata = {k: v for k, v in metadata.items() if v is not None}

    create_memory("events", content, metadata=metadata)
    print(f"{content}")
    write_to_log(f"{content}")


def get_events(type=None, n_results=None, filter_metadata=None):
    """
    Get the last n events from the 'events' collection.
    """
    if filter_metadata is None:
        filter_metadata = {}
    if type is not None:
        filter_metadata = {"type": type}
    return get_memories("events", filter_metadata=filter_metadata, n_results=n_results)


def search_events(search_text, n_results=None):
    """
    Search the 'events' collection by search text
    """
    return search_memory("events", search_text, n_results=n_results)
