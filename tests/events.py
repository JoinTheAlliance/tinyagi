from tinyagi import increment_event_epoch, get_event_epoch

def run_tests():

    ### EPOCHS ###

    increment_event_epoch()

    epoch = get_event_epoch()

    assert epoch == 1, "Epoch should be 1"

    # Add 9 more epochs
    for i in range(9):
        increment_event_epoch()

    epoch = get_event_epoch()

    assert epoch == 10, "Epoch should be 10"

    print("All event tests complete")
    return True