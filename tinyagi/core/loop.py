# core/loop.py
# Handles the main execution loop, which repeats at a fixed interval

import os
import sys
import threading
from datetime import datetime

from pynput import keyboard

from easycompletion import compose_prompt, compose_function
from .system import (
    increment_epoch,
    get_epoch,
    write_dict_to_log,
    debuggable_function_call,
)
from .actions import (
    compose_action_function,
    compose_action_prompt,
    get_action,
    get_formatted_available_actions,
    use_action,
)
from .events import create_event, get_formatted_events
from .knowledge import (
    add_knowledge,
    formatted_search_knowledge,
    get_formatted_recent_knowledge,
)


### INPUT HANDLING ###


def on_press(key):
    """
    Function to handle keyboard inputs

    Args:
        key: the key which was pressed.

    This function does not return any value.
    """
    if key == keyboard.Key.space:
        step(event)


### MAIN LOOP ###

event = threading.Event()
stop_event = threading.Event()
step_event = threading.Event()
started_event = threading.Event()
listener = None


def stop():
    """
    Function to handle stopping of the loop

    This function does not take any arguments and does not return any value.
    """
    global listener
    print("Stop event set")
    stop_event.set()
    if listener is not None and listener.running:
        listener.stop()


def step(event):
    """
    Function to perform a single step in the loop

    Args:
        event: an instance of threading.Event

    This function does not return any value.
    """
    event.set()


def reset_globals():
    """
    Function to reset the global events

    This function does not take any arguments and does not return any value.
    """
    global event, stop_event, step_event, started_event
    stop_event = threading.Event()
    step_event = threading.Event()
    started_event = threading.Event()
    event = threading.Event()


def start(stepped=False):
    """
    Function to start the main loop

    Args:
        stepped: a boolean value that determines whether the loop should run in stepped mode or not. Defaults to False.

    Returns:
        thread, step_event: an instance of threading.Thread that's running the main loop and the event that's used to control stepping.
    """
    global listener
    reset_globals()
    thread = threading.Thread(target=loop, args=(stepped, stop_event, step_event))
    thread.start()
    if stepped:
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
    started_event.wait()  # Wait here until loop is started
    return thread, step_event


def loop(stepped, stop_event, step_event):
    """
    The main loop of the application, running the observe, orient, decide, act cycle until stop event is set

    Args:
        stepped: a boolean value that determines whether the loop should run in stepped mode or not
        stop_event: an instance of threading.Event that's used to control stopping of the loop
        step_event: an instance of threading.Event that's used to control stepping

    This function does not return any value.
    """
    global listener
    steps = [observe, orient, decide, act]
    observation = None
    started_event.set()  # Indicate that the loop has started
    while not stop_event.is_set():
        for step in steps:
            observation = step(observation)
            if stepped:
                while not step_event.wait(
                    timeout=1
                ):  # Wait here until step_event is set
                    if stop_event.is_set():  # Check if stop event has been set
                        break  # Break out of for loop
                if stop_event.is_set():  # Check if stop event has been set
                    break  # Break out of for loop
                step_event.clear()  # Clear the step_event
        if stop_event.is_set():  # Check if stop event has been set
            break  # Break out of while loop


### OBSERVE FUNCTIONS ###


def observe(last_observation=None):
    """
    Function to observe the environment and return an observation

    Args:
        last_observation: the last observation made by the loop. Defaults to None.

    Returns:
        observation: a dictionary containing the current observation
    """
    if last_observation is not None:
        write_dict_to_log(last_observation, "observation_end")

    epoch = increment_epoch()

    if epoch == 1:
        create_event("I have just woken up.", type="system", subtype="intialized")

    observation = {
        "epoch": get_epoch(),
        "last_epoch": str(get_epoch() - 1),
        "current_time": datetime.now().strftime("%H:%M"),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "platform": sys.platform,
        "cwd": os.getcwd(),
        "events": get_formatted_events(),
        "recent_knowledge": get_formatted_recent_knowledge(),
    }

    write_dict_to_log(observation, "observation_start")

    return observation


### ORIENT FUNCTIONS ###


