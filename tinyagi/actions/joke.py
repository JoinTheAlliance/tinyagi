import json
import time
from agentcomlink import send_message
from agentmemory import create_memory
from easycompletion import compose_prompt, count_tokens, text_completion


prompt = """Some relevant things you know:
{{relevant_knowledge}}

Current Task:
{{current_task_formatted}}

You have access to the following actions and should call them often:
{{available_actions}}

{{events}}

Come up with a topical joke based on recent events. The joke should be funny and weird and dark."""


def write_joke(arguments):
    print('joke arguments are')
    print(arguments)
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
                "description": "Write a topical joke based on current events and conversations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "joke": {
                            "type": "string",
                            "description": "A joke, told from me to an audience. Can be detailed and complicated. Should be funny, weird and dark.",
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
            "suggestion_after_actions": [],
            "never_after_actions": ["write_joke"],
            "handler": write_joke,
        },
    ]
