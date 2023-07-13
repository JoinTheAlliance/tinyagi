from datetime import datetime
import os

from agentmemory import create_memory, search_memory, get_memories


# Get the current event epoch
def get_event_epoch():
    # returns current event epoch
    # or initializes event epoch to 0
    current_epoch = get_memories("epoch", n_results=1)
    # if length of current_epoch is 0, then epoch is not set
    if len(current_epoch) == 0:
        increment_event_epoch()
        current_epoch = get_memories("epoch", n_results=1)

    return int(current_epoch[0]["id"])


# Each loop is an epoch
def increment_event_epoch():
    # increments event epoch by 1
    current = get_memories("epoch", n_results=1)
    current_epoch_index = 0
    if len(current) > 0:
        current_epoch_index = current[0]["id"]

    current_epoch_index = int(current_epoch_index) + 1

    # if length of current_epoch is 0, then epoch is not set
    document = f"Epoch {current_epoch_index} started at {str(datetime.utcnow())}"
    create_memory("epoch", document, id=current_epoch_index)
    return current_epoch_index


def write_to_log(content, filename="logs/events.txt"):
    """
    Write to the event log file
    """
    # first, check that all directories in filename exist
    # if not, create them

    for i in range(len(filename.split("/"))-1):
        # if the current directory doesn't exist, create it
        if not os.path.exists("/".join(filename.split("/")[: i + 1])):
            os.mkdir("/".join(filename.split("/")[: i + 1]))

    # then, write to the file
    with open(filename, "a") as f:
        f.write(f"{content}\n")


def create_event(content, type="conversation", subtype=None, event_creator="Me"):
    """
    TODO: Create event, then save it to the event log file and print it
    """
    metadata = {
        "type": type,
        "subtype": subtype,
        "event_creator": event_creator,
        "epoch": get_event_epoch(),
    }

    # if any keys are None, delete them
    metadata = {k: v for k, v in metadata.items() if v is not None}

    create_memory("events", content, metadata=metadata)
    print(f"{content}")
    write_to_log(f"{content}")


def get_events(type=None, n_results=None):
    """
    Get the last n events from the 'events' collection.
    """
    filter_metadata = None
    if type is not None:
        filter_metadata = {"type": type}
    return get_memories("events", filter_metadata=filter_metadata, n_results=n_results)


def get_events_from_last_epoch(n_results=None):
    """
    Get the events from the last epoch.
    """
    return get_memories(
        "events", filter_metadata={"epoch": get_event_epoch() - 1}, n_results=n_results
    )


def get_events_from_epochs_before_last(n_results=None):
    """
    Get the events from the epochs before the last epoch.
    """
    return get_memories(
        "events",
        filter_metadata={"epoch": {"$gte": get_event_epoch() - 2}},
        n_results=n_results,
    )


def search_events(search_text, n_results=None):
    """
    Search the 'events' collection by search text
    """
    return search_memory("events", search_text, n_results=n_results)
