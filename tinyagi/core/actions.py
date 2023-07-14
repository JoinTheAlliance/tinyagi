# core/actions.py

# Dynamically load actions and use them
# actions are executed by the "function calling" feature of the OpenAI API.

import os
import sys
import importlib
import json

from agentmemory import (
    create_memory,
    delete_memory,
    get_memories,
    search_memory,
    wipe_category,
)
from easycompletion import count_tokens

from tinyagi.core.constants import TOKEN_DISPLAY_LIMIT
from .events import create_event, debug_log, get_epoch

# Create an empty dictionary to hold the actions
actions = {}


def get_actions():
    global actions
    return actions


def add_to_action_history(action_name, action_arguments={}, success=True):
    debug_log(f"Adding action to history: {action_name}")
    action_arguments["success"] = success
    current_epoch = get_epoch()
    action_arguments["epoch"] = current_epoch
    create_memory("action_history", action_name, action_arguments)


def get_action_history(n_results=20):
    # get the current epoch
    current_epoch = get_epoch()
    # now search for actions that occured within the last n epochs
    memories = get_memories(
        category="action_history",
        filter_metadata={"epoch": {"$gte": max(0, current_epoch - n_results)}},
    )
    debug_log(f"Getting action history: {memories}")
    return memories


def get_last_action():
    history = get_action_history(n_results=1)
    if len(history) == 0:
        return None
    last = history[0]["document"]
    debug_log(f"Getting last action: {last}")
    return last

def get_formatted_available_actions(summary):
    available_actions = get_available_actions(summary)
    formatted_available_actions = "\n".join(available_actions)
    while count_tokens(formatted_available_actions) > TOKEN_DISPLAY_LIMIT:
        if len(available_actions) == 1:
            raise Exception(
                "Single knowledge length is greater than token limit, should not happen"
            )
        # remove the last event
        available_actions = available_actions[:-1]
        formatted_available_actions = "\n".join([k["document"] for k in available_actions])

def get_available_actions(summary):
    available_actions = search_actions(search_text=summary, n_results=10)
    recommended_actions = []
    ignored_actions = []

    last_action = get_last_action()
    if last_action is not None:
        recommended_actions = actions[last_action]["suggestion_after_actions"]
        ignored_actions = actions[last_action]["never_after_actions"]
    merged_actions = []
    for action in available_actions:
        # check if the available action is in the actions dictionary
        if action["id"] in recommended_actions:
            merged_actions.append(f"(recommended) {action['document']}")
        elif action["id"] in ignored_actions:
            continue
        else:
            merged_actions.append(action["document"])
    debug_log(f"Getting available actions: {merged_actions}")
    return merged_actions


def search_actions(search_text, n_results=5):
    """
    Searches for actions based on a query text.

    Returns a list of actions.
    """
    # Search for actions in the 'actions' collection
    search_results = search_memory(
        "actions", search_text=search_text, n_results=n_results
    )
    debug_log(f"Searching actions: {search_results}")
    return search_results


def use_action(function_name, arguments):
    if function_name not in actions:
        add_to_action_history(function_name, arguments, success=False)
        return {"success": False, "response": "Action not found"}

    add_to_action_history(function_name, arguments)
    result = actions[function_name]["handler"](arguments)

    debug_log(f"Using action: {function_name} with arguments: {arguments}")
    debug_log(f"Use action result: {result}")

    return {"success": True, "result": result}


def add_action(name, action):
    """
    Adds a new action to the actions dictionary and to the 'actions' collection.

    If the action is not present in the 'actions' collection, it is added.
    """
    # Add the action to the 'actions' dictionary
    actions[name] = action
    create_memory(
        "actions",
        f"{name} - {action['function']['description']}",
        {"name": name, "function": json.dumps(action["function"])},
        id=name,
    )
    debug_log(f"Adding action: {name} with function: {action['function']}")


def get_action(name):
    """
    Returns a action based on its name from the 'actions' dictionary.
    """
    debug_log(f"Getting action: {name}")
    if name in actions:
        return actions[name]
    else:
        return None


def remove_action(name):
    """
    Removes a action based on its name from both the 'actions' dictionary and the 'actions' collection.

    Also, logs the removal of a action as an event.
    """
    debug_log(f"Removing action: {name}")
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
    debug_log("Registering actions")
    # Wipe any existing actions to prevent split sources of truth
    wipe_category("actions")
    global actions
    actions = {}

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

                # Actions are an array of objects
                # Iterate through the array
                for i in range(len(action_funcs)):
                    name = action_funcs[i]["function"]["name"]
                    add_action(name, action_funcs[i])

    # Remove the added path from the Python system path
    sys.path.pop(0)
    debug_log("Registered actions")
