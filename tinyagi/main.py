import importlib
import json
import os
import sys
import time
from agentaction import import_actions
from agentmemory import create_memory, wipe_all_memories
from dotenv import load_dotenv
from pyfiglet import Figlet
from rich.console import Console

from agentloop import start as start_loop

from tinyagi.steps import act
from tinyagi.steps import decide
from tinyagi.steps import orient

# Suppress warning
os.environ["TOKENIZERS_PARALLELISM"] = "False"

console = Console()

load_dotenv()  # take environment variables from .env.


def import_context_builders(context_dir):
    """
    Import all the actions present in the 'context_dir' directory
    First, check if get_actions function exists inside python file
    The actions returned are then added to the 'actions' dictionary.

    Returns:
    None
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
    context_builders = import_context_builders(context_dir)
    def build_context(context={}):
        """
        Build the context dictionary by calling all the context builders

        Returns:
        context: the context dictionary
        """

        if context is None:
            context = {}
        
        for context_builder in context_builders:
            context = context_builder(context)
        return context

    return build_context


def print_ascii_art():
    """
    Prints ASCII art of the given text using pyfiglet.

    Parameters:
    - text (str): the text to print as ASCII art
    """

    f = Figlet(font="letters")
    print("\n")
    console.print(f.renderText("tinyagi"), style="yellow")
    console.print("Starting...\n\n", style="BRIGHT_BLACK")


def seed_from_file(filename="./seeds.json"):
    with open(filename, "r") as f:
        return seed_from_json(json.load(f))


def seed_from_json(data):
    timestamps = [time.time() - (10 * i) for i in range(len(data))]
    for i, entry in enumerate(data):
        timestamp = timestamps[i]
        entry["metadata"]["created_at"] = str(timestamp)
        create_memory(entry["collection"], entry["message"], entry["metadata"])


def seed(seed_input):
    # if seed is a dictionary, use it as the seed data
    if isinstance(seed_input, dict):
        seed_from_json(seed_input)

    elif isinstance(seed_input, str) and seed_input.endswith(".json"):
        seed_from_file(seed_input)

    elif seed_input is True:
        seed_from_file
    # if seed is a string, try parsing it as a json file
    elif seed_input is not None:
        try:
            # parse string to dict
            seed_data = json.loads(seed_input)
            seed_from_json(seed_data)
        except:
            print("Invalid seed data. Must be a JSON file or a JSON string.")
            return


def start(
    steps=None,
    actions_dir="./tinyagi/actions",
    context_dir="./tinyagi/context",
    seed_data=None,
    reset=False,
):
    print_ascii_art()
    if steps is None:
        context_step = build_context_step(context_dir)
        steps = [context_step, orient, context_step, decide, context_step, act]

    if reset:
        wipe_all_memories()

    if seed_data is not None:
        seed(seed_data)

    if actions_dir is not None:
        import_actions(actions_dir)

    loop_dict = start_loop(steps)
    return loop_dict
