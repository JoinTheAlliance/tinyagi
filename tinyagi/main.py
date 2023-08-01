import asyncio
import os
import threading
from agentcomlink import register_message_handler
from dotenv import load_dotenv
from agentlogger import print_header
from tinyagi.actions.chat import initialize_twitch, response_handler
from tinyagi.constants import set_loop_dict
from tinyagi.utils import log

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


def start(
    steps=None,
    actions_dir="./tinyagi/actions",
    context_dir="./tinyagi/context",
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

    from uvicorn import Config, Server

    config = Config(
        "agentcomlink:start_server",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        factory=True,
    )
    server = Server(config)

    def start_server():
        asyncio.run(server.serve())

    # start the server in a new thread
    threading.Thread(target=start_server, daemon=True).start()

    # Register the message handler
    register_message_handler(lambda data: response_handler(data, loop_dict))

    initialize_twitch()

    return loop_dict
