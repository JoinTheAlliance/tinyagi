# think about things that are going on
from core.completion import create_chat_completion
from core.memory import add_event, get_all_values_for_text
from core.utils import compose_prompt
from core.constants import agent_name


def get_skills():
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


def write_poem(arguments):
    topic = arguments.get("topic", None)
    values_to_replace = get_all_values_for_text(topic)
    user_prompt = compose_prompt("poem", values_to_replace)
    # replace {topic} with topic in user_prompt
    user_prompt = user_prompt.replace("{topic}", topic)

    messages = [
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
    response = create_chat_completion(messages=messages)
    response_message = response.get("message", None)
    if response_message != None:
        add_event(response_message, agent_name, type="poem")