from easycompletion import (
    count_tokens,
)

from agentaction import (
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
    # check if context['summary'] exists
    search_text = context.get("summary", None)
    if search_text is None:
        return context
    header_text = "Available actions for me to choose from:"
    available_actions = get_available_actions(search_text)
    formatted_available_actions = "\n".join(available_actions)
    while count_tokens(formatted_available_actions) > MAX_PROMPT_TOKENS:
        formatted_available_actions = "\n".join(
            [k["document"] for k in available_actions]
        )

    short_actions = ", ".join([k["metadata"]["name"] for k in available_actions])
    context["available_actions_short"] = "Available actions (name): " + short_actions

    context["available_actions"] = header_text + "\n" + formatted_available_actions + "\n"
    return context

def get_context_builders():
    """
    Returns a list of functions that build context dictionaries

    Returns:
        context_builders: a list of functions that build context dictionaries
    """
    return [get_formatted_available_actions]