from agentagenda import create_task, search_tasks, cancel_task, finish_task, finish_step, add_step, cancel_step

def create_task_handler(arguments):
    """
    Handler action for creating a new task document.
    """
    goal = arguments["goal"]
    create_task(goal)
    print('created task')

def cancel_task_handler(arguments):
    goal = arguments["goal"]
    # TODO: get the neartest task to the goal and cancel it
    tasks = search_tasks(goal)
    if len(tasks) > 0:
        task = tasks[0]
        cancel_task(task)
    print('canceled task')


def complete_task_handler(arguments):
    goal = arguments["goal"]
    tasks = search_tasks(goal)
    if len(tasks) > 0:
        task = tasks[0]
        finish_task(task)
    print('completed task')


def complete_step_handler(arguments):
    # TODO: might be wrong lol
    goal = arguments["goal"]
    step = arguments["step"]
    tasks = search_tasks(goal)
    if len(tasks) > 0:
        # search for steps
        task = tasks[0]
        steps = task["steps"]
        for s in steps:
            if s["name"] == step:
                finish_step(task, s)
    print('completed step')

def add_step_handler(arguments):
    goal = arguments["goal"]
    step = arguments["step"]
    tasks = search_tasks(goal)
    if len(tasks) > 0:
        task = tasks[0]
        add_step(task, step)
    print('added step')

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
    print('canceled step')

def get_actions():
    return [
        {
            "function": {
                "name": "create_task",
                "description": "Create a new task with the given goal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "acknowledgement": {
                            "type": "string",
                            "description": "An acknowledgement to the user and explanation of what you are about to do.",
                        },
                        "goal": {
                            "type": "string",
                            "description": "The goal of the task.",
                        }
                    },
                    "required": ["acknowledgement", "goal"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": create_task_handler,
        },
        {
            "function": {
                "name": "cancel_task",
                "description": "Cancel a task if it is impossible, redundant or unnecessary.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "acknowledgement": {
                            "type": "string",
                            "description": "An acknowledgement to the user and explanation of what you are about to do.",
                        },
                        "goal": {
                            "type": "string",
                            "description": "The goal of the task to cancel.",
                        }
                    },
                    "required": ["acknowledgement", "goal"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": create_task_handler,
        },
        {
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "acknowledgement": {
                            "type": "string",
                            "description": "An acknowledgement to the user and explanation of what you are about to do.",
                        },
                        "goal": {
                            "type": "string",
                            "description": "The goal of the task to complete.",
                        }
                    },
                    "required": ["acknowledgement", "goal"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": complete_task_handler,
        },
        {
            "function": {
                "name": "complete_step",
                "description": "Mark a step as complete.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "acknowledgement": {
                            "type": "string",
                            "description": "An acknowledgement to the user and explanation of what you are about to do.",
                        },
                        "goal": {
                            "type": "string",
                            "description": "The goal of the task to complete.",
                        },
                        "step": {
                            "type": "string",
                            "description": "The step to complete.",
                        }
                    },
                    "required": ["acknowledgement", "goal", "step"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": complete_step_handler,
        },
        {
            "function": {
                "name": "add_step",
                "description": "Add a step to a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "acknowledgement": {
                            "type": "string",
                            "description": "An acknowledgement to the user and explanation of what you are about to do.",
                        },
                        "goal": {
                            "type": "string",
                            "description": "The goal of the task to complete.",
                        },
                        "step": {
                            "type": "string",
                            "description": "The step to complete.",
                        }
                    },
                    "required": ["acknowledgement", "goal", "step"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": add_step_handler,
        },
        {
            "function": {
                "name": "cancel_step",
                "description": "Cancel a step.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "acknowledgement": {
                            "type": "string",
                            "description": "An acknowledgement to the user and explanation of what you are about to do.",
                        },
                        "goal": {
                            "type": "string",
                            "description": "The goal of the task to complete.",
                        },
                        "step": {
                            "type": "string",
                            "description": "The step to complete.",
                        }
                    },
                    "required": ["acknowlegement", "goal", "step"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": cancel_step_handler,
        },
    ]