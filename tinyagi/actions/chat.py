import asyncio
import os
import threading
from agentmemory import create_memory, get_memories
from easycompletion import (
    compose_function,
    compose_prompt,
    function_completion,
    text_completion,
)
from agentcomlink import (
    async_send_message,
    register_message_handler,
    list_files_formatted,
)

from agentloop import pause, unpause

from tinyagi.context.events import build_events_context

from tinyagi.utils import log
from agentagenda import list_tasks_as_formatted_string

from tinyagi.context.knowledge import build_relevant_knowledge

from tinyagi.constants import get_loop_dict

from agentaction import get_actions as get_all_actions

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
    # TODO: simplify epoch
    events = get_memories("events", n_results=1)
    if len(events) > 0:
        epoch = events[0]["metadata"]["epoch"]
    else:
        epoch = 0
    create_memory(
        "event", message, metadata={"type": "message", "sender": "user", "epoch": epoch}
    )

    # check if there is an existing event loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # no event loop running:
        asyncio.run(async_send_message(message))
    else:
        loop.create_task(async_send_message(message))


started = False

prompt = """\
{{relevant_knowledge}}

{{events}}
{{user_files}}
Recent Conversation:
{{chat}}

Administrator: {{message}}

TASK: Respond to the to the administrator as me. Do not explain, hedge or acknolwedge. Just write the response as if you were me.\
- Be conversational, i.e. brief and not lengthy or verbose.
- Do not add the speaker's name, or say 'got it' or anything like that. Just the chat message itself.
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

    # actions is a dictionary of actions, where the name of the action is the key
    # get the function from each action
    functions = [action["function"] for action in actions.values()]

    response = function_completion(text=text, functions=functions)

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
            if content is None:
                await async_send_message(message)
        elif action is not None:
            if content is None and arguments.get("acknowledgement", None) is not None:
                await async_send_message(arguments["acknowledgement"])
            action["handler"](arguments)
            print("Action executed successfully")

    create_memory(
        "event",
        str(content),
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

        # start an async loop to get tasks
        # if the tasks change, post the tasks to websockets
        async def handle_tasks():
            while True:
                tasks = list_tasks_as_formatted_string()
                if tasks == "" or tasks is None:
                    tasks = "No tasks"
                await async_send_message(tasks, "task")
                await asyncio.sleep(3)

        asyncio.run(handle_tasks())

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
            "prompt": prompt,
            # "builder": compose_chat_prompt,
            "handler": use_chat,
            "suggestion_after_actions": [],
            "never_after_actions": [],
        }
    ]


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
                    print(
                        "Error..."
                    )

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
            for message in new_messages:
                create_memory(
                    "twitch_message",
                    message["message"],
                    metadata={"user": message["username"], "handled": "False"},
                )
        await asyncio.sleep(1)
        if ii >= 5:
            ii = 0
            memories = get_memories(
                "twitch_message", filter_metadata={"handled": "False"}
            )

            if len(memories) > 0:
                respond_to_twitch()


def respond_to_twitch():
    context = build_twitch_context({})
    context = build_events_context(context)
    context = build_chat_context(context)
    context["user_files"] = list_files_formatted()
    context["tasks"] = list_tasks_as_formatted_string()
    composed_prompt = compose_prompt(twitch_prompt, context)
    response = text_completion(text=composed_prompt)
    content = response.get("text", None)
    if content is not None:
        use_chat({"message": content})


twitch_prompt = """\
{{user_files}}

{{events}}

Recent Twitch Chat
{{twitch}}

TASK: I am currently streaming. Write a response to the messages under Recent Twitch Chat from my perspective.\
- Be conversational, i.e. brief and not lengthy or verbose.
- ONLY write what I should say. JUST the message content itself.
- Don't say sure, got it, etc. Just write the response I should say.
- Don't add the speaker's name, e.g. 'User: ' or 'Administrator: '. Just the message itself.
"""


def build_twitch_context(context={}):
    memories = get_memories("twitch_message", filter_metadata={"handled": "False"})

    for memory in memories:
        # update memory
        update_memory("twitch_message", id=memory["id"], metadata={"handled": "True"})

    # reverse events
    memories = memories[::-1]

    # annotated events
    context["twitch"] = (
        "\n".join(
            [
                (memory["metadata"]["user"] + ": " + memory["document"])
                for memory in memories
            ]
        )
        + "\n"
    )
    return context
