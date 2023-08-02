import asyncio
import concurrent.futures
import json
import os
import random
import re
import socket
import time
from queue import Queue
from agentagenda import (
    get_current_task,
    get_task_as_formatted_string,
    list_tasks_as_formatted_string,
)
from agentcomlink import async_send_message, list_files_formatted
from agentmemory import create_memory, get_memories, update_memory
from easycompletion import (
    compose_function,
    compose_prompt,
    count_tokens,
    function_completion,
)

from tinyagi.constants import get_current_epoch
from tinyagi.context.events import build_events_context
from tinyagi.context.knowledge import build_relevant_knowledge
from tinyagi.steps.initialize import initialize

MAX_TIME_TO_WAIT_FOR_LOGIN = 3


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

Write a response to the new messages from my perspective.
- I want to sound conversational, i.e. brief and not lengthy or verbose.
- ONLY write what I should say. JUST the message content itself.
- Be creative and interesting. Try things you might not normally try.
- Don't say "hey everyone" -- pretend I'm already in the middle of the conversation
- Don't say sure, got it, etc. Just write the response I should say.
- Don't add the speaker's name, e.g. 'User: ' or 'Administrator: '. Just the message itself.
- Extract any URLS and include them as an array in your response. Do not include any URLs if none were mentioned in recent chat

{{old_twitch}}
(New messages below)
{{twitch}}
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


def respond_to_twitch():
    context = initialize()
    context = build_twitch_context(context)
    context = build_events_context(context)
    context = build_relevant_knowledge(context)
    context["user_files"] = list_files_formatted()
    context["tasks"] = list_tasks_as_formatted_string()
    composed_prompt = compose_prompt(twitch_prompt, context)

    response = function_completion(
        text=composed_prompt,
        system_message=system_prompt,
        functions=twitch_function,
    )
    arguments = response.get("arguments", None)

    if arguments is not None:
        banter = arguments["banter"]
        urls = arguments.get("urls", [])

        # for each url, call a subprocess to download the url with wget to the ./files dir
        for url in urls:
            os.system(f"wget -P ./files {url}")

        create_memory(
            "twitch_message",
            banter,
            metadata={"user": "Me", "handled": "True"},
        )

        create_memory(
            "events",
            banter,
            metadata={
                "type": "message",
                "sender": "user",
                "urls": json.dumps(urls),
                "epoch": get_current_epoch(),
            },
        )
        message = json.dumps(
            {
                "message": banter,
            }
        )

        # check if there is an existing event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # no event loop running:
            asyncio.run(async_send_message(message, source="use_chat"))
        else:
            loop.create_task(async_send_message(message, source="use_chat"))
        duration = count_tokens(banter) / 3.0
        time.sleep(duration)
        return {"success": True, "output": message, "error": None}


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
TWITCH_CHANNEL = "isekai_citrine"
MAX_WORKERS = 100  # Maximum number of threads you can process at a time

last_time = time.time()
message_queue = []
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
active_tasks = []

t = Twitch()
t.twitch_connect(TWITCH_CHANNEL)


twitch_queue = Queue()
twitch_active_tasks = []


async def twitch_handle_messages():
    global twitch_active_tasks
    global twitch_queue
    while True:
        new_messages = t.twitch_receive_messages()
        if new_messages:
            for message in new_messages:
                create_memory(
                    "twitch_message",
                    message["message"],
                    metadata={"user": message["username"], "handled": "False"},
                )
        await asyncio.sleep(1)
        memories = get_memories("twitch_message", filter_metadata={"handled": "False"})

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
        await async_send_message(formatted, "task", source="task_update_loop")


def start_connector(loop_dict):
    t = Twitch()
    t.twitch_connect(TWITCH_CHANNEL)
    asyncio.run(twitch_handle_messages())
