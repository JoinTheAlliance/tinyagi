import subprocess
import uuid

from connectors.terminal import terminal
from core.memory import add_event
from core.constants import agent_name


def create_tab(arguments):
    session_id = str(uuid.uuid4())
    terminal.get_sessions()[session_id] = {
        "last_command": None,
        "last_output": None,
        "current_directory": terminal.get_current_directory(),
    }
    terminal.set_current_session_id(session_id)
    add_event(
        "I created a new tab in the terminal for session ID " + session_id,
        agent_name,
        type="terminal_command",
    )
    return session_id


def switch_to(arguments):
    session_id = arguments.get("session_id")
    if session_id in terminal.get_sessions():
        terminal.set_current_session_id(session_id)
        add_event(
            "I switched to the terminal for session ID "
            + session_id
            + ". Now I can use the terminal by calling run_command.",
            agent_name,
            type="terminal_command",
        )
    else:
        session_id = terminal.current_session_id
        add_event(
            "I tried to switch to a different session on the terminal, but the session ID didn't exist. So I got the default session, which has the session ID "
            + session_id,
            agent_name,
            type="terminal_command",
        )


def close_tab(arguments):
    session_id = arguments.get("session_id")
    if session_id in terminal.get_sessions():
        del terminal.get_sessions()[session_id]
        if terminal.current_session_id == session_id:
            terminal.set_current_session_id(None)
        add_event(
            "I closed a tab in the terminal for session ID " + session_id,
            agent_name,
            type="terminal_command",
        )
    else:
        add_event(
            "I tried to close a tab in the terminal, but it didn't exist. The session ID was "
            + session_id,
            agent_name,
            type="terminal_command",
        )
        raise ValueError(f"Session ID {session_id} does not exist.")


def get_tabs(arguments):
    add_event(
        "I got a list of tabs from the terminal:\n"
        + str(terminal.get_sessions())
        + "\n"
        + "Next I can run a command in the terminal (run_command function).",
        agent_name,
        type="terminal_command",
    )

    return terminal.get_sessions()


def get_tabs_formatted_as_string(arguments):
    formatted_string = ""
    for session_id, info in terminal.get_sessions().items():
        formatted_string += f"Session ID: {session_id}\n"
        formatted_string += f"Last Command: {info['last_command']}\n"
        formatted_string += f"Last Output: {info['last_output']}\n"
        formatted_string += f"Current Directory: {info['current_directory']}\n"
        formatted_string += "----\n"
    add_event(
        "I got a list of tabs from the terminal:\n"
        + formatted_string
        + "\n"
        + "Next I can run a command in the terminal (run_command function).",
        agent_name,
        type="terminal_command",
    )
    return formatted_string


def run_command(arguments):
    command = arguments.get("command")
    if not terminal.current_session_id:
        raise ValueError("No active session.")
    session = terminal.get_sessions()[terminal.current_session_id]
    try:
        result = subprocess.check_output(
            command, shell=True, cwd=session["current_directory"]
        )
    except subprocess.CalledProcessError as e:
        result = e.output

    session["last_command"] = command
    session["last_output"] = result
    command_trimmed = command[:100]
    add_event(
        "I ran the command: "
        + command_trimmed
        + "\n"
        + "The output was: "
        + result.decode("utf-8"),
        agent_name,
        type="terminal_command",
    )
    return result.decode("utf-8")


def change_current_working_directory(arguments):
    directory = arguments.get("directory", None)
    try:
        terminal.set_current_directory(directory)
        add_event(
            f"I have changed the current working directory to: {directory}",
            agent_name,
            type="shell_command",
        )
    except Exception as e:
        add_event(
            f"I tried to change the current working directory to: {directory}, but I got an error: {str(e)}",
            agent_name,
            type="shell_command",
        )


def get_current_working_directory(arguments):
    description = arguments.get("description", None)
    add_event(
        "I'm getting the current working directory because: " + description,
        agent_name,
        type="shell_command",
    )
    cwd = terminal.get_current_directory()
    add_event(
        "The current working directory is: " + cwd,
        agent_name,
        type="shell_command",
    )


def write_python_file(arguments):
    file_name = arguments.get("file_name", None)
    file_contents = arguments.get("file_contents", None)
    command = "echo " + file_contents + " > " + file_name
    try:
        # Use terminal's run_command method
        run_command({"command": command})
        add_event(
            "I am writing a Python file: ```"
            + file_name
            + "```\nWith the contents: ```"
            + file_contents
            + "```",
            agent_name,
            type="shell_command",
        )
    except Exception as e:
        add_event(
            "I tried to write a Python file: ```"
            + file_name
            + "```\nWith the contents: ```"
            + file_contents
            + "```\nBut I got an error: "
            + str(e),
            agent_name,
            type="shell_command",
        )


