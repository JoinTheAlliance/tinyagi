# functions/functions.py

import os
import json

from core.memory import memory_client, create_event, get_collection_data
from core.functions import (
    add_function as core_add_function,
    remove_function as core_remove_function,
)

def search_functions(arguments):
    query = arguments.get("query")
    # Here we are assuming the collection supports a search function
    collection_data = get_collection_data("functions", query)
    collection_data_documents = collection_data["documents"][0]
    # join collection_data_documents with newlines
    function_documents = "\n".join(collection_data_documents)

    create_event("I searched for functions and got the following:\n" + function_documents)
    return function_documents

def get_functions():
    return {
        "search_functions": {
            "payload": {
                "name": "search_functions",
                "description": "Query the function collection and return the most likely functions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query to search for functions",
                        },
                    },
                    "required": ["query"],
                },
            },
            "handler": search_functions,
        }
    }


# Test your functions
if __name__ == "__main__":
    def add_function(arguments):
        name = arguments.get("name")
        function_payload = arguments.get("function_payload")
        function_handler = arguments.get("function_handler")

        # Create python script for function
        script_content = (
            """
    def get_functions():
        return {
            \""""
            + name
            + """\": {
                "payload": """
            + json.dumps(function_payload, indent=4)
            + """,
                "handler": """
            + function_handler.__name__
            + """
            }
        }
        """
        )

        with open(f"functions/{name}.py", "w") as function_script:
            function_script.write(script_content)

        # Add function in core.functions module
        function_info = {"payload": function_payload, "handler": function_handler}
        core_add_function(name, function_info)


    def remove_function(arguments):
        name = arguments.get("name")
        # Remove python script for function
        os.remove(f"functions/{name}.py")

        # Remove function in core.functions module
        core_remove_function(name)

    # Test add_function
    add_function({"name": "test_function", "function_payload": {"description": "This is a test function."}, "function_handler": add_function})

    # Test search_functions
    search_functions_results = search_functions({"query": "test_function"})
    print("search_functions_results")
    print(search_functions_results)

    # Test remove_function
    remove_function({"name": "test_function"})