# core/actions.py

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

from tinyagi.core.constants import MAX_PROMPT_TOKENS
from .events import create_event, debug_log, get_epoch

# Create an empty dictionary to hold the actions
actions = {}


def compose_action_function(action, observation):
    """
    This function generates a specific action function based on the given action and observation.

    Args:
        action: A dictionary representing an action. This action contains a 'function' key that
                represents the function to be composed.
        observation: A dictionary representing an observation that will be used to fill placeholders
                     in the action function.

    Returns:
        A string representing the composed function.
    """
    # TODO: iterate through keys and replace {{}} with observation[key]
    return action["function"]


def compose_action_prompt(action, observation):
    """
    This function generates a specific action prompt based on the given action and observation.

    Args:
        action: A dictionary representing an action. This action contains a 'prompt' key that
                represents the prompt to be composed.
        observation: A dictionary representing an observation that will be used to fill placeholders
                     in the action prompt.

    Returns:
        A string representing the composed prompt.
    """
    return action["prompt"](observation)


def get_actions():
    """
    This function retrieves all the actions present in the global `actions` dictionary.

    Returns:
        A dictionary of all actions.
    """
    global actions
    return actions


def add_to_action_history(action_name, action_arguments={}, success=True):
    """
    This function adds an executed action to the action history.

    Args:
        action_name: A string representing the name of the action that was executed.
        action_arguments: A dictionary representing the arguments that were used to execute the action.
        success: A boolean indicating whether the action was successfully executed or not.
    """
    debug_log(f"Adding action to history: {action_name}")
    action_arguments["success"] = success
    current_epoch = get_epoch()
    action_arguments["epoch"] = current_epoch
    create_memory("action_history", action_name, action_arguments)


def get_action_history(n_results=20):
    """
    This function retrieves the most recent actions executed within the last `n_results` epochs.

    Args:
        n_results: An integer representing the number of epochs to consider for retrieving the action history.

    Returns:
        A list of actions that were executed within the last `n_results` epochs.
    """
    current_epoch = get_epoch()
    memories = get_memories(
        category="action_history",
        filter_metadata={"epoch": {"$gte": max(0, current_epoch - n_results)}},
    )
    debug_log(f"Getting action history: {memories}")
    return memories


def get_last_action():
    """
    This function retrieves the last executed action from the action history.

    Returns:
        A string representing the name of the last executed action or None if no action was found.
    """
    history = get_action_history(n_results=1)
    if len(history) == 0:
        return None
    last = history[0]["document"]
    debug_log(f"Getting last action: {last}")
    return last


def get_formatted_available_actions(summary):
    """
    This function retrieves a formatted string of the available actions based on the given summary.

    Args:
        summary: A string representing a summary that is used to determine which actions are available.

    Returns:
        A string representing the available actions.
    """
    header_text = "Available actions for me to choose from:"
    available_actions = get_available_actions(summary)
    formatted_available_actions = "\n".join(available_actions)
    while count_tokens(formatted_available_actions) > MAX_PROMPT_TOKENS:
        if len(available_actions) == 1:
            raise Exception(
                "Single knowledge length is greater than token limit, should not happen"
            )
        available_actions = available_actions[:-1]
        formatted_available_actions = "\n".join(
            [k["document"] for k in available_actions]
        )
    return header_text + "\n" + formatted_available_actions + "\n"


def get_available_actions(summary):
    """
    This function retrieves the available actions based on the given summary.

    Args:
        summary: A string representing a summary that is used to determine which actions are available.

    Returns:
        A list of strings representing the available actions.
    """
    available_actions = search_actions(search_text=summary, n_results=10)
    recommended_actions = []
    ignored_actions = []

    last_action = get_last_action()
    if last_action is not None:
        recommended_actions = actions[last_action]["suggestion_after_actions"]
        ignored_actions = actions[last_action]["never_after_actions"]
    merged_actions = []
    for action in available_actions:
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

    Args:
        search_text: A string representing the query text used to search for actions.
        n_results: An integer representing the maximum number of results to return.

    Returns:
        A list of dictionaries representing the found actions.
    """
    search_results = search_memory(
        "actions", search_text=search_text, n_results=n_results
    )
    debug_log(f"Searching actions: {search_results}")
    return search_results


def use_action(function_name, arguments):
    """
    Execute a specific action by its function name.

    Arguments:
    function_name (str): The name of the action's function to execute.
    arguments (dict): The arguments required by the action's function.

    Returns:
    dict: Contains the "success" key, which is True if the action was found and executed, False otherwise.
          If the action was found and executed, the dictionary also contains the "result" key,
          which carries the result of the action execution.
    """
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
    Add a new action to the actions dictionary and the 'actions' collection in memory.

    Arguments:
    name (str): The name of the action.
    action (dict): The action data to be added.

    Returns:
    None
    """
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
    Retrieve a specific action by its name from the 'actions' dictionary.

    Arguments:
    name (str): The name of the action to retrieve.

    Returns:
    dict or None: The action if found in the 'actions' dictionary, otherwise None.
    """
    debug_log(f"Getting action: {name}")
    if name in actions:
        return actions[name]
    else:
        return None


def remove_action(name):
    """
    Remove a specific action by its name from both the 'actions' dictionary and the 'actions' collection in memory.

    Arguments:
    name (str): The name of the action to remove.

    Returns:
    None
    """
    debug_log(f"Removing action: {name}")
    if name in actions:
        del actions[name]
        delete_memory("actions", name)
        create_event(f"I removed the action {name}", "action")


def register_actions():
    """
    Register all the actions present in the 'actions' directory by importing the Python files and calling the
    get_actions function if it exists. The actions returned are then added to the 'actions' dictionary.

    This function first unregisters any previously registered actions before registering new ones.

    Returns:
    None
    """
    unregister_actions()

    debug_log("Registering actions")

    parent_dir = os.path.dirname(os.path.abspath(__file__))
    actions_dir = os.path.join(parent_dir, "..", "actions")
    sys.path.insert(0, os.path.join(parent_dir, ".."))

    for filename in os.listdir(actions_dir):
        if filename.endswith(".py"):
            module = importlib.import_module(f"actions.{filename[:-3]}")

            if hasattr(module, "get_actions"):
                action_funcs = module.get_actions()

                for i in range(len(action_funcs)):
                    name = action_funcs[i]["function"]["name"]
                    add_action(name, action_funcs[i])

    sys.path.pop(0)
    debug_log("Registered actions")


def unregister_actions():
    """
    Unregister all the actions by wiping the 'actions' collection in memory and resetting the 'actions' dictionary.

    Returns:
    None
    """
    wipe_category("actions")
    global actions
    actions = {}
