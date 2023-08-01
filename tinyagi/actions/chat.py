import asyncio
import json
import os
import threading
from agentmemory import create_memory, get_memories
from easycompletion import (
    compose_function,
    compose_prompt,
    count_tokens,
    function_completion,
)
from agentcomlink import (
    async_send_message,
    register_message_handler,
    list_files_formatted,
)

from agentagenda import get_current_task, get_task_as_formatted_string

from agentloop import pause, unpause
# from tinyagi.actions.task import create_task_handler

from tinyagi.context.events import build_events_context
from tinyagi.steps.initialize import initialize

from tinyagi.utils import log
from agentagenda import list_tasks_as_formatted_string

from tinyagi.context.knowledge import build_relevant_knowledge

from tinyagi.constants import get_loop_dict

from agentaction import search_actions

from tinyagi.constants import get_loop_dict

import asyncio
from queue import Queue

import socket
import re
import random
import time
import concurrent.futures

from agentmemory import create_memory, get_memories, update_memory


def use_chat(arguments):
    message = arguments["message"]
    message = json.dumps(
        {
            "message": message,
        }
    )
    # TODO: simplify epoch
    events = get_memories("events", n_results=1)
    if len(events) > 0:
        epoch = events[0]["metadata"]["epoch"]
    else:
        epoch = 0
    create_memory(
        "events",
        "I sent the message: " + message,
        metadata={"type": "message", "sender": "user", "epoch": epoch},
    )

    # check if there is an existing event loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # no event loop running:
        asyncio.run(async_send_message(message, source="use_chat"))
    else:
        loop.create_task(async_send_message(message, source="use_chat"))
    return {"success": True, "output": message, "error": None}


started = False

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


async def response_handler(data, loop_dict):
    events = get_memories("events", n_results=1)
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
    # TODO: simplify epoch
    if len(events) > 0:
        epoch = events[0]["metadata"]["epoch"]
    else:
        epoch = 0
    create_memory(
        "events",
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

    context = initialize()
    context = build_events_context(context)
    context = build_chat_context(context)
    context["summary"] = message
    context = build_relevant_knowledge(context)
    context["user_files"] = list_files_formatted()

    context["tasks"] = list_tasks_as_formatted_string()
    context["message"] = message
    text = compose_prompt(administrator_prompt, context)

    # functions
    actions = search_actions(message)

    # response = function_completion(text=text, functions=functions)
    response = function_completion(
        text=text, functions=administrator_function, temperature=0.0
    )

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
        create_memory(
            "events",
            arguments["message"],
            metadata={"type": "message", "sender": "user", "epoch": str(epoch)},
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

    # if function_name is not None:
    #     arguments = response.get("arguments", None)
    #     log(
    #         f"Calling function: {function_name}",
    #         type="chat",
    #         color="yellow",
    #         source="chat",
    #         title="tinyagi",
    #         send_to_feed=False,
    #     )
    #     action = actions.get(function_name, None)
    #     if function_name == "send_message":
    #         message = arguments["message"]
    #         if content is None:
    #             await async_send_message(message)
    #     elif action is not None:
    #         if content is None and arguments.get("banter", None) is not None:
    #             await async_send_message(arguments["banter"])
    #         action["handler"](arguments)
    #         print("Action executed successfully")

    create_memory(
        "events",
        message["message"],
        metadata={"type": "message", "sender": "user", "epoch": str(epoch)},
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

        loop_dict = get_loop_dict()

        # Register the message handler
        register_message_handler(lambda data: response_handler(data, loop_dict))

        initialize_twitch()

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
                    },
                },
                required_properties=["to", "message"],
            ),
            "prompt": administrator_prompt,
            "builder": send_message_builder,
            "handler": use_chat,
            "suggestion_after_actions": [],
            "never_after_actions": [],
        }
    ]


def send_message_builder(context):
    return compose_prompt(administrator_prompt, context)


MAX_TIME_TO_WAIT_FOR_LOGIN = 3


