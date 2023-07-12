from agentmemory import (
    create_memory,
    delete_memory,
    search_memory,
    update_memory,
)

def learn_handler(arguments):
    """
    Handler action for creating a new knowledge document in the 'knowledge' collection.
    """
    text = arguments.get("text")
    document_id = arguments.get("document_id")

    if text:
        create_memory("knowledge", text, id=document_id)
        return True
    else:
        return False


def search_knowledge_handler(arguments):
    """
    Handler action for searching knowledge documents based on a query text.
    """
    search_text = arguments.get("search_text")
    n_results = arguments.get("n_results", 5)

    search_results = search_memory(
        "knowledge", search_text=search_text, n_results=n_results
    )

    return search_results


def delete_knowledge_handler(arguments):
    """
    Handler action for deleting a knowledge document from the 'knowledge' collection based on its ID.
    """
    document_id = arguments.get("document_id")

    if document_id:
        # Delete the knowledge document from the 'knowledge' collection
        delete_memory("knowledge", document_id)
        return True
    else:
        return False


def update_knowledge_handler(arguments):
    """
    Handler action for updating a knowledge document in the 'knowledge' collection based on its ID.
    """
    document_id = arguments.get("document_id")
    new_text = arguments.get("new_text")

    if document_id and new_text:
        # Update the knowledge document in the 'knowledge' collection
        update_memory("knowledge", document_id, new_text)
        return True
    else:
        return False


def get_actions():
    """
    Returns a dictionary of actions related to knowledge.
    """
    return {
        "learn": {
            "function": {
                "name": "learn",
                "description": "Learn something new. Create a new knowledge document.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text content to add to memory.",
                        },
                        "document_id": {
                            "type": "string",
                            "description": "The ID of the knowledge document (optional).",
                        },
                    },
                    "required": ["text"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": learn_handler,
        },
        "search_knowledge": {
            "function": {
                "name": "search_knowledge",
                "description": "Search for knowledge documents based on a query text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_text": {
                            "type": "string",
                            "description": "The query text to search knowledge documents.",
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "The number of search results to retrieve. Defaults to 5.",
                        },
                    },
                    "required": ["search_text"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": search_knowledge_handler,
        },
        "delete_knowledge": {
            "function": {
                "name": "delete_knowledge",
                "description": "Delete a knowledge document based on its ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "The ID of the knowledge document to delete.",
                        }
                    },
                    "required": ["document_id"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": delete_knowledge_handler,
        },
        "update_knowledge": {
            "function": {
                "name": "update_knowledge",
                "description": "Update a knowledge document based on its ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "The ID of the knowledge document to update.",
                        },
                        "new_text": {
                            "type": "string",
                            "description": "The new text content of the knowledge document.",
                        },
                    },
                    "required": ["document_id", "new_text"],
                },
            },
            "suggest_next_actions": [],
            "ignore_next_actions": [],
            "handler": update_knowledge_handler,
        },
    }


if __name__ == "__main__":
    # Test learn_handler
    arguments = {"text": "This is a test document.", "document_id": "test_doc_id"}
    assert learn_handler(arguments) is True, "Test for learn_handler failed."

    # Test search_knowledge_handler
    arguments = {"search_text": "test", "n_results": 5}
    search_results = search_knowledge_handler(arguments)
    assert isinstance(search_results, str), "Test for search_knowledge_handler failed."
    assert len(search_results) > 0, "Test for search_knowledge_handler failed."

    # Test update_knowledge_handler
    arguments = {
        "document_id": "test_doc_id",
        "new_text": "This is an updated test document.",
    }
    assert (
        update_knowledge_handler(arguments) is True
    ), "Test for update_knowledge_handler failed."

    # Test delete_knowledge_handler
    arguments = {"document_id": "test_doc_id"}
    assert (
        delete_knowledge_handler(arguments) is True
    ), "Test for delete_knowledge_handler failed."

    # Test get_actions
    actions = get_actions()
    assert isinstance(actions, dict), "Test for get_actions failed."
    assert "learn" in actions, "Test for get_actions failed."
    assert "search_knowledge" in actions, "Test for get_actions failed."
    assert "delete_knowledge" in actions, "Test for get_actions failed."
    assert "update_knowledge" in actions, "Test for get_actions failed."
    assert "find_similar_knowledge" in actions, "Test for get_actions failed."

    print("All tests passed!")