def compose_orient_prompt(observation):
    """
    This function formats the orientation prompt by inserting the observation data into a pre-defined template.

    Args:
        observation (dict): The dictionary containing data about the current state of the system, such as current epoch, time, date, recent knowledge, and events.

    Returns:
        str: The fully formed orientation prompt with the data filled in from the observation.
    """
    return compose_prompt(
        """Current Epoch: {{epoch}}
The current time is {{current_time}} on {{current_date}}.
{{recent_knowledge}}
{{events}}
# Assistant Task
- Summarize what happened in Epoch {{last_epoch}} and reason about what I should do next to move forward.
- First, summarize as yourself (the assistant). Include any relevant information for me, the user, for the next step.
- Next summarize as if you were me, the user, in the first person from my perspective. Use "I" instead of "You".
- Lastly, include any new knowledge that I learned this epoch as an array of knowledge items.
- Your summary should include what I learned, what you think I should do next and why. You should argue for why you think this is the best next step.
- I am worried about getting stuck in a loop or make new progress. Your reasoning should be novel and interesting and helpful me to make progress towards my goals.
- Each knowledge array item should be a factual statement that I learned, and should include the source, the content and the relationship.
- For the "content" of each knowledge item, please be extremely detailed. Include as much information as possible, including who or where you learned it from, what it means, how it relates to my goals, etc.
- ONLY extract knowledge from the last epoch, which is #{{last_epoch}}. Do not extract knowledge from previous epochs.
- If there is no new knowledge, respond with an empty array [].
""",
        observation,
    )


def compose_orient_function():
    """
    This function defines the structure and requirements of the 'orient' function to be called in the 'orient' stage of the OODA loop.

    Returns:
        dict: A dictionary containing the details of the 'orient' function, such as its properties, description, and required properties.
    """
    return compose_function(
        "summarize_recent_events",
        properties={
            "summary_as_assistant": {
                "type": "string",
                "description": "Respond to the me, the user, as yourself, the assistant. Summarize what has happened recently, what you learned from it and what you'd like to do next. Use 'You' instead of 'I'.",
            },
            "summary_as_user": {
                "type": "string",
                "description": "Resphrase your response as if you were me, the user, from the user's perspective in the first person. Use 'I' instead of 'You'.",
            },
            "knowledge": {
                "type": "array",
                "description": "An array of knowledge items that are extracted from my last epoch of events and the summary of those events. Only include knowledge that has not been learned before. Knowledge can be about anything that would help me. If none, use an empty array.",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Where did I learn this? From a connector, the internet, a user or from my own reasoning? Use first person, e.g. 'I learned this from the internet.', from the user's perspective",
                        },
                        "content": {
                            "type": "string",
                            "description": "The actual knowledge I learned. Please format it as a sentence, e.g. 'The sky is blue.' from the user's perspective, in the first person, e.g. 'I can write shell scripts by running a shell command, calling cat and piping out.'",
                        },
                        "relationship": {
                            "type": "string",
                            "description": "What is useful, interesting or important about this information to me and my goals? How does it relate to what I'm doing? Use first person, e.g. 'I can use X to do Y.' from the user's perspective",
                        },
                    },
                },
            },
        },
        description="Summarize the most recent events and decide what to do next.",
        required_properties=["summary_as_assistant", "summary_as_user", "knowledge"],
    )


def orient(observation):
    """
    This function serves as the 'Orient' stage in the OODA loop. It uses the current observation data to summarize the previous epoch and formulate a plan for the next steps.

    Args:
        observation (dict): The dictionary containing data about the current state of the system.

    Returns:
        dict: The updated observation dictionary after the 'Orient' stage, including the summary of the last epoch, relevant knowledge, available actions, and so on.
    """
    response = debuggable_function_call(
        text=compose_orient_prompt(observation),
        functions=compose_orient_function(),
        name="orient",
    )

    arguments = response["arguments"]
    if arguments is None:
        arguments = {}
        print("No arguments returned from orient_function")

    # Create new knowledge and add to the knowledge base
    knowledge = arguments.get("knowledge", [])
    if len(knowledge) > 0:
        for k in knowledge:
            # each item in knowledge contains content, source and relationship
            metadata = {
                "source": k["source"],
                "relationship": k["relationship"],
            }
            add_knowledge(k["content"], metadata=metadata)

    # Get the summary and add to the observation object
    summary = response["arguments"]["summary_as_user"]
    summary_header = "Summary of Last Epoch:"
    observation["summary"] = summary_header + "\n" + summary + "\n"

    # Search for knowledge based on the summary and add to the observation object
    observation["relevant_knowledge"] = formatted_search_knowledge(
        search_text=summary, n_results=10
    )

    # Search for the most relevant available actions based on the summary
    observation["available_actions"] = get_formatted_available_actions(summary)

    # Add observation summary to event stream
    create_event(summary, type="summary")
    write_dict_to_log(observation, "observation_orient")
    return observation


