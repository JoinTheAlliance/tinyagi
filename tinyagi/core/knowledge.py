from agentmemory import (
    create_memory,
    delete_memory,
    search_memory,
)

from .events import get_epoch


def add_knowledge(content, metadata={}, max_similarity=.92):
    """
    Search for similar knowledge. If there is none, create it.
    """

    max_distance = 1.0 - max_similarity

    similar_knowledge = search_knowledge(
        content, max_distance=max_distance, n_results=1
    )

    metadata = {
            "epoch": get_epoch(),
        }

    if len(similar_knowledge) == 0:
        metadata["unique"] = True
        # Create a new knowledge item
        create_memory("knowledge", content, metadata=metadata)
        return

    metadata["related_to"] = similar_knowledge[0]["id"]
    metadata["related_document"] = similar_knowledge[0]["document"]
    create_memory("knowledge", content, metadata=metadata)


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


def search_knowledge(search_text, min_distance=None, max_distance=None, n_results=5):
    """
    Search the 'knowledge' collection by search text
    """
    return search_memory(
        "knowledge",
        min_distance=min_distance,
        max_distance=max_distance,
        search_text=search_text,
        n_results=n_results,
        filter_metadata={ "unique": True }
    )
