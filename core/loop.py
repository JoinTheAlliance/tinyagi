import uuid
from memory import (
    get_events,
    get_all_values_for_text,
    get_client,
    get_collections,
)
from skill_handling import use_skill
from completion import create_chat_completion
from constants import agent_name
from utils import (
    compose_prompt,
)

chroma_client = get_client()
collections = get_collections()


def check_for_user_input():
    new_messages = collections["events"].get(where={ "$and": [{"type": "conversation"}, {"read": "false"}]})

    # if none, skip the rest of this function
    if len(new_messages["ids"]) == 0:
        return False

    for i in range(len(new_messages["ids"])):
        metadata = new_messages["metadatas"][i]
        collections["events"].update(
            ids=new_messages["ids"][i],
            metadatas=[{"type": "conversation", "read": "true", "event_creator": metadata["event_creator"]}],
        )

    return True

def check_for_tasks():
    new_tasks = collections["tasks"].get(where={ "$and": [{"cancelled": "false"}, {"completed": "false"}]})

    # if none, skip the rest of this function
    if len(new_tasks["ids"]) == 0:
        return False

    for i in range(len(new_tasks["ids"])):
        metadata = new_tasks["metadatas"][i]
        collections["tasks"].update(
            ids=new_tasks["ids"][i],
            metadatas=[{"type": "task", "read": "true", "event_creator": metadata["event_creator"]}],
        )

    return True

def main():

    events = get_events()

    if events == None:
        events = "You have awaken."
    
    values_to_replace = get_all_values_for_text(events)

    user_prompt = compose_prompt("loop_user", values_to_replace)
    system_prompt = compose_prompt("loop_system", values_to_replace)

    response = create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    response_message = response.get("message", None)

    if(response_message != None):
        response_message = response_message.replace(f"{agent_name}: ", "", 1)

    # add the response to the terminal_input_history collection
    collections["events"].add(
        ids=[str(uuid.uuid4())],
        documents=[response_message],
        metadatas=[{"type": "conversation", "connector": "admin_chat", "read": "true", "event_creator": agent_name}],
    )

    function = response.get("function", None)
    if function != None:
        print('*** Function!!! ')
        use_skill(function)