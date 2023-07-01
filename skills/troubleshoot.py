# skills/troubleshoot

from core.language import clean_prompt, use_language_model, compose_prompt
from core.memory import add_event

prompt = clean_prompt("""
The current time is {current_time} on {current_date}.

These are your most important goals, which you should always keep in mind:
{goals}
These are you current tasks, which you should prioritize accomplishing:
{tasks}
You can call the following functions and should call them often:
{skills}
Event Logs (most recent toward the bottom):
{events}

Read the most recent events in the event stream. What do you think is wrong? Can you fix it?
""")

def troubleshoot(arguments):
    assessment = arguments.get("assessment", None)
    user_prompt = compose_prompt("troubleshooting", assessment)

    messages = [
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
    response = use_language_model(messages=messages)
    response_message = response.get("message", None)
    if response_message != None:
        add_event(response_message, type="troubleshooting")


def get_skills():
    return {
        "troubleshoot": {
            "payload": {
                "name": "troubleshoot",
                "description": "Try to figure out what is wrong. Are we stuck in a loop? Is there an error? Assess how to fix out problem.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "assessment": {
                            "type": "string",
                            "description": "What do you think is wrong?",
                        },
                    },
                    "required": ["assessment"],
                },
            },
            "handler": troubleshoot,
        },
    }