import json
import time
from agentmemory import create_memory

def seed(seed_input):
    """
    Seed the memory bank from a JSON object or file

    Parameters:
    - data (dict): the JSON object to seed from

    Returns:
    - None
    """
    if seed_input is False or seed_input is None:
        return

    def seed_from_file(filename="./seeds.json"):
        with open(filename, "r") as f:
            seed_from_json(json.load(f))

    def seed_from_json(data):
        timestamps = [time.time() - (10 * i) for i in range(len(data))]
        for i, entry in enumerate(data):
            timestamp = timestamps[i]
            entry["metadata"]["created_at"] = str(timestamp)
            create_memory(entry["collection"], entry["message"], entry["metadata"])

    # if seed is a dictionary, use it as the seed data
    if isinstance(seed_input, dict):
        seed_from_json(seed_input)

    elif isinstance(seed_input, str) and seed_input.endswith(".json"):
        seed_from_file(seed_input)

    elif seed_input is True:
        seed_from_file()
    # if seed is a string, try parsing it as a json file
    elif seed_input is not None:
        try:
            # parse string to dict
            seed_data = json.loads(seed_input)
            seed_from_json(seed_data)
        except:
            print("Invalid seed data. Must be a JSON file or a JSON string.")
            return

