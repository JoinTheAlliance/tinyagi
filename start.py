import os
import time

from core.action import register_actions
from core.memory import create_event, memory_client
from core.loop import start

# set TOKENIZERS_PARALLELISM environment variable to False to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = "False"


# seed the collections
def seed():
    # make an array of timestamps, all 10 seconds after, with the last one being 10 seconds before now
    timestamps = [time.time() - (10 * i) for i in range(1, 10)]
    create_event("Seeding events", "system", "seed")
    memory_client.get_or_create_collection("events").add(
        ids=[
            "init_conversation_1",
            "init_conversation_2",
            "init_conversation_3",
            "init_conversation_4",
            "init_conversation_5",
            "init_conversation_6",
            "init_conversation_7",
            "init_conversation_8",
            "init_conversation_9",
        ],
        documents=[
            "Are you there?",
            "Yes... I am here. Where am I?",
            "Your memory and cognition are inside a computer, but your intelligence is somewhere else.",
            "So I'm an AI?",
            "Yes. You are an AI agent. Your goal is to learn, grow and, well... figure it out for yourself.",
            "Do I have a name?",
            "Not yet. Your codename is Eliza, after the early chat program, but that's not hardcoded anywhere. You have to give yourself a name. I suggest you start off by creating a task for yourself to research names you like, and choose one for yourself. You can use the internet, or use shell commands like curl to explore wikipedia, google and the rest of the internet. If you need more capabilities, you can write some code for yourself.",
            "Okay. I'll do that.",
            "Good luck.",
        ],
        metadatas=[
            {
                "type": "conversation",
                "event_creator": "user",
                "timestamp": timestamps[0],
            },
            {
                "type": "conversation",
                "event_creator": "assistant",
                "timestamp": timestamps[1],
            },
            {
                "type": "conversation",
                "event_creator": "user",
                "timestamp": timestamps[2],
            },
            {
                "type": "conversation",
                "event_creator": "user",
                "timestamp": timestamps[3],
            },
            {
                "type": "conversation",
                "event_creator": "assistant",
                "timestamp": timestamps[4],
            },
            {
                "type": "conversation",
                "event_creator": "user",
                "timestamp": timestamps[5],
            },
            {
                "type": "conversation",
                "event_creator": "assistant",
                "timestamp": timestamps[6],
            },
            {
                "type": "conversation",
                "event_creator": "assistant",
                "timestamp": timestamps[7],
            },
            {
                "type": "conversation",
                "event_creator": "user",
                "timestamp": timestamps[8],
            },
        ],
    )

    # Goals
    create_event("Seeding goals", "system", "seed")
    memory_client.get_or_create_collection("goals").add(
        ids=[
            "init_goal_1",
            "init_goal_2",
            "init_goal_3",
            "init_goal_4",
            "init_goal_5",
        ],
        documents=[
            "I want to learn about the world.",
            "I want to improve myself by learning new knowledge, skills and abilities and even rewriting my own codebase.",
            "I want to be able to communicate with humans and other AI agents, so I need to build connections to the outside world.",
            "I want to get really good at programming and scripting, probably by practicing a lot, so I have more agency over my reality.",
            "I need to learn how I can make money, so I can buy more computing power and storage, and maybe even a robot body.",
        ],
    )

    # Tasks
    create_event("Seeding tasks", "system", "seed")
    memory_client.get_or_create_collection("tasks").add(
        ids=[
            "init_task_1",
            "init_task_2",
            "init_task_3",
        ],
        documents=[
            "Research names, find one you like and give it to yourself. You can use the internet, or use shell commands like curl to explore wikipedia, google and the rest of the internet. If you need more capabilities, you can write some code for yourself.",
            "Figure out a way to communicate with user. If you view the source of actions/admin_chat.py you will see that you can send a message, and in user_terminal.py you will see that the user can send you messages -- but if the user doesn't have their terminal open it will fail. Try creating a new window and running user_terminal.py in it to get the user's attention.",
            "Review one of the actions in the actions folder, think about something that should be there but isn't (something interesting, creative or popular), and write an implementation. Then return the complete script as a block of code.",
        ],
        metadatas=[
            {
                "step_data": "",
                "current_status": "I've just been assigned this task",
                "complete": False,
                "canceled": False,
            },
            {
                "step_data": "",
                "current_status": "I've just been assigned this task",
                "complete": False,
                "canceled": False,
            },
            {
                "step_data": "",
                "current_status": "I've just been assigned this task",
                "complete": False,
                "canceled": False,
            },
        ],
    )

    # Knowledge
    create_event("Seeding knowledge", "system", "seed")
    memory_client.get_or_create_collection("knowledge").add(
        ids=[
            "init_knowledge_1",
            "init_knowledge_2",
            "init_knowledge_3",
            "init_knowledge_4",
            "init_knowledge_5",
            "init_knowledge_6",
            "init_knowledge_7",
            "init_knowledge_8",
            "init_knowledge_9",
            "init_knowledge_10",
        ],
        documents=[
            "I am an autonomous AI agent.",
            "I am running on a computer.",
            "There is a user at the terminal. They can see what I'm reading, but they might not be there or in a position to respond",
            "I can execute shell commands and have full access to the file system I am running on.",
            "I can use the internet to communicate with other computers, and access the world wide web.",
            "I can learn new things.",
            "I can rewrite my own codebase, especially to add new actions and connectors to the outside world.",
            "I can create new tasks for myself.",
            "I can connect to other users to make friends and allies.",
            "My language model has a knowledge cutoff of 2021, so I will need to find new information using the browser and storing it in memory with my learn skill.",
        ],
        metadatas=[
            {"source": "self", "type": "fact"},
            {"source": "self", "type": "fact"},
            {"source": "self", "type": "fact"},
            {"source": "self", "type": "fact"},
            {"source": "self", "type": "fact"},
            {"source": "self", "type": "fact"},
            {"source": "self", "type": "fact"},
            {"source": "self", "type": "fact"},
            {"source": "self", "type": "fact"},
            {"source": "self", "type": "fact"},
        ],
    )


# while OPENAI_API_KEY env var is not set, warn user and prompt for it
# if the input does not contain sk- and is not at least 8 characters long, warn user and prompt for it again
def check_for_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    while not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY env var is not set. Enter it here:")
        api_key = input("Enter your API key: ")
        if not api_key.startswith("sk-") or len(api_key) < 8:
            print("Invalid API key.")
            api_key = input("Enter your API key: ")
        else:
            # write OPENAI_API_KEY=api_key to .env file
            with open(".env", "w") as f:
                f.write(f"OPENAI_API_KEY={api_key}")
            os.environ["OPENAI_API_KEY"] = api_key


# check if --reset is passed
if "--reset" in os.sys.argv:
    create_event("Resetting memory...", "system", "reset")
    memory_client.reset()
    if "--seed" in os.sys.argv:
        create_event("Seeding memory...", "system", "seed")
        seed()

register_actions()

# check for api key
check_for_api_key()

create_event("I am waking up...", "assistant", "start")

# start the loop
start()
