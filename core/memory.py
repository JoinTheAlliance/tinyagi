# Handles the operations on ChromaDB collections like search, retrieval, and seeding.
import os
import time
import json
import uuid

import chromadb

from core.constants import agent_name

# Create a ChromaDB client
chroma_client = chromadb.Client()

# Define collection names
collection_names = [
    "skills",
    "personality",
    "goals",
    "events",
    "tasks",
    "knowledge",
    "connectors",  # 'people' could be added here as well
]

collections = {}  # Holds all the collections

seeds = ["goals", "knowledge", "personality"]  # Seeds to start the DB with


def seed(collections):
    """
    Seeds the DB collections with initial data.
    """
    for seed in seeds:
        counter = 0
        with open("seeds/" + seed + ".txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().replace("\n", "").replace("'", "").replace('"', "")
                # Check if line is already in the collection. If it is, skip it.
                if (
                    line
                    in collections[seed].get(where_document={"$contains": line})[
                        "documents"
                    ]
                ):
                    continue
                # Add line to the collection if it's not already there
                collections[seed].add(
                    ids=[str(counter)],
                    documents=[line],
                )
                counter += 1


# Create or get collections
for collection_name in collection_names:
    collection = chroma_client.get_or_create_collection(collection_name)
    collections[collection_name] = collection

# Seed the collections
seed(collections)

# Below are functions for handling various operations on the collections


def get_client():
    """Returns the ChromaDB client."""
    return chroma_client


def get_collections():
    """Returns all collections."""
    return collections


def get_collection(collection_name):
    """Returns a specified collection."""
    return collections[collection_name]


def search_collection(
    collection_name,
    query_texts,
    where=None,
    where_document=None,
    n_results=5,
    include=["metadatas", "documents"],
):
    """
    Search a collection with given query texts.
    """
    return collections[collection_name].query(
        query_texts=query_texts,
        where=where,
        where_document=where_document,
        n_results=n_results,
        include=include,
    )


def get_documents(collection_name, where=None, include=["metadatas", "documents"]):
    """Returns documents from a specified collection."""
    return collections[collection_name].get(where=where, include=include)


def get_collection_data(collection_name, query_text, n_results=5):
    """Gets data from a specified collection."""
    collection_data = search_collection(
        collection_name=collection_name,
        query_texts=[query_text],
        include=["metadatas", "documents"],
        n_results=n_results,
    )
    return collection_data


def get_formatted_collection_data(
    collection_name, query_text, n_results=5, deduplicate=True
):
    """
    This function returns a formatted string of the data from the specified collection.
    It removes duplicate entries if the deduplicate flag is set to True.
    """
    # Search the collection with the query text
    collection_data = search_collection(
        collection_name=collection_name,
        query_texts=[query_text],
        include=["metadatas", "documents"],
        n_results=n_results,
    )

    # Access the documents and the metadatas from the search result
    collection_data_documents = collection_data["documents"][0]
    collection_data_metadatas = collection_data["metadatas"][0]

    if deduplicate:
        # Create a set to hold the unique documents
        unique_docs = set()
        # This list will hold the indices of the duplicate entries
        duplicate_indices = []

        # Enumerate through the documents to find duplicates
        for i, doc in enumerate(collection_data_documents):
            if doc in unique_docs:
                # If a document is already in the set, it's a duplicate
                duplicate_indices.append(i)
            else:
                unique_docs.add(doc)

        # Remove duplicates from the document and metadata lists
        for i in sorted(duplicate_indices, reverse=True):
            collection_data_documents.pop(i)
            collection_data_metadatas.pop(i)

    # Initialize an empty string to hold the formatted data
    formatted_collection_data = ""

    # Format the documents and metadata into a single string
    for i in range(len(collection_data_documents)):
        metadata = collection_data_metadatas[i]
        document = collection_data_documents[i]

        # Add a newline character between each document
        if i > 0:
            formatted_collection_data += "\n"

        new_string = ""
        if metadata is not None:
            type = metadata.get("type", None)
            if type is not None:
                new_string += f"[{type}] "
            event_creator = metadata.get("event_creator", None)
            function_call = metadata.get("function_call", None)

            # If function_call is a string, parse it as a json
            if function_call is not None:
                if isinstance(function_call, str):
                    function_call = json.loads(function_call)
                name = function_call.get("name", None)
                new_string += f"[function called: {name}] "

            if event_creator is not None:
                new_string += f"{event_creator}: "

        new_string += document
        formatted_collection_data += new_string

    return formatted_collection_data


def get_functions(query_text, n_results=5):
    """
    This function fetches the functions associated with a particular query text from the 'skills' collection.
    """
    collection_data = get_collection_data("skills", query_text, n_results)
    functions = []

    # Extract the function calls from the metadata
    for i in range(len(collection_data["metadatas"][0])):
        metadata = collection_data["metadatas"][0][i]

        # If metadata is a string, convert it to a Python dictionary
        if isinstance(metadata, str):
            metadata = json.loads(metadata)

        if "function_call" in metadata:
            function_call = metadata["function_call"]
            if isinstance(function_call, str):
                function_call = json.loads(function_call)
            functions.append(function_call)

    return functions


def get_skills(query_text, n_results=5):
    """
    Fetches skills data that match the query text.
    """
    return get_formatted_collection_data("skills", query_text, n_results)


def get_goals(query_text, n_results=5):
    """
    Fetches goal data that match the query text.
    """
    return get_formatted_collection_data("goals", query_text, n_results)


def get_events(query_text, n_results=5):
    """
    Fetches event data that match the query text.
    """
    return get_formatted_collection_data("events", query_text, n_results)


def get_tasks(query_text, n_results=5):
    """
    Fetches task data that match the query text.
    """
    return get_formatted_collection_data("tasks", query_text, n_results)


def get_knowledge(query_text, n_results=5):
    """
    Fetches knowledge data that match the query text.
    """
    return get_formatted_collection_data("knowledge", query_text, n_results)


def get_personality(query_text, n_results=5):
    """
    Fetches personality data that match the query text.
    """
    return get_formatted_collection_data("personality", query_text, n_results)


def get_all_values_for_text(text):
    """
    Returns a dictionary of various data associated with the provided text.
    """
    values = {
        "current_time": get_formatted_time(),
        "current_date": get_current_date(),
        "agent_name": get_agent_name(),
        "skills": get_skills(text),
        "goals": get_goals(text),
        "tasks": get_tasks(text),
        "events": get_events(limit=12),
        "personality": get_personality(text),
        "knowledge": get_knowledge(text),
    }
    return values


def get_conversation_history(limit=10):
    """
    Returns the conversation history from the 'events' collection.
    """
    return messages_to_dialogue(collections["events"].get(limit=limit))


def get_events(limit=12):
    """
    Returns a stream of events from the 'events' collection.
    """
    events = events_to_stream(collections["events"].peek(limit=limit))
    return events


def add_event(userText, event_creator, type="conversation", document_id=None):
    """
    Adds an event to the 'events' collection.
    """
    if document_id is None:
        document_id = str(uuid.uuid4())

    collections["events"].add(
        ids=[str(document_id)],
        documents=[userText],
        metadatas=[{"type": type, "event_creator": event_creator}],
    )

    # Log the event and print the user text
    write_log(userText)
    print(userText)

def get_formatted_time():
    """
    Returns the current time in the format of 'HH:MM:SS AM/PM'.
    """
    current_time = time.time()
    formatted_time = time.strftime("%I:%M:%S %p", time.localtime(current_time))
    return formatted_time

def get_current_date():
    """
    Returns the current date in the format of 'YYYY-mm-dd'.
    """
    current_time = time.time()
    current_date = time.strftime("%Y-%m-%d", time.localtime(current_time))
    return current_date

def events_to_stream(messages):
    """
    Converts a list of messages into a string of event stream.

    messages: a dictionary that contains message ids, metadatas and documents
    """
    event_stream = "\n".join(
        f'{msg_meta["event_creator"]}: {msg_doc}'
        for msg_meta, msg_doc in zip(messages["metadatas"], messages["documents"])
    )
    return event_stream

def write_log(text, header=None):
    """
    Writes a log message to a log file, with an optional header.

    text: the log message
    header: an optional header for the log message
    """
    # Add timestamp and current date to the log message
    prefix = f"{get_formatted_time()}|{get_current_date()}|>"
    if header is not None:
        prefix += f"{header}\n"
    text = prefix + text

    # Ensure the 'logs' directory exists
    os.makedirs("logs", exist_ok=True)

    # Ensure the 'feed.log' file exists
    if not os.path.exists("logs/feed.log"):
        with open("logs/feed.log", "w") as f:
            pass

    # Open the 'feed.log' file and append the log message
    with open("logs/feed.log", "a") as f:
        f.write(text + "\n")

def get_agent_name():
    """
    Returns the agent's name from the constants module.
    """
    return agent_name