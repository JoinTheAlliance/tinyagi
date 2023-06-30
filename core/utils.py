import os
import time
from constants import debug, agent_name

# compose a prompt from a template and a list of values to replace
def compose_prompt(prompt_template_name, values_to_replace):
    prompt_template = get_prompt_template(prompt_template_name)

    prompt_template = replace_all_in_string(prompt_template, values_to_replace)

    write_debug_log(prompt_template_name + ":\n" + prompt_template)

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