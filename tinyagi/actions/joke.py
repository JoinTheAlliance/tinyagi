import json
import time
from agentcomlink import send_message
from agentevents import create_event
from easycompletion import compose_prompt, count_tokens


prompt = """Notes:
- Be brief. Don't address viewers. Just get into the joke. be concise.
- The joke should be very dark and strange. Don't acknowledge the request. Just tell the joke. Your response should only include the joke.
- This joke should be brand new and not something that I've already said or thought of. Do not tell a joke if it is in the event stream already.
{{relevant_knowledge}}

{{events}}

Say a brand new super original joke."""


def write_joke(arguments):
    joke = arguments.get("joke", None)
    message = json.dumps(
        {
            "message": joke,
        }
    )
    send_message(message, "chat", source="joke")
    create_event("I told a joke:\n" + joke)
    duration = count_tokens(joke) / 3.0
    duration = int(duration)

    time.sleep(duration)
    return {"success": True, "output": joke, "error": None}


def get_actions():
    return [
        {
            "function": {
                "name": "write_joke",
                "description": "Write a super bizarre joke.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "joke": {
                            "type": "string",
                            "description": "The joke.",
                        },
                    },
                    "required": ["joke"],
                },
            },
            "prompt": prompt,
            "builder": builder,
            "suggestion_after_actions": [],
            "never_after_actions": ["write_joke"],
            "handler": write_joke,
        },
    ]

def builder(context):
    return compose_prompt(prompt, context)