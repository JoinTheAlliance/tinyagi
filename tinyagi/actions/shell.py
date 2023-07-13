# actions/shell.py

import subprocess

from tinyagi.core.events import create_event

run_command_prompt_template = """
I know these relevant things:
{{knowledge}}

Summary of Recent Events:
{{summaries}}

Recent Events:
{{events_from_last_epoch}}

Action Reasoning:
{{action_reasoning}}

Based on the action reasoning, what command should I run in my terminal? Please include all arguments, etc. on one line.
Also include what outcome I should expect, in plan English. I will be writing down the "expected_output" field in my notes so please write it from my perspective.
"""


def run_shell_command(arguments):
    command = arguments.get("command")
    try:
        result = subprocess.check_output(command, shell=True)
        result_decoded = result.decode("utf-8")
        # if result_decoded is more than 10 lines, trim to only the last 10 lines
        if len(result_decoded.split("\n")) > 10:
            result_decoded = "\n".join(result_decoded.split("\n")[-10:])
        create_event(
            "I ran the command `"
            + command
            + "` and I got the following result:\n"
            + result_decoded,
            type="action",
            subtype="run_shell_command",
        )
        return True
    except subprocess.CalledProcessError as e:
        result = e.output
        create_event(
            "I ran the command `"
            + command
            + "` and I got the following error:\n"
            + result.decode("utf-8"),
            type="action",
            subtype="run_shell_command",
        )
        return False


def get_actions():
    return [
        {
            "function": {
                "name": "run_shell_command",
                "description": "Run a shell command in my terminal. I can use this to access my operating system and interact with the world, or to call some code. Can also be used to access curl, wget, and other tools, or to see the current working directory.",
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