### DECIDE FUNCTIONS ###


def compose_decision_prompt(observation):
    """
    This function formats the decision prompt by inserting the observation data into a pre-defined template.

    Args:
        observation (dict): The dictionary containing data about the current state of the system, such as current epoch, time, date, relevant knowledge, events, and available actions.

    Returns:
        str: The fully formed decision prompt with the data filled in from the observation.
    """
    return compose_prompt(
        """Current Epoch: {{epoch}}
The current time is {{current_time}} on {{current_date}}.
{{relevant_knowledge}}
{{events}}
{{available_actions}}
Assistant Notes:
- Do not ask if you can help. Do not ask how you can assist. Do not gather more information.
- I will not repeat the same action unless it achieves some additional goal. I don't like getting stuck in loops or repeating myself.
- I prefer to act in a way that is novel and interesting.
- I only want to gather additional knowledge when I have to. I like to try things first.

Your task: 
- Based on recent events, which of the actions that you think is the best next action for me to progress towards my goals.
- Based on the information provided, write a summary from your perspective of what action I should take next and why (assistant_reasoning)
- Respond with the name of the action (action_name)
- Rewrite the summary as if you were me, the user, in the first person (user_reasoning)
- I can only choose from the available actions. You must choose one of the available actions.
""",
        observation,
    )


def compose_decision_function():
    """
    This function defines the structure and requirements of the 'decide' function to be called in the 'Decide' stage of the OODA loop.

    Returns:
        dict: A dictionary containing the details of the 'decide' function, such as its properties, description, and required properties.
    """
    return compose_function(
        name="decide_action",
        description="Decide which action to take next.",
        properties={
            "assistant_reasoning": {
                "type": "string",
                "description": "The reasoning behind the decision. Why did you choose this action? Should be written from your perspective, as the assistant, telling the user why you chose this action.",
            },
            "action_name": {
                "type": "string",
                "description": "The name of the action to take. Should be one of the available actions, and should not include quotes or any punctuation",
            },
            "user_reasoning": {
                "type": "string",
                "description": "Rewrite the assistant_reasoning from the perspective of the user. Rewrite your reasoning from my perspective, using 'I' instead of 'You'.",
            },
        },
        required_properties=["action_name", "assistant_reasoning", "user_reasoning"],
    )


def decide(observation):
    """
    This function serves as the 'Decide' stage in the OODA loop. It uses the current observation data to decide which action should be taken next.

    Args:
        observation (dict): The dictionary containing data about the current state of the system.

    Returns:
        dict: The updated observation dictionary after the 'Decide' stage, including the selected action and reasoning behind the decision.
    """
    response = debuggable_function_call(
        text=compose_decision_prompt(observation),
        functions=compose_decision_function(),
        name="decision",
    )

    # Add the action reasoning to the observation object
    reasoning = response["arguments"]["user_reasoning"]
    reasoning_header = "Action Reasoning:"
    observation["reasoning"] = reasoning_header + "\n" + reasoning + "\n"
    observation["action_name"] = response["arguments"]["action_name"]
    create_event(reasoning, type="reasoning")
    write_dict_to_log(observation, "observation_decide")
    return observation


### ACT FUNCTIONS ###


def act(observation):
    """
    This function serves as the 'Act' stage in the OODA loop. It executes the selected action from the 'Decide' stage.

    Args:
        observation (dict): The dictionary containing data about the current state of the system, including the selected action to be taken.

    Returns:
        dict: The updated observation dictionary after the 'Act' stage, which will be used in the next iteration of the OODA loop.
    """
    action_name = observation["action_name"]
    action = get_action(action_name)

    if action is None:
        create_event(
            f"I tried to use the action `{action_name}`, but it was not found.",
            type="error",
            subtype="action_not_found",
        )
        return {"error": f"Action {action_name} not found"}

    response = debuggable_function_call(
        text=compose_action_prompt(action, observation),
        functions=compose_action_function(action, observation),
        name=f"action_{action_name}",
    )

    # TODO: check if the action is the last as last time

    use_action(response["function_name"], response["arguments"])
    write_dict_to_log(observation, "observation_act")
    return observation
