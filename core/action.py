# core/action.py

# Dynamically load actions and use them
# actions are executed by the "action calling" feature of the OpenAI API.

import os
import sys
import importlib
import json

from core.memory import create_event, memory_client

# Create an empty dictionary to hold the actions
actions = {}


def use_action(name, arguments):
    """
    Executes a action based on its name and arguments.

    If the action is present in the 'actions' dictionary, it calls the action with its arguments.
    Also, the usage of a action is logged as an event.
    """
    # If arguments are a JSON string, parse it to a dictionary
    decoded_correctly = True
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except:
            decoded_correctly = False

    # Convert the arguments dictionary to a string representation
    argument_string = ", ".join(f"{key}: {str(val)}" for key, val in arguments.items())

    # Call the action with its arguments if it exists in the 'actions' dictionary
    if name in actions:
        if decoded_correctly:
            # Log the usage of a action as an event
            create_event(
                f"I called the action (action call) `{name}` with the arguments: {argument_string}",
                "action",
            )
            return actions[name](arguments)
    create_event(
        f"I tried to call the action (action call) `{name}` with the arguments `{argument_string}` but it was not available. I should try again with one of the actions in my memory.",
        "action",
    )
    return None


def add_action(name, action):
    """
    Adds a new action to the actions dictionary and to the 'actions' collection.

    If the action is not present in the 'actions' collection, it is added.
    """
    # Add the action to the 'actions' dictionary
    actions[name] = action["handler"]
    collection = memory_client.get_or_create_collection("actions")
    # Check if the action is already present in the 'actions' collection
    if not collection.get(ids=[name])["ids"]:
        # If not, add the new action to the 'actions' collection
        collection.add(
            ids=[name],
            documents=[f"{name} - {action['function']['description']}"],
            metadatas=[{"action_call": json.dumps(action["function"])}],
        )


def get_action_handler(name):
    """
    Fetches a action based on its name.

    Returns the action if it is present in the 'actions' dictionary.
    """
    return actions.get(name, None)


def remove_action(name):
    """
    Removes a action based on its name from both the 'actions' dictionary and the 'actions' collection.

    Also, logs the removal of a action as an event.
    """
    if name in actions:
        # Remove the action from the 'actions' dictionary
        del actions[name]
        collection = memory_client.get_or_create_collection("actions")
        # Remove the action from the 'actions' collection
        if collection.get(ids=[name]):
            collection.delete(ids=[name])

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
            "handler": test_action_handler,
        },
    }
    # for each in test_action:
    for each in test_action:
        add_action(each, test_action[each])
    assert each in actions

    # Test for use_action
    assert use_action("test", {"input": "test"}) == "test"

    # Test for get_action_handler
    assert get_action_handler("test") == test_action_handler

    # Test for remove_action
    remove_action("test")
    assert "test" not in actions
