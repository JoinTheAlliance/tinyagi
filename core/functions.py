# core/functions.py

# Dynamically load functions and use them
# Functions are executed by the "function calling" feature of the OpenAI API.

import os
import sys
import importlib
import json

from core.memory import create_event, memory_client

# Create an empty dictionary to hold the functions
functions = {}


def use_function(name, arguments):
    """
    Executes a function based on its name and arguments.

    If the function is present in the 'functions' dictionary, it calls the function with its arguments.
    Also, the usage of a function is logged as an event.
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

    # Call the function with its arguments if it exists in the 'functions' dictionary
    if name in functions:
        if decoded_correctly:
            # Log the usage of a function as an event
            create_event(
                f"I called the function (function call) `{name}` with the arguments: {argument_string}",
                "function",
            )
            return functions[name](arguments)
    create_event(
        f"I tried to call the function (function call) `{name}` with the arguments `{argument_string}` but it was not available. I should try again with one of the functions in my memory.",
        "function",
    )
    return None


def add_function(name, function):
    """
    Adds a new function to the functions dictionary and to the 'functions' collection.

    If the function is not present in the 'functions' collection, it is added.
    """
    # Add the function to the 'functions' dictionary
    functions[name] = function["handler"]
    collection = memory_client.get_or_create_collection("functions")
    # Check if the function is already present in the 'functions' collection
    if not collection.get(ids=[name])["ids"]:
        # If not, add the new function to the 'functions' collection
        collection.add(
            ids=[name],
            documents=[f"{name} - {function['payload']['description']}"],
            metadatas=[{"function_call": json.dumps(function["payload"])}],
        )


def get_function_handler(name):
    """
    Fetches a function based on its name.

    Returns the function if it is present in the 'functions' dictionary.
    """
    return functions.get(name, None)


def remove_function(name):
    """
    Removes a function based on its name from both the 'functions' dictionary and the 'functions' collection.

    Also, logs the removal of a function as an event.
    """
    if name in functions:
        # Remove the function from the 'functions' dictionary
        del functions[name]
        collection = memory_client.get_or_create_collection("functions")
        # Remove the function from the 'functions' collection
        if collection.get(ids=[name]):
            collection.delete(ids=[name])

        # Log the removal of a function as an event
        create_event(f"I removed the function {name}", "function")


def register_functions():
    """
    Registers all the functions present in the 'functions' directory.

    For each Python file in the 'functions' directory, it imports the file and calls the get_functions function if it exists.
    Then, it adds the returned functions to the 'functions' dictionary.
    """
    # Get the absolute path to the parent directory of the current file
    parent_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the absolute path to the 'functions' directory
    functions_dir = os.path.join(parent_dir, "..", "functions")

    # Add the parent directory of functions to the Python system path
    sys.path.insert(0, os.path.join(parent_dir, ".."))

    # Iterate through all of the files in the 'functions' directory
    for filename in os.listdir(functions_dir):
        if filename.endswith(".py"):
            # Import the file if it's a Python file
            module = importlib.import_module(f"functions.{filename[:-3]}")

            # Check if the file has a get_functions function
            if hasattr(module, "get_functions"):
                # If yes, call the function and retrieve the functions
                function_funcs = module.get_functions()

                # Add the functions to the 'functions' dictionary
                for name in function_funcs:
                    add_function(name, function_funcs[name])

    # Remove the added path from the Python system path
    sys.path.pop(0)


if __name__ == "__main__":
    register_functions()

    def test_function_handler(arguments):
        input = arguments["input"]
        return input

    # Test for add_function
    test_function = {
        "test": {
            "payload": {
                "name": "test",
                "description": "A test function",
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
            "handler": test_function_handler,
        },
    }
    # for each in test_function:
    for each in test_function:
        add_function(each, test_function[each])
    assert each in functions

    # Test for use_function
    assert use_function("test", {"input": "test"}) == "test"

    # Test for get_function_handler
    assert get_function_handler("test") == test_function_handler

    # Test for remove_function
    remove_function("test")
    assert "test" not in functions
