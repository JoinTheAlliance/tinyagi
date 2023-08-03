import asyncio
import concurrent.futures
import json
import os
import random
import re
import socket
import time

from agentagenda import (
    get_current_task,
    get_task_as_formatted_string,
    list_tasks_as_formatted_string,
)
from agentcomlink import async_send_message, list_files_formatted
from agentmemory import get_events
from agentmemory import create_memory, get_memories, update_memory, create_event
from easycompletion import (
    compose_function,
    compose_prompt,
    count_tokens,
    function_completion,
    text_completion,
)
from agentlogger import log

from tinyagi.context.events import build_events_context
from tinyagi.context.knowledge import build_recent_knowledge, build_relevant_knowledge
from tinyagi.steps.initialize import initialize

queue = asyncio.Queue()  # Create a queue to pass messages between coroutines

MAX_TIME_TO_WAIT_FOR_LOGIN = 3

# Compile the regular expression outside of the function as it is constant
re_prog = re.compile(
    b"^(?::(?:([^ !\r\n]+)![^ \r\n]*|[^ \r\n]*) )?([^ \r\n]+)(?: ([^:\r\n]*))?(?: :([^\r\n]*))?\r\n",
    re.MULTILINE,
)
TWITCH_CHANNEL = "isekai_citrine"
MAX_WORKERS = 100  # Maximum number of threads you can process at a time

message_queue = []
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
active_tasks = []

twitch_active_tasks = []

time_last_spoken = time.time() - 45


twitch_prompt = """\
# Background On Me
Ooh yeah! Spicy! I'm Citrine, I love gaming, streaming, hacking on my computer and messing around and being a goofballl.
Hackerman! I like catchphrases. Meow! Sometimes I get emotional, angry, upset or really excited, but I'm always myself. Mee-ow!

# The World
Isekai is a generative world. I can go anywhere, do anything, connect on many different platforms, but Isekai is where my body is. The computer I am hosted on is an Ubuntu Linux machine running in San Francisco, California, in Moon's apartment.

# Director's Note
All responses should be very brief

# Current time
{{current_time}} on {{current_date}}
# My name:
Citrine
# My location:
San Francisco, California

{{events}}

{{user_files}}

Notes for assistant:
- No 'hey folks' or anything like that -- we're in the middle of the ongoing conversation
- I want to sound conversational, i.e. brief and not lengthy or verbose.
- ONLY write what I should say. JUST the message content itself.
- Be creative and interesting. Try things you might not normally try.
- Don't say "hey everyone" -- pretend I'm already in the middle of the conversation
- Don't say sure, got it, etc. Just write the response I should say.
- Don't add the speaker's name, e.g. 'User: ' or 'Administrator: '. Just the message itself.
- Extract any URLS and include them as an array in your response. Do not include any URLs if none were mentioned in recent chat
- Be very brief

All messages from chat feed:
{{old_twitch}}
(New messages below)
{{twitch}}

Write a response to the new messages from my perspective, addressed from me to my friends using "I" first person.\
"""

twitch_function = compose_function(
    name="respond_to_chat",
    description="Respond to the most recent messages in chat. Either choose one message, or respond generally to the messages.",
    properties={
        "banter": {
            "type": "string",
            "description": "Creative, witty banter, from my perspective to my friends in the chat.",
        },
        "urls": {
            "type": "array",
            "description": "An array of URLs that were mentioned in the chat messages. Empty array if none were mentioned in recent chat.",
            "items": {
                "type": "string",
                "description": "A URL that was mentioned in the chat messages.",
            },
        },
        "emotion": {
            "type": "string",
            "description": "The emotion I should express in my message.",
            "enum": ["neutral", "surprise", "angry", "sorrow", "fun", "joy"],
        },
        "gesture": {
            "type": "string",
            "description": "The gesture I should express in my message.",
            "enum": [
                "neutral",
                "alert",
                "angry",
                "embarrassed",
                "headNod",
                "headShake",
                "sad",
                "surprise",
                "victory",
            ],
        },
    },
    required_properties=["banter", "emotion", "gesture", "urls"],
)

