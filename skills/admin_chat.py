import requests
import logging
import threading
from core.memory import add_event
from core.constants import agent_name


from flask import Flask, request

app = Flask(__name__)

log = logging.getLogger("werkzeug")
log.disabled = True


@app.route("/msg")
def create_input_event():
    userText = request.args.get("msg")  # Get data from input, we named it 'msg'
    add_event("user: " + userText, "user", "conversation")
    return "", 200  # Return a successful HTTP response


def run_app():
    app.run()


flask_thread = threading.Thread(target=run_app)
flask_thread.start()


def respond(arguments):
    message = arguments["message"]
    # Send a message to the user terminal listener
    add_event(message, agent_name, "conversation")
    try:
        requests.get("http://127.0.0.1:5001/response", params={"msg": message})
        add_event("The user is connected. I sent them a message.", agent_name, "response_status")
    except:
        # noop
        add_event("The user is not connected. They might be able to read the terminal but they might not be there. I guess I'll have to figure it out myself and try them later.", agent_name, "response_status")

# respond to user input
def get_skills():
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
            "handler": respond,
        },
    }
