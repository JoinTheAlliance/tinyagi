# think about things that are going on
from core.language import clean_prompt, use_language_model, compose_prompt
from core.memory import add_event

prompt = clean_prompt("""
The current time is {current_time} on {current_date}.

I'm having some issues.

These are my most important goals, which I should always keep in mind:
{goals}
These are my current tasks, which I should prioritize accomplishing
{tasks}
I have access to the following functions and should call them often:
{skills}
Recent Event History:
{events}

How do I fix it?
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