# actions/shell.py

import subprocess
import os
import time
import re

from easycompletion import compose_function, compose_prompt, count_tokens

from tinyagi.core.events import create_event

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


run_command_prompt = """TIME: {{current_time}}
DATE: {{current_date}}
PLATFORM: {{platform}}
PROJECT DIRECTORY: {{cwd}}
PWD: {{current_working_directory}}
{{files_in_current_directory}}
{{relevant_knowledge}}
{{events}}
{{summary}}
{{reasoning}}
TASK: Based on the action reasoning, what command should I run in my terminal? Please include all arguments, etc. on one line.
- Write a one-liner that I can run in my terminal (command)
- Then, write a summary of what output you expect to see (expected_output)
- If I ran a command, I probably should not run it again, so please don't suggest the same command twice in a row. Since you already know the cwd and files in the current directory, you shouldn't just run ls or pwd.
- DO NOT suggest running any commands that will provide us with the same information we already have. For example, if we already know the current working directory, don't suggest running pwd.
"""


def compose_run_command_prompt(observation):
    observation["current_working_directory"] = current_working_directory
    observation["files_in_current_directory"] = (
        "\n" + "Files in the current directory (ls -alh):\n"
        "============================================\n"
        "" + ("\n".join(get_files_in_current_directory())) + "\n"
        "============================================\n"
    )

    return compose_prompt(run_command_prompt, observation)


def run_shell_command(arguments):
    global current_working_directory

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
                + filename
                + "`\n"
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
            "function": compose_function(
                name="run_shell_command",
                description="Run a shell command in my terminal. I can use this to access my operating system and interact with the world, or to call some code. This is a full terminal, so any code that works in bash will work.",
                properties={
                    "command": {
                        "type": "string",
                        "description": "The full command to run in my shell, including all arguments, etc.",
                    },
                    "expected_output": {
                        "type": "string",
                        "description": "Describe the expected output of the command. Write it from the user's perspective, in the first person, e.g. 'I should see the current working directory.'",
                    },
                },
                required_properties=["command", "expected_output"],
            ),
            "prompt": run_command_prompt,
            "composer": compose_run_command_prompt,
            "handler": run_shell_command,
            "suggestion_after_actions": ["run_shell_command"],  # suggest self
            "never_after_actions": [],
        }
    ]


if __name__ == "__main__":
    # Test get_current_working_directory action
    try:
        run_shell_command({"command": "ls"})
    except Exception as e:
        print(f"get_current_working_directory action failed with exception: {e}")
    print("All tests complete")
