import os
from dotenv import load_dotenv
from agentlogger import log, print_header

from agentaction import import_actions
from agentmemory import wipe_all_memories
from agentloop import (
    start as start_loop,
    create_context_builders,
)

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


def start(
    steps=None,
    actions_dir="./tinyagi/actions",
    context_dir="./tinyagi/context",
    seed_data=None,
    reset=False,
):
    print_logo()

    if steps is None:
        context_step = create_context_builders(context_dir)
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

    # if seed_data is not None:
    #     import_file_to_memory(seed_data)

    if actions_dir is not None:
        import_actions(actions_dir)

    loop_dict = start_loop(steps)
    return loop_dict
