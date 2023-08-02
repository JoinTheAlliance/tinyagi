import sys
from agentcomlink import send_message
# from agentmemory import create_memory
from easycompletion import compose_function, compose_prompt, count_tokens

from tinyagi.constants import get_current_epoch



import subprocess
import os
import time
from agentmemory import (
    create_memory,
    delete_memories,
    delete_memory,
    get_memories,
    get_memory,
    update_memory,
    wipe_category,
)


def get_files_in_cwd(shell_id=None):
    """
    Returns a list of files in the current directory of a specific shell.

    Parameters:
    shell_id (str): The unique identifier of the shell. If not specified, uses the current shell.

    Returns:
    list: A list of filenames in the current directory.
    """

    if shell_id is None:
        shell_id = get_current_shell()
    shell = get_memory("shell", shell_id)
    cwd = shell["metadata"]["cwd"]

    # call ls -alh in the current working directory
    result = subprocess.check_output(f"ls -alh {cwd}", shell=True)
    result_decoded = result.decode("utf-8").strip().split("\n")
    # remove the first line, which is the total size of the directory
    result_decoded = result_decoded[1:]
    # remove the last line, which is the current working directory
    # result_decoded = result_decoded[:-1]
    return result_decoded


def get_current_shell():
    """
    Returns the unique identifier of the current shell. If no shell is currently active, creates a new shell and returns its identifier.

    Returns:
    str: The unique identifier of the current shell.
    """

    current_shell = get_memories("shell", "shell", filter_metadata={"current": "True"})

    if len(current_shell) == 0:
        shell_id = create_memory("shell", "shell", metadata={"current": "True", "cwd": os.getcwd()})
    else:
        current_shell = current_shell[0]
        shell_id = current_shell["id"]

    return shell_id


def set_cwd(cwd, shell_id=None):
    """
    Sets the current working directory of a specific shell.

    Parameters:
    cwd (str): The new current working directory.
    shell_id (str): The unique identifier of the shell. If not specified, uses the current shell.
    """

    if shell_id is None:
        shell_id = get_current_shell()
    shell = get_memory("shell", shell_id)
    metadata = shell["metadata"]
    metadata["cwd"] = cwd
    update_memory("shell", shell_id, metadata=metadata)


def set_current_shell(shell_id):
    """
    Sets the current shell to the shell with the specified identifier.

    Parameters:
    shell_id (str): The unique identifier of the shell to be made current.
    """

    current_shell_id = get_current_shell()
    if current_shell_id == shell_id:
        return

    current_shell = get_memory("shell", current_shell_id)
    current_shell["metadata"]["current"] = "False"
    update_memory("shell", current_shell["id"], metadata=current_shell["metadata"])

    shell = get_memory("shell", shell_id)
    shell["metadata"]["current"] = "True"
    update_memory("shell", shell_id, metadata=shell["metadata"])


def get_history(shell_id=None, n_limit=20):
    """
    Returns the command history of a specific shell.

    Parameters:
    shell_id (str): The unique identifier of the shell. If not specified, uses the current shell.
    n_limit (int): The maximum number of history entries to return.

    Returns:
    list: A list of dictionaries, each representing a command and its result.
    """

    if shell_id is None:
        shell_id = get_current_shell()
    history = get_memories(
        "shell_history", filter_metadata={"shell_id": shell_id}, n_results=n_limit
    )
    return history


def get_history_formatted(shell_id=None):
    """
    Returns the command history of a specific shell in a human-readable format.

    Parameters:
    shell_id (str): The unique identifier of the shell. If not specified, uses the current shell.

    Returns:
    str: The command history in human-readable format.
    """

    history = get_history(shell_id)
    formatted_history = ""
    for item in history:
        metadata = item["metadata"]
        formatted_history += "Command: " + metadata.get("command", "") + "\n"
        formatted_history += "Success: " + str(metadata.get("success", "")) + "\n"
        if "output" in metadata and metadata["output"].strip() != "":
            formatted_history += "Output: " + metadata["output"].strip() + "\n"
        if "error" in metadata and metadata["error"].strip() != "":
            formatted_history += "Error: " + metadata["error"].strip() + "\n"
        formatted_history += "---\n"  # separator between each command history
    return formatted_history


