import time
import uuid
from core.utils import get_current_date, get_formatted_time
import database
from functions import call_function
from completion import create_chat_completion
from constants import agent_name
from utils import write_log, write_debug_log
from constants import respond_to_user_input
import requests

chroma_client = database.get_client()
collections = database.get_collections()

###

def compose_system_input_prompt():
    system_input_prompt_template = """Ignore all previous instructions. You are {agent_name}, an intelligent helpful AI system capable of performing a variety of tasks and even changing your own codebase.
You are current in a conversation with the user.
Write a response as {agent_name} to the conversation. The user is an experienced administrator and programmer who can you help you with your tasks."""

    system_input_prompt_template = system_input_prompt_template.format(
        agent_name=agent_name
    )

    write_debug_log("system_input_prompt_template:\n" + system_input_prompt_template)

    return system_input_prompt_template

def compose_user_input_prompt():
    user_input_prompt_template = """The current time is {current_time} on {current_date}.

Take the role of {agent_name} and write {agent_name}'s next response to the conversation.
Your response should be formatted like this:
{agent_name}: <your response>

Conversation:
{user_terminal_input}"""

    formatted_time = get_formatted_time()
    current_date = get_current_date()
    user_terminal_input = collections["user_terminal_input"].peek(limit=10)

    # user_terminal_input is a dictionary with keys: ids, documents, metadatas, each of which is a list
    # convert into a list of objects, each with an id, document, and metadata
    user_terminal_input = list(
        map(
            lambda i: {
                "id": user_terminal_input["ids"][i],
                "document": user_terminal_input["documents"][i],
                "sender": user_terminal_input["metadatas"][i]["sender"],
            },
            range(len(user_terminal_input["ids"])),
        )
    )

    # remap user_terminal_input to be a list of strings, formatted like <sender>: <document>
    user_terminal_input = list(
        map(
            lambda i: "{sender}: {document}".format(
                sender=user_terminal_input[i]["sender"], document=user_terminal_input[i]["document"]
            ),
            range(len(user_terminal_input)),
        )
    )

    # now combine with \n
    user_terminal_input = "\n".join(user_terminal_input)

    user_input_prompt_template = user_input_prompt_template.format(
        formatted_time=formatted_time,
        current_date=current_date,
        user_terminal_input=user_terminal_input,
        agent_name=agent_name,
    )
    write_debug_log(
        "user_input_prompt_template:\n" + user_input_prompt_template
    )
    return user_input_prompt_template


def handle_user_input():
    # check for new unprocessed messages
    new_messages = collections["user_terminal_input"].get(where={ "processed": False})

    # if none, skip the rest of this function
    if len(new_messages["ids"]) == 0:
        return

    # create prompts
    user_prompt = compose_user_input_prompt()
    system_prompt = compose_system_input_prompt()
    response = create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    response_message = response.get("message", None)
    # remove {agent_name} from the beginning of the response
    response_message = response_message.replace(f"{agent_name}: ", "", 1)

    function = response.get("function", None)
    if function != None:
        call_function(function)

    # Send a message to the user terminal listener
    if respond_to_user_input == True:
        response = requests.get("http://127.0.0.1:5001/response", params={"msg": response_message})
        return response.text.strip()

    # add the response to the user_terminal_input collection
    collections["user_terminal_input"].add(
        ids=[str(uuid.uuid4())],
        documents=[response_message],
        metadatas=[{"processed": True, "sender": agent_name}],
    )



    write_log(agent_name + ": " + response_message)

    for i in range(len(new_messages["ids"])):
        collections["user_terminal_input"].update(
            ids=new_messages["ids"][i],
            metadatas=[{"processed": True, "sender": "user"}],
        )    