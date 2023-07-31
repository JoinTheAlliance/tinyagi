from agentaction import (
    compose_action_prompt,
    get_action,
    use_action,
)

from agentmemory import create_memory
from easycompletion import openai_function_call
from tinyagi.utils import log


def act(context):
    """
    This function serves as the 'Act' stage in the OODA loop. It executes the selected action from the 'Decide' stage.

    Args:
        context (dict): The dictionary containing data about the current state of the system, including the selected action to be taken.

    Returns:
        dict: The updated context dictionary after the 'Act' stage, which will be used in the next iteration of the OODA loop.
    """
    action_name = context["action_name"]
    action = get_action(action_name)

    if action is None:
        create_memory(
            "events",
            f"I tried to use the action `{action_name}`, but it was not found.",
            metadata={
                "type": "error",
                "subtype": "action_not_found",
                "epoch": context["epoch"],
            },
        )
        return {"error": f"Action {action_name} not found"}

    response = openai_function_call(
        text=compose_action_prompt(action, context), functions=action["function"], debug=context["verbose"]
    )

    formatted_arguments = ""
    for key, value in response["arguments"].items():
        formatted_arguments += f"{key}: {value}\n"

    log_content = (
        f"Using action {response['function_name']} with arguments {formatted_arguments}"
    )

    log(log_content, type="step", source="decide", title="tinyagi")

    action_result = use_action(response["function_name"], response["arguments"])

    if action_result is None or action_result["success"] is False:
        create_memory(
            "events",
            f"I tried to use the action `{action_name}`, but it failed.",
            metadata={
                "type": "error",
                "subtype": "action_failed",
                "epoch": context["epoch"],
            },
        )
        log(
            f"Action {action_name} failed",
            type="error",
            source="decide",
            title="tinyagi",
        )
    else:
        create_memory(
            "events",
            f"I used the action `{action_name}` successfully.\nOutput:\n{action_result.get('output', '')}",
            metadata={
                "type": "success",
                "subtype": "action_success",
                "epoch": context["epoch"],
            },
        )
        log(
            f"Action {action_name} succeeded\nOutput:\n{action_result.get('output', '')}",
            type="success",
            source="decide",
            title="tinyagi",
        )

    return context
