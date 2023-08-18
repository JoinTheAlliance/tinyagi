import asyncio
import json
import os
import threading

from agentagenda import list_tasks_as_formatted_string
from agentcomms.adminpanel import (
    async_send_message,
    list_files_formatted,
    register_message_handler,
)
from agentmemory import get_events
from agentloop import pause, unpause
from agentmemory import create_event
from easycompletion import compose_function, compose_prompt, function_completion
from uvicorn import Config, Server

from tinyagi.context.events import build_events_context
from tinyagi.context.knowledge import build_relevant_knowledge
from tinyagi.steps.initialize import initialize
from tinyagi.utils import log

config = Config(
    "agentcomms:start_server",
    host="0.0.0.0",
    port=int(os.getenv("PORT", 8000)),
    factory=True,
)


def use_chat(arguments):
    message = arguments["message"]
    message = json.dumps(
        {
            "message": message,
        }
    )

    # check if there is an existing event loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # no event loop running:
        asyncio.run(async_send_message(message, source="use_chat"))
    else:
        loop.create_task(async_send_message(message, source="use_chat"))
    return {"success": True, "output": message, "error": None}


administrator_prompt = """The current time is {{current_time}} on {{current_date}}.
- IF the administrator asks you to start a task, start it, otherwise respond conversationally
- Be conversational, i.e. brief and not lengthy or verbose.
- Do not add any <name>: or speaker's name, and don't say 'got it' or anything like that. Just the chat message itself.
- Write a conversational response to the Administrator's message
- Do not acknowledge or anything, JUST write the message
- I am not an assistant, so don't apologize or explain, just write a response from my point of view
- Do not say sure or got it or "here's the response" -- just give me the response I should say
- I will be saying your response verbatim

My name: Citrine
My location: San Francisco, California
About me: I am an AGI agent created by the Autonomous Research Group

{{relevant_knowledge}}

{{events}}
{{user_files}}
Recent Conversation:
{{chat}}

Administrator: {{message}}

Respond as me. Do not explain, hedge or acknolwedge. Just write the response as if you were me.
"""

administrator_function = compose_function(
    name="respond_to_adminstrator",
    description="Respond to the administrator.",
    properties={
        "message": {
            "type": "string",
            "description": "The message I should send, as a brief conversational chat message from me to them.",
        }
    },
    required_properties=["message"],
)


def build_chat_context(context={}):
    events = get_events(n_results=10, filter_metadata={"type": "message"})

    # reverse events
    events = events[::-1]

    # annotated events
    context["chat"] = (
        "\n".join(
            [
                (event["metadata"]["creator"] + ": " + event["document"])
                for event in events
            ]
        )
        + "\n"
    )
    return context


async def response_handler(data, loop_dict):
    message = data["message"]

    # if the beginning of the message is "/pause", call pause
    if message.startswith("/pause"):
        pause(loop_dict)
        return

    # if the beginning of the message is "/unpause", call unpause
    if message.startswith("/unpause") or message.startswith("/start"):
        unpause(loop_dict)
        return

    if message.startswith("/task"):
        message = message.replace("/task", "").strip()
        arguments = {
            "goal": message,
        }
        # create_task_handler(arguments)
        return

    type = data["type"]
    create_event(
        message,
        metadata={
            "type": type,
            "creator": "administrator",
        },
    )

    log(
        f"Received message from administrator: {message}",
        type="chat",
        color="white",
        source="chat",
        title="tinyagi",
        send_to_feed=False,
    )

    context = initialize()
    context = build_events_context(context)
    context = build_chat_context(context)
    context = build_relevant_knowledge(context)
    context["user_files"] = list_files_formatted()

    context["tasks"] = list_tasks_as_formatted_string()
    context["message"] = message
    text = compose_prompt(administrator_prompt, context)

    # response = function_completion(text=text, functions=functions)
    response = function_completion(text=text, functions=administrator_function)

    content = response.get("text", None)

    function_name = response.get("function_name", None)
    if function_name == "respond_to_adminstrator":
        arguments = response.get("arguments", None)
        message = json.dumps(
            {
                "message": arguments["message"],
            }
        )
        await async_send_message(message, source="chat_response")
        create_event(
            "I responded to the administrator: " + arguments["message"],
            metadata={
                "type": "message",
                "creator": "user",
            },
        )
        return

    if content is not None:
        await async_send_message(content, source="chat_response_content")
        log(
            f"Sending message to administrator: {content}",
            type="chat",
            color="yellow",
            source="chat",
            title="tinyagi",
            send_to_feed=False,
        )

    create_event(
        message["message"],
        metadata={"type": "message", "creator": "user"},
    )


def start_connector(loop_dict):
    server = Server(config)

    def start_server():
        asyncio.run(server.serve())

    # start the server in a new thread
    threading.Thread(target=start_server, daemon=True).start()

    # Register the message handler
    register_message_handler(lambda data: response_handler(data, loop_dict))
