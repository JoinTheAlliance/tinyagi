# Dynamically load skills and use them
# Skills are executed by the "function calling" feature of the OpenAI API.

import os
import sys
import importlib
import json

from core.constants import agent_name
from core.memory import add_event, get_collection

# Create an empty dictionary to hold the functions
functions = {}

# Retrieve the collection of skills
skill_collection = get_collection("skills")


def use_skill(name, arguments):
    """
    Executes a skill based on its name and arguments.

    If the skill is present in the 'functions' dictionary, it calls the skill with its arguments.
    Also, the usage of a skill is logged as an event.
    """
    # If arguments are a JSON string, parse it to a dictionary
    if isinstance(arguments, str):
        arguments = json.loads(arguments)

    # Convert the arguments dictionary to a string representation
    argument_string = ", ".join(f"{key}: {str(val)}" for key, val in arguments.items())

    # Log the usage of a skill as an event
    add_event(
        f"I used the skill `{name}` with the arguments: {argument_string}",
        agent_name,
        "skill",
    )

    # Call the function with its arguments if it exists in the 'functions' dictionary
    if name in functions:
        return functions[name](arguments)
    else:
        return None


def add_skill(name, function):
    """
    Adds a new skill to the functions dictionary and to the 'skills' collection.

    If the skill is not present in the 'skills' collection, it is added.
    """
    # Add the function to the 'functions' dictionary
    functions[name] = function["handler"]

    # Check if the skill is already present in the 'skills' collection
    if not skill_collection.get(ids=[name])["ids"]:
        # If not, add the new skill to the 'skills' collection
        skill_collection.add(
            ids=[name],
            documents=[f"{name} - {function['payload']['description']}"],
            metadatas=[{"function_call": json.dumps(function["payload"])}],
        )


def get_skill(name):
    """
    Fetches a skill based on its name.

    Returns the function if it is present in the 'functions' dictionary.
    """
    return functions.get(name, None)


def get_all_skills():
    """
    Returns all skills in the 'functions' dictionary.
    """
    return functions


def remove_skill(name):
    """
    Removes a skill based on its name from both the 'functions' dictionary and the 'skills' collection.

    Also, logs the removal of a skill as an event.
    """
    if name in functions:
        # Remove the skill from the 'functions' dictionary
        del functions[name]

        # Remove the skill from the 'skills' collection
        if skill_collection.get(ids=[name]):
            skill_collection.delete(ids=[name])

        # Log the removal of a skill as an event
        add_event(f"I removed the skill {name}", agent_name, "skill")


def register_skills():
    """
    Registers all the skills present in the 'skills' directory.

    For each Python file in the 'skills' directory, it imports the file and calls the get_skills function if it exists.
    Then, it adds the returned functions to the 'functions' dictionary.
    """
    # Get the absolute path to the parent directory of the current file
    parent_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the absolute path to the 'skills' directory
    skills_dir = os.path.join(parent_dir, "..", "skills")

    # Add the parent directory of skills to the Python system path
    sys.path.insert(0, os.path.join(parent_dir, ".."))

    # Iterate through all of the files in the 'skills' directory
    for filename in os.listdir(skills_dir):
        if filename.endswith(".py"):
            # Import the file if it's a Python file
            module = importlib.import_module(f"skills.{filename[:-3]}")

            # Check if the file has a get_skills function
            if hasattr(module, "get_skills"):
                # If yes, call the function and retrieve the skills
                skill_funcs = module.get_skills()

                # Add the skills to the 'functions' dictionary
                for name in skill_funcs:
                    add_skill(name, skill_funcs[name])

    # Remove the added path from the Python system path
    sys.path.pop(0)


if __name__ == "__main__":
    register_skills()
    def test_skill_handler(arguments):
        input = arguments["input"]
        return input

    # Test for add_skill
    test_skill = {
        "test": {
            "payload": {
                "name": "test",
                "description": "A test skill",
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
            "handler": test_skill_handler,
        },
    }
    # for each in test_skill:
    for each in test_skill:
        add_skill(each, test_skill[each])
    assert each in functions

    # Test for use_skill
    assert use_skill("test", {"input": "test"}) == "test"

    # Test for get_skill
    assert get_skill("test") == test_skill_handler

    # Test for get_all_skills
    all_skills = get_all_skills()
    assert all_skills["test"] == test_skill_handler

    # Test for remove_skill
    remove_skill("test")
    assert "test" not in functions
    assert not skill_collection.get(ids=["test"])["ids"]
    print("All tests passed!")