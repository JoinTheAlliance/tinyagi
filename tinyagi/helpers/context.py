import importlib
import os
import sys

def import_context_builders(context_dir):
    """
    Import all the context builders present in the 'context_dir' directory
    First, check if get_context_builders function exists inside python file
    The builders returned as the context_builders array

    Returns:
    context_builders: array of context builders
    """

    context_dir = os.path.abspath(context_dir)
    sys.path.insert(0, context_dir)

    context_builders = []

    for filename in os.listdir(context_dir):
        if filename.endswith(".py"):
            module = importlib.import_module(f"{filename[:-3]}")

            if hasattr(module, "get_context_builders"):
                new_context_builders = module.get_context_builders()
                for context_builder in new_context_builders:
                    context_builders.append(context_builder)
    sys.path.remove(context_dir)
    return context_builders


def build_context_step(context_dir):
    """
    Build a context step function from the context builders in the given directory

    Returns:
    context: the context dictionary
    """
    context_builders = import_context_builders(context_dir)

    def build_context(context={}):
        if context is None:
            context = {}

        for context_builder in context_builders:
            context = context_builder(context)
        return context

    return build_context

