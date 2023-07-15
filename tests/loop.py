import time
import threading

from tinyagi.core.loop import (
    compose_decision_function,
    compose_decision_prompt,
    compose_orient_prompt,
    compose_orient_function,
    observe,
    orient,
    decide,
    act,
    start,
    stop,
    step,
)


from tinyagi.core.actions import register_actions, unregister_actions

def test_observe():
    observation = observe()
    assert isinstance(observation, dict)
    assert "epoch" in observation
    assert "last_epoch" in observation
    assert "current_time" in observation
    assert "current_date" in observation
    assert "platform" in observation
    assert "cwd" in observation
    assert "events" in observation
    assert "recent_knowledge" in observation


def test_orient():
    observation = observe()
    orient_observation = orient(observation)
    assert isinstance(orient_observation, dict)
    assert "summary" in orient_observation
    assert "relevant_knowledge" in orient_observation
    assert "available_actions" in orient_observation


def test_compose_orient_function():
    function = compose_orient_function()
    assert isinstance(function, dict)
    assert "name" in function
    assert "description" in function
    assert "properties" in function
    assert "required_properties" in function


def test_compose_orient_prompt():
    observation = observe()
    prompt = compose_orient_prompt(observation)
    assert isinstance(prompt, str)


def test_decide():
    observation = observe()
    orient_observation = orient(observation)
    decision_observation = decide(orient_observation)
    assert isinstance(decision_observation, dict)
    assert "reasoning" in decision_observation
    assert "action_name" in decision_observation


def test_compose_decision_function():
    function = compose_decision_function()
    assert isinstance(function, dict)
    assert "name" in function
    assert "description" in function
    assert "properties" in function["parameters"]
    assert "required" in function["parameters"]


def test_compose_decision_prompt():
    observation = observe()
    orient_observation = orient(observation)
    prompt = compose_decision_prompt(orient_observation)
    assert isinstance(prompt, str)


def test_act():
    observation = observe()
    orient_observation = orient(observation)
    decision_observation = decide(orient_observation)
    act_observation = act(decision_observation)
    assert isinstance(act_observation, dict)


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
    time.sleep(5)  # Let the thread run for 5 seconds
    assert isinstance(thread, threading.Thread)
    assert isinstance(step_event, threading.Event)
    assert thread.is_alive() == True
    stop()  # Stop the loop
    thread.join(timeout=10)
    time.sleep(20)  # Give the thread time to stop
    assert thread.is_alive() == False


def test_start_stepped():
    thread, step_event = start(stepped=True)
    time.sleep(5)  # Let the thread run for 5 seconds
    assert isinstance(thread, threading.Thread)
    assert isinstance(step_event, threading.Event)
    assert thread.is_alive() == True
    for _ in range(5):
        step(step_event)
        time.sleep(2)
    stop()  # Stop the loop
    thread.join(timeout=10)
    time.sleep(20)  # Give the thread time to stop
    assert thread.is_alive() == False


def run_tests():
    # Setup
    unregister_actions()
    register_actions()

    # COMPOSE PROMPT TESTS
    test_compose_orient_prompt()
    test_compose_decision_prompt()

    # COMPOSE FUNCTION TESTS
    test_compose_decision_function()
    test_compose_orient_function()

    # OODA TESTS
    test_observe()
    test_orient()
    test_decide()
    test_act()

    # LOOP TESTS
    test_start_stepped()
    test_start()
    test_compose_prompt()
    test_compose_orient_function()

    # Teardown
    unregister_actions()
