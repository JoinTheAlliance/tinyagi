from tinyagi import (
    add_knowledge,
    remove_knowledge,
    delete_knowledge_by_id,
    search_knowledge,
)
from agentmemory import count_memories, get_memories, wipe_all_memories


def test_add_knowledge():
    wipe_all_memories()  # Ensure clean state before test
    add_knowledge("test")
    count = count_memories("knowledge")
    assert count == 1, "Knowledge should be added"

    add_knowledge("test")
    memories = get_memories("knowledge")
    unique_memories = []
    not_unique_memories = []
    for memory in memories:
        if memory["metadata"].get("unique", False):
            unique_memories.append(memory)
        else:
            not_unique_memories.append(memory)

    assert len(unique_memories) == 1, "Each memory should be unique"
    assert len(not_unique_memories) == 1, "Not-unique memories should be marked as such"
    knowledge = search_knowledge("test")
    assert len(knowledge) > 0 and knowledge[0]["document"] == "test"
    delete_knowledge_by_id(not_unique_memories[0]["id"])

    example_text = "Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie Land."
    add_knowledge(example_text)
    count = count_memories("knowledge")
    assert count == 2, "Knowledge should be added"

    knowledge = search_knowledge(example_text, max_distance=0.05)
    assert (
        len(knowledge) > 0 and knowledge[0]["document"] == example_text
    ), "Knowledge should be example_text"

    knowledge = search_knowledge(example_text, max_distance=1.0, min_distance=0.1)
    assert (
        len(knowledge) == 1 and knowledge[0]["document"] == "test"
    ), "Knowledge should be test"


def test_remove_knowledge():
    wipe_all_memories()  # Ensure clean state before test
    add_knowledge("test")
    removed = remove_knowledge("test")
    knowledge = search_knowledge("test")
    assert removed and len(knowledge) == 0


def test_delete_knowledge_by_id():
    wipe_all_memories()  # Ensure clean state before test
    add_knowledge("test")
    knowledge = search_knowledge("test")
    id = knowledge[0]["id"]
    delete_knowledge_by_id(id)
    knowledge = search_knowledge("test")
    assert len(knowledge) == 0


def test_search_knowledge():
    wipe_all_memories()  # Ensure clean state before test
    add_knowledge("test")
    knowledge = search_knowledge("test")
    assert len(knowledge) > 0 and knowledge[0]["document"] == "test"


def run_tests():
    test_add_knowledge()
    test_remove_knowledge()
    test_search_knowledge()
    test_delete_knowledge_by_id()
    print("All tests passed!")


if __name__ == "__main__":
    run_tests()
