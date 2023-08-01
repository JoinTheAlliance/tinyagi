import json
import time
from agentcomlink import send_message
from agentmemory import create_memory
from easycompletion import compose_prompt, count_tokens


prompt = """\
{{relevant_knowledge}}

{{events}}

{{summary}}

Recent Banter:
{{banter}}

Say a super weird random joke based on the most recent events. The joke should be very dark and strange. The joke should be different from the banter.
- Before the joke, add a brief silly presentation from my perspective. Like "hey guys, I just thought of a joke, it's really bad but I'm going to tell it anyways!"""


def write_joke(arguments):
    joke = arguments.get("joke", None)
    emotion = arguments["emotion"]
    gesture = arguments["gesture"]
    message = json.dumps(
        {
            "message": joke,
            "emotion": emotion,
            "gesture": gesture,
        }
    )
    send_message(message, "chat")
    create_memory("events", "I told a joke:\n" + joke)
    duration = count_tokens(joke) / 2.5
    duration = int(duration)

    time.sleep(duration)
    return {"success": True, "output": joke, "error": None}


def get_actions():
    return [
        {
            "function": {
                "name": "write_joke",
                "description": "Write a super weird bizarre joke based on current events and conversations. Should be a completely original joke that you have never said before.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "joke": {
                            "type": "string",
                            "description": "A joke, told from me to my friends. Can be detailed and complicated. Should be funny, weird and dark. Esoteric and strange -- NOT just a normal average joke.",
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
                    "required": ["joke", "emotion", "gesture"],
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