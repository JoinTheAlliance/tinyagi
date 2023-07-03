from core.memory import memory_client, get_formatted_collection_data


def create_personality_handler(arguments):
    """
    Handler action for creating a new personality document.
    """
    text = arguments.get("text")
    document_id = arguments.get("document_id")

    if text:
        # Create a new personality document in the 'personality' collection
        collection = memory_client.get_or_create_collection("personality")
        collection.add(ids=[document_id], documents=[text])
        return True
    else:
        return False


def search_personality_handler(arguments):
    """
    Handler action for searching personality documents based on a query text.
    """
    query_text = arguments.get("query_text")
    n_results = arguments.get("n_results", 5)

    # Search for personality documents in the 'personality' collection
    collection_data = get_formatted_collection_data(
        "personality", query_text, limit=n_results, max_tokens=1200, deduplicate=False
    )

    return collection_data


def delete_personality_handler(arguments):
    """
    Handler action for deleting a personality document based on its ID.
    """
    document_id = arguments.get("document_id")

    if document_id:
        # Delete the specified personality document from the 'personality' collection
        collection = memory_client.get_or_create_collection("personality")
        collection.delete(ids=[document_id])
        return True
    else:
        return False


def update_personality_handler(arguments):
    """
    Handler action for updating a personality document based on its ID.
    """
    document_id = arguments.get("document_id")
    new_text = arguments.get("new_text")

    if document_id and new_text:
        # Update the personality document in the 'personality' collection
        collection = memory_client.get_or_create_collection("personality")
        collection.update(ids=[document_id], documents=[new_text])
        return True
    else:
        return False


def find_similar_personality_handler(arguments):
    """
    Handler action for finding similar personality documents and deleting them if they are too similar.
    """
    document_id = arguments.get("document_id")
    threshold = arguments.get("threshold", 0.9)

    if document_id:
        # Retrieve the specified personality document
        collection = memory_client.get_or_create_collection("personality")
        document_data = collection.get(ids=[document_id])

        if document_data and len(document_data["documents"]) > 0:
            # Calculate the similarity scores with other personality documents
            documents = document_data["documents"]
            similarity_scores = collection.similarity(
                ids=document_id, documents=documents
            )

            # Delete the personality documents that are too similar
            delete_indices = []
            for i, score in enumerate(similarity_scores[0]):
                if i != document_data["indices"][0] and score >= threshold:
                    delete_indices.append(i)

            if len(delete_indices) > 0:
                collection.delete(indices=delete_indices)

            return True

    return False


def get_actions():
    """
    Returns a dictionary of actions related to personality documents.
    """
    return {
        "create_personality": {
            "function": {
                "name": "create_personality",
                "description": "Create a new personality document.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text content of the personality document.",
                        },
                        "document_id": {
                            "type": "string",
                            "description": "The ID of the personality document. If not provided, a new ID will be generated.",
                        },
                    },
                    "required": ["text"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": create_personality_handler,
        },
        "search_personality": {
            "function": {
                "name": "search_personality",
                "description": "Search personality documents based on a query text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {
                            "type": "string",
                            "description": "The query text to search for.",
                        },
                        "n_results": {
                            "type": "number",
                            "description": "The maximum number of search results to retrieve. Defaults to 5.",
                        },
                    },
                    "required": ["query_text"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": search_personality_handler,
        },
        "delete_personality": {
            "function": {
                "name": "delete_personality",
                "description": "Delete a personality document based on its ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "The ID of the personality document to delete.",
                        }
                    },
                    "required": ["document_id"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": delete_personality_handler,
        },
        "update_personality": {
            "function": {
                "name": "update_personality",
                "description": "Update a personality document based on its ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "The ID of the personality document to update.",
                        },
                        "new_text": {
                            "type": "string",
                            "description": "The new text content of the personality document.",
                        },
                    },
                    "required": ["document_id", "new_text"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": update_personality_handler,
        },
        "find_similar_personality": {
            "function": {
                "name": "find_similar_personality",
                "description": "Find similar personality documents and delete them if they are too similar.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "The ID of the personality document to find similarities.",
                        },
                        "threshold": {
                            "type": "number",
                            "description": "The similarity threshold. Documents with similarity scores above this threshold will be deleted. Defaults to 0.9.",
                        },
                    },
                    "required": ["document_id"],
                },
            },
            "chain_from": [],
            "dont_chain_from": [],
            "handler": find_similar_personality_handler,
        },
    }


if __name__ == "__main__":

    def test_create_personality():
        arguments = {"text": "New personality document"}
        assert create_personality_handler(arguments) == True

    def test_search_personality():
        arguments = {"query_text": "search"}
        result = search_personality_handler(arguments)
        assert isinstance(result, dict)

    def test_delete_personality():
        arguments = {"document_id": "document1"}
        assert delete_personality_handler(arguments) == True

    def test_update_personality():
        arguments = {"document_id": "document1", "new_text": "Updated text"}
        assert update_personality_handler(arguments) == True

    def test_find_similar_personality():
        arguments = {"document_id": "document1", "threshold": 0.8}
        assert find_similar_personality_handler(arguments) == False

    def test_get_actions():
        actions = get_actions()
        assert isinstance(actions, dict)
        assert "create_personality" in actions
        assert "list_personality" in actions
        assert "search_personality" in actions
        assert "delete_personality" in actions
        assert "update_personality" in actions
        assert "find_similar_personality" in actions

    print("All tests passed!")
