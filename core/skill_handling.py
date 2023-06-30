# Skill handling
# Skills in this case specifically refer to functions that can be called by the OpenAI API.

import importlib
import os
import sys
from utils import write_debug_log
from memory import get_collection

functions = {}
skill_collection = get_collection("skills")

def use_skill(name, *args, **kwargs):
    write_debug_log("use_skill called on " + name + "\nargs: " + str(args) + "\nkwargs: " + str(kwargs))
    if name in functions:
        return functions[name](*args, **kwargs)
    else:
        return None

# add function
def add_skill(name, function):
    write_debug_log("add_skill called: " + name)
    functions[name] = function["handler"]
    print("functions[name]")
    print(functions[name])

    # check if skill is in skills collection
    if skill_collection.get(ids=[name]) != []:
        # remove the skill and re-add it
        skill_collection.delete(ids=[name])

    # add skill to skills collection
    # use the description as the document
    skill_collection.add(
        ids=[name],
        documents=[name + " - " + function["payload"]["description"]],
        metadatas=[{"function": str(function["payload"])}],
    )

# get function
def get_skill(name):
    write_debug_log("get_skill called on " + name)
    if name in functions:
        return functions[name]
    else:
        return None


# get all functions
def get_all_skills():
    write_debug_log("get_all_skills called")
    return functions


# remove function
def remove_skill(name):
    if skill_collection.get(ids=[name]) != []:
        # remove the skill and re-add it
        skill_collection.delete(ids=[name])

    write_debug_log("remove_skill called on " + name)
    if name in functions:
        del functions[name]
    else:
        return None



def register_skills():
    write_debug_log("register_skills called")
    # Get the absolute path to the parent directory of the current file
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    skills_dir = os.path.join(parent_dir, "..", "skills")

    # Add the parent directory of skills to the Python system path
    sys.path.insert(0, os.path.join(parent_dir, ".."))

    # Search through all of the files in the skills directory
    for filename in os.listdir(skills_dir):
        if filename.endswith(".py"):
            write_debug_log("reading skill functions from " + filename)
            # Import the file
            module = importlib.import_module("skills." + filename[:-3])

            # Check if the file has a get_functions function
            if hasattr(module, "get_functions"):
                # Call the function
                functions = module.get_functions()
                # Add the functions to the functions dictionary
                for name in functions:
                    add_skill(name, functions[name])
            else:
                # The file does not have a get_functions function
                pass
        else:
            # The file is not a python file
            pass