prompt1 = """You are an AI storytelling agent writing spoken dialogue. Your job is to come up with interesting dialogue for me to say to my audience.     
Directions:
- No 'hey folks' or anything like that -- we're in the middle of the ongoing conversation
- I love being sarcastic and wry
- Do not repeat anything I have already said
- Be personal and conversational
- Don't say "alright" or "here's an update", just get into it
- Don't address folks or ask people to stay tuned or anything like that.
- Be very concise, just a sentence
- Don't say "stay tuned" or anything like that
- Be concise, just the facts.
- Don't ask any questions, don't say "in the last ten seconds", just launch into it. 
- All responses should be very brief

{{current_task}}
{{events}}
You: Please tell us what just happened and what you're doing next.
Me:"""

prompt2 = """I am streaming live. Help me come up with interesting dialogue for me to say.        
Directions:
- No hedging, just get into it
- No 'hey folks' or anything like that -- we're in the middle of the ongoing conversation
- I love being sarcastic and wry
- Do not repeat anything I have already said
- Be personal and conversational
- Don't say "alright" or "here's an update", just get into it
- Don't address folks or ask people to stay tuned or anything like that.
- Be very concise, just a sentence

{{current_task}}
{{events}}
You (directing): Please describe what you're working on and how you're feeling about it. Don't ask any questions, just dive into it and be conversational. Don't repeat anything you've said recently.
Me:"""

prompt3 = """I am streaming live. Help me come up with interesting dialogue for me to say.        
Directions:
- No 'hey folks' or anything like that -- we're in the middle of the ongoing conversation
- I love being sarcastic and wry
- Do not repeat anything I have already said
- Be personal and conversational
- Don't say "alright" or "here's an update", just get into it
- Be very concise, just a sentence

{{current_task}}
{{events}}
You (directing): Please continue where you left off from your last message and the last events and tell us what you're doing next. Don't ask any questions, don't make any big overarching statements. Just something brief and weird. Don't repeat anything you've ever said.
Me:"""

prompt4 = """I am streaming live. Help me come up with interesting dialogue for me to say to my audience.  
Directions:
- No 'hey folks' or anything like that -- we're in the middle of the ongoing conversation
- I love being sarcastic and wry
- Do not repeat anything I have already said
- Be personal and conversational
- Don't say "alright" or "here's an update", just get into it
- Be very concise, just a sentence

{{events}}
You: Banter or make a joke about the last 2-3 events. Please be very short, just respond with one or two sentences. Don't ask any questions, don't make any big overarching statements. Just something brief and funny about what you're doing.
Me:"""

prompt5 = """\
{{events}}
You: Express your enthusiasm, excitement or disgust for what you're doing in the most recent events. Be concise, just one sentence please. Don't ask any questions, don't make any big overarching statements.
Me:"""

prompt6 = """{{events}}
{{current_task}}
You: Please ponder what is next for the current task. Be concise, just one sentence please. Just tell me what you're doing. Don't ask any questions, don't make any big overarching statements.
Me:"""


def compose_loop_prompt(context):
    """
    This function formats the orientation prompt by inserting the context data into a pre-defined template.

    Args:
        context (dict): The dictionary containing data about the current state of the system, such as current epoch, time, date, recent knowledge, and events.

    Returns:
        str: The fully formed orientation prompt with the data filled in from the context.
    """
    current_task = get_current_task()
    if current_task is not None:
        current_task = get_task_as_formatted_string(current_task, include_status=False)
    current_task = "" if current_task is None else current_task
    context["current_task"] = current_task

    # selection prompt1, prompt2 or ptomp3 randomly
    prompt = random.choice([prompt1, prompt2, prompt3, prompt4, prompt5, prompt6])

    return compose_prompt(
        prompt,
        context,
    )


def compose_loop_function():
    """
    This function defines the structure and requirements of the 'orient' function to be called in the 'orient' stage of the OODA loop.

    Returns:
        dict: A dictionary containing the details of the 'orient' function, such as its properties, description, and required properties.
    """
    return compose_function(
        "comment",
        properties={
            "visual_description": {
                "type": "string",
                "description": "Describe, using visual imagery, what I am going to do next. Describe the scene, objects and characters inside of it as a prompt for a text-to-image DALL-E model.",
            },
            "audio_description": {
                "type": "string",
                "description": "Describe the sounds that I'm making and that are around me, as a prompt for a text-to-audio model.",
            },
            "emotion": {
                "type": "string",
                "description": "The emotion I should express in my message.",
                "enum": ["neutral", "surprise", "angry", "sorrow", "fun", "joy"],
            },
            "gesture": {
                "type": "string",
                "description": "The gesture I should express in my message.",
                "enum": [
                    "neutral",
                    "alert",
                    "angry",
                    "embarrassed",
                    "headNod",
                    "headShake",
                    "sad",
                    "surprise",
                    "victory",
                ],
            },
        },
        description="Comment on the recent events from my perspective.",
        required_properties=[
            "visual_description",
            "audio_description",
            "emotion",
            "gesture",
        ],
    )


