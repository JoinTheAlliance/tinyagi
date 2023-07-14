# actions/shell.py

import subprocess
import os
import time
import re

from easycompletion import count_tokens, trim_prompt

from tinyagi.core.events import create_event
from tinyagi.core.actions import get_actions as get_all_actions

SHELL_COMMAND_TOKEN_LIMIT = 2048

# Initial directory
original_cwd = os.getcwd()
current_working_directory = original_cwd


def get_files_in_current_directory():
    # call ls -alh in the current working directory
    result = subprocess.check_output(f"ls -alh {current_working_directory}", shell=True)
    result_decoded = result.decode("utf-8").strip().split("\n")
    # remove the first line, which is the total size of the directory
    result_decoded = result_decoded[1:]
    # remove the last line, which is the current working directory
    result_decoded = result_decoded[:-1]
    return result_decoded


run_command_prompt_template = """TIME: {{current_time}}
DATE: {{current_date}}
PLATFORM: {{platform}}
PROJECT DIRECTORY: {{cwd}}
PWD: {{current_working_directory}}

Files in the current directory (ls -alh):
### BEGIN FILES IN CURRENT DIRECTORY ###
{{files_in_current_directory}}
### END FILES IN CURRENT DIRECTORY ###

I know these relevant things:
{{knowledge}}

Recent Events are formatted as follows:
Epoch # | <Type>::<Subtype> (Creator): <Event>
============================================
{{events}}

Summary of Last Epoch:
{{summary}}

Action Reasoning:
{{reasoning}}

TASK: Based on the action reasoning, what command should I run in my terminal? Please include all arguments, etc. on one line.
- Write a one-liner that I can run in my terminal (command)
- Then, write a summary of what output you expect to see (expected_output)
- If I ran a command, I probably should not run it again, so please don't suggest the same command twice in a row. Since you already know the cwd and files in the current directory, you shouldn't just run ls or pwd.
- DO NOT suggest running any commands that will provide us with the same information we already have. For example, if we already know the current working directory, don't suggest running pwd.
"""

# Replace {{files_in_current_directory}} with the files in the current directory
# This ill be auto-replaced later but needs to be initialized once
run_command_prompt_template = run_command_prompt_template.replace(
    "{{files_in_current_directory}}", "\n".join(get_files_in_current_directory())
).replace("{{current_working_directory}}", current_working_directory)


def compose_prompt_with_local_variables():
    prompt_lines = run_command_prompt_template.split("\n")

    # now find the line that starts with "CWD: "
    for i, line in enumerate(prompt_lines):
        if line.startswith("PWD:"):
            # replace the line with the current working directory
            prompt_lines[i] = f"PWD: {current_working_directory}"

    line_number_start = None
    line_number_end = None

    # get the index of the line that contains "### BEGIN FILES IN CURRENT DIRECTORY ###"
    for i, line in enumerate(prompt_lines):
        if line.startswith("### BEGIN FILES IN CURRENT DIRECTORY ###"):
            line_number_start = i + 1
            # now iterate through and get the index of the line that contains "### END FILES IN CURRENT DIRECTORY ###"
            for j, line in enumerate(prompt_lines):
                if line.startswith("### END FILES IN CURRENT DIRECTORY ###"):
                    line_number_end = j
                    break

    if line_number_start is not None and line_number_end is not None:
        files_in_current_directory = get_files_in_current_directory()
        # replace the lines between line_number_start and line_number_end with the files in the current directory
        prompt_lines[line_number_start:line_number_end] = files_in_current_directory

    # now join the prompt lines back together
    prompt = "\n".join(prompt_lines)
    return prompt


def run_shell_command(arguments):
    global current_working_directory

    run_command_prompt_template = compose_prompt_with_local_variables()
    get_all_actions()["run_shell_command"]["prompt"] = run_command_prompt_template

    command = arguments.get("command")
    # Execute command in the current working directory
    command_to_run = f"cd {current_working_directory} && {command}"
    process = subprocess.run(command_to_run, shell=True, text=True, capture_output=True)

    # If the process completed successfully
    if process.returncode == 0:
        result = process.stdout

        result_split = result.strip().split("\n")
        updated_directory = result_split[-1]

        if os.path.isdir(updated_directory):
            current_working_directory = updated_directory
            result_split = result_split[:-1]
            result_split = "\n".join(result_split)
        else:
            result_split = "\n".join(result_split)

        result_tokens = count_tokens(result)
        if result_tokens > SHELL_COMMAND_TOKEN_LIMIT:
            # create a filename from the timestamp and command
            command_string = re.sub(r"[^a-zA-Z0-9_]+", "", command)
            # trim command string to under 10 characters
            command_string = command_string[:10]
            # check if ./logs/shell_output/ exists and create it if it doesn't
            if not os.path.isdir(f"{original_cwd}/logs/shell_output"):
                os.mkdir(f"{original_cwd}/logs/shell_output")
            filename = (
                f"{original_cwd}/logs/shell_output/{command_string}_{time.time()}.txt"
            )
            # Save the result to a file
            with open(filename, "w") as f:
                f.write(result)

            create_event(
                "I ran the command `"
                + command
                + "`\n"
                + "(NOTE: The output may be truncated. The complete output has been saved to `"
                + filename + "`\n"
                + "I got the following result:\n"
                + result,
                type="action",
                subtype="run_shell_command",
            )
            return True

        event_text = (
            "I ran the command `" + command + "` in `" + current_working_directory
        )
        result = result.strip()
        if result != "":
            event_text += "` and I got the following result:\n" + result
        create_event(event_text, type="action", subtype="run_shell_command")
        return True

    else:  # If the process did not complete successfully
        error_message = process.stderr
        create_event(
            f"I ran the command `{command}` in `{current_working_directory}` and got an error\n: {error_message.strip()}",
            type="action",
            subtype="run_shell_command",
        )
        return False


def get_actions():
    return [
        {
            "function": {
                "name": "run_shell_command",
                "description": "Run a shell command in my terminal. I can use this to access my operating system and interact with the world, or to call some code. This is a full terminal, so any code that works in bash will work.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The full command to run in my shell, including all arguments, etc.",
                        },
                        "expected_output": {
                            "type": "string",
                            "description": "Describe the expected output of the command. Write it from the user's perspective, in the first person, e.g. 'I should see the current working directory.'",
                        },
                    },
                    "required": ["command", "expected_output"],
                },
            },
            "suggestion_after_actions": ["run_shell_command"],  # suggest self
            "never_after_actions": [],
            "prompt": run_command_prompt_template,
            "handler": run_shell_command,
        }
    ]


if __name__ == "__main__":
    # Test get_current_working_directory action
    try:
        run_shell_command({"command": "ls"})
    except Exception as e:
        print(f"get_current_working_directory action failed with exception: {e}")
    print("All tests complete")
