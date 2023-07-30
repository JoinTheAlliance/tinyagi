import asyncio
import os
import threading
from agentmemory import create_memory, get_memories
from easycompletion import (
    compose_function,
    compose_prompt,
    function_completion,
)
from agentcomlink import (
    async_send_message,
    send_message,
    register_message_handler,
    list_files_formatted,
)

from agentloop import pause, unpause

from tinyagi.context.events import build_events_context

from tinyagi.utils import log
from agentagenda import list_tasks_as_formatted_string

from tinyagi.context.knowledge import build_relevant_knowledge

from tinyagi.constants import get_loop_dict

from agentaction import get_action, get_actions as get_all_actions

from tinyagi.constants import get_loop_dict

def use_chat(arguments):
    message = arguments["message"]
    # TODO: simplify epoch
    events = get_memories("events", n_results=1)
    if len(events) > 0:
        epoch = events[0]["metadata"]["epoch"]
    else:
        epoch = 0
    create_memory(
        "event", message, metadata={"type": "message", "sender": "user", "epoch": epoch}
    )
    # send_message is asynchronous, so we need to start with asyncio
    thread = get_loop_dict()["thread"]
    # get the event loop from the thread
    loop = asyncio.new_event_loop()
    # set the event loop for the thread
    asyncio.set_event_loop(loop)
    # run the coroutine in the thread
    asyncio.run_coroutine_threadsafe(async_send_message(message), loop)


started = False

prompt = """\
{{relevant_knowledge}}

{{events}}
{{user_files}}
Recent Conversation:
{{chat}}

Administrator: {{message}}

TASK: Write a chat message response to the administrator as me, the user. Do not explain or hedge. Just write the response as if you were me, the user, speaking to the adminstrator and giving them the information they need.\
- Be conversational, i.e. brief and not lengthy or verbose.
- Do not add the speaker's name, e.g. 'User: ' or 'Administrator: '. Just the chat message itself.
"""

create_task_function = compose_function(
    name="create_task",
    description="Create a task with the given objective.",
    properties={
        "objective": {
            "type": "string",
            "description": "The objective of the task to be created.",
        }
    },
    required_properties=["objective"],
)


def build_chat_context(context={}):
    events = get_memories("events", n_results=10, filter_metadata={"type": "message"})

    # reverse events
    events = events[::-1]

    # annotated events
    context["chat"] = (
        "\n".join(
            [
                (event["metadata"]["sender"] + ": " + event["document"])
                for event in events
            ]
        )
        + "\n"
    )
    return context


async def response_handler(data):
    events = get_memories("events", n_results=1)
    message = data["message"]

    # if the beginning of the message is "/pause", call pause
    if message.startswith("/pause"):
        pause(get_loop_dict())
        return

    # if the beginning of the message is "/unpause", call unpause
    if message.startswith("/unpause"):
        unpause(get_loop_dict())
        return

    type = data["type"]
    # TODO: simplify epoch
    if len(events) > 0:
        epoch = events[0]["metadata"]["epoch"]
    else:
        epoch = 0
    create_memory(
        "event",
        message,
        metadata={"type": type, "sender": "administrator", "epoch": epoch},
    )

    log(
        f"Received message from administrator: {message}",
        type="chat",
        color="white",
        source="chat",
        title="tinyagi",
        send_to_feed=False,
    )

    context = build_events_context({})
    context = build_chat_context(context)
    context = build_relevant_knowledge(context)
    context["user_files"] = list_files_formatted()

    context["tasks"] = list_tasks_as_formatted_string()
    context["message"] = message
    text = compose_prompt(prompt, context)

    # functions
    actions = get_all_actions()

    print("actions")
    print(actions)
    
    # actions is a dictionary of actions, where the name of the action is the key
    # get the function from each action
    functions = [action["function"] for action in actions.values()]

    print('**********************')
    print('functions')
    print(functions)

    response = function_completion(text=text, functions=functions)
    print('*************************')
    print('response')
    print(response)

    content = response.get("text", None)

    function_name = response.get("function_name", None)
    arguments = response.get("arguments", None)

    if content is not None:
        await async_send_message(content)
        log(
        f"Sending message to administrator: {content}",
        type="chat",
        color="yellow",
        source="chat",
        title="tinyagi",
        send_to_feed=False,
    )
        
    if function_name is not None:
        action = actions.get(function_name, None)
        if function_name == "send_message":
            message = arguments["message"]
            await async_send_message(message)
        elif action is not None:
            if arguments.get("acknowledgement", None) is not None:
                await async_send_message(arguments["acknowledgement"])
            action["handler"](arguments)
            print("Action executed successfully")

    print('********** CONTENT')
    print(content)

    create_memory(
        "event", str(content), metadata={"type": "message", "sender": "user", "epoch": str(epoch)}
    )


def get_actions():
    global started
    # check if server is running
    if started is False:
        started = True
        from uvicorn import Config, Server

        config = Config(
            "agentcomlink:start_server",
            host="0.0.0.0",
            port=int(os.getenv("PORT", 8000)),
            factory=True,
        )
        server = Server(config)

        def start_server():
            asyncio.run(server.serve())

        # start the server in a new thread
        threading.Thread(target=start_server, daemon=True).start()

        # Register the message handler
        register_message_handler(response_handler)

    return [
        {
            "function": compose_function(
                name="send_message",
                description="Send a message.",
                properties={
                    "to": {
                        "type": "string",
                        "description": "The name of the person I should send the message to.",
                    },
                    "message": {
                        "type": "string",
                        "description": "The message I should send, as a brief conversational chat message from me to them.",
                    }
                },
                required_properties=["to", "message"],
            ),
            "prompt": prompt,
            # "builder": compose_chat_prompt,
            "handler": use_chat,
            "suggestion_after_actions": [],
            "never_after_actions": [],
        }
    ]
