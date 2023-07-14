from agentmemory import count_memories, wipe_all_memories
from tinyagi import create_event, get_events, search_events


def test_create_event():
    """
    Test to confirm create_event function works correctly
    """
    wipe_all_memories()
    previous_count = count_memories("events")
    create_event("Test event")
    current_count = count_memories("events")
    assert current_count == previous_count + 1, "Event creation did not increase count"


def test_get_events():
    """
    Test to confirm get_events function works correctly
    """
    wipe_all_memories()
    # create 6 events
    for i in range(6):
        create_event("Test event" + str(i))
    events = get_events(n_results=5)
    assert len(events) <= 5, "get_events returned more results than requested"


def test_search_events():
    """
    Test to confirm search_events function works correctly
    """
    # This test assumes that you have at least one event with "Test event" in its content
    wipe_all_memories()
    for i in range(6):
        create_event("Test event" + str(i))
    search_results = search_events("Test event", n_results=5)
    assert len(search_results) > 0, "search_events did not find any results"


def run_tests():
    test_create_event()
    test_get_events()
    test_search_events()
    print("All tests passed!")


if __name__ == "__main__":
    run_tests()
