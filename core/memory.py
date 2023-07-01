import chromadb
import json
import random
import uuid

from core.utils import (
    get_current_date,
    get_formatted_time,
    get_agent_name,
    messages_to_dialogue,
    events_to_stream,
    write_log
)

chroma_client = chromadb.Client()

collection_names = [
    "skills",
    "personality",
    "goals",
    "events",
    "tasks",
    "knowledge",
    "connectors"
]  # add people

collections = {}

seeds = ["goals", "knowledge", "personality"]

def seed(collections):
    for seed in seeds:
        # split seed by line
        # add each line to collection
        counter = 0
        with open("seeds/" + seed + ".txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                # check if the line exists in the collection
                # if it does, skip it
                # sanitize the line
                line = line.strip().replace("\n", "").replace("'", "").replace('"', "")
                if line in collections[seed].get(where_document={"$contains": line})["documents"]:
                    continue

                # if it doesn't, add it
                collections[seed].add(
                    ids=[str(counter)],
                    documents=[line],
                )
                counter += 1

def get_client():
    return chroma_client

for collection_name in collection_names:
    collection = chroma_client.get_or_create_collection(collection_name)
    collections[collection_name] = collection

seed(collections)

def get_collections():
    return collections


def get_collection(collection_name):
    return collections[collection_name]


def search_collection(
    collection_name,
    query_texts,
    where=None,
    where_document=None,
    n_results=5,
    include=["metadatas", "documents"],
):
    return collections[collection_name].query(
        query_texts=query_texts,
        where=where,
        where_document=where_document,
        n_results=n_results,
        include=include,
    )

def get_documents(collection_name, where=None, include=["metadatas", "documents"]):
    return collections[collection_name].get(where=where, include=include)

def get_collection_data(collection_name, query_text, n_results=5):
    collection_data = search_collection(
        collection_name=collection_name,
        query_texts=[query_text],
        include=["metadatas", "documents"],
        n_results=n_results
    )
    return collection_data

def get_formatted_collection_data(collection_name, query_text, n_results=5, deduplicate=True):
    collection_data = search_collection(
        collection_name=collection_name,
        query_texts=[query_text],
        include=["metadatas", "documents"],
        n_results=n_results
    )
    # if randomize is true, randomize the collection data
    collection_data_documents = collection_data["documents"][0]
    collection_data_metadatas = collection_data["metadatas"][0]

    if(deduplicate):
        # use a set to keep track of the unique documents
        unique_docs = set()
        # stores the indices of duplicates
        duplicate_indices = []
        for i, doc in enumerate(collection_data_documents):
            # if the document is already in the set, it's a duplicate
            if doc in unique_docs:
                duplicate_indices.append(i)
            else:
                unique_docs.add(doc)
        # iterate over the list of duplicate indices in reverse order
        # (to not mess with the indices of remaining elements)
        for i in sorted(duplicate_indices, reverse=True):
            collection_data_documents.pop(i)
            collection_data_metadatas.pop(i)

    formatted_collection_data = ""
    for i in range(len(collection_data_documents)):
        metadata = collection_data_metadatas[i]
        document = collection_data_documents[i]
        if(i > 0):
            formatted_collection_data += "\n"

        new_string = ""
        if(metadata != None):
            # try to get type from metadata
            type = metadata.get("type", None)
            if(type != None):
                new_string += f"[{type}] "
            event_creator = metadata.get("event_creator", None)
            function_call = metadata.get("function_call", None)
            # if function_call is a string, parse is as a json
            if(function_call != None):
                if isinstance(function_call, str):
                    function_call = json.loads(function_call)
                name = function_call.get("name", None)
                new_string += f"[function called: {name}] "
            if(event_creator != None):
                new_string += f"{event_creator}: "
        new_string += document
        formatted_collection_data += new_string
    return formatted_collection_data

# get the payload
def get_functions(query_text, n_results=5):
    collection_data = get_collection_data("skills", query_text, n_results)
    functions = []
    for i in range(len(collection_data["metadatas"][0])):
        metadata = collection_data["metadatas"][0][i]
        # if metadata is a string, into a python dict
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        # get the function name
        if("function_call" in metadata):
            function_call = metadata["function_call"]
            if isinstance(function_call, str):
                # convert it to a python dictionary
                function_call = json.loads(function_call)
            functions.append(function_call)
    return functions

def get_skills(query_text, n_results=5):
    return get_formatted_collection_data("skills", query_text, n_results)

def get_goals(query_text, n_results=5):
    return get_formatted_collection_data("goals", query_text, n_results)

def get_events(query_text, n_results=5):
    return get_formatted_collection_data("events", query_text, n_results)

def get_tasks(query_text, n_results=5):
    return get_formatted_collection_data("tasks", query_text, n_results)

def get_knowledge(query_text, n_results=5):
    return get_formatted_collection_data("knowledge", query_text, n_results)

def get_personality(query_text, n_results=5):
    return get_formatted_collection_data("personality", query_text, n_results)

def get_all_values_for_text(text):
    values = {
        "current_time": get_formatted_time(),
        "current_date": get_current_date(),
        "agent_name": get_agent_name(),
        "skills": get_skills(text),
        "goals": get_goals(text),
        "tasks": get_tasks(text),
        "events": get_events(limit=12),
        "personality": get_personality(text),
        "knowledge": get_knowledge(text)
    }
    return values

def get_conversation_history(limit=10):
    return messages_to_dialogue(
        collections["events"].get(limit=limit)
    )

def get_events(limit=12):
    events = events_to_stream(
        collections["events"].peek(limit=limit)
    )
    return events

def add_event(userText, event_creator, type="conversation", document_id=None ):
    if(document_id == None):
        document_id = (str(uuid.uuid4()))
    collections["events"].add(
        ids=[str(document_id)],
        documents=[userText],
        metadatas=[{"type": type, "event_creator": event_creator}],
    )
    write_log(userText)
    print(userText)