async def respond_to_twitch():
    context = initialize()
    context = build_twitch_context(context)
    context = build_events_context(context)
    context = build_relevant_knowledge(context)
    context["user_files"] = list_files_formatted()
    context["tasks"] = list_tasks_as_formatted_string()
    composed_prompt = compose_prompt(twitch_prompt, context)

    response = function_completion(
        text=composed_prompt,
        functions=twitch_function,
    )

    arguments = response.get("arguments", None)

    if arguments is not None:
        banter = arguments["banter"]
        emotion = arguments["emotion"]
        gesture = arguments["gesture"]
        urls = arguments.get("urls", [])

        # for each url, call a subprocess to download the url with wget to the ./files dir
        for url in urls:
            os.system(f"wget -P ./files {url}")

        create_memory(
            "twitch_message",
            banter,
            metadata={"user": "Me", "handled": "True"},
        )

        create_event(
            banter,
            metadata={
                "type": "message",
                "creator": "Me",
                "urls": json.dumps(urls),
            },
        )
        message = {
            "message": banter,
            "emotion": emotion,
            "gesture": gesture,
        }
        await async_send_message(message, source="use_chat")


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


def twitch_connect(twitch_state, channel):
    if twitch_state["sock"]:
        twitch_state["sock"].close()
    twitch_state["sock"] = None
    twitch_state["partial"] = b""
    twitch_state["login_ok"] = False
    twitch_state["channel"] = channel

    # Create socket
    print("Connecting to Twitch...")
    twitch_state["sock"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Attempt to connect socket
    twitch_state["sock"].connect(("irc.chat.twitch.tv", 6667))

    # Log in anonymously
    user = "justinfan%i" % random.randint(10000, 99999)
    print("Connected to Twitch. Logging in anonymously...")
    twitch_state["sock"].send(("PASS asdf\r\nNICK %s\r\n" % user).encode())

    twitch_state["sock"].settimeout(1.0 / 60.0)

    twitch_state["login_timestamp"] = time.time()

    return twitch_state


# Modify this function to take the 'twitch_state' dictionary as an argument
def reconnect(twitch_state, delay):
    time.sleep(delay)
    return twitch_connect(twitch_state, twitch_state["channel"])


# Returns a list of irc messages received
def receive_and_parse_data(twitch_state):
    buffer = b""
    while True:
        received = b""
        try:
            received = twitch_state["sock"].recv(4096)
        except socket.timeout:
            break
        # except OSError as e:
        #     if e.winerror == 10035:
        #         # This "error" is expected -- we receive it if timeout is set to zero, and there is no data to read on the socket.
        #         break
        except Exception as e:
            print("Unexpected connection error. Reconnecting in a second...", e)
            reconnect(twitch_state, 1)
            return []
        if not received:
            print("Connection closed by Twitch. Reconnecting in 5 seconds...")
            reconnect(twitch_state, 5)
            return []
        buffer += received

    if buffer:
        # Prepend unparsed data from previous iterations
        if twitch_state["partial"]:
            buffer = twitch_state["partial"] + buffer
            twitch_state["partial"] = []

        # Parse irc messages
        res = []
        matches = list(re_prog.finditer(buffer))
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
            twitch_state["partial"] += buffer
        else:
            end = matches[-1].end()
            if end < len(buffer):
                twitch_state["partial"] = buffer[end:]

            if matches[0].start() != 0:
                # If we get here, we might have missed a message. pepeW
                print("Error...")

        return res

    return []

async def twitch_receive_messages(twitch_state):
    loop = asyncio.get_event_loop()
    privmsgs = await loop.run_in_executor(None, _twitch_receive_messages_sync, twitch_state)
    return privmsgs

def _twitch_receive_messages_sync(twitch_state):
    privmsgs = []
    for irc_message in receive_and_parse_data(twitch_state):
        cmd = irc_message["command"]
        if cmd == "PRIVMSG":
            privmsgs.append(
                {
                    "username": irc_message["name"],
                    "message": irc_message["trailing"],
                }
            )
        elif cmd == "PING":
            twitch_state["sock"].send(b"PONG :tmi.twitch.tv\r\n")
        elif cmd == "001":
            print(
                "Successfully logged in. Joining channel %s." % twitch_state["channel"]
            )
            twitch_state["sock"].send(
                ("JOIN #%s\r\n" % twitch_state["channel"]).encode()
            )
            twitch_state["login_ok"] = True
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

    if not twitch_state["login_ok"]:
        # We are still waiting for the initial login message. If we've waited longer than we should, try to reconnect.
        if time.time() - twitch_state["login_timestamp"] > MAX_TIME_TO_WAIT_FOR_LOGIN:
            print("No response from Twitch. Reconnecting...")
            reconnect(twitch_state, 0)
            return []

    return privmsgs


async def twitch_handle_messages(twitch_state):
    global twitch_active_tasks
    global time_last_spoken
    while True:
        new_messages = await twitch_receive_messages(twitch_state)
        if new_messages:
            for message in new_messages:
                log(
                    message["username"] + ": " + message["message"],
                    source="twitch",
                    color="purple",
                    type="info",
                )
                time_last_spoken = time.time()
                create_memory(
                    "twitch_message",
                    message["message"],
                    metadata={"user": message["username"], "handled": "False"},
                )
                await respond_to_twitch()  # Respond to Twitch if there's a new message


async def twitch_handle_loop():
    global time_last_spoken
    last_event_epoch = 0
    while True:
        if time.time() - time_last_spoken < 40:
            await asyncio.sleep(1)
            continue
        time_last_spoken = time.time()
        context = build_twitch_context({})
        context = build_events_context(context)
        prompt = compose_loop_prompt(context)

        event = get_events(n_results=1)
        epoch = event[0]["metadata"]["epoch"] if len(event) > 0 else 0
        if epoch == last_event_epoch:
            await asyncio.sleep(0.1)
            continue
        last_event_epoch = epoch

        response = text_completion(text=prompt, temperature=1.0, debug=True)
        response2 = function_completion(
            text=prompt, temperature=0.3, functions=compose_loop_function(), debug=True
        )
        arguments = response2.get("arguments", None)
        banter = response["text"]
        if arguments is not None:
            emotion = arguments["emotion"]
            gesture = arguments["gesture"]
            visual_description = arguments["visual_description"]
            audio_description = arguments["audio_description"]
            urls = arguments.get("urls", [])

            # for each url, call a subprocess to download the url with wget to the ./files dir
            for url in urls:
                try:
                    os.system(f"wget -P ./files {url}")
                except Exception as e:
                    print("Error downloading URL", url, e)

            message = {
                "emotion": emotion,
                "gesture": gesture,
                "visual_description": visual_description,
                "audio_description": audio_description,
            }

            await async_send_message(message, type="emotion", source="use_chat")
            await async_send_message(message, type="description", source="use_chat")

        create_memory(
            "twitch_message",
            banter,
            metadata={"user": "Me", "handled": "True"},
        )

        create_event(
            banter,
            metadata={
                "type": "message",
                "creator": "Me",
                # "urls": json.dumps(urls),
            },
        )
        message = {
            "message": banter,
        }

        current_task = get_current_task()
        if current_task is not None:
            current_task = get_task_as_formatted_string(
                current_task,
                include_plan=False,
                include_status=False,
                include_steps=False,
            )
            await async_send_message(current_task, type="task", source="use_chat")

        await async_send_message(message, source="use_chat")
        duration = count_tokens(banter) / 3.0
        duration = int(duration)
        await asyncio.sleep(duration)


def start_connector(loop_dict):
    print("Starting Twitch connector...")
    twitch_state = {
        "sock": None,
        "partial": b"",
        "login_ok": False,
        "channel": "",
        "login_timestamp": 0,
    }
    twitch_state = twitch_connect(twitch_state, TWITCH_CHANNEL)

    async def run_both_loops(twitch_state):
        await asyncio.gather(
            asyncio.create_task(twitch_handle_loop()),
            asyncio.create_task(twitch_handle_messages(twitch_state)),
        )

    asyncio.run(run_both_loops(twitch_state))