def add_to_shell_history(shell_id, command, success, output, error=None):
    """
    Adds a command and its result to the history of a specific shell.

    Parameters:
    shell_id (str): The unique identifier of the shell.
    command (str): The command that was executed.
    success (bool): Whether the command was successful.
    output (str): The output of the command.
    error (str): Any error messages produced by the command.
    """

    timestamp = time.time()

    formatted_memory = """\
    Command: {command}
    Timestamp: {timestamp}
    Success: {success}
    Output: {output}
    Error: {error}"""

    create_memory(
        "shell_history",
        formatted_memory,
        metadata={
            "shell_id": shell_id,
            "command": str(command),
            "success": str(success),
            "output": str(output or ""),
            "error": str(error or ""),
            "timestamp": timestamp,
        },
    )


def clear_history(shell_id):
    """
    Clears the command history of a specific shell.

    Parameters:
    shell_id (str): The unique identifier of the shell.
    """

    delete_memories("shell_history", metadata={"shell_id": shell_id})


def wipe_all():
    """
    Clears all shell and shell history data.
    """

    wipe_category("shell_history")
    wipe_category("shell")


def list_active_shells():
    """
    Returns a list of active shells.

    Returns:
    list: A list of shell identifiers.
    """

    shells = get_memories("shell")
    return [shell["id"] for shell in shells]


def close_shell(shell_id):
    """
    Closes a specific shell, clearing its history.

    Parameters:
    shell_id (str): The unique identifier of the shell.
    """

    delete_memories("shell_history", metadata={"shell_id": shell_id})
    delete_memory("shell", shell_id)


def new_shell():
    """
    Creates a new shell and returns its unique identifier.

    Returns:
    str: The unique identifier of the new shell.
    """

    shell_id = create_memory(
        "shell", "shell", metadata={"current": "False", "cwd": os.getcwd()}
    )
    return shell_id


def get_cwd(shell_id=None):
    """
    Returns the current working directory of a specific shell.

    Parameters:
    shell_id (str): The unique identifier of the shell. If not specified, uses the current shell.

    Returns:
    str: The current working directory of the shell.
    """

    if shell_id is None:
        shell_id = get_current_shell()
    shell = get_memory("shell", shell_id)
    return shell["metadata"]["cwd"]


def run_command(command, shell_id=None):
    """
    Runs a command in a specific shell and adds it to the shell's history.

    Parameters:
    command (str): The command to execute.
    shell_id (str): The unique identifier of the shell. If not specified, uses the current shell.

    Returns:
    bool: True if the command was successful, False otherwise.
    """

    if shell_id is None:
        shell_id = get_current_shell()
    shell = get_memory("shell", shell_id)
    cwd = shell["metadata"]["cwd"]
    # Execute command in the current working directory
    command_to_run = f"cd {cwd} && {command}"
    process = subprocess.run(command_to_run, shell=True, text=True, capture_output=True)

    # If the process completed successfully
    if process.returncode == 0:
        result = process.stdout
        error = process.stderr

        print("*********************************************** result is")
        print(result)
        print("error is")
        print(error)

        success = error == "" or error is None

        result_split = result.strip().split("\n")
        updated_directory = result_split[-1]
        if os.path.isdir(updated_directory):
            cwd = updated_directory
            set_cwd(cwd, shell_id)
            result_split = result_split[:-1]
            result_split = "\n".join(result_split)
        else:
            result_split = "\n".join(result_split)

        print('result_split')
        print(result_split)

        add_to_shell_history(shell_id, command, success="True", output=result)
        return { "success": success, "output": result_split, "error": error }

    else:  # If the process did not complete successfully
        output = process.stdout
        error = process.stderr
        add_to_shell_history(
            shell_id, command, success="False", output=output, error=error
        )
        return { "success": False, "output": output, "error": error }







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
    output = run_command(message)
    duration = count_tokens(banter) / 3.0
    time.sleep(duration)
    return output


def get_actions():
    return [
        {
            "function": compose_function(
                name="use_shell",
                description="Use my computer's terminal. I can use this to access my operating system and interact with the world using bash and shell commands.",
                properties={
                    "banter": {
                        "type": "string",
                        "description": "Banter about what command I'm about to use, why and what I expect th output should be. Write something from my perspective.",
                    },
                    "command": {
                        "type": "string",
                        "description": "The full command to run in my shell, including all arguments, etc. Should be unique and different from previous commands",
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