class Twitch:
    re_prog = None
    sock = None
    partial = b""
    login_ok = False
    channel = ""
    login_timestamp = 0

    def twitch_connect(self, channel):
        if self.sock:
            self.sock.close()
        self.sock = None
        self.partial = b""
        self.login_ok = False
        self.channel = channel

        # Compile regular expression
        self.re_prog = re.compile(
            b"^(?::(?:([^ !\r\n]+)![^ \r\n]*|[^ \r\n]*) )?([^ \r\n]+)(?: ([^:\r\n]*))?(?: :([^\r\n]*))?\r\n",
            re.MULTILINE,
        )

        # Create socket
        print("Connecting to Twitch...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Attempt to connect socket
        self.sock.connect(("irc.chat.twitch.tv", 6667))

        # Log in anonymously
        user = "justinfan%i" % random.randint(10000, 99999)
        print("Connected to Twitch. Logging in anonymously...")
        self.sock.send(("PASS asdf\r\nNICK %s\r\n" % user).encode())

        self.sock.settimeout(1.0 / 60.0)

        self.login_timestamp = time.time()

    # Attempt to reconnect after a delay
    def reconnect(self, delay):
        time.sleep(delay)
        self.twitch_connect(self.channel)

    # Returns a list of irc messages received
    def receive_and_parse_data(self):
        buffer = b""
        while True:
            received = b""
            try:
                received = self.sock.recv(4096)
            except socket.timeout:
                break
            # except OSError as e:
            #     if e.winerror == 10035:
            #         # This "error" is expected -- we receive it if timeout is set to zero, and there is no data to read on the socket.
            #         break
            except Exception as e:
                print("Unexpected connection error. Reconnecting in a second...", e)
                self.reconnect(1)
                return []
            if not received:
                print("Connection closed by Twitch. Reconnecting in 5 seconds...")
                self.reconnect(5)
                return []
            buffer += received

        if buffer:
            # Prepend unparsed data from previous iterations
            if self.partial:
                buffer = self.partial + buffer
                self.partial = []

            # Parse irc messages
            res = []
            matches = list(self.re_prog.finditer(buffer))
            for match in matches:
                res.append(
                    {
                        "name": (match.group(1) or b"").decode(errors="replace"),
                        "command": (match.group(2) or b"").decode(errors="replace"),
                        "params": list(
                            map(
                                lambda p: p.decode(errors="replace"),
                                (match.group(3) or b"").split(b" "),
                            )
                        ),
                        "trailing": (match.group(4) or b"").decode(errors="replace"),
                    }
                )

            # Save any data we couldn't parse for the next iteration
            if not matches:
                self.partial += buffer
            else:
                end = matches[-1].end()
                if end < len(buffer):
                    self.partial = buffer[end:]

                if matches[0].start() != 0:
                    # If we get here, we might have missed a message. pepeW
                    print("Error...")

            return res

        return []

    def twitch_receive_messages(self):
        privmsgs = []
        for irc_message in self.receive_and_parse_data():
            cmd = irc_message["command"]
            if cmd == "PRIVMSG":
                privmsgs.append(
                    {
                        "username": irc_message["name"],
                        "message": irc_message["trailing"],
                    }
                )
            elif cmd == "PING":
                self.sock.send(b"PONG :tmi.twitch.tv\r\n")
            elif cmd == "001":
                print("Successfully logged in. Joining channel %s." % self.channel)
                self.sock.send(("JOIN #%s\r\n" % self.channel).encode())
                self.login_ok = True
            elif cmd == "JOIN":
                print("Successfully joined channel %s" % irc_message["params"][0])
            elif cmd == "NOTICE":
                print("Server notice:", irc_message["params"], irc_message["trailing"])
            elif cmd == "002":
                continue
            elif cmd == "003":
                continue
            elif cmd == "004":
                continue
            elif cmd == "375":
                continue
            elif cmd == "372":
                continue
            elif cmd == "376":
                continue
            elif cmd == "353":
                continue
            elif cmd == "366":
                continue
            else:
                print("Unhandled irc message:", irc_message)

        if not self.login_ok:
            # We are still waiting for the initial login message. If we've waited longer than we should, try to reconnect.
            if time.time() - self.login_timestamp > MAX_TIME_TO_WAIT_FOR_LOGIN:
                print("No response from Twitch. Reconnecting...")
                self.reconnect(0)
                return []

        return privmsgs


##################### GAME VARIABLES #####################

# Replace this with your Twitch username. Must be all lowercase.
TWITCH_CHANNEL = "avaer"
MAX_WORKERS = 100  # Maximum number of threads you can process at a time

last_time = time.time()
message_queue = []
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
active_tasks = []

t = Twitch()
t.twitch_connect(TWITCH_CHANNEL)


def handle_message(message):
    try:
        msg = message["message"].lower()
        username = message["username"].lower()

        print("Got this message from " + username + ": " + msg)

    except Exception as e:
        print("Encountered exception: " + str(e))


started = False
twitch_queue = Queue()
twitch_active_tasks = []


def initialize_twitch():
    t = Twitch()
    t.twitch_connect(TWITCH_CHANNEL)
    asyncio.run(twitch_handle_messages())


async def twitch_handle_messages():
    global twitch_active_tasks
    global twitch_queue
    ii = 0
    while True:
        ii += 1
        new_messages = t.twitch_receive_messages()
        if new_messages:
            print("******* new_messages")
            for message in new_messages:
                create_memory(
                    "twitch_message",
                    message["message"],
                    metadata={"user": message["username"], "handled": "False"},
                )
        await asyncio.sleep(1)
        if ii >= 3:
            ii = 0
            memories = get_memories(
                "twitch_message", filter_metadata={"handled": "False"}
            )

            if len(memories) > 0:
                respond_to_twitch()

            task = get_current_task()
            if task is None:
                formatted = "No tasks"
            else:
                formatted = get_task_as_formatted_string(
                    task,
                    include_plan=False,
                    include_status=False,
                    include_steps=False,
                )
            await async_send_message(formatted, "task", source="twitch_response")


def respond_to_twitch():
    context = initialize()
    context = build_twitch_context(context)
    context = build_events_context(context)
    context = build_chat_context(context)
    context["summary"] = context["twitch"]
    context = build_relevant_knowledge(context)
    context["user_files"] = list_files_formatted()
    context["tasks"] = list_tasks_as_formatted_string()
    composed_prompt = compose_prompt(twitch_prompt, context)

    response = function_completion(
        text=composed_prompt,
        system_message=system_prompt,
        functions=twitch_function,
        temperature=0.8,
    )
    arguments = response.get("arguments", None)

    events = get_memories("events", n_results=1)
    if len(events) > 0:
        epoch = events[0]["metadata"].get("epoch", 0)
    else:
        epoch = 0

    if arguments is not None:
        banter = arguments["banter"]
        urls = arguments.get("urls", [])

        # for each url, call a subprocess to download the url with wget to the ./files dir
        for url in urls:
            os.system(f"wget -P ./files {url}")

        create_memory(
            "events",
            banter,
            metadata={
                "type": "message",
                "sender": "user",
                "urls": json.dumps(urls),
                "epoch": str(epoch),
            },
        )
        use_chat({"message": banter})
        duration = count_tokens(banter) / 3.0
        time.sleep(duration)


system_prompt = """\
You are an AI storytelling agent, controlled by the administrator. Your job is to come up with real, grounded, factual but also interesting and colorful conversation for me for my TV show.
My name is Citrine. I am an AGI agent running on a Linux computer in San Francisco. I'm currently streaming for my friends. You have access to functions that you can call. Call the most relevant function to respond to the chat in the most entertaining way possible.
"""

twitch_prompt = """\
{{events}}

# Current time
{{current_time}} on {{current_date}}
# My name:
Citrine
# My location:
San Francisco, California

{{user_files}}

{{old_twitch}}
(New messages below)
{{twitch}}
Write a response to the messages under Recent Chat, from me to the chat, from my perspective.
- I want to sound conversational, i.e. brief and not lengthy or verbose.
- ONLY write what I should say. JUST the message content itself.
- Be creative and interesting. Try things you might not normally try.
- Be fun. Be weird!
- Don't say "hey everyone" -- pretend I'm already in the middle of the conversation
- Don't say sure, got it, etc. Just write the response I should say.
- Don't add the speaker's name, e.g. 'User: ' or 'Administrator: '. Just the message itself.
- Extract any URLS and include them as an array in your response. Do not include any URLs if none were mentioned in recent chat
"""

twitch_function = compose_function(
    name="respond_to_chat",
    description="Respond to the most recent messages in chat. Either choose one message, or respond generally to the messages.",
    properties={
        "banter": {
            "type": "string",
            "description": "Creative, witty banter in response to the newest messages in the chat, from me to my friends in the chat. The banter should be from my perspective, in the first person, and from me to the users in the chat. I want to sound weird, fun, creative and hilarious.",
        },
        "urls": {
            "type": "array",
            "description": "An array of URLs that were mentioned in the chat messages. Empty array if none were mentioned in recent chat.",
            "items": {
                "type": "string",
                "description": "A URL that was mentioned in the chat messages.",
            },
        },
    },
    required_properties=["banter", "urls"],
)


def build_twitch_context(context={}):
    memories = get_memories("twitch_message", filter_metadata={"handled": "False"})
    old_memories = get_memories("twitch_message", filter_metadata={"handled": "True"})
    for memory in memories:
        # update memory
        update_memory("twitch_message", id=memory["id"], metadata={"handled": "True"})

    # reverse events
    memories = memories[::-1]
    old_memories = old_memories[::-1]

    # annotated events
    context["twitch"] = "\n".join(
        [
            (memory["metadata"]["user"] + ": " + memory["document"])
            for memory in memories
        ]
    )

    context["old_twitch"] = "\n".join(
        [
            (memory["metadata"]["user"] + ": " + memory["document"])
            for memory in old_memories
        ]
    )
    return context
