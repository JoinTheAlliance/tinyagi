# Handles the main execution loop, which repeats at a fixed internal


from core.memory import (
    add_event,
    get_functions,
    get_events,
    get_all_values_for_text,
    get_client,
    get_collections,
)
from core.language import use_language_model, compose_prompt
from core.constants import agent_name
from core.skills import use_skill

# as memory handling, composing prompts, handling skills, and creating chat completions.

# Get Chroma client
chroma_client = get_client()
# Get all collections
collections = get_collections()

def main():
    """
    Main execution function. This retrieves events, prepares prompts, handles skills,
    and creates chat completions.
    """
    # Get the last 5 events
    events = get_events(limit=5) or "I have awaken."

    # Get all the values that need to be replaced in the events text
    values_to_replace = get_all_values_for_text(events)

    # Compose user and system prompts
    user_prompt = compose_prompt("loop", values_to_replace)
    system_prompt = compose_prompt("system", values_to_replace)

    # Get functions from the events
    functions = get_functions(events)

    # Create a chat completion
    response = use_language_model(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        functions=functions,
    )
    # Extract response message and remove the agent's name from it
    response_message = response["message"]
    if response_message:
        response_message = response_message.replace(f"{agent_name}: ", "", 1)
        add_event("I wrote this response: " + response_message, agent_name, "loop")

    # Extract function call from the response
    function_call = response["function_call"]
    if function_call:
        function_name = function_call.get("name")
        args = function_call.get("arguments")
        use_skill(function_name, args)
