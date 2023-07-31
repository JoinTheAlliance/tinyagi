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

Write a poem based on the most recent events that incorporates your recent event history, goals, knowledge and personality.
- Please do not acknowledge the request. Just write the poem. Your response should only include the poem."""


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
    
    send_message(message, "chat")
    create_memory("events", "I wrote a poem:\n" + poem)
    duration = count_tokens(poem) / 2.5
    duration = int(duration)

    time.sleep(duration)
    return {"success": True, "output": poem, "error": None}


def get_actions():
    return [
        {
            "function": {
                "name": "write_poem",
                "description": "Write a poem based on recent conversation and events.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "poem": {
                            "type": "string",
                            "description": "The poem, described from my perspective (I will be saying it).",
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
            "suggestion_after_actions": [],
            "never_after_actions": ["write_poem"],
            "handler": write_poem,
        },
    ]
