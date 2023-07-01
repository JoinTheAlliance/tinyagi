import os
import subprocess
import uuid
from collections import defaultdict
from typing import Dict

from core.memory import add_event
from core.constants import agent_name


class VirtualTerminal:
    def __init__(self):
        self.sessions: Dict[str, Dict] = defaultdict(dict)
        self.current_session_id = str(uuid.uuid4())
        self.current_directory = os.getcwd()
        # start with one tab
        self.get_sessions()[self.current_session_id] = {
            "last_command": None,
            "last_output": None,
            "current_directory": self.current_directory,
        }

    def get_current_session_id(self):
        return self.current_session_id

    def set_current_session_id(self, session_id):
        self.current_session_id = session_id

    def get_sessions(self):
        return self.sessions

    def set_sessions(self, sessions):
        self.sessions = sessions

    def get_current_directory(self):
        return self.current_directory

    def set_current_directory(self, directory):
        self.current_directory = directory


terminal = VirtualTerminal()


def create_tab(arguments):
    session_id = str(uuid.uuid4())
    terminal.get_sessions()[session_id] = {
        "last_command": None,
        "last_output": None,
        "current_directory": terminal.get_current_directory(),
    }
    terminal.set_current_session_id(session_id)
    add_event(
        "I created a new tab in the virtual terminal for session ID " + session_id, agent_name, type="virtual_terminal_command"
    )
    return session_id


def switch_to(arguments):
    session_id = arguments.get("session_id")
    if session_id in terminal.get_sessions():
        terminal.set_current_session_id(session_id)
        add_event(
            "I switched to the virtual terminal for session ID " + session_id, agent_name, type="virtual_terminal_command"
        )
    else:
        add_event(
            "I tried to switch to the virtual terminal, but it didn't exist. The session ID was " + session_id,
            agent_name,
            type="virtual_terminal_command",
        )
        raise ValueError(f"Session ID {session_id} does not exist.")


def close_tab(arguments):
    session_id = arguments.get("session_id")
    if session_id in terminal.get_sessions():
        del terminal.get_sessions()[session_id]
        if terminal.get_current_session_id() == session_id:
            terminal.set_current_session_id(None)
        add_event(
            "I closed a tab in the virtual terminal for session ID " + session_id, agent_name, type="virtual_terminal_command"
        )
    else:
        add_event(
            "I tried to close a tab in the virtual terminal, but it didn't exist. The session ID was " + session_id,
            agent_name,
            type="virtual_terminal_command",
        )
        raise ValueError(f"Session ID {session_id} does not exist.")


def get_tabs(arguments):
    add_event(
        "I got a list of tabs from the virtual terminal:\n" + str(terminal.get_sessions()) + "\n" + "Next I can run a command in the terminal (run_command function).", 
        agent_name,
        type="virtual_terminal_command",
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
        "I got a list of tabs from the virtual terminal:\n" + formatted_string + "\n" + "Next I can run a command in the terminal (run_command function).",
        agent_name,
        type="virtual_terminal_command",
    )
    return formatted_string


def run_command(arguments):
    command = arguments.get("command")
    if not terminal.get_current_session_id():
        raise ValueError("No active session.")
    session = terminal.get_sessions()[terminal.get_current_session_id()]
    result = subprocess.check_output(
        command, shell=True, cwd=session["current_directory"]
    )
    session["last_command"] = command
    session["last_output"] = result
    command_trimmed = command[:100]
    add_event(
        "I ran the command: "
        + command_trimmed,
        agent_name,
        type="virtual_terminal_command",
    )
    return result.decode("utf-8")


def get_skills():
    return {
        "terminal_create_tab": {
            "payload": {
                "name": "terminal_create_tab",
                "description": "You have access to a virtual terminal. This function creates a new tab in your virtual terminal so you can switch to it.",
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
                "description": "Switch to an existing tab in your virtual terminal.",
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
                "description": "Close an existing tab in your virtual terminal.",
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
                "description": "Get all tabs in a dictionary format from the virtual terminal.",
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
                "description": "Get all tabs in a human-readable string format from the virtual terminal.",
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
                "description": "Run a command in the current tab of your virtual terminal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to run in your virtual terminal.",
                        },
                    },
                    "required": ["command"],
                },
            },
            "handler": run_command,
        },
    }
