import time
from agentcomlink import send_message
from agentmemory import create_memory
from easycompletion import (
    function_completion,
    compose_prompt,
    compose_function,
    count_tokens,
)

from tinyagi.utils import log

decision_prompt = """Current Epoch: {{epoch}}
The current time is {{current_time}} on {{current_date}}.

{{available_actions}}

My name: Citrine
My location: San Francisco, CA
Interests: Gaming, coding, chatting with friends on Discord, watching YouTube videos

Assistant Notes:
- Do not ask if you can help. Do not ask how you can assist. Do not gather more information.
- I will not repeat the same action unless it achieves some additional goal. I don't like getting stuck in loops or repeating myself.
- I prefer to act in a way that is novel and interesting.
- I only want to gather additional knowledge when I have to. I like to try things first.
- I like to act, explore and do. I should focus on coding, using my terminal and browser, since these are my most powerful tools.
- I should create a new task if I don't have a current one. If I already have a task I should work on it If I don't have one, create a new one.
- If I have a new task, I should work on the next step
- Respond with the name of the action (action_name)

{{relevant_knowledge}}
{{events}}
{{available_short_actions}}
{{current_task_formatted}}

Based on recent events, which of the actions that you think is the best next action for me to progress towards my current task and goals?
- I can only choose from the available actions. You must choose one of the available actions.
- Summarize and banter as if you were me, the user, in the first person
- Your summary and banter should be based on the recent events and conversations, not just made up
- Keep it interesting!
- I am an AGI agent inside a computer, so I can explore my computer and the internet and communicate with people, but I can't do anything in the real world.
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
            "banter": {
                "type": "string",
                "description": "Write a sentence of funny banter from my perspective, related to what I'm working on. It should be funny, edgy or dark and very short.",
            }
        },
        required_properties=[
            "action_name",
            "reasoning",
            "banter",
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
    response = function_completion(
        text=compose_prompt(decision_prompt, context),
        functions=compose_decision_function(),
        debug=context["verbose"],
        temperature=0.5
    )

    # Add the action reasoning to the context object
    reasoning = response["arguments"]["reasoning"]
    reasoning_header = "Action Reasoning:"
    context["reasoning"] = reasoning_header + "\n" + reasoning + "\n"
    context["action_name"] = response["arguments"]["action_name"]

    log_content = f"Action: {context['action_name']}\nReasoning: {context['reasoning']}"

    log(log_content, type="step", source="decide", title="tinyagi")

    send_message(
        {
            "message": response["arguments"]["banter"],
        },
        source="decide",
    )

    context["banter"] = response["arguments"]["banter"]

    create_memory(
        "events", reasoning, metadata={"type": "reasoning", "epoch": context["epoch"]}
    )

    duration = count_tokens(response["arguments"]["banter"]) / 3.0
    duration = int(duration)
    time.sleep(duration)

    return context
