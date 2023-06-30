import threading
import time
import uuid
import logging

from skill_handling import register_skills, get_all_skills

import loop
import memory

from flask import Flask, request

app = Flask(__name__)

log = logging.getLogger("werkzeug")
log.disabled = True

chroma_client = memory.get_client()
collections = memory.get_collections()

@app.route("/msg")
def create_input_event():
    userText = request.args.get("msg")  # Get data from input, we named it 'msg'
    # generate a uuid
    document_id = uuid.uuid4()

    collections["events"].add(
        ids=[str(document_id)],
        documents=[userText],
        metadatas=[{"type": "conversation", "connector": "admin_chat", "read": True, "event_creator": "administrator"}],
    )

    return "", 200  # Return a successful HTTP response


def run_loop():
    while True:
        loop.main()
        time.sleep(1)


def main():
    register_skills()
    print("Registering skills...")
    print(get_all_skills())
    print("I am waking up...")
    # Start the loop in a separate thread
    threading.Thread(target=run_loop, daemon=True).start()


if __name__ == "__main__":
    main()
    app.run()
