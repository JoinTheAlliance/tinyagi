import os
from dotenv import load_dotenv
from agentlogger import print_header
from tinyagi.constants import set_loop_dict
from tinyagi.utils import log
import importlib
import os
import sys
from agentaction import import_actions
from agentmemory import wipe_all_memories
from agentloop import (
    start as start_loop,
)
from tinyagi.context.builder import create_context_builders

from tinyagi.steps.initialize import initialize

from tinyagi.steps import act
from tinyagi.steps import decide
from tinyagi.steps import orient

# Suppress warning
os.environ["TOKENIZERS_PARALLELISM"] = "False"

load_dotenv()  # take environment variables from .env.


def print_logo():
    """
    Prints ASCII logo using pyfiglet.
    """

    print("\n")
    print_header("tinyagi", color="yellow", font="slant")
    log("Starting...", type="system", color="BRIGHT_BLACK")


def start_connectors(connectors_dir, loop_dict):
    """
    Build a context step function from the context builders in the given directory

    Returns:
    context: the context dictionary
    """
    connectors_dir = os.path.abspath(connectors_dir)
    sys.path.insert(0, connectors_dir)

    for filename in os.listdir(connectors_dir):
        if filename.endswith(".py"):
            module = importlib.import_module(f"{filename[:-3]}")

            if hasattr(module, "start_connector"):
                module.start_connector(loop_dict)
    sys.path.remove(connectors_dir)


def start(
    steps=None,
    actions_dir="./tinyagi/actions",
    context_dir="./tinyagi/context",
    connectors_dir="./tinyagi/connectors",
    seed_data=None,
    reset=False,
    paused=False,
    verbose=False
):
    print_logo()

    if steps is None:
        context_step = create_context_builders(context_dir, verbose)
        steps = [
            initialize,
            orient,
            context_step,
            decide,
            context_step,
            act,
        ]
    if reset:
        wipe_all_memories()

    if actions_dir is not None:
        print("Imported actions from " + actions_dir)
        import_actions(actions_dir)
    else:
        print("No actions directory provided, skipping import")

    # if seed_data is not None:
    #     import_file_to_memory(seed_data)
    print("Starting loop...")
    loop_dict = start_loop(steps, paused=paused)
    set_loop_dict(loop_dict)

    start_connectors(connectors_dir, loop_dict)

    return loop_dict
