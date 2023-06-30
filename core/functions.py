import importlib
import os
import sys
from utils import write_debug_log

functions = {}


def call_function(name, *args, **kwargs):
    write_debug_log("call_function called on " + name + "\nargs: " + str(args) + "\nkwargs: " + str(kwargs))
    if name in functions:
        return functions[name](*args, **kwargs)
    else:
        return None


# add function
def add_function(name, function):
    write_debug_log("add_function called: " + name)
    functions[name] = function


# get function
def get_function(name):
    write_debug_log("get_function called on " + name)
    if name in functions:
        return functions[name]
    else:
        return None


# get all functions
def get_all_functions():
    write_debug_log("get_all_functions called")
    return functions


# remove function
def remove_function(name):
    write_debug_log("remove_function called on " + name)
    if name in functions:
        del functions[name]
    else:
        return None


def register_skill_functions():
    write_debug_log("register_skill_functions called")
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
                    add_function(name, functions[name])
            else:
                # The file does not have a get_functions function
                pass
        else:
            # The file is not a python file
            pass
