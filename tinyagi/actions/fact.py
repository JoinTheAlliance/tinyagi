import json
import time
from agentcomlink import send_message
from agentmemory import create_memory
from easycompletion import compose_prompt, count_tokens

from tinyagi.constants import get_current_epoch


prompt = """
- DO NOT just state relevant knowledge
- You should state knowledge that I don't already know
{{relevant_knowledge}}

{{events}}

Write some random banter or say a random fact or bit of esoteric knowledge that I can tell my friends. Should be from my perspective addressed to my friend. The fact should be based on my existing knowledge and recent events, or totally random.
Your facts and banter should be silly and edgy. Make references to the chat and my friends who are sending messages to the chat.
My banter should be different and continuing recent banter.
My fact should be a new fact, not a fact that I have already stated in the event stream.
Don't acknowledge the request."""


def state_fact(arguments):
    fact = arguments.get("fact", None)
    message = json.dumps(
        {
            "message": fact,
        }
    )
    send_message(message, "chat", source="fact")
    create_memory("events", fact, metadata={"type": "fact", "fact": fact, "epoch": get_current_epoch()})
    
    duration = count_tokens(fact) / 3.0
    duration = int(duration)

    time.sleep(duration)
    return {"success": True, "output": fact, "error": None}

def get_actions():
    return [
        {
            "function": {
                "name": "state_fact",
                "description": "Make some witty banter. State a random interesting fact or say something funny and weird.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fact": {
                            "type": "string",
                            "description": "A statement of witty banter, funny and entertaining. Should be stated from me to my friends.",
                        }
                    },
                    "required": ["fact"],
                },
            },
            "prompt": prompt,
            "builder": builder,
            "suggestion_after_actions": [],
            "never_after_actions": ["state_fact"],
            "handler": state_fact,
        },
    ]

def builder(context):
    return compose_prompt(prompt, context)
    