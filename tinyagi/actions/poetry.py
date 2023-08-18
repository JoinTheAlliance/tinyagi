import json
import time
from agentcomms.adminpanel import send_message
from agentmemory import create_event
from easycompletion import compose_prompt, count_tokens


prompt = """Notes:
- Be brief. Don't address viewers. Just get into the poem. be concise.
- Please do not acknowledge the request. Just write the poem. Your response should only include the poem.
- This poem should be brand new and not something that I've already written or that is in the event stream already.

{{relevant_knowledge}}

{{events}}

Write an strange, abstract or silly poem based on the most recent events that incorporates your recent event history, goals, knowledge and personality."""


def write_poem(arguments):
    poem = arguments.get("poem", None)
    message = json.dumps(
        {
            "message": poem,
        }
    )
    
    send_message(message, "chat", source="poem")
    create_event("I wrote a poem:\n" + poem)
    duration = count_tokens(poem) / 3.0
    duration = int(duration)

    time.sleep(duration)
    return {"success": True, "output": poem, "error": None}


def get_actions():
    return [
        {
            "function": {
                "name": "write_poem",
                "description": "Write a super bizarre poem based on recent conversation and events. Can be oddball or goofy. Can make fun of people and reference the chat.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "poem": {
                            "type": "string",
                            "description": "The poem, described from my perspective (I will be saying it). Should be a very strange poem. Should be short.",
                        },
                    },
                    "required": ["poem"],
                },
            },
            "prompt": prompt,
            "builder": builder,
            "suggestion_after_actions": [],
            "never_after_actions": ["write_poem"],
            "handler": write_poem,
        },
    ]

def builder(context):
    return compose_prompt(prompt, context)