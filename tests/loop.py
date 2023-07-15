from tinyagi.core.loop import (
    compose_orient_prompt,
    compose_orient_function,
    step,
    start,
    stop,
)
import threading
import time

### Test for compose_prompt function ###


def test_compose_prompt():
    sample_observation = {
        "epoch": 1,
        "current_time": "12:00",
        "current_date": "2023-07-14",
        "events": [],
    }

    prompt = compose_orient_prompt(sample_observation)
    print("prompt: ", prompt)
    assert "{{epoch}}" not in prompt
    assert "{{current_time}}" not in prompt
    assert "{{current_date}}" not in prompt
    assert str(sample_observation["epoch"]) in prompt
    assert sample_observation["current_time"] in prompt
    assert sample_observation["current_date"] in prompt


### Test for compose_orient_function function ###


def test_compose_orient_function():
    func = compose_orient_function()
    assert func["name"] == "summarize_recent_events"
    assert "summary_as_assistant" in func["parameters"]["properties"]
    assert "summary_as_user" in func["parameters"]["properties"]
    assert "knowledge" in func["parameters"]["properties"]


### Test for start function ###


def test_start():
    thread, step_event = start(stepped=False)
    time.sleep(20)  # Let the thread run for longer before stopping
    assert isinstance(thread, threading.Thread)
    assert isinstance(step_event, threading.Event)
    assert thread.is_alive() == True
    stop()  # Stop the loop
    time.sleep(5)  # Give the thread time to stop
    thread.join(timeout=10)
    assert thread.is_alive() == False


def test_start_stepped():
    thread, step_event = start(stepped=True)
    assert isinstance(thread, threading.Thread)
    assert isinstance(step_event, threading.Event)
    assert thread.is_alive() == True
    for _ in range(10):
        step(step_event)
        time.sleep(2)  # Add delay between steps
    stop()  # Stop the loop
    time.sleep(5)  # Give the thread time to stop
    thread.join(timeout=10)
    assert thread.is_alive() == False


def run_tests():
    test_start()
    test_start_stepped()
    test_compose_prompt()
    test_compose_orient_function()
    print("All tests passed.")
