import json
import time
from agentcomlink import send_message
from agentmemory import create_memory
from easycompletion import compose_prompt, count_tokens


prompt = """
{{events}}

Come up with a random, highly creative idea or thought for me.
- Write the thought from my perspective, as the user.
- The thought should be extremely strange and random, but not offensive, and ideally related to the current events.
- Please do not acknowledge the request. Just write the thought. Your response should only include the thought."""


def have_thought(arguments):
    print('thought arguments are')
    print(arguments)
    thought = arguments.get("thought", None)
    emotion = arguments["emotion"]
    gesture = arguments["gesture"]
    message = json.dumps(
        {
            "message": thought,
            "emotion": emotion,
            "gesture": gesture,
        }
    )
    send_message(message, "chat")
    create_memory("events", "I had this thought: " + thought)
    duration = count_tokens(thought) / 2.5
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
                            "description": "A thought, described from my perspective (I will be saying it). Should be a very strange thought. Should be short and totally bizarre and random.",
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
                    "required": ["thought", "emotion", "gesture"],
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