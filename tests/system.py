from agentmemory import wipe_all_memories
from tinyagi import increment_epoch, get_epoch


def test_get_epoch():
    """
    Test to confirm get_epoch function returns a valid value (integer)
    """
    wipe_all_memories()
    epoch = get_epoch()
    assert epoch == 0, "Epoch should be 0"

    # Add 10 more epochs
    for i in range(10):
        increment_epoch()

    epoch = get_epoch()

    assert epoch == 10, "Epoch should be 10"


def test_increment_epoch():
    """
    Test to confirm increment_epoch function works correctly
    """
    wipe_all_memories()
    current_epoch = get_epoch()
    new_epoch = increment_epoch()
    assert new_epoch == current_epoch + 1, "New epoch is not incremented correctly"


def run_tests():
    test_get_epoch()
    test_increment_epoch()
    print("All tests passed!")


if __name__ == "__main__":
    run_tests()
