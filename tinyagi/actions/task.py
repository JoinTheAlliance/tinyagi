from agentagenda import (
    create_task,
    search_tasks,
    cancel_task,
    finish_task,
    finish_step,
    add_step,
    cancel_step,
)
from agentmemory import create_event
from easycompletion import compose_prompt


def create_task_handler(arguments):
    """
    Handler action for creating a new task document.
    """
    goal = arguments["goal"]
    create_task(goal)
    create_event("I created a new task:\n" + goal)
    return {"success": True, "output": "I created a new task:\n" + goal, "error": None}


def cancel_task_handler(arguments):
    goal = arguments["goal"]
    # TODO: get the neartest task to the goal and cancel it
    tasks = search_tasks(goal)
    if len(tasks) > 0:
        task = tasks[0]
        cancel_task(task)
    create_event("I canceled a task: " + goal)
    return {"success": True, "output": "I canceled a task: " + goal, "error": None}


def complete_task_handler(arguments):
    goal = arguments["goal"]
    tasks = search_tasks(goal)
    if len(tasks) > 0:
        task = tasks[0]
        finish_task(task)
    create_event("I completed a task: " + goal)
    return {"success": True, "output": "I completed a task: " + goal, "error": None}


def complete_step_handler(arguments):
    # TODO: might be wrong lol
    goal = arguments["goal"]
    step = arguments["step"]
    tasks = search_tasks(goal)
    if len(tasks) > 0:
        # search for steps
        task = tasks[0]
        steps = task.get("steps", [])
        for s in steps:
            if s["name"] == step:
                finish_step(task, s)
    create_event("I completed a step: " + step)
    return {"success": True, "output": "I completed a step: " + step, "error": None}


def add_step_handler(arguments):
    goal = arguments["goal"]
    step = arguments["step"]
    tasks = search_tasks(goal)
    if len(tasks) > 0:
        task = tasks[0]
        add_step(task, step)
    create_event("I added a step: " + step)
    return {"success": True, "output": "I added a step: " + step, "error": None}


def cancel_step_handler(arguments):
    goal = arguments["goal"]
    step = arguments["step"]
    tasks = search_tasks(goal)
    if len(tasks) > 0:
        task = tasks[0]
        steps = task["steps"]
        for s in steps:
            if s["name"] == step:
                cancel_step(task, s)
    create_event("I canceled a step:\n" + step)
    return {"success": True, "output": "I canceled a step: " + step, "error": None}


create_task_prompt = """\
Current Time: {{current_time}}
Current Date: {{current_date}}
{{relevant_knowledge}}
{{events}}
{{summary}}
{{reasoning}}

Based on the reasoning, create a new task
"""

cancel_task_prompt = """\
{{summary}}
{{reasoning}}
{{formatted_tasks}}
{{current_task_formatted}}
{{events}}

Based on the reasoning, should I cancel a task, and if so, which one? If you don't want to cancel the task, respond with 'none', otherwise respond with the name or goal of the task you want to cancel."""

complete_task_prompt = """\
{{summary}}
{{reasoning}}
{{formatted_tasks}}
{{current_task_formatted}}
{{events}}

Based on the reasoning, should I complete a task, and if so, which one? If I shouldn't cancel the task, respond with 'none', otherwise respond with the name or goal of the task I should cancel."""


complete_step_prompt = """\
{{summary}}
{{reasoning}}
{{formatted_tasks}}
{{current_task_formatted}}
{{events}}

Based on the reasoning, should I complete a step on the task, and if so, which one? None, respond with 'none' for task and step."""

add_step_prompt = """\
{{summary}}
{{reasoning}}
{{formatted_tasks}}
{{current_task_formatted}}
{{events}}

Based on the reasoning, should I add a step to the task, and if so, which task and what step? None, respond with 'none' for task and step."""

cancel_step_prompt = """\
{{summary}}
{{reasoning}}
{{formatted_tasks}}
{{current_task_formatted}}
{{events}}

Based on the reasoning, should I cancel a step in the task, and if so, which task and what step? None, respond with 'none' for task and step."""


def create_task_builder(context):
    return compose_prompt(create_task_prompt, context)


def cancel_task_builder(context):
    return compose_prompt(cancel_task_prompt, context)


def complete_task_builder(context):
    return compose_prompt(complete_task_prompt, context)


def complete_step_builder(context):
    return compose_prompt(complete_step_prompt, context)


def add_step_builder(context):
    return compose_prompt(add_step_prompt, context)


def cancel_step_builder(context):
    return compose_prompt(cancel_step_prompt, context)


def get_actions():
    return [
        {
            "function": {
                "name": "start_task",
                "description": "Start a new task with the given goal. This is a good option for complex and multi-step actions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "The goal of the task.",
                        },
                    },
                    "required": ["goal"],
                },
            },
            "prompt": create_task_prompt,
            "suggestion_after_actions": [],
            "never_after_actions": ["start_task"],
            "builder": create_task_builder,
            "handler": create_task_handler,
        },
        {
            "function": {
                "name": "cancel_task",
                "description": "Cancel a task if it is impossible, redundant or unnecessary.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "The goal of the task to cancel.",
                        },
                    },
                    "required": ["goal"],
                },
            },
            "prompt": cancel_task_prompt,
            "suggestion_after_actions": [],
            "never_after_actions": [],
            "builder": cancel_task_builder,
            "handler": cancel_task_handler,
        },
        {
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "The goal of the task to complete.",
                        },
                    },
                    "required": ["goal"],
                },
            },
            "prompt": complete_task_prompt,
            "suggestion_after_actions": [],
            "never_after_actions": [],
            "builder": complete_task_builder,
            "handler": complete_task_handler,
        },
        {
            "function": {
                "name": "complete_step",
                "description": "Mark a step as complete.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "The goal of the task to complete.",
                        },
                        "step": {
                            "type": "string",
                            "description": "The step to complete.",
                        },
                    },
                    "required": ["goal", "step"],
                },
            },
            "prompt": complete_step_prompt,
            "suggestion_after_actions": [],
            "never_after_actions": [],
            "builder": complete_step_builder,
            "handler": complete_step_handler,
        },
        {
            "function": {
                "name": "add_step",
                "description": "Add a step to a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "The goal of the task to complete.",
                        },
                        "step": {
                            "type": "string",
                            "description": "The step to complete.",
                        },
                    },
                    "required": ["goal", "step"],
                },
            },
            "suggestion_after_actions": [],
            "never_after_actions": [],
            "prompt": add_step_prompt,
            "builder": add_step_builder,
            "handler": add_step_handler,
        },
        {
            "function": {
                "name": "cancel_step",
                "description": "Cancel a step.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "The goal of the task to complete.",
                        },
                        "step": {
                            "type": "string",
                            "description": "The step to complete.",
                        },
                    },
                    "required": ["goal", "step"],
                },
            },
            "suggestion_after_actions": [],
            "never_after_actions": [],
            "handler": cancel_step_handler,
            "builder": cancel_step_builder,
            "prompt": cancel_step_prompt,
        },
    ]
