from easycompletion import (
    count_tokens,
)

from agentactions import (
    get_available_actions,
)

MAX_PROMPT_TOKENS = 3072  # 4096 - 1024


def get_formatted_available_actions(context):
    """
    TODO: this needs to be updated
    Retrieve a formatted string of the available actions based on search text

    Args:
        search_text: Find most revelant actions whith are available.

    Returns:
        A string representing the available actions.
    """
    # check if context['reasoning'] exists
    search_text = context.get("reasoning", None)
    if search_text is None:
        return context
    header_text = "Available actions for me to choose from:"
    available_actions = get_available_actions(search_text)
    formatted_available_actions = "\n".join(available_actions)
    while count_tokens(formatted_available_actions) > MAX_PROMPT_TOKENS:
        if len(available_actions) == 1:
            raise Exception("Single knowledge length greater than token limit")
        available_actions = available_actions[:-1]
        formatted_available_actions = "\n".join(
            [k["document"] for k in available_actions]
        )

    # TODO: call compose here with the available actions
    return header_text + "\n" + formatted_available_actions + "\n"