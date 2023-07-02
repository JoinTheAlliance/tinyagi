# actions/actions.py

import os
import json

from core.memory import memory_client, create_event, get_collection_data
from core.action import (
    add_action as core_add_action,
    remove_action as core_remove_action,
)

def search_actions(arguments):
    query = arguments.get("query")
    # Here we are assuming the collection supports a search action
    collection_data = get_collection_data("actions", query)
    collection_data_documents = collection_data["documents"][0]
    # join collection_data_documents with newlines
    function_documents = "\n".join(collection_data_documents)

    create_event("I searched for actions and got the following:\n" + function_documents)
    return function_documents

def get_actions():
    return {
        "search_actions": {
            "function": {
                "name": "search_actions",
                "description": "Query the action collection and return the most likely actions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query to search for actions",
                        },
                    },
                    "required": ["query"],
                },
            },
            "handler": search_actions,
        }
    }


# Test your actions
if __name__ == "__main__":
    def add_action(arguments):
        name = arguments.get("name")
        function_action = arguments.get("function_action")
        function_handler = arguments.get("function_handler")

        # Create python script for action
        script_content = (
            """
    def get_actions():
        return {
            \""""
            + name
            + """\": {
                "function": """
            + json.dumps(function_action, indent=4)
            + """,
                "handler": """
            + function_handler.__name__
            + """
            }
        }
        """
        )

        with open(f"actions/{name}.py", "w") as function_script:
            function_script.write(script_content)

        # Add action in core.actions module
        function_info = {"function": function_action, "handler": function_handler}
        core_add_action(name, function_info)


    def remove_action(arguments):
        name = arguments.get("name")
        # Remove python script for action
        os.remove(f"actions/{name}.py")

        # Remove action in core.actions module
        core_remove_action(name)

    # Test add_action
    add_action({"name": "test_action", "function_action": {"description": "This is a test action."}, "function_handler": add_action})

    # Test search_actions
    search_actions_results = search_actions({"query": "test_action"})
    print("search_actions_results")
    print(search_actions_results)

    # Test remove_action
    remove_action({"name": "test_action"})