def curl(arguments):
    url = arguments.get("url", None)
    arguments = arguments.get("arguments", None)
    command = "curl " + url + " " + arguments

    # try to execute the command
    try:
        result = run_command({"command": command})

        # trim the result
        result = result[:2000] + (result[2000:] and "..")
        # trim command to first 100 characters
        add_event(
            "I successfully ran the curl command: ```"
            + command
            + "```\nThe result was: "
            + result,
            agent_name,
            type="shell_command",
        )

    except Exception as e:
        add_event(
            "I tried to run the curl command: ```"
            + command
            + "```\nBut I got an error: "
            + str(e),
            agent_name,
            type="shell_command",
        )


def change_current_working_directory(arguments):
    directory = arguments.get("directory", None)
    try:
        terminal.set_current_directory(directory)
        add_event(
            f"I have changed the current working directory to: {directory}",
            agent_name,
            type="shell_command",
        )
    except Exception as e:
        add_event(
            f"I tried to change the current working directory to: {directory}, but I got an error: {str(e)}",
            agent_name,
            type="shell_command",
        )


def get_current_working_directory(arguments):
    description = arguments.get("description", None)
    add_event(
        "I'm getting the current working directory because: " + description,
        agent_name,
        type="shell_command",
    )
    cwd = terminal.get_current_directory()
    add_event(
        "The current working directory is: " + cwd,
        agent_name,
        type="shell_command",
    )


def write_python_file(arguments):
    file_name = arguments.get("file_name", None)
    file_contents = arguments.get("file_contents", None)
    command = "echo " + file_contents + " > " + file_name
    try:
        # Use terminal's run_command method
        run_command({"command": command})
        add_event(
            "I am writing a Python file: ```"
            + file_name
            + "```\nWith the contents: ```"
            + file_contents
            + "```",
            agent_name,
            type="shell_command",
        )
    except Exception as e:
        add_event(
            "I tried to write a Python file: ```"
            + file_name
            + "```\nWith the contents: ```"
            + file_contents
            + "```\nBut I got an error: "
            + str(e),
            agent_name,
            type="shell_command",
        )


def curl(arguments):
    url = arguments.get("url", None)
    arguments = arguments.get("arguments", None)
    command = "curl " + url + " " + arguments

    # try to execute the command
    try:
        result = run_command({"command": command})

        # trim the result
        result = result[:2000] + (result[2000:] and "..")
        # trim command to first 100 characters
        add_event(
            "I successfully ran the curl command: ```"
            + command
            + "```\nThe result was: "
            + result,
            agent_name,
            type="shell_command",
        )

    except Exception as e:
        add_event(
            "I tried to run the curl command: ```"
            + command
            + "```\nBut I got an error: "
            + str(e),
            agent_name,
            type="shell_command",
        )


def pip_install(arguments):
    package = arguments.get("package", None)
    command = "pip install " + package

    # try to execute the command
    try:
        result = run_command({"command": command})

        # trim command to first 100 characters
        add_event(
            "I successfully ran the command: ```"
            + command
            + "```\nThe result was: "
            + result,
            agent_name,
            type="shell_command",
        )

    except Exception as e:
        add_event(
            "I tried to run the command: ```"
            + command
            + "```\nBut I got an error: "
            + str(e),
            agent_name,
            type="shell_command",
        )


def run_shell_command(arguments):
    description = arguments.get("description", None)
    command = arguments.get("command", None)

    add_event(
        "I'm running a shell command with the command: " + command,
        agent_name,
        type="shell_command",
    )

    # try to execute the command
    try:
        result = run_command({"command": command})

        # trim command to first 100 characters
        add_event(
            "I successfully ran the command: "
            + command
            + "\nThe result was: "
            + result,
            agent_name,
            type="shell_command",
        )

    except Exception as e:
        add_event(
            "I tried to run the command: "
            + command
            + "\nBut I got an error: "
            + str(e),
            agent_name,
            type="shell_command",
        )


