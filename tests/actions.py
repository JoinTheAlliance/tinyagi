from tinyagi.core.actions import (
    add_to_action_history,
    get_action_history,
    get_last_action,
    get_available_actions,
    search_actions,
    use_action,
    add_action,
    get_action,
    remove_action,
    register_actions,
    get_actions,
)
from agentmemory import wipe_all_memories
from tinyagi.core.events import increment_epoch


def setup_test_action():
    return {
        "function": {
            "name": "test",
            "description": "A test action",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "Some test input",
                    },
                },
            },
            "required": ["input"],
        },
        "suggestion_after_actions": [],
        "never_after_actions": [],
        "handler": lambda args: args["input"],
    }


def cleanup():
    wipe_all_memories()


def test_add_to_action_history():
    cleanup()  # Ensure clean state before test
    add_to_action_history("test 0", {"input": "test 0"})
    history = get_action_history(n_results=1)
    assert len(history) == 1 and history[0]["document"] == "test 0"

    # add 30 history items
    for i in range(30):
        increment_epoch()
        add_to_action_history("test " + str(i), {"input": "test " + str(i)})
    history = get_action_history(n_results=20)
    assert len(history) == 20  # Should only return 20 results
    assert history[0]["document"] == "test 29"  # Should be the last item
    assert history[-1]["document"] == "test 10"  # Should be the first item
    cleanup()  # Cleanup after the test


def test_get_last_action():
    cleanup()  # Ensure clean state before test
    assert get_last_action() is None  # Should be None when no history
    add_to_action_history("test first", {"input": "test first"})
    add_to_action_history("test last", {"input": "test last"})
    assert get_last_action() == "test last"
    cleanup()  # Cleanup after the test


def test_add_and_use_action():
    cleanup()  # Ensure clean state before test
    test_action = setup_test_action()
    add_action("test", test_action)
    assert get_action("test") is not None  # Action should now exist
    result = use_action("test", {"input": "test"})
    assert result["success"] and result["response"] == "test"
    cleanup()  # Cleanup after the test


def test_remove_action():
    cleanup()  # Ensure clean state before test
    test_action = setup_test_action()
    add_action("test", test_action)
    remove_action("test")
    assert get_action("test") is None  # Action should not exist after removal
    cleanup()  # Cleanup after the test


def test_register_actions():
    cleanup()  # Ensure clean state before test
    register_actions()
    assert len(get_actions()) > 0  # At least one action should be registered
    cleanup()  # Cleanup after the test


def test_search_actions():
    cleanup()  # Ensure clean state before test
    test_action = setup_test_action()
    add_action("test", test_action)
    search_results = search_actions("test")
    assert len(search_results) > 0  # At least one action should be found
    cleanup()  # Cleanup after the test


def test_get_available_actions():
    cleanup()  # Ensure clean state before test
    test_action = setup_test_action()
    add_action("test", test_action)
    add_to_action_history(
        "test", {"input": "test"}
    )  # Add an action to history so there is a "last action"
    available_actions = get_available_actions("test")
    assert len(available_actions) > 0  # At least one action should be available
    cleanup()  # Cleanup after the test


def run_tests():
    test_add_to_action_history()
    test_get_last_action()
    test_add_and_use_action()
    test_remove_action()
    test_register_actions()
    test_search_actions()
    test_get_available_actions()

    print("All tests passed!")


if __name__ == "__main__":
    run_tests()
