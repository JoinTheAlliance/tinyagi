# actions/reflect.py

# reflect on things that are going on
from core.language import clean_prompt, use_language_model, compose_prompt
from core.memory import create_event

prompt = clean_prompt(
    """
The current time is {current_time} on {current_date}.

Here are some relevant memories:
{knowledge}
Here are some key details about your personality:
{personality}
These are your most important goals, which you should always keep in mind:
{goals}
These are your current tasks, which you should prioritize accomplishing
{tasks}
You can call the following actions and should call them often:
{actions}
Recent Event History:
{events}

Reflect on this topic: {topic}
- Are there any issues in the recent event stream?
- Are you pursuing your goals?
- Do you have any tasks that you should be working on?
- Is there anything that you should be doing differently?
Pick one of these that is most important to you and write a paragraph about it.
Your respond should be a single paragraph. Be concise and to the point.
"""
)


def get_actions():
    return {
        "reflect": {
            "function": {
                "name": "reflect",
                "description": "Reflect on a topic and how things have been going in the event stream.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to reflect on",
                        },
                    },
                    "required": ["topic"],
                },
            },
            "handler": reflect,
        },
    }


def reflect(arguments):
    topic = arguments.get("topic", None)
    user_prompt = compose_prompt(prompt, topic)
    # replace {topic} with topic in user_prompt
    user_prompt = user_prompt.replace("{topic}", topic)

    messages = [
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    response = use_language_model(messages=messages)
    response_message = response["content"]
    if response_message != None:
        create_event(response_message, type="reflection")
