import os
import json
import time

from agentmemory import wipe_all_memories, create_memory
from tinyagi.core.actions import register_actions
from tinyagi.core.loop import start

# set TOKENIZERS_PARALLELISM environment variable to False to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = "False"


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


# Seed the database with core memories
def seed(filename="seeds.json"):
    # Load the data from the JSON file
    with open(filename, "r") as f:
        seed_data = json.load(f)

    # generate array of timestamps that are 10 seconds apart, from newest to oldest
    timestamp = time.time()
    timestamps = [timestamp - (10 * i) for i in range(len(seed_data))]

    # Iterate over each entry in the JSON data
    for i, entry in enumerate(seed_data):
        # Get the timestamp from timestamps list
        timestamp = timestamps[i]

        # Add the timestamp to the metadata
        entry["metadata"]["created_at"] = str(timestamp)
        
        # Create the memory
        create_memory(
            entry["collection"], entry["message"], entry["metadata"]
        )


# check if --reset is passed
if "--reset" in os.sys.argv:
    wipe_all_memories()
    if "--seed" in os.sys.argv:
        seed()

register_actions()

# check for api key
check_for_api_key()

# start the loop
start()
