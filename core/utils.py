import os
import time
from constants import debug

def messages_to_dialogue(messages):
    # dialogue is a string of <sender>: <message>\n
    dialogue = ""
    for i in range(len(messages["ids"])):
        dialogue += messages["metadatas"][i]["sender"] + ": " + messages["documents"][i] + "\n"
    return dialogue

# write to the main log stream
# this will be referenced by the agent
def write_log(text):
    print(text)
    # if logs directory does not exist, create it
    os.makedirs("logs", exist_ok=True)
    # if logs/log.txt doesn't exist, write it
    if not os.path.exists("logs/log.txt"):
        with open("logs/log.txt", "w") as f:
            f.write("")
    # write to logs/log.txt
    with open("logs/log.txt", "a") as f:
        f.write(text + "\n")
    write_debug_log(text)


# write to the debug log
# Debug logs are helpful to understand the full agent stream, but can be very slow
# Set DEBUG=False in .env to disable debug logs when deploying
def write_debug_log(text):
    if debug == False:
        return
    # if logs directory does not exist, create it
    os.makedirs("logs", exist_ok=True)
    # if logs/log.txt doesn't exist, write it
    if not os.path.exists("logs/debug_log.txt"):
        with open("logs/debug_log.txt", "w") as f:
            f.write("")
    # write to logs/log.txt
    with open("logs/debug_log.txt", "a") as f:
        f.write(text + "\n")


def get_formatted_time():
    current_time = time.time()
    formatted_time = time.strftime("%H:%M:%S", time.localtime(current_time))
    return formatted_time

def get_current_date():
    current_time = time.time()
    current_date = time.strftime("%Y-%m-%d", time.localtime(current_time))
    return current_date