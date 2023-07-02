import uuid

from core.memory import create_event, memory_client

def add_goal_handler(arguments):
    """
    Handler function for adding a new goal to the 'goals' collection.
    """
    goal = arguments.get("goal")
    print("**** GOAL")
    print(arguments)
    print(goal)
    if goal:
        goal_id = str(uuid.uuid4())
        collection = memory_client.get_or_create_collection("goals")
        collection.add(
            ids=[goal_id],  # Use the UUID as the ID
            documents=[goal],
            metadatas=[{"type": "goal", "id": goal_id}]  # Store the UUID in metadata
        )
        print(f"Added goal with ID {goal_id}: {goal}")  # Debug print
        create_event(f"Added goal: {goal}", "function")
        return True

def remove_goal_handler(arguments):
    """
    Handler function for removing an existing goal from the 'goals' collection.
    """
    goal = arguments.get("goal")
    print("**** GOAL")
    print(arguments)
    if goal:
        collection = memory_client.get_or_create_collection("goals")
        goal_data = collection.get(where_document={"$contains": goal}, include=["metadatas"])
        if goal_data["metadatas"]:
            goal_id = goal_data["metadatas"][0].get("id")
            if goal_id:
                collection.delete(ids=[goal_id])
                create_event(f"Removed goal: {goal}", "function")
                return True
        create_event(f"Goal not found: {goal}", "function")
        return False
    else:
        create_event("Failed to remove goal. Missing 'goal' argument.", "function")
        return False

def view_goals_handler(arguments):
    """
    Handler function for retrieving all current goals from the 'goals' collection.
    """
    collection = memory_client.get_or_create_collection("goals")
    goals = collection.get(include=["metadatas", "documents"])
    goal_list = [doc for doc in goals["documents"]]
    goal_list = "\n".join(goal_list)
    if goal_list:
        create_event("I have these goals:\n" + goal_list, "function")
    return goal_list

def get_functions():
    """
    Returns a dictionary of functions associated with the goal-related operations.
    """
    return {
        "add_goal": {
            "payload": {
                "name": "add_goal",
                "description": "Add a new goal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "The goal to add."
                        }
                    },
                    "required": ["goal"]
                }
            },
            "handler": add_goal_handler
        },
        "remove_goal": {
            "payload": {
                "name": "remove_goal",
                "description": "Remove an existing goal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "The goal to remove."
                        }
                    },
                    "required": ["goal"]
                }
            },
            "handler": remove_goal_handler
        },
        "view_goals": {
            "payload": {
                "name": "view_goals",
                "description": "View all current goals.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [""]
                }
            },
            "handler": view_goals_handler
        }
    }

# Tests
if __name__ == "__main__":
    # Test add_goal_handler
    arguments = {"goal": "Learn Python"}
    assert add_goal_handler(arguments) is True

    # Test remove_goal_handler
    arguments = {"goal": "Learn Python"}
    assert remove_goal_handler(arguments) is True

    # Test view_goals_handler
    assert isinstance(view_goals_handler({}), list)

    # Test get_functions
    functions = get_functions()
    assert isinstance(functions, dict)
    assert "add_goal" in functions
    assert "remove_goal" in functions
    assert "view_goals" in functions

    print("All tests passed!")
