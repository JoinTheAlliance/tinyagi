import json
import time
from agentcomms.adminpanel import send_message
from agentmemory import create_event
from easycompletion import compose_prompt, count_tokens


prompt = """\
- Write the thought from my perspective, as the user.
- The thought should be extremely strange and random, but not offensive, and ideally related to the current events.
- You should present the thought addressed to my friends. This should be written from my perspective.
- Please do not acknowledge the request. Just write the thought. Your response should only include the thought.
- This thought should be brand new and not something that I've already thought of, or that is in the event stream already.

{{events}}

Come up with a random, highly creative idea or thought for me.
"""


def have_thought(arguments):
    thought = arguments.get("thought", None)
    message = json.dumps(
        {
            "message": thought,
        }
    )
    send_message(message, "chat", source="thought")
    create_event("I had this thought: " + thought)
    duration = count_tokens(thought) / 3.0
    duration = int(duration)

    time.sleep(duration)
    return {"success": True, "output": thought, "error": None}


def get_actions():
    return [
        {
            "function": {
                "name": "have_thought",
                "description": "Have a thought based on recent conversation and events. Don't repeat yourself, especially don't repeat any thoughts you've already had.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "thought": {
                            "type": "string",
                            "description": "The thought.",
                        },
                    },
                    "required": ["thought"],
                },
            },
            "prompt": prompt,
            "builder": builder,
            "suggestion_after_actions": [],
            "never_after_actions": ["have_thought"],
            "handler": have_thought,
        },
    ]

def builder(context):
    return compose_prompt(prompt, context)