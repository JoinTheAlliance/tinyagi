from datetime import datetime
import os
import time

from agentmemory import count_memories, create_memory
from easycompletion import openai_function_call

from tinyagi.core.constants import DEBUG


def check_log_dirs():
    """
    Checks if the directories /logs and /logs/loop exist, if not they are created.
    This function does not take any arguments or return any outputs.
    """
    if not os.path.isdir("./logs"):
        os.mkdir("./logs")
    if not os.path.isdir("./logs/loop"):
        os.mkdir("./logs/loop")


def get_epoch():
    """
    Returns the current event epoch or initializes it to 0 if it is not set.
    This function does not take any arguments.
    Return: Integer value of the current event epoch.
    """
    count = count_memories("epoch")
    debug_log("Getting epoch: " + str(count))
    return count


def increment_epoch():
    """
    Increments the event epoch by 1.
    This function does not take any arguments.
    Return: Integer value of the new event epoch.
    """
    new_epoch_index = get_epoch() + 1
    document = f"Epoch {new_epoch_index} started at {str(datetime.utcnow())}"
    create_memory("epoch", document, id=new_epoch_index)
    debug_log("Incrementing epoch: " + str(new_epoch_index))
    return new_epoch_index


def debug_log(content, filename="logs/events.txt"):
    """
    Writes content to the debug log file.
    Arguments:
    - content: String to be written in the debug log file.
    - filename: Name of the file where the content is written.
    Return: None
    """
    if DEBUG:
        print(f"{content}")
        write_to_log(content, write_to_debug=True, filename=filename)


def write_to_log(content, write_to_debug=False, filename="logs/events.txt"):
    """
    Writes content to the event log file.
    Arguments:
    - content: String to be written in the log file.
    - write_to_debug: Boolean flag indicating whether the content is written to debug file or not.
    - filename: Name of the file where the content is written.
    Return: None
    """
    for i in range(len(filename.split("/")) - 1):
        if not os.path.exists("/".join(filename.split("/")[: i + 1])):
            os.mkdir("/".join(filename.split("/")[: i + 1]))

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


def write_dict_to_log(dictionary, filename="observation"):
    """
    Writes a dictionary to a log file.
    Arguments:
    - dictionary: The dictionary to be written to the log file.
    - filename: Name of the file where the content is written.
    Return: None
    """
    if os.environ.get("TINYAGI_DEBUG") not in ["1", "true", "True"]:
        return

    check_log_dirs()

    text = ""
    for key, value in dictionary.items():
        text += f"{key}: {value}\n"

    with open(f"./logs/loop/{filename}_{time.time()}.txt", "w") as f:
        f.write(text)


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
    if DEBUG:
        debug_log(
            f"openai_function_call\nprompt:\n{text}\nfunctions:\n{functions}\nresponse:\n{response}"
        )
        check_log_dirs()
        with open(f"./logs/loop/{name}_{time.time()}.txt", "w") as f:
            f.write(text)

    return response
