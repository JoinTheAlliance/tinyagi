# File: ./actions/tasks.py

import uuid

from core.memory import memory_client, get_formatted_collection_data

collection_name = "tasks"

def create_task_handler(arguments):
    """
    Handler action for creating a new task document.
    """
    task_text = arguments.get("text")
    if task_text:
        task_id = str(uuid.uuid4())  # Generate a unique ID for the task document
        collection = memory_client.get_or_create_collection(collection_name)
        collection.add(ids=[task_id], documents=[task_text])
        return task_id  # Return the generated task ID
    else:
        return None


def list_tasks_handler(arguments):
    """
    Handler action for listing recent tasks.
    """
    limit = arguments.get("limit", 10)
    collection_data = get_formatted_collection_data(
        collection_name, query_text="", n_results=limit
    )
    return collection_data


def search_tasks_handler(arguments):
    """
    Handler action for searching tasks based on a query text.
    """
    query_text = arguments.get("query_text")
    n_results = arguments.get("n_results", 5)
    collection_data = get_formatted_collection_data(
        collection_name, query_text=query_text, n_results=n_results
    )
    return collection_data


def delete_task_handler(arguments):
    """
    Handler action for deleting a task document based on its ID.
    """
    task_id = arguments.get("task_id")
    if task_id:
        collection = memory_client.get_or_create_collection(collection_name)
        collection.delete(ids=[task_id])
        return True
    else:
        return False


def update_task_handler(arguments):
    """
    Handler action for updating a task document based on its ID.
    """
    task_id = arguments.get("task_id")
    new_text = arguments.get("new_text")
    if task_id and new_text:
        collection = memory_client.get_or_create_collection(collection_name)
        collection.update(ids=[task_id], documents=[new_text])
        return True
    else:
        return False


def get_actions():
    """
    Returns a dictionary of actions related to tasks.
    """
    return {
        "create_task": {
            "function": {
                "name": "create_task",
                "description": "Create a new task document.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text content of the task document."
                        }
                    },
                    "required": ["text"]
                }
            },
            "handler": create_task_handler
        },
        "list_tasks": {
            "function": {
                "name": "list_tasks",
                "description": "List recent task documents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "number",
                            "description": "The maximum number of tasks to retrieve. Defaults to 10."
                        }
                    }
                }
            },
            "handler": list_tasks_handler
        },
        "search_tasks": {
            "function": {
                "name": "search_tasks",
                "description": "Search task documents based on a query text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {
                            "type": "string",
                            "description": "The query text to search for in task documents."
                        },
                        "n_results": {
                            "type": "number",
                            "description": "The maximum number of search results to retrieve. Defaults to 5."
                        }
                    },
                    "required": ["query_text"]
                }
            },
            "handler": search_tasks_handler
        },
        "delete_task": {
            "function": {
                "name": "delete_task",
                "description": "Delete a task document based on its ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The ID of the task document to delete."
                        }
                    },
                    "required": ["task_id"]
                }
            },
            "handler": delete_task_handler
        },
        "update_task": {
            "function": {
                "name": "update_task",
                "description": "Update a task document based on its ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The ID of the task document to update."
                        },
                        "new_text": {
                            "type": "string",
                            "description": "The new text content of the task document."
                        }
                    },
                    "required": ["task_id", "new_text"]
                }
            },
            "handler": update_task_handler
        },
    }


if __name__ == "__main__":
    arguments = {"text": "New task document"}
    task_id = create_task_handler(arguments)
    assert create_task_handler(arguments) != None

    arguments = {"limit": 5}
    result = list_tasks_handler(arguments)
    assert isinstance(result, str)

    arguments = {"query_text": "search"}
    result = search_tasks_handler(arguments)
    assert isinstance(result, str)

    arguments = {"task_id": task_id, "new_text": "Updated task"}
    assert update_task_handler(arguments) == True

    arguments = {"task_id": task_id}
    assert delete_task_handler(arguments) == True