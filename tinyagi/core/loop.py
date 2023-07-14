# core/loop.py
# Handles the main execution loop, which repeats at a fixed internal

import os
import time

from easycompletion import (
    openai_function_call,
    compose_prompt,
)

from .system import debug_log, increment_epoch, get_epoch

from .actions import (
    get_action,
    get_available_actions,
    use_action,
)
from .events import create_event

from .knowledge import add_knowledge, search_knowledge

from .prompts import (
    orient_prompt,
    decision_prompt,
    orient_function,
    decision_function,
    compose_observation,
)


def function_call(text, functions, name="prompt"):
    # Wraps openai_function_call in debug logging
    response = openai_function_call(text=text, functions=functions)
    if os.environ.get("TINYAGI_DEBUG") in ["1", "true", "True"]:
        debug_log(
            f"openai_function_call\nprompt:\n{text}\nfunctions:\n{functions}\nresponse:\n{response}"
        )
        # check if /logs and /logs/prompts exists and create them if they don't
        if not os.path.isdir("./logs"):
            os.mkdir("./logs")
        if not os.path.isdir("./logs/prompts"):
            os.mkdir("./logs/prompts")
        timestamp = time.time()
        # write the prompt, functions and response to a file
        with open(f"./logs/prompts/{name}_{timestamp}.txt", "w") as f:
            f.write(text)

    return response


def loop():
    """
    Main execution loop. This is modeled on the OODA loop -- https://en.wikipedia.org/wiki/OODA_loop
    # The steps are observe, oriented, decide, act
    # Observe - collect inputs and summarize the current world state - what is currently going on and what actions might we take next?
    # Orient - summarize the last epoch and think about what to do next, then augment the observation
    # Decide - based on the orientation and observation, decide which relevant action to take
    # Act - execute the action that was decided on
    """

    # Each run of the loop is an epoch
    increment_epoch()
    epoch = get_epoch()

    if epoch == 1:
        create_event("I have just woken up.", type="loop", subtype="init")

    epoch = get_epoch()

    ### OBSERVE ###
    # Collect inputs and summarize the current world state - what is currently going on and what actions might we take next?
    observation = compose_observation()

    debug_log(f"observation:\n{observation}")

    ### ORIENT ###
    # Summarize the last epoch and think about what to do next

    composed_orient_prompt = compose_prompt(orient_prompt, observation)
    response = function_call(text=composed_orient_prompt, functions=orient_function, name="orient")

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
                "document": k["content"],
            }
            document = f"From {k['source']}: {k['content']} - {k['relationship']}"
            add_knowledge(document, metadata=metadata)

    # Get the summary and add to the observation object
    summary = response["arguments"]["summary_as_user"]
    observation["summary"] = summary

    # Search for knowledge based on the summary and add to the observation object
    knowledge = search_knowledge(search_text=summary, n_results=10)
    formatted_knowledge = "\n".join([k["document"] for k in knowledge])
    observation["knowledge"] = formatted_knowledge

    available_actions = get_available_actions(summary)
    formatted_available_actions = "\n".join(available_actions)
    observation["available_actions"] = formatted_available_actions

    # Add observation summary to event stream
    create_event(summary, type="loop", subtype="observation")

    ### DECIDE ###
    # Based on the orientation, decide which relevant action to take
    composed_decision_prompt = compose_prompt(decision_prompt, observation)
    response = function_call(text=composed_decision_prompt, functions=decision_function, name="decision")

    # Add the action reasoning to the observation object
    action_reasoning = response["arguments"]["user_reasoning"]
    observation["action_reasoning"] = action_reasoning
    create_event(action_reasoning, type="loop", subtype="decision_reasoning")

    ### ACT ###
    # Execute the action that was decided on
    # parse the name and arguments from the response object to call an action
    action = get_action(response["arguments"]["action_name"])

    composed_action_prompt = compose_prompt(action["prompt"], observation)

    response = function_call(text=composed_action_prompt, functions=action["function"], name="action")

    use_action(response["function_name"], response["arguments"])

def start():
    while True:
        interval = os.getenv("UPDATE_INTERVAL") or 1
        interval = int(interval)
        loop()
        time.sleep(interval)
