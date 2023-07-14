from datetime import datetime
import os

from agentmemory import count_memories, create_memory


def check_log_dirs():
        # check if /logs and /logs/loop exists and create them if they don't
    if not os.path.isdir("./logs"):
        os.mkdir("./logs")
    if not os.path.isdir("./logs/loop"):
        os.mkdir("./logs/loop")

# Get the current event epoch
def get_epoch():
    # returns current event epoch
    # or initializes event epoch to 0
    count = count_memories("epoch")
    debug_log("Getting epoch: " + str(count))
    return count


# Each loop is an epoch
def increment_epoch():
    new_epoch_index = get_epoch() + 1

    # if length of current_epoch is 0, then epoch is not set
    document = f"Epoch {new_epoch_index} started at {str(datetime.utcnow())}"
    create_memory("epoch", document, id=new_epoch_index)
    debug_log("Incrementing epoch: " + str(new_epoch_index))
    return new_epoch_index


def debug_log(content, filename="logs/events.txt"):
    """
    Write to the debug log file
    """
    if os.environ.get("TINYAGI_DEBUG") in ["1", "true", "True"]:
        print(f"{content}")
        write_to_log(content, write_to_debug=True, filename=filename)


def write_to_log(content, write_to_debug=False, filename="logs/events.txt"):
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
    if write_to_debug is False:
        with open(filename, "a") as f:
            f.write(f"{content}\n")
        return

    if write_to_debug is True or os.environ.get("TINYAGI_DEBUG") in [
        "1",
        "true",
        "True",
    ]:
        debug_filename = filename.replace(".txt", "_debug.txt")
        with open(debug_filename, "a") as f:
            f.write(f"DEBUG >>> {content}\n")