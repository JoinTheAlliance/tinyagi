# think about things that are going on
from core.language import clean_prompt, use_language_model, compose_prompt
from core.memory import add_event, get_all_values_for_text

prompt = clean_prompt(
    """
The current time is {current_time} on {current_date}.

Here are some relevant things that I have recalled from my memory:
{knowledge}
Here are some key details about my personality:
{personality}
These are my most important goals, which I should always keep in mind:
{goals}
These are my current tasks, which I should prioritize accomplishing
{tasks}
I have access to the following functions and should call them often:
{skills}
Recent Event History:
{events}

Think about this topic: {topic}
"""
)


def get_skills():
    return {
        "think": {
            "payload": {
                "name": "think",
                "description": "Think about a topic, consider what to do next or dig into a creative impulse.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to think about",
                        },
                    },
                    "required": ["topic"],
                },
            },
            "handler": think,
        },
    }


def think(arguments):
    topic = arguments.get("topic", None)
    values_to_replace = get_all_values_for_text(topic)
    user_prompt = compose_prompt(prompt, values_to_replace)
    # replace {topic} with topic in user_prompt
    user_prompt = user_prompt.replace("{topic}", topic)

    messages = [
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    response = use_language_model(messages=messages)
    response_message = response.get("message", None)
    if response_message != None:
        add_event(response_message, type="thought")
