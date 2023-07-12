# actions/shell.py

import subprocess

def run_command(arguments):
    command = arguments.get("command")
    try:
        result = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as e:
        result = e.output

    return result.decode("utf-8")


def get_actions():
    return {
       "run_shell_command": {
            "function": {
                "name": "run_shell_command",
                "description": "Run a shell command in your shell. Use this to access your operating system and interact with the world, or to call some code. Can also be used to access curl, wget, and other tools, or to see the current working directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The full command to run in your shell, including all arguments, etc.",
                        },
                    },
                    "required": ["command"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": run_command,
        }
    }


if __name__ == "__main__":
    # Test get_current_working_directory action
    try:
        run_command(
            {"command": "ls"}
        )
    except Exception as e:
        print(f"get_current_working_directory action failed with exception: {e}")
    print("All tests complete")
