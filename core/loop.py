import json
import uuid

from core.memory import (
    add_event,
    get_functions,
    get_events,
    get_all_values_for_text,
    get_client,
    get_collections,
)
from core.completion import create_chat_completion
from core.constants import agent_name
from core.skill_handling import use_skill
from core.utils import (
    compose_prompt,
)

chroma_client = get_client()
collections = get_collections()

def get_most_recent_from_logs(max_characters=1000):
    with open("logs/feed.log", "r") as f:
        lines = f.readlines()
        lines.reverse()
        lines = "".join(lines)
        lines = lines[:max_characters]
        return lines

def main():
    events = get_events(limit=5)

    if events == None or len(events) == 0:
        events = "I have awaken."

    # TODO: we should make sure we're getting a good search here
    values_to_replace = get_all_values_for_text(events)

    user_prompt = compose_prompt("loop", values_to_replace)
    system_prompt = compose_prompt("system", values_to_replace)

    functions = get_functions(events)
    response = create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        functions=functions,
    )
    response_message = response["message"]

    if response_message != None:
        response_message = response_message.replace(f"{agent_name}: ", "", 1)
        add_event("I wrote this response: " + response_message, agent_name, "loop")

    function_call = response["function_call"]

    if function_call != None:
        function_name = function_call.get("name", None)
        args = function_call.get("arguments", None)
        use_skill(function_name, args)