def get_skills():
    return {
        "terminal_create_tab": {
            "payload": {
                "name": "terminal_create_tab",
                "description": "You have access to a terminal. This function creates a new tab in your terminal so you can switch to it.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "What am I doing with this new terminal tab?.",
                        },
                    },
                    "required": ["description"],
                },
            },
            "handler": create_tab,
        },
        "terminal_switch_to": {
            "payload": {
                "name": "terminal_switch_to",
                "description": "Switch to an existing tab in your terminal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "The id of the session/tab to switch to.",
                        },
                    },
                    "required": ["session_id"],
                },
            },
            "handler": switch_to,
        },
        "terminal_close_tab": {
            "payload": {
                "name": "terminal_close_tab",
                "description": "Close an existing tab in your terminal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "The id of the session/tab to close.",
                        },
                    },
                    "required": ["session_id"],
                },
            },
            "handler": close_tab,
        },
        "terminal_get_tabs": {
            "payload": {
                "name": "terminal_get_tabs",
                "description": "Get all tabs in a dictionary format from the terminal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "What am I doing with this new terminal tab?.",
                        },
                    },
                    "required": ["description"],
                },
            },
            "handler": get_tabs,
        },
        "terminal_get_tabs_formatted_as_string": {
            "payload": {
                "name": "terminal_get_tabs_formatted_as_string",
                "description": "Get all tabs in a human-readable string format from the terminal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "What am I doing with this new terminal tab?.",
                        },
                    },
                    "required": ["description"],
                },
            },
            "handler": get_tabs_formatted_as_string,
        },
        "terminal_run_command": {
            "payload": {
                "name": "terminal_run_command",
                "description": "Run a command in the current tab of your terminal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to run in your terminal.",
                        },
                    },
                    "required": ["command"],
                },
            },
            "handler": run_command,
        },
        "use_terminal": {
            "payload": {
                "name": "use_terminal",
                "description": "Use the terminal to run a shell command.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to run in your terminal.",
                        },
                    },
                    "required": ["command"],
                },
            },
            "handler": run_command,
        },
        "get_current_working_directory": {
            "payload": {
                "name": "get_current_working_directory",
                "description": "Write the current working directory into the event stream. This is useful for knowing where I am currently when I'm running and want to execute shell commands.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Why do I want to get the current working directory?.",
                        },
                    },
                    "required": ["description"],
                },
            },
            "handler": get_current_working_directory,
        },
        "pip_install": {
            "payload": {
                "name": "pip_install",
                "description": "Install a Python package using pip. This is useful for installing packages that I don't have yet.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "package": {
                            "type": "string",
                            "description": "The name of the package to install",
                        }
                    },
                    "required": ["package"],
                },
            },
            "handler": pip_install,
        },
        "curl": {
            "payload": {
                "name": "curl",
                "description": "Execute a curl command. This is useful for downloading files from the internet.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The url to download from",
                        },
                        "arguments": {
                            "type": "string",
                            "description": "The arguments to pass to curl. Make sure it's all on one line and properly escaped.",
                        },
                    },
                    "required": ["url", "arguments"],
                },
            },
            "handler": curl,
        },
        "write_python_file": {
            "payload": {
                "name": "write_python_file",
                "description": "Write a Python file to disk. This is useful for creating new skills.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": "The name of the file to write",
                        },
                        "file_contents": {
                            "type": "string",
                            "description": "The contents of the file to write",
                        },
                    },
                    "required": ["file_name", "file_contents"],
                },
            },
            "handler": write_python_file,
        }
    }


if __name__ == "__main__":
    # Test get_current_working_directory function
    try:
        get_current_working_directory(
            {"description": "Testing get_current_working_directory function"}
        )
    except Exception as e:
        print(f"get_current_working_directory function failed with exception: {e}")

    # Test run_shell_command function
    try:
        run_shell_command(
            {
                "description": "Testing run_shell_command function",
                "command": "echo 'Hello World'",
            }
        )
    except Exception as e:
        print(f"run_shell_command function failed with exception: {e}")

    # Test pip_install function
    try:
        pip_install(
            {"package": "pytest"}
        )  # We're using pytest for an example, you can replace it with any safe package
    except Exception as e:
        print(f"pip_install function failed with exception: {e}")

    # Test curl function
    try:
        curl({"url": "https://www.google.com", "arguments": ""})
    except Exception as e:
        print(f"curl function failed with exception: {e}")

    # Test write_python_file function
    try:
        write_python_file(
            {"file_name": "test.py", "file_contents": "print('Hello World')"}
        )
    except Exception as e:
        print(f"write_python_file function failed with exception: {e}")

    print("All tests complete")
