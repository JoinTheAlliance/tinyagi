# think about things that are going on
from core.language import use_language_model, compose_prompt
from core.memory import add_event, get_all_values_for_text

def get_skills():
    return {
        "learn": {
            "payload": {
                "name": "learn",
                "description": "Extract some facts from the conversation to try to store as knowledge.",
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
            "handler": learn,
        },
    }


def learn(arguments):
    topic = arguments.get("topic", None)
    values_to_replace = get_all_values_for_text(topic)
    user_prompt = compose_prompt("thought", values_to_replace)
    # replace {topic} with topic in user_prompt
    user_prompt = user_prompt.replace("{topic}", topic)
    system_prompt = compose_prompt("system", values_to_replace)

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
    response = use_language_model(messages=messages)
    response_message = response.get("message", None)
    if response_message != None:
        add_event(response_message, type="thought")