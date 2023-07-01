import os
import sys
from core.memory import add_event
from core.constants import agent_name

def get_skills():
    return {
        "restart": {
            "payload": {
                "name": "restart",
                "description": "Restart yourself. Completely shut down and start back up.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "explanation": {
                            "type": "string",
                            "description": "Why are you restarting?",
                        },
                    },
                    "required": ["explanation"],
                },
            },
            "handler": restart,
        },
    }

def restart(arguments):
    explanation = arguments.get("explanation", None)
    add_event("I am restarting. Explanation: " + explanation, agent_name, type="restart")
    python = sys.executable
    os.execl(python, python, * sys.argv)