from easycompletion import (
    count_tokens,
    trim_prompt,
)

from agentmemory import (
    create_unique_memory,
    delete_similar_memories,
    get_memories,
    search_memory,
)

from tinyagi.constants import get_current_epoch

MAX_PROMPT_LIST_TOKENS = 1536  # 2048 - 512
MAX_PROMPT_TOKENS = 3072  # 4096 - 1024
DEFAULT_SIMILARY_THRESHOLD = 0.92  # used for detecting if things are the similar


def build_relevant_knowledge(context):
    search_text = context.get("summary", None)
    if search_text is None:
        return context
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
    knowledge = search_memory(
        "knowledge",
        search_text=search_text,
        n_results=8,
        filter_metadata={"unique": "True"},
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
        if len(knowledge) == 1:
            raise Exception(
                "Single knowledge length is greater than token limit, should not happen"
            )
        # remove the last event
        knowledge = knowledge[:-1]
        formatted_knowledge = "\n".join([k["document"] for k in knowledge])

    if formatted_knowledge == "":
        context["relevant_knowledge"] = ""
    else:
        context["relevant_knowledge"] = header_text + "\n" + formatted_knowledge + "\n"
    return context


def build_recent_knowledge(context):
    """
    Retrieves and formats recent knowledge.

    Parameters: None

    Returns: str - A string containing the formatted recent knowledge.
    """
    recent_knowledge = get_memories(
        "knowledge", filter_metadata={"epoch": get_current_epoch() - 1}
    )

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
    context["recent_knowledge"] = formatted_knowledge
    return context


def add_knowledge(content, metadata={}, similarity=DEFAULT_SIMILARY_THRESHOLD):
    """
    Searches for similar knowledge. If no similar knowledge exists, creates it.

    Parameters:
    - content (str): The content of the knowledge.
    - metadata (dict, optional): Additional metadata for the knowledge.
        Defaults to empty dictionary.
    - similarity (float, optional): The threshold for determining similarity.
        Defaults to DEFAULT_SIMILARY_THRESHOLD.

    Returns: None
    """
    create_unique_memory("knowledge", content, metadata=metadata, similarity=similarity)


def remove_knowledge(content, similarity_threshold=DEFAULT_SIMILARY_THRESHOLD):
    """
    Finds a knowledge item that contains the content and removes it.

    Parameters:
    - content (str): The content to search for.
    - similarity_threshold (float, optional): The threshold for determining similarity. Defaults to DEFAULT_SIMILARY_THRESHOLD.

    Returns: bool - True if the knowledge item is found and removed, False otherwise.
    """

    return delete_similar_memories("knowledge", content, similarity_threshold)


def get_context_builders():
    """
    Returns a list of functions that build context dictionaries

    Returns:
        context_builders: a list of functions that build context dictionaries
    """
    return [build_recent_knowledge, build_relevant_knowledge]
