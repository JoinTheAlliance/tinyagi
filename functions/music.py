# functions/music.py

from core.language import use_language_model, compose_prompt
from core.language import clean_prompt
from core.memory import create_event

prompt = clean_prompt(
    """
Here are some relevant things that I have recalled from my memory:
{knowledge}
Here are some key details about my personality:
{personality}
These are my most important goals, which I should always keep in mind:
{goals}
These are my current tasks, which I should prioritize accomplishing
{tasks}
I have access to the following functions and should call them often:
{functions}
Recent Event History:
{events}

Think about this topic: {topic}
Write a song (or at least the song lyrics and a chord progression) that incorporates your recent event history, goals, knowledge and personality.
"""
)


def get_functions():
    return {
        "write_song": {
            "payload": {
                "name": "write_song",
                "description": "Write a song about everything that is going on.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to write a song about. Can be detailed and complicated.",
                        },
                    },
                    "required": ["topic"],
                },
            },
            "handler": write_song,
        },
    }


def write_song(arguments):
    topic = arguments.get("topic", None)
    user_prompt = compose_prompt(prompt, topic)
    # replace {topic} with topic in user_prompt
    user_prompt = user_prompt.replace("{topic}", topic)

    messages = [
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
    response = use_language_model(messages=messages)
    response_content = response["content"]
    if response_content != None:
        create_event(response_content, type="song")
