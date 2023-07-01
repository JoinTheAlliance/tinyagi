# functions/poetry.py

from core.language import clean_prompt, use_language_model, compose_prompt
from core.memory import create_event

prompt = clean_prompt(
    """
Some relevant things you know:
{knowledge}

Key details about your personality:
{personality}

You most important goals, which you should always keep in mind:
{goals}

Your current tasks, which you should prioritize accomplishing
{tasks}

You have access to the following functions and should call them often:
{functions}

Event Logs:
{events}

Topic: {topic}
Write a poem based on the most recent events and topic that incorporates your recent event history, goals, knowledge and personality.
"""
)


def write_poem(arguments):
    topic = arguments.get("topic", None)
    user_prompt = compose_prompt(prompt, topic)

    messages = [
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
    response = use_language_model(messages=messages)
    response_message = response.get("message", None)
    if response_message != None:
        create_event(response_message, type="poem")


def get_functions():
    return {
        "write_poem": {
            "payload": {
                "name": "write_poem",
                "description": "Write a poem about everything that is going on.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to write a poem about about. Can be detailed and complicated.",
                        },
                    },
                    "required": ["topic"],
                },
            },
            "handler": write_poem,
        },
    }
