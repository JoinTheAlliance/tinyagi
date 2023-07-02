from core.memory import create_event, memory_client, get_formatted_collection_data
import uuid

def create_event_handler(arguments):
    """
    Handler action for creating a new event in the 'events' collection.
    """
    text = arguments.get("text")
    event_creator = arguments.get("event_creator", "assistant")
    event_type = arguments.get("event_type", "conversation")
    event_id = arguments.get("event_id", str(uuid.uuid4()))  # generate a new UUID if event_id is not provided
    
    # Add the event to the 'events' collection
    collection = memory_client.get_or_create_collection("events")
    collection.add(
        ids=[event_id],
        documents=[text],
        metadatas=[{
            "type": event_type,
            "event_creator": event_creator
        }]
    )
    create_event("I created a new event!", "assistant", "action_call")
    return True

def list_events_handler(arguments):
    """
    Handler action for listing the recent events from the 'events' collection.
    """
    limit = arguments.get("limit", 10)
    
    # Retrieve the recent events from the 'events' collection
    collection = memory_client.get_or_create_collection("events")
    events = collection.peek(limit=limit)
    
    # Format the events as a string
    formatted_events = "\n".join(
        f'{msg_meta["event_creator"]}: {msg_doc}'
        for msg_meta, msg_doc in zip(events["metadatas"], events["documents"])
    )
    create_event("I got a list of recent events:\n" + formatted_events, "assistant", "action_call")
    return formatted_events

def search_events_handler(arguments):
    """
    Handler action for searching events in the 'events' collection.
    """
    query_text = arguments.get("query_text")
    n_results = arguments.get("n_results", 5)
    
    # Search for events in the 'events' collection based on the query text
    formatted_collection_data = get_formatted_collection_data(
        "events",
        query_text=query_text,
        n_results=n_results
    )

    create_event("I searched for events with the query text '" + query_text + "' and got the following results:\n" + formatted_collection_data, "assistant", "action_call")
    return formatted_collection_data

def delete_event_handler(arguments):
    """
    Handler action for deleting an event from the 'events' collection based on its ID.
    """
    event_id = arguments.get("event_id")
    
    if event_id:
        # Delete the event from the 'events' collection
        collection = memory_client.get_or_create_collection("events")
        try:
            collection.delete(ids=[event_id])
            print("I deleted the event with ID ", str(event_id))
        except:
            print("I couldn't delete the event, the ID wasn't in the collection")
            return False
        return True
    else:
        print("I called the delete event action but didn't provide an event ID")
        return False

def update_event_handler(arguments):
    """
    Handler action for updating an event in the 'events' collection based on its ID.
    """
    event_id = arguments.get("event_id")
    new_text = arguments.get("new_text")
    
    if event_id and new_text:
        # Get the event in the 'events' collection
        collection = memory_client.get_or_create_collection("events")
        
        # Check if the event exists before updating
        event = collection.get(ids=[event_id])
        
        # If the event does not exist, return False
        if not event["documents"]:
            return False
        
        # If the event exists, update it
        collection.update(ids=[event_id], documents=[new_text])
        print("I updated the event for ID " + str(event_id))
        return True
    else:
        return False


def get_actions():
    """
    Returns a dictionary of actions associated with event-related operations.
    """
    return {
        "create_event": {
            "function": {
                "name": "create_event",
                "description": "Create a new event.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text content of the event."
                        },
                        "event_creator": {
                            "type": "string",
                            "description": "The creator of the event. Defaults to 'assistant'."
                        },
                        "event_type": {
                            "type": "string",
                            "description": "The type of the event. Defaults to 'conversation'."
                        },
                        "event_id": {
                            "type": "string",
                            "description": "The ID of the event. If not provided, a new ID is generated."
                        }
                    },
                    "required": ["text"]
                }
            },
            "handler": create_event_handler
        },
        "list_events": {
            "function": {
                "name": "list_events",
                "description": "List recent events.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "The maximum number of events to retrieve. Defaults to 10."
                        },
                        "max_tokens": {
                            "type": "integer",
                            "description": "The maximum number of tokens in the event list. Defaults to 1200."
                        }
                    }
                }
            },
            "handler": list_events_handler
        },
        "search_events": {
            "function": {
                "name": "search_events",
                "description": "Search events based on a query text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {
                            "type": "string",
                            "description": "The query text to search events."
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "The number of search results to retrieve. Defaults to 5."
                        }
                    },
                    "required": ["query_text"]
                }
            },
            "handler": search_events_handler
        },
        "delete_event": {
            "function": {
                "name": "delete_event",
                "description": "Delete an event based on its ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "The ID of the event to delete."
                        }
                    },
                    "required": ["event_id"]
                }
            },
            "handler": delete_event_handler
        },
        "update_event": {
            "function": {
                "name": "update_event",
                "description": "Update an event based on its ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "The ID of the event to update."
                        },
                        "new_text": {
                            "type": "string",
                            "description": "The new text content of the event."
                        }
                    },
                    "required": ["event_id", "new_text"]
                }
            },
            "handler": update_event_handler
        }
    }

if __name__ == "__main__":


    def test_create_event_handler():
        arguments = {
            "text": "Test event",
            "event_creator": "user123",
            "event_type": "task",
            "event_id": "123456789"
        }
        result = create_event_handler(arguments)
        assert result == True

    def test_list_events_handler():
        arguments = {
            "limit": 5,
            "max_tokens": 2000
        }
        result = list_events_handler(arguments)
        assert isinstance(result, str)

    def test_search_events_handler():
        arguments = {
            "query_text": "test"
        }
        result = search_events_handler(arguments)
        assert isinstance(result, str)

    def test_delete_event_handler():
        arguments = {
            "event_id": "123456789"
        }
        result = delete_event_handler(arguments)
        assert result == True

    def test_update_event_handler():
        # Create an event first
        create_arguments = {
            "text": "Test event",
            "event_creator": "user123",
            "event_type": "task",
            "event_id": "123"
        }
        create_result = create_event_handler(create_arguments)
        assert create_result == True

        # Now, update the event
        update_arguments = {
            "event_id": "123",
            "new_text": "Updated event"
        }
        update_result = update_event_handler(update_arguments)
        assert update_result == True

    # Run the tests
    test_create_event_handler()
    test_list_events_handler()
    test_search_events_handler()
    test_delete_event_handler()
    test_update_event_handler()
