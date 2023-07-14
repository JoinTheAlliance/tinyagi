from agentmemory import (
    create_memory,
    delete_memory,
    get_memories,
    search_memory,
)
from easycompletion import count_tokens, trim_prompt

from tinyagi.core.constants import MAX_PROMPT_LIST_TOKENS, SIMILARY_THRESHOLD, MAX_PROMPT_TOKENS

from .events import get_epoch


def add_knowledge(content, metadata={}, similarity=SIMILARY_THRESHOLD):
    """
    Search for similar knowledge. If there is none, create it.
    """

    max_distance = 1.0 - similarity

    similar_knowledge = search_knowledge(
        content, max_distance=max_distance, n_results=1
    )

    print("similar knowledge:")
    print(similar_knowledge)

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


def remove_knowledge(content, similarity_threshold=SIMILARY_THRESHOLD):
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
    

def get_knowledge_from_epoch(epoch=get_epoch()):
    """
    Get knowledge from a specific epoch
    """
    memories = get_memories("knowledge", filter_metadata={"epoch": epoch})
    return memories

def formatted_search_knowledge(search_text, min_distance=None, max_distance=None, n_results=5):
    knowledge = search_knowledge(search_text, min_distance=min_distance, max_distance=max_distance, n_results=n_results)
    # trim any individual knowledge, just in case
    for i in range(len(knowledge)):
        document = knowledge[i]["document"]
        if count_tokens(document) > MAX_PROMPT_LIST_TOKENS:
            knowledge[i]["document"] = (
                trim_prompt(document, MAX_PROMPT_LIST_TOKENS - 5) + " ..."
            )
    formatted_knowledge = "\n".join([k["document"] for k in knowledge])

    while count_tokens(formatted_knowledge) > MAX_PROMPT_TOKENS:
        if len(recent_knowledge) == 1:
            raise Exception(
                "Single knowledge length is greater than token limit, should not happen"
            )
        # remove the last event
        recent_knowledge = recent_knowledge[:-1]
        formatted_knowledge = "\n".join([k["document"] for k in recent_knowledge])

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
        filter_metadata={"unique": True},
    )
