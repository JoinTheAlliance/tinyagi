import uuid


def create_task_handler(arguments):
    """
    Handler action for creating a new task document.
    """
    pass

def cancel_task_handler(arguments):
    pass

def complete_task_handler(arguments):
    pass

def complete_step_handler(arguments):
    pass

def add_step_handler(arguments):
    pass

def list_tasks(arguments):
    pass



def get_task_actions():
    """
    Returns a dictionary of actions related to tasks.
    """
    return [
        {
            "function": {
                "name": "create_task",
                "description": "Create a new task document.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text content of the task document.",
                        }
                    },
                    "required": ["text"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": create_task_handler,
        }
    ]

def get_actions():
    return [
        {
            "function": {
                "name": "complete_step",
                "description": "Complete a step in a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text content of the task document.",
                        }
                    },
                    "required": ["text"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": create_task_handler,
        }
    ]