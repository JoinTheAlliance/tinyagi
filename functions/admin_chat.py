# functions/admin_chat.py

import os
import sys
import requests
import logging
import threading
from core.memory import create_event, wipe_memory


from flask import Flask, request

app = Flask(__name__)

log = logging.getLogger("werkzeug")
log.disabled = True


@app.route("/msg")
def handle_incoming_message():
    receive_message(request.args.get("msg"))
    return "", 200  # Return a successful HTTP response


def run_app():
    app.run()


flask_thread = threading.Thread(target=run_app)
flask_thread.start()


def receive_message(msg):
    # if the user calls "reset database", reset the database (wipe_memory)
    if msg == "reset database":
        wipe_memory()
    if msg == "restart":
        python = sys.executable
        os.execl(python, python, *sys.argv)
    else:
        create_event("user: " + msg, "user", "conversation")


def send_message(arguments):
    message = arguments["message"]
    # Send a message to the user terminal listener
    create_event(message, "assistant", "conversation")
    try:
        requests.get("http://127.0.0.1:5001/response", params={"msg": message})
        create_event(
            "The user is connected. I sent them a message.",
            "assistant",
            "response_status",
        )
    except:
        # noop
        create_event(
            "The user is not connected. They might be able to read the terminal but they might not be there. I guess I'll have to figure it out myself and try them later.",
            "assistant",
            "response_status",
        )


# respond to user input
def get_functions():
    # return an empty dict
    return {
        "message_user": {
            "payload": {
                "name": "message_user",
                "description": "Send a message to the user's connected terminal window, either as a response to an incoming message in the event stream or to let them know that things are okay, or ask for help if you get stuck. ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The message to send to the person",
                        }
                    },
                    "required": ["message"],
                },
            },
            "handler": send_message,
        },
    }


if __name__ == "__main__":
    # Test send_message
    try:
        send_message({"message": "Test message"})
    except Exception as e:
        print(f"send_message crashed with exception: {e}")

    # Test receive_message
    try:
        receive_message("Test message")
    except Exception as e:
        print(f"receive_message crashed with exception: {e}")

    print("Test complete.")
