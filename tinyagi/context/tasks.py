from agentagenda import get_current_task, get_task_as_formatted_string, list_tasks, list_tasks_as_formatted_string

def built_task_context(context):
    # get current task
    # get current task formatted
    # get all tasks
    # get all tasks formatted
    tasks = list_tasks()
    context["tasks"] = ""
    if len(tasks) > 0:
        context["tasks"] = tasks
    context["formatted_tasks"] = list_tasks_as_formatted_string()
    if len(context["formatted_tasks"]) > 0:
        context["formatted_tasks"] = "Tasks:\n" + context["formatted_tasks"]
    context["current_task"] = get_current_task()
    if context["current_task"] is None:
        context["current_task_formatted"] = ""
    else:
        context["current_task_formatted"] = get_task_as_formatted_string(context["current_task"])
        if len(context["current_task_formatted"]) > 0:
            context["current_task_formatted"] = "Current Task:\n" + context["current_task_formatted"]

    return context

def get_context_builders():
    """
    Returns a list of functions that build context dictionaries

    Returns:
        context_builders: a list of functions that build context dictionaries
    """
    return [built_task_context]
