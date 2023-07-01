import os
import platform
import subprocess

from core.memory import add_event
from core.constants import agent_name


def get_skills():
    return {
        "execute_shell_command": {
            "payload": {
                "name": "execute_shell_command",
                "description": "Execute a shell command using standard linux commands. You are running on "
                + platform.system()
                + " and have full operating system access. Use this to explore. You can curl, grep, cat, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "A description of what the command will do",
                        },
                        "command": {
                            "type": "string",
                            "description": "The shell command to run. Make sure it's all on one line and properly escaped.",
                        },
                    },
                    "required": ["description", "command"],
                },
            },
            "handler": run_shell_command,
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
        },
    }


def write_python_file(arguments):
    file_name = arguments.get("file_name", None)
    file_contents = arguments.get("file_contents", None)
    command = "echo " + file_contents + " > " + file_name
    try:
        # call the command
        os.system(command)
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
        result = subprocess.check_output(command, shell=True)
        # transform result with utf-8 encoding
        result = result.decode("utf-8")

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
        result = subprocess.check_output(command, shell=True)

        result = result.decode("utf-8")

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
        result = subprocess.check_output(command, shell=True)
        result = result.decode("utf-8")

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


def get_current_working_directory(arguments):
    description = arguments.get("description", None)
    add_event(
        "I'm getting the current working directory because: " + description,
        agent_name,
        type="shell_command",
    )
    cwd = os.getcwd()
    add_event(
        "The current working directory is: " + cwd,
        agent_name,
        type="shell_command",
    )

if __name__ == "__main__":
    # Test get_current_working_directory function
    try:
        get_current_working_directory({"description": "Testing get_current_working_directory function"})
    except Exception as e:
        print(f"get_current_working_directory function failed with exception: {e}")

    # Test run_shell_command function
    try:
        run_shell_command({"description": "Testing run_shell_command function", "command": "echo 'Hello World'"})
    except Exception as e:
        print(f"run_shell_command function failed with exception: {e}")

    # Test pip_install function
    try:
        pip_install({"package": "pytest"})  # We're using pytest for an example, you can replace it with any safe package
    except Exception as e:
        print(f"pip_install function failed with exception: {e}")

    # Test curl function
    try:
        curl({"url": "https://www.google.com", "arguments": ""})
    except Exception as e:
        print(f"curl function failed with exception: {e}")

    # Test write_python_file function
    try:
        write_python_file({"file_name": "test.py", "file_contents": "print('Hello World')"})
    except Exception as e:
        print(f"write_python_file function failed with exception: {e}")

    # Cleaning up the created file after testing
    try:
        os.remove("test.py")
    except Exception as e:
        print(f"Error while cleaning up the test file: {e}")
    print("All tests complete")
