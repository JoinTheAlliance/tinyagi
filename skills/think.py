# think about things that are going on
def get_functions():
    # return an empty dict
    return {
        "think": {
            "payload": {
                "name": "think",
                "description": "Think about things that are going on, consider what to do next or dig into a creative impulse. This is a good place to start if you're not sure what to do next.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to think about",
                        }
                    },
                    "required": ["topic"],
                },
            },
            "handler": think,
        }
    }

def think(properties):
    topic = properties["topic"]
    print("I'm thinking about " + topic)