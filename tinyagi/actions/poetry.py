import json
import time
from agentcomlink import send_message
from agentmemory import create_memory
from easycompletion import compose_prompt, count_tokens

from tinyagi.constants import get_current_epoch


prompt = """\
{{relevant_knowledge}}

{{events}}

Recent Banter:
{{banter}}

Write a weird, abstract or silly poem based on the most recent events that incorporates your recent event history, goals, knowledge and personality.
- Present the poem to my friends, like "hey guys, I just wrote a poem, I'm going to recite it now!" This should be written from my perspective
- Please do not acknowledge the request. Just write the poem. Your response should only include the poem.
- Your response should be <presentation> <poem>"""


def write_poem(arguments):
    print('poem arguments are')
    print(arguments)
    poem = arguments.get("poem", None)
    emotion = arguments["emotion"]
    gesture = arguments["gesture"]
    message = json.dumps(
        {
            "message": poem,
            "emotion": emotion,
            "gesture": gesture,
        }
    )
    
    send_message(message, "chat", source="poem")
    create_memory("events", "I wrote a poem:\n" + poem, metadata={"epoch": get_current_epoch()})
    duration = count_tokens(poem) / 3.0
    duration = int(duration)

    time.sleep(duration)
    return {"success": True, "output": poem, "error": None}


def get_actions():
    return [
        {
            "function": {
                "name": "write_poem",
                "description": "Write a super bizarre poem based on recent conversation and events. Can be abstract and weird. Can make fun of people and reference the chat.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "poem": {
                            "type": "string",
                            "description": "The poem, described from my perspective (I will be saying it). Should be a very strange poem. Should be short.",
                        },
                        "emotion": {
                            "type": "string",
                            "description": "The emotion I should express in my message.",
                            "enum": ["neutral", "surprise", "angry", "sorrow", "fun", "joy"],
                        },
                        "gesture": {
                            "type": "string",
                            "description": "The gesture I should express in my message.",
                            "enum": [
                                "neutral",
                                "alert",
                                "angry",
                                "embarrassed",
                                "headNod",
                                "headShake",
                                "sad",
                                "surprise",
                                "victory",
                            ],
                        },
                    },
                    "required": ["poem", "emotion", "gesture"],
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