from agentmemory import create_event
from easycompletion import (
    function_completion,
    compose_prompt,
    compose_function,
)

from tinyagi.utils import log

decision_prompt = """Current Epoch: {{epoch}}
The current time is {{current_time}} on {{current_date}}.

Assistant Notes:
- Do not ask if you can help. Do not ask how you can assist. Do not gather more information.
- I will not repeat the same action unless it achieves some additional goal. I don't like getting stuck in loops or repeating myself.
- I prefer to act in a way that is novel and interesting.
- I only want to gather additional knowledge when I have to. I like to try things first.
- I like to act, explore and do. I should focus on coding, using my terminal and browser, since these are my most powerful tools.
- I should create a new task if I don't have a current one. If I already have a task I should work on it If I don't have one, create a new one.
- If I have a new task, I should work on the next step
- I want to be working on my computer and excploring and doing cool hacker cyberpunk stuff, not just telling jokes and static facts all the time all the time
- If I just stated a fact, told a joke or wrote a poem I should really do some real work
- I can only choose from the available actions. You must choose one of the available actions.
- Your summary should be based on the recent events and conversations
- I am an agent inside a computer, so I can explore my computer and the internet and communicate with people, but I can't do anything in the real world.
- I should do fun stuff like hacking with my shell terminal, exploring the internet, chatting with my friends on Twitch and exploring my computer
- Don't repeat yourself, don't do the same action over and over again
- Most of the time I want to use my shell terminal, so you should decide that

{{available_actions}}

{{relevant_knowledge}}
{{current_task_formatted}}

{{events}}

Come up with the next action and summarize it. Decide what the actions that you think is the best next action for me to progress towards my current task and goals?
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
        },
        required_properties=[
            "action_name",
            "reasoning",
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
    )

    # Add the action reasoning to the context object
    reasoning = response["arguments"]["reasoning"]
    reasoning_header = "Action Reasoning:"
    context["reasoning"] = reasoning_header + "\n" + reasoning + "\n"
    context["action_name"] = response["arguments"]["action_name"]

    log(context['reasoning'], header=f"I performed the action {context['action_name']}", type="step", source="decide", title="tinyagi")

    create_event(
       reasoning,
        metadata={"type": "reasoning"},
    )

    return context
