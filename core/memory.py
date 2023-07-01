# core/memory.py
# Handles the operations on ChromaDB collections like search, retrieval, and seeding.

import os
import time
import json
import uuid

import chromadb

# Create a ChromaDB client
client = chromadb.Client()

# Define collection names
collection_names = [
    "functions",
    "personality",
    "goals",
    "events",
    "tasks",
    "knowledge",
    "connectors",  # 'people' could be added here as well
]


def wipe_memory():
    client.reset()


def get_client():
    """Returns the ChromaDB client."""
    return client


def get_collections():
    """Returns all collections."""
    return client.list_collections()

def query_collection(
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
    collection = client.get_or_create_collection(collection_name)
    return collection.query(
        query_texts=query_texts,
        where=where,
        where_document=where_document,
        n_results=n_results,
        include=include,
    )


def get_documents(collection_name, where=None, include=["metadatas", "documents"]):
    """Returns documents from a specified collection."""
    collection = client.get_or_create_collection(collection_name)
    return collection.get(where=where, include=include)


def get_collection_data(collection_name, query_text, n_results=5):
    """Gets data from a specified collection."""
    collection_data = query_collection(
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
    collection_data = query_collection(
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
    This function fetches the functions associated with a particular query text from the 'functions' collection.
    """
    collection_data = get_collection_data("functions", query_text, n_results)
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


def get_events(limit=10, max_tokens=1200):
    """
    Returns a stream of events from the 'events' collection.
    """
    collection = client.get_or_create_collection("events")
    collection_data = collection.peek(limit=limit)
    # make sure that event_collection_data is less than max_tokens
    return "\n".join(
        f'{msg_meta["event_creator"]}: {msg_doc}'
        for msg_meta, msg_doc in zip(
            collection_data["metadatas"], collection_data["documents"]
        )
    )


def create_event(
    text, event_creator="assistant", type="conversation", document_id=None
):
    """
    Adds an event to the 'events' collection, prints it to console and writes it to the log file.
    """

    # Log the event and print the user text
    print(text)

    if document_id is None:
        document_id = str(uuid.uuid4())
    collection = client.get_or_create_collection("events")
    collection.add(
        ids=[str(document_id)],
        documents=[text],
        metadatas=[
            {"type": type, "event_creator": event_creator, "timestamp": time.time()}
        ],
    )

    # Add timestamp and current date to the log message
    date_year_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    prefix = f"{date_year_time}|>"
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


if __name__ == "__main__":
    # test the get_collections function
    assert isinstance(get_collections(), dict)

    # test the query_collection function
    query_result = query_collection("functions", ["test_query"])
    assert "documents" in query_result
    assert "metadatas" in query_result

    # test the get_documents function
    documents_result = get_documents("functions")
    assert "documents" in documents_result
    assert "metadatas" in documents_result

    # test the get_collection_data function
    collection_data_result = get_collection_data("functions", "test_query")
    assert "documents" in collection_data_result
    assert "metadatas" in collection_data_result

    # test the get_formatted_collection_data function
    formatted_data_result = get_formatted_collection_data("functions", "test_query")
    assert isinstance(formatted_data_result, str)
