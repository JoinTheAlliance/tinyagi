from core.memory import (
    memory_client,
    get_formatted_collection_data,
)


def learn_handler(arguments):
    """
    Handler action for creating a new knowledge document in the 'knowledge' collection.
    """
    text = arguments.get("text")
    document_id = arguments.get("document_id")

    if text:
        # Create a new knowledge document
        collection = memory_client.get_or_create_collection("knowledge")
        collection.add(
            ids=[document_id] if document_id else None,
            documents=[text],
        )
        return True
    else:
        return False


def search_knowledge_handler(arguments):
    """
    Handler action for searching knowledge documents based on a query text.
    """
    query_text = arguments.get("query_text")
    n_results = arguments.get("n_results", 5)

    # Search for knowledge documents in the 'knowledge' collection based on the query text
    formatted_collection_data = get_formatted_collection_data(
        "knowledge", query_text=query_text, n_results=n_results
    )
    return formatted_collection_data


def delete_knowledge_handler(arguments):
    """
    Handler action for deleting a knowledge document from the 'knowledge' collection based on its ID.
    """
    document_id = arguments.get("document_id")

    if document_id:
        # Delete the knowledge document from the 'knowledge' collection
        collection = memory_client.get_or_create_collection("knowledge")
        collection.delete(ids=[document_id])
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
        collection = memory_client.get_or_create_collection("knowledge")
        collection.update(ids=[document_id], documents=[new_text])
        return True
    else:
        return False


def find_similar_knowledge_handler(arguments):
    """
    Handler action for finding similar knowledge documents and deleting them if they are too similar.
    """
    document_id = arguments.get("document_id")
    threshold = arguments.get("threshold", 0.9)

    if document_id:
        # Retrieve the specified knowledge document
        collection = memory_client.get_or_create_collection("knowledge")
        document_data = collection.get(ids=[document_id])

        if document_data and len(document_data["documents"]) > 0:
            # Calculate the distances with other knowledge documents
            documents = document_data["documents"]
            n_results = len(documents)
            if n_results < 2:
                return False

            distances = collection.query(
                query_texts=documents, n_results=n_results, include=["distances"]
            )["distances"][0]

            # Delete the knowledge documents that are too similar
            delete_indices = []
            indices = document_data.get("indices", [])
            for i, distance in enumerate(distances):
                if i != indices[0] and distance <= threshold:
                    delete_indices.append(i)

            if len(delete_indices) > 0:
                collection.delete(indices=delete_indices)

            return True

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
            "handler": learn_handler,
        },
        "search_knowledge": {
            "function": {
                "name": "search_knowledge",
                "description": "Search for knowledge documents based on a query text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {
                            "type": "string",
                            "description": "The query text to search knowledge documents.",
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "The number of search results to retrieve. Defaults to 5.",
                        },
                    },
                    "required": ["query_text"],
                },
            },
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
            "handler": update_knowledge_handler,
        },
        "find_similar_knowledge": {
            "function": {
                "name": "find_similar_knowledge",
                "description": "Find similar knowledge documents and delete them if they are too similar.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "The ID of the knowledge document to find similarities.",
                        },
                        "threshold": {
                            "type": "number",
                            "description": "The distance threshold. Documents with distances below this threshold will be deleted. Defaults to 0.9.",
                        },
                    },
                    "required": ["document_id"],
                },
            },
            "handler": find_similar_knowledge_handler,
        },
    }


if __name__ == "__main__":
    # Test learn_handler
    arguments = {"text": "This is a test document.", "document_id": "test_doc_id"}
    assert (
        learn_handler(arguments) is True
    ), "Test for learn_handler failed."

    # Test search_knowledge_handler
    arguments = {"query_text": "test", "n_results": 5}
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

    # Test find_similar_knowledge_handler
    arguments = {"document_id": "test_doc_id", "threshold": 0.9}
    assert (
        find_similar_knowledge_handler(arguments) is False
    ), "Test for find_similar_knowledge_handler failed."

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
