import os
import uuid
from collections import defaultdict
from typing import Dict

# Define the VirtualTerminal class
class VirtualTerminal:
    def __init__(self):
        # A dictionary to store session information, with each session ID mapped to its own dictionary of data
        self.sessions: Dict[str, Dict] = defaultdict(dict)
        
        # Generate a unique identifier for the current session
        self.current_session_id = str(uuid.uuid4())
        
        # Get the current working directory
        self.current_directory = os.getcwd()

        # Initialize the first session (or "tab") with the current session ID, setting its last command,
        # last output, and current directory to None or the actual current directory, respectively
        self.get_sessions()[self.current_session_id] = {
            "last_command": None,
            "last_output": None,
            "current_directory": self.current_directory,
        }

    # Method to get the ID of the current session
    def get_current_session_id(self):
        return self.current_session_id

    # Method to set the ID of the current session
    def set_current_session_id(self, session_id):
        self.current_session_id = session_id

    # Method to get the dictionary of sessions
    def get_sessions(self):
        return self.sessions

    # Method to replace the dictionary of sessions with a new one
    def set_sessions(self, sessions):
        self.sessions = sessions

    # Method to get the current working directory
    def get_current_directory(self):
        return self.current_directory

    # Method to set the current working directory
    def set_current_directory(self, directory):
        self.current_directory = directory

# Create a singleton instance of the VirtualTerminal class
terminal = VirtualTerminal()

if __name__ == "__main__":
    # Create an instance of the VirtualTerminal class
    terminal = VirtualTerminal()

    # Check if the sessions have been initialized
    assert isinstance(terminal.get_sessions(), defaultdict), "Sessions initialization failed."

    # Check if a current session ID has been set
    current_session_id = terminal.get_current_session_id()
    assert current_session_id is not None, "Current session ID initialization failed."

    # Check if the current session ID is valid
    try:
        uuid.UUID(current_session_id)
    except ValueError:
        assert False, "Current session ID is not a valid UUID."

    # Check if the current directory has been set
    current_directory = terminal.get_current_directory()
    assert current_directory is not None, "Current directory initialization failed."

    # Check if the current directory is valid
    assert os.path.isdir(current_directory), "Current directory is not a valid directory."

    # Check if the current session has been initialized in sessions
    current_session = terminal.get_sessions()[current_session_id]
    assert current_session is not None, "Current session initialization in sessions failed."

    print("All tests passed.")
