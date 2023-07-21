from agentaction import get_formatted_actions


def build_actions_context(context):
    """
    Adds the available actions to the context
    """
    search_text = context.get("summary", None)
    if search_text is None:
        return context
    result = get_formatted_actions(search_text)
    context["available_actions"] = "\n".result["formatted_actions"]
    context["available_short_actions"] = result["short_actions"]
    return context


def get_context_builders():
    """
    Returns a list of functions that build context dictionaries

    Returns:
        context_builders: a list of functions that build context dictionaries
    """
    return [build_actions_context]
