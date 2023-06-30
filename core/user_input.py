import uuid
from memory import get_personality, get_goals, get_skills, get_tasks
import memory
from functions import call_function
from completion import create_chat_completion
from constants import agent_name
from utils import (
    get_current_date,
    get_formatted_time,
    messages_to_dialogue,
    write_log,
    get_agent_name,
    compose_prompt,
)
from constants import respond_to_user_input
import requests

chroma_client = memory.get_client()
collections = memory.get_collections()


def user_input():
    # check for new unprocessed messages
    new_messages = collections["terminal_input_history"].get(where={"processed":"false"})

    # if none, skip the rest of this function
    if len(new_messages["ids"]) == 0:
        print("No new messages")
        return
    
    for i in range(len(new_messages["ids"])):
        metadata = new_messages["metadatas"][i]
        collections["terminal_input_history"].update(
            ids=new_messages["ids"][i],
            metadatas=[{"processed":"true", "sender": metadata["sender"]}],
        )


    print("New messages")
    print(new_messages)


    short_dialogue = messages_to_dialogue(
        collections["terminal_input_history"].peek(limit=4)
    )

    print("short_dialogue", short_dialogue)

    # get recent messages
    terminal_input_history = messages_to_dialogue(
        collections["terminal_input_history"].peek(limit=10)
    )

    values_to_replace = {
        "formatted_time": get_formatted_time(),
        "current_date": get_current_date(),
        "terminal_input_history": terminal_input_history,
        "agent_name": get_agent_name(),
        "skills": get_skills(short_dialogue),
        "goals": get_goals(short_dialogue),
        "tasks": get_tasks(short_dialogue),
        "personality": get_personality(short_dialogue),
    }

    user_prompt = compose_prompt("terminal_input_user", values_to_replace)
    system_prompt = compose_prompt("terminal_input_system", values_to_replace)

    print ("system_prompt", system_prompt)
    print ("user_prompt", user_prompt)

    response = create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    response_message = response.get("message", None)
    # remove {agent_name} from the beginning of the response
    response_message = response_message.replace(f"{agent_name}: ", "", 1)

    # add the response to the terminal_input_history collection
    collections["terminal_input_history"].add(
        ids=[str(uuid.uuid4())],
        documents=[response_message],
        metadatas=[{"processed":"true", "sender": agent_name}],
    )
    
    function = response.get("function", None)
    if function != None:
        call_function(function)

    # Send a message to the user terminal listener
    if respond_to_user_input == True:
        requests.get(
            "http://127.0.0.1:5001/response", params={"msg": response_message}
        )

    write_log("Conversation:")
    write_log(terminal_input_history)
    write_log(agent_name + ": " + response_message)