import os
import time
from core.constants import agent_name


# compose a prompt from a template and a list of values to replace
def compose_prompt(prompt_template_name, values_to_replace):
    prompt_template = get_prompt_template(prompt_template_name)

    prompt_template = replace_all_in_string(prompt_template, values_to_replace)

    return prompt_template


# replacements is a key value dictionary
def replace_all_in_string(string, replacements):
    for key, value in replacements.items():
        string = string.replace("{" + key + "}", value)
    return string


def get_agent_name():
    return agent_name


def get_prompt_template(template_name):
    # read the file in templates/template_name.txt
    with open("templates/" + template_name + ".txt", "r") as f:
        return f.read()


def messages_to_dialogue(messages):
    # dialogue is a string of <sender>: <message>\n
    dialogue = ""
    for i in range(len(messages["ids"])):
        dialogue += (
            messages["metadatas"][i]["event_creator"]
            + ": "
            + messages["documents"][i]
            + "\n"
        )
    print("dialogue", dialogue)
    return dialogue

def events_to_stream(messages):
    event_stream = ""
    for i in range(len(messages["ids"])):
        event_stream += (
            messages["metadatas"][i]["event_creator"]
            + ": "
            + messages["documents"][i]
            + "\n"
        )
    return event_stream

# write to the main log stream
# this will be referenced by the agent
def write_log(text, header=None):
    print(text)
    # add timestamp
    prefix = get_formatted_time() + "|" + get_current_date() + "|>"
    if header != None:
        prefix += header + "\n"
    text = prefix + text
    # if logs directory does not exist, create it
    os.makedirs("logs", exist_ok=True)

    if not os.path.exists("logs/feed.log"):
        with open("logs/feed.log", "w") as f:
            f.write("")

    with open("logs/feed.log", "a") as f:
        f.write(text + "\n")

def get_formatted_time():
    current_time = time.time()
    formatted_time = time.strftime("%H:%M:%S", time.localtime(current_time))
    # is it AM or PM?
    if int(formatted_time.split(":")[0]) > 12:
        formatted_time += " PM"
    else:
        formatted_time += " AM"
    return formatted_time


def get_current_date():
    current_time = time.time()
    current_date = time.strftime("%Y-%m-%d", time.localtime(current_time))
    return current_date
