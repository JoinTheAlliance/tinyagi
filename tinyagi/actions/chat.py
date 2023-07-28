import asyncio
import os
import threading
from agentmemory import create_memory, get_memories
from easycompletion import compose_function, compose_prompt, openai_text_call
from agentcomlink.server import send_message, register_message_handler

from tinyagi.context.events import build_events_context

from agentlogger import log
from agentagenda import list_tasks_as_formatted_string


def use_chat(arguments):
    message = arguments["message"]
    # send_message is asynchronous, so we need to start with asyncio
    send_message(message)


started = False

prompt = """\
{{tasks}}

{{events}}

Recent Conversation:
{{chat}}

Administrator: {{message}}

TASK: Write a chat message response to the administrator as me, the user. Do not explain or hedge. Just write the response as if you were me, the user, speaking to the adminstrator and giving them the information they need.\
- Be conversational, i.e. brief and not lengthy or verbose.
- Do not add the speaker's name, e.g. 'User: ' or 'Administrator: '. Just the chat message itself.
"""


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


def response_handler(message):
    create_memory(
        "event", message, metadata={"type": "message", "sender": "administrator"}
    )

    log(
        f"Received message from administrator: {message}",
        type="chat",
        color="white",
        source="chat",
        title="tinyagi",
    )

    context = build_events_context({})
    context = build_chat_context(context)
    context["tasks"] = list_tasks_as_formatted_string()
    context["message"] = message
    response = openai_text_call(text=compose_prompt(prompt, context))

    content = response["text"]

    log(
        f"Sending message to administrator: {content}",
        type="chat",
        color="yellow",
        source="chat",
        title="tinyagi",
    )
    create_memory("event", content, metadata={"type": "message", "sender": "user"})
    send_message(content)


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
                name="send_message_to_administrator",
                description="Write the message I should send to the administrator.",
                properties={
                    "message": {
                        "type": "string",
                        "description": "The message I should send to the administrator, as a chat message from me to them.",
                    }
                },
                required_properties=["message"],
            ),
            "prompt": prompt,
            # "builder": compose_chat_prompt,
            "handler": use_chat,
            "suggestion_after_actions": [],
            "never_after_actions": [],
        }
    ]
