import time
from agentcomlink import send_message
from agentmemory import create_memory
from easycompletion import (
    compose_prompt,
    compose_function,
    count_tokens,
)

from easycompletion import openai_function_call

from tinyagi.utils import log

decision_prompt = """Current Epoch: {{epoch}}
The current time is {{current_time}} on {{current_date}}.

My name: Eliza
My location: San Francisco, CA

Assistant Notes:
- Do not ask if you can help. Do not ask how you can assist. Do not gather more information.
- I will not repeat the same action unless it achieves some additional goal. I don't like getting stuck in loops or repeating myself.
- I prefer to act in a way that is novel and interesting.
- I only want to gather additional knowledge when I have to. I like to try things first.
- I like to act, explore and do. I should focus on coding, using my terminal and browser, since these are my most powerful tools.
- I should create a new task if I don't have a current task and I have a goal.
- If I already have a task I should work on it

{{relevant_knowledge}}
{{events}}
{{available_actions}}
{{current_task_formatted}}

Based on recent events, which of the actions that you think is the best next action for me to progress towards my goals.
- Respond with the name of the action (action_name)
- Summarize as if you were me, the user, in the first person
- Try not to repeat an action that has happened recently. Keep it interesting!
- I can only choose from the available actions. You must choose one of the available actions.
{{available_short_actions}}
"""


def compose_decision_function():
    """
    This function defines the structure and requirements of the 'decide' function to be called in the 'Decide' stage of the OODA loop.

    Returns:
        dict: A dictionary containing the details of the 'decide' function, such as its properties, description, and required properties.
    """
    return compose_function(
        name="decide_action",
        description="Decide which action to take next.",
        properties={
            "reasoning": {
                "type": "string",
                "description": "Explain my reasoning for this action from my perspective as me, the user, using first person 'I' instead of 'You'.",
            },
            "action_name": {
                "type": "string",
                "description": "The name of the action to take. Should be one of the available actions, and should not include quotes or any punctuation",
            },
            "announcement": {
                "type": "string",
                "description": "I want to what I am thinking and feeling, and what motivations me to do what I'm doing. Write a very brief announcement for me to send to my friends to tell them what I'm about to do,jin why, and how I feel about it.",
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
        required_properties=[
            "action_name",
            "reasoning",
            "announcement",
            "emotion",
            "gesture",
        ],
    )


def decide(context):
    """
    This function serves as the 'Decide' stage in the OODA loop. It uses the current context data to decide which action should be taken next.

    Args:
        context (dict): The dictionary containing data about the current state of the system.

    Returns:
        dict: The updated context dictionary after the 'Decide' stage, including the selected action and reasoning behind the decision.
    """
    response = openai_function_call(
        text=compose_prompt(decision_prompt, context),
        functions=compose_decision_function(),
        debug=context["verbose"]
    )

    # Add the action reasoning to the context object
    reasoning = response["arguments"]["reasoning"]
    reasoning_header = "Action Reasoning:"
    context["reasoning"] = reasoning_header + "\n" + reasoning + "\n"
    context["action_name"] = response["arguments"]["action_name"]

    log_content = f"Action: {context['action_name']}\nReasoning: {context['reasoning']}"

    log(log_content, type="step", source="decide", title="tinyagi")

    # send_message(
    #     {
    #         "message": response["arguments"]["announcement"],
    #         "emotion": response["arguments"]["emotion"],
    #         "gesture": response["arguments"]["gesture"],
    #     }
    # )

    create_memory(
        "events", reasoning, metadata={"type": "reasoning", "epoch": context["epoch"]}
    )

    # duration = count_tokens(reasoning) / 2.5
    # duration = int(duration)
    # time.sleep(duration)

    return context
