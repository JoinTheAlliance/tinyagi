from datetime import datetime

from agentmemory import create_memory, delete_memory, search_memory, get_memories

from events import get_event_epoch


def create_knowledge(content):
    """
    Create event, then save it to the event log file and print it
    """
    timestamp = datetime.utcnow()
    metadata = {
        "timestamp": timestamp,
        "epoch": get_event_epoch(),
    }

    create_memory("knowledge", content, metadata=metadata)


def get_knowledge(n_results=10):
    """
    Get the most recent knowledge from the 'knowledge' collection.
    """
    return get_memories("knowledge", n_results=n_results)


def remove_knowledge(content, similarity_threshold=0.9):
    """
    Find goal that contains content, then remove it
    """
    knowledge = search_memory("knowledge", content)
    if len(knowledge) > 0:
        goal = knowledge[0]
        goal_similarity = 1.0 - goal["distance"]
        if goal_similarity > similarity_threshold:
            goal_id = goal["id"]
            delete_memory("knowledge", goal_id)
            return True
    return False


def delete_knowledge_by_id(id):
    delete_memory("knowledge", id)


def search_knowledge(search_text, n_results=10):
    """
    Search the 'knowledge' collection by search text
    """
    return search_memory("knowledge", search_text, n_results=n_results)
