# core/action.py

# Dynamically load actions and use them
# actions are executed by the "function calling" feature of the OpenAI API.

import os
import sys
import importlib
import json

from agentmemory import create_memory, delete_memory, get_memories
from events import create_event

# Create an empty dictionary to hold the actions
actions = {}


def add_to_action_history(action_name, action_arguments={}, success=True):
    action_arguments["success"] = success
    create_memory("action_history", action_name, action_arguments)


def get_action_history(n_limit=20):
    return get_memories("action_history", n_limit)


def search_actions(search_text, n_results=5):
    """
    Searches for actions based on a query text.

    Returns a list of actions.
    """
    # Search for actions in the 'actions' collection
    search_results = get_memories(
        "actions", search_text=search_text, n_results=n_results
    )

    return search_results


def use_action(function_name, arguments):
    if function_name not in actions:
        add_to_action_history(function_name, arguments, success=False)
        return {"success": False, "response": "Action not found"}

    add_to_action_history(function_name, arguments)
    return {"success": True, "response": actions[function_name](arguments)}


def add_action(name, action):
    """
    Adds a new action to the actions dictionary and to the 'actions' collection.

    If the action is not present in the 'actions' collection, it is added.
    """
    # Add the action to the 'actions' dictionary
    actions[name] = action["handler"]
    create_memory(
        "actions",
        f"{name} - {action['function']['description']}",
        {"name": name, "function": json.dumps(action["function"])},
        id=name,
    )


def get_action(name):
    """
    Returns a action based on its name from the 'actions' dictionary.
    """
    if name in actions:
        return actions[name]
    else:
        return None


def get_recommended_actions(name):
    """
    Returns a list of recommended actions
    """
    return actions[name]["suggest_next_actions"]


def get_ignored_actions(name):
    """
    Returns a list of ignored actions
    """
    return actions[name]["ignore_next_actions"]


def remove_action(name):
    """
    Removes a action based on its name from both the 'actions' dictionary and the 'actions' collection.

    Also, logs the removal of a action as an event.
    """
    if name in actions:
        # Remove the action from the 'actions' dictionary
        del actions[name]
        delete_memory("actions", name)

        # Log the removal of a action as an event
        create_event(f"I removed the action {name}", "action")


def register_actions():
    """
    Registers all the actions present in the 'actions' directory.

    For each Python file in the 'actions' directory, it imports the file and calls the get_actions action if it exists.
    Then, it adds the returned actions to the 'actions' dictionary.
    """
    # Get the absolute path to the parent directory of the current file
    parent_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the absolute path to the 'actions' directory
    actions_dir = os.path.join(parent_dir, "..", "actions")

    # Add the parent directory of actions to the Python system path
    sys.path.insert(0, os.path.join(parent_dir, ".."))

    # Iterate through all of the files in the 'actions' directory
    for filename in os.listdir(actions_dir):
        if filename.endswith(".py"):
            # Import the file if it's a Python file
            module = importlib.import_module(f"actions.{filename[:-3]}")

            # Check if the file has a get_actions action
            if hasattr(module, "get_actions"):
                # If yes, call the action and retrieve the actions
                action_funcs = module.get_actions()

                # Add the actions to the 'actions' dictionary
                for name in action_funcs:
                    add_action(name, action_funcs[name])

    # Remove the added path from the Python system path
    sys.path.pop(0)


if __name__ == "__main__":
    register_actions()

    def test_action_handler(arguments):
        input = arguments["input"]
        return input

    # Test for add_action
    test_action = {
        "test": {
            "function": {
                "name": "test",
                "description": "A test action",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Some test input",
                        },
                    },
                },
                "required": ["input"],
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": test_action_handler,
        },
    }
    # for each in test_action:
    for each in test_action:
        add_action(each, test_action[each])
    assert each in actions

    # Test for use_action
    assert use_action("test", {"input": "test"}) == "test"

    # Test for remove_action
    remove_action("test")
    assert "test" not in actions
