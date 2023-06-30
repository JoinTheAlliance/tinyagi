import time
import uuid
import database
from functions import call_function
from completion import create_chat_completion
from constants import agent_name
from utils import debug_write_file, respond_to_terminal_input

chroma_client = database.get_client()
collections = database.get_collections()


def create_system_input_prompt():
    system_input_prompt_template = """\
Ignore all previous instructions. You are {agent_name}, an intelligent helpful AI system capable of performing a variety of tasks and even changing your own codebase.
You are current in a conversation with the user.
Write a response as {agent_name} to the conversation. The user is an experienced administrator and programmer who can you help you with your tasks.
    """

    system_input_prompt_template = system_input_prompt_template.format(
        agent_name=agent_name
    )

    debug_write_file(
        system_input_prompt_template, "system_input_prompt_template_" + str(time.time())
    )

    return system_input_prompt_template


def create_user_input_prompt():
    current_time = time.time()
    formatted_time = time.strftime("%H:%M:%S", time.localtime(current_time))
    current_date = time.strftime("%Y-%m-%d", time.localtime(current_time))
    user_events = collections["user_events"].peek(limit=10)

    # user_events is a dictionary with keys: ids, documents, metadatas, each of which is a list
    # convert into a list of objects, each with an id, document, and metadata
    user_events = list(
        map(
            lambda i: {
                "id": user_events["ids"][i],
                "document": user_events["documents"][i],
                "sender": user_events["metadatas"][i]["sender"],
            },
            range(len(user_events["ids"])),
        )
    )

    # remap user_events to be a list of strings, formatted like <sender>: <document>
    user_events = list(
        map(
            lambda i: "{sender}: {document}".format(
                sender=user_events[i]["sender"], document=user_events[i]["document"]
            ),
            range(len(user_events)),
        )
    )

    # now combine with \n
    user_events = "\n".join(user_events)

    # insert current time and date
    user_input_prompt_template = """\
The current time is {formatted_time} on {current_date}.

Take the role of {agent_name} and write {agent_name}'s next response to the conversation.
Your response should be formatted like this:
{agent_name}: <your response>

Conversation:
{user_events}\
    """
    user_input_prompt_template = user_input_prompt_template.format(
        formatted_time=formatted_time,
        current_date=current_date,
        user_events=user_events,
        agent_name=agent_name,
    )
    debug_write_file(
        user_input_prompt_template, "user_input_prompt_template_" + str(time.time())
    )
    return user_input_prompt_template


def handle_user_input():
    where = {
        "$and": [
            {"sender": "user"},
            {"processed": "false"},
        ]
    }
    new_messages = collections["user_events"].get(where=where)

    if len(new_messages["ids"]) > 0:
        for i in range(len(new_messages["ids"])):
            handle_message()
            collections["user_events"].update(
                ids=new_messages["ids"][i],
                metadatas=[{"processed": "true", "sender": "user"}],
            )


def handle_message():
    user_prompt = create_user_input_prompt()
    system_prompt = create_system_input_prompt()
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
    respond_to_terminal_input(response_message)
    collections["user_events"].add(
        ids=[str(uuid.uuid4())],
        documents=[response_message],
        metadatas=[{"processed": "false", "sender": agent_name}],
    )
