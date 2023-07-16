from agentactions import (
    compose_action_prompt,
    get_action,
    use_action,
)

from tinyagi.main import create_event, openai_function_call


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
        create_event(
            f"I tried to use the action `{action_name}`, but it was not found.",
            type="error",
            subtype="action_not_found",
        )
        return {"error": f"Action {action_name} not found"}

    response = openai_function_call(
        text=compose_action_prompt(action, context),
        functions=action["function"],
        name=f"action_{action_name}",
    )

    # TODO: check if the action is the last as last time

    use_action(response["function_name"], response["arguments"])
    return context