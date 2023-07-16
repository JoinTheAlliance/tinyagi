import json
import os
import time
from agentaction import import_actions
from agentmemory import create_memory, wipe_all_memories
from dotenv import load_dotenv
from pyfiglet import Figlet
from rich.console import Console

from agentloop import start as start_loop

from steps import orient, decide, act

# Suppress warning
os.environ["TOKENIZERS_PARALLELISM"] = "False"

console = Console()

load_dotenv()  # take environment variables from .env.


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
    timestamps = [time.time() - (10 * i) for i in range(len(seed_data))]
    for i, entry in enumerate(data):
        timestamp = timestamps[i]
        entry["metadata"]["created_at"] = str(timestamp)
        create_memory(entry["collection"], entry["message"], entry["metadata"])


def seed(seed_input):
    # if seen is a dictionary, use it as the seed data
    if isinstance(seed_input, dict):
        seed_from_json(seed_input)

    elif seed_input is not None and seed_input.endswith(".json"):
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
    steps=[orient, decide, act],
    actions_dir="./tinyagi/actions",
    seed_data=None,
    reset=False,
):
    if seed_data is not None:
        seed(seed_data)

    if reset:
        wipe_all_memories()

    if actions_dir is not None:
        import_actions(actions_dir)

    print_ascii_art()
    loop_dict = start_loop(steps)
    return loop_dict
