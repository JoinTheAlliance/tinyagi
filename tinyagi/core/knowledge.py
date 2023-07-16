from agentmemory import (
    create_memory,
    delete_memory,
    get_memories,
    search_memory,
)
from easycompletion import count_tokens, trim_prompt

from tinyagi.core.constants import (
    MAX_PROMPT_LIST_TOKENS,
    SIMILARY_THRESHOLD,
    MAX_PROMPT_TOKENS,
)

from agentevents import get_epoch


def add_knowledge(content, metadata={}, similarity=SIMILARY_THRESHOLD):
    """
    Searches for similar knowledge. If no similar knowledge exists, creates it.

    Parameters:
    - content (str): The content of the knowledge.
    - metadata (dict, optional): Additional metadata for the knowledge. Defaults to empty dictionary.
    - similarity (float, optional): The threshold for determining similarity. Defaults to SIMILARY_THRESHOLD.

    Returns: None
    """

    max_distance = 1.0 - similarity

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


def remove_knowledge(content, similarity_threshold=SIMILARY_THRESHOLD):
    """
    Finds a knowledge item that contains the content and removes it.

    Parameters:
    - content (str): The content to search for.
    - similarity_threshold (float, optional): The threshold for determining similarity. Defaults to SIMILARY_THRESHOLD.

    Returns: bool - True if the knowledge item is found and removed, False otherwise.
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
    """
    Deletes a knowledge item by its ID.

    Parameters:
    - id (str): The ID of the knowledge item to be deleted.

    Returns: None
    """
    delete_memory("knowledge", id)


def get_knowledge_from_epoch(epoch=get_epoch()):
    """
    Retrieves knowledge from a specific epoch.

    Parameters:
    - epoch (int, optional): The epoch to retrieve knowledge from. Defaults to the current epoch.

    Returns: list of knowledge documents from the specified epoch
    """
    memories = get_memories("knowledge", filter_metadata={"epoch": epoch})
    return memories


def formatted_search_knowledge(
    search_text, min_distance=None, max_distance=None, n_results=5
):
    """
    Searches for knowledge and formats the results.

    Parameters:
    - search_text (str): The text to search for.
    - min_distance (float, optional): The minimum distance for search results. Defaults to None.
    - max_distance (float, optional): The maximum distance for search results. Defaults to None.
    - n_results (int, optional): The number of results to return. Defaults to 5.

    Returns: str - A string containing the formatted results of the search.
    """
    header_text = "I know these relevant things:"
    knowledge = search_knowledge(
        search_text,
        min_distance=min_distance,
        max_distance=max_distance,
        n_results=n_results,
    )
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
    return "\n" + header_text + "\n" + formatted_knowledge + "\n"


def get_formatted_recent_knowledge():
    """
    Retrieves and formats recent knowledge.

    Parameters: None

    Returns: str - A string containing the formatted recent knowledge.
    """
    recent_knowledge = get_knowledge_from_epoch(get_epoch() - 1)

    # trim any individual knowledge, just in case
    for i in range(len(recent_knowledge)):
        document = recent_knowledge[i]["document"]
        if count_tokens(document) > MAX_PROMPT_LIST_TOKENS:
            recent_knowledge[i]["document"] = (
                trim_prompt(document, MAX_PROMPT_LIST_TOKENS - 5) + " ..."
            )

    formatted_knowledge = "\n".join([k["document"] for k in recent_knowledge])

    while count_tokens(formatted_knowledge) > MAX_PROMPT_TOKENS:
        if len(recent_knowledge) == 1:
            raise Exception(
                "Single knowledge length is greater than token limit, should not happen"
            )
        # remove the first event
        recent_knowledge = recent_knowledge[1:]
        formatted_knowledge = "\n".join([k["document"] for k in recent_knowledge])
    return formatted_knowledge


def search_knowledge(search_text, min_distance=None, max_distance=None, n_results=5):
    """
    Searches the 'knowledge' collection by search text.

    Parameters:
    - search_text (str): The text to search for.
    - min_distance (float, optional): The minimum distance for search results. Defaults to None.
    - max_distance (float, optional): The maximum distance for search results. Defaults to None.
    - n_results (int, optional): The number of results to return. Defaults to 5.

    Returns: list of knowledge documents that match the search criteria
    """
    return search_memory(
        "knowledge",
        min_distance=min_distance,
        max_distance=max_distance,
        search_text=search_text,
        n_results=n_results,
        filter_metadata={"unique": True},
    )
