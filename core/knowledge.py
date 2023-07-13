from agentmemory import (
    create_memory,
    delete_memory,
    search_memory,
    get_memories,
    update_memory,
)

from core.events import get_event_epoch


def add_new_knowledge(content, metadata={}, min_distance=0.05):
    """
    Search for similar knowledge. If there is none, create it.
    """
    similar_knowledge = search_knowledge(
        content, min_distance=min_distance, n_results=1
    )
    if len(similar_knowledge) == 0:
        create_knowledge(content, metadata=metadata)
        return

    # iterate through similar knowledge and increment the added_count
    for knowledge in similar_knowledge:
        knowledge["metadata"]["added_count"] += 1
        update_memory("knowledge", knowledge["id"], metadata=knowledge)


def create_knowledge(content, metadata={}):
    """
    Create event, then save it to the event log file and print it
    """
    metadata["epoch"] = (get_event_epoch())
    metadata["added_count"] = 1

    create_memory("knowledge", content, metadata=metadata)


def get_knowledge(n_results=None):
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


def search_knowledge(search_text, min_distance=None, max_distance=None, n_results=None):
    """
    Search the 'knowledge' collection by search text
    """
    return search_memory(
        "knowledge",
        min_distance=min_distance,
        max_distance=max_distance,
        search_text=search_text,
        n_results=n_results,
    )
