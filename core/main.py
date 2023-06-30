import threading
import time
import uuid
import logging

from functions import register_skill_functions, get_all_functions

import loop
import database

from flask import Flask, request

from handle_user_input import handle_user_input

app = Flask(__name__)

log = logging.getLogger("werkzeug")
log.disabled = True

chroma_client = database.get_client()
collections = database.get_collections()
user_input_collection = collections["user_terminal_input"]


@app.route("/msg")
def create_input_event():
    userText = request.args.get("msg")  # Get data from input, we named it 'msg'
    # generate a uuid
    document_id = uuid.uuid4()

    user_input_collection.add(
        ids=[str(document_id)],
        documents=[userText],
        metadatas=[{"processed": False, "sender": "user"}],
    )
    print("input event created")
    return "", 200  # Return a successful HTTP response


def run_loop():
    while True:
        handle_user_input()
        loop.main()
        time.sleep(1)


def main():
    register_skill_functions()
    print("Registering skills...")
    print(get_all_functions())
    print("I am waking up...")
    # Start the loop in a separate thread
    threading.Thread(target=run_loop, daemon=True).start()


if __name__ == "__main__":
    main()
    app.run()
