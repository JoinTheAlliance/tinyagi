import sys
from agentcomlink import send_message
from agentmemory import create_memory
from easycompletion import compose_function, compose_prompt

from agentshell.main import get_files_in_cwd, run_command

from tinyagi.constants import get_current_epoch


use_shell_prompt = """TIME: {{current_time}}
DATE: {{current_date}}
PLATFORM: {{platform}}
PROJECT DIRECTORY: {{cwd}}
PWD: {{cwd}}
{{relevant_knowledge}}
{{files_in_current_directory}}
{{events}}
{{summary}}
{{reasoning}}

Based on the action reasoning, what command should I run in my terminal? Please include all arguments, etc. on one line.
- Be concise. Don't hedge or say 'based on my reasoning', just say the reasoning and command
- Write a one-liner that I can run in my terminal (command)
- Then, write a summary of what output you expect to see (expected_output)
- If I ran a command, I probably should not run it again, so please don't suggest the same command twice in a row.
"""


def compose_use_shell_prompt(context):
    context["files_in_current_directory"] = (
        "\n" + "Files in the current directory:\n"
        "============================================\n"
        "" + ("\n".join(get_files_in_cwd())) + "\n"
        "============================================\n"
    )

    return compose_prompt(use_shell_prompt, context)


def use_shell_handler(arguments):
    command = arguments.get("command")
    banter = arguments.get("banter")
    message = {
        "message": banter,
    }
    send_message(message, "chat", source="shell")
    create_memory("events", "I ran a command in my shell:\n" + command, metadata={"epoch": get_current_epoch()})
    return run_command(command)


def get_actions():
    return [
        {
            "function": compose_function(
                name="use_shell",
                description="Use my computer's terminal. I can use this to access my operating system and interact with the world using bash and shell commands.",
                properties={
                    "banter": {
                        "type": "string",
                        "description": "Banter about using the shell terminal. Write something from my perspective, for me to say out loud. Hackerman!.",
                    },
                    "command": {
                        "type": "string",
                        "description": "The full command to run in my shell, including all arguments, etc.",
                    },
                    "expected_output": {
                        "type": "string",
                        "description": "Describe the expected output of the command. Write it from the user's perspective, in the first person, e.g. 'I should see the current working directory.'",
                    },
                },
                required_properties=["banter", "command", "expected_output"],
            ),
            "prompt": use_shell_prompt,
            "builder": compose_use_shell_prompt,
            "handler": use_shell_handler,
            "suggestion_after_actions": ["use_shell"],  # suggest self
            "never_after_actions": [],
        }
    ]
