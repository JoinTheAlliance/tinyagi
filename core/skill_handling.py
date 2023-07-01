# Skill handling
# Skills in this case specifically refer to functions that can be called by the OpenAI API.
import os
import sys
import importlib

from core.constants import agent_name
from core.memory import add_event, get_collection
import json

functions = {}
skill_collection = get_collection("skills")


def use_skill(name, arguments):
    # If arguments are a JSON string, parse it to a dictionary
    if isinstance(arguments, str):
        arguments = json.loads(arguments)
    argument_string = ""

    for key in arguments:
        argument_string += key + ": " + str(arguments[key]) + ", "
    # Remove the last comma
    argument_string = argument_string[:-2]
    
    add_event("I used the skill `" + name + "` with the arguments: " + argument_string, agent_name, "skill")
    if name in functions:
        return functions[name](arguments)
    else:
        return None

# add function
def add_skill(name, function):
    functions[name] = function["handler"]
    
    if skill_collection.get(ids=[name])["ids"] == []:
        skill_collection.add(
            ids=[name],
            documents=[name + " - " + function["payload"]["description"]],
            metadatas=[{"function_call": json.dumps(function["payload"])}],
        )

# get function
def get_skill(name):
    if name in functions:
        return functions[name]
    else:
        return None


# get all functions
def get_all_skills():
    return functions


# remove function
def remove_skill(name):
    if skill_collection.get(ids=[name]) != []:
        # remove the skill and re-add it
        skill_collection.delete(ids=[name])

    if name in functions:
        add_event("I removed the skill " + name, agent_name, "skill")
        del functions[name]
    else:
        return None



def register_skills():
    # Get the absolute path to the parent directory of the current file
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    skills_dir = os.path.join(parent_dir, "..", "skills")

    # Add the parent directory of skills to the Python system path
    sys.path.insert(0, os.path.join(parent_dir, ".."))

    # Search through all of the files in the skills directory
    for filename in os.listdir(skills_dir):
        if filename.endswith(".py"):
            # Import the file
            module = importlib.import_module("skills." + filename[:-3])

            # Check if the file has a get_skills function
            if hasattr(module, "get_skills"):
                # Call the function
                functions = module.get_skills()
                # Add the functions to the functions dictionary
                for name in functions:
                    add_skill(name, functions[name])
            else:
                # The file does not have a get_skills function
                pass
        else:
            # The file is not a python file
            pass

    # reset the path
    sys.path.pop(0)