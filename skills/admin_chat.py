import requests

# respond to user input
def get_functions():
    # return an empty dict
    return {
        "respond_to_admin_chat": {
            "payload": {
                "name": "admin_chat",
                "description": "Respond to a message from the admin_chat channel. ",
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
        "message_to_admin_chat": {
            "payload": {
                "name": "admin_chat",
                "description": "Send a message to admin_chat to let the admin know things are okay, or ask for help if you get stuck. ",
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
        }
    }

def respond(properties):
    message = properties["message"]
    print("I'm thinking")
    # Send a message to the user terminal listener
    requests.get("http://127.0.0.1:5001/response", params={"msg": message})
