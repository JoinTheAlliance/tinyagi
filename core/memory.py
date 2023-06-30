import chromadb
from seed_collections import seed_collections
from utils import (
    get_current_date,
    get_formatted_time,
    get_agent_name,
    write_debug_log,
    messages_to_dialogue,
    events_to_stream
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

def get_client():
    return chroma_client

for collection_name in collection_names:
    collection = chroma_client.get_or_create_collection(collection_name)
    collections[collection_name] = collection

seed_collections(collections)

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

def get_formatted_collection_data(collection_name, query_text, n_results=5):
    if query_text == None:
        print("query_text is None for collection_name", collection_name)
        return
    write_debug_log(f"Searching for similar " + collection_name)
    collection_data = search_collection(
        collection_name=collection_name,
        query_texts=[query_text],
        include=["metadatas", "documents"],
        n_results=n_results
    )
    formatted_collection_data = ""
    for document in collection_data["documents"]:
        # if document is an array, join it
        if isinstance(document, list):
            document = "\n".join(document)
        formatted_collection_data += document + "\n"
    return formatted_collection_data

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
    conversation = messages_to_dialogue(
        collections["events"].peek(limit=12)
    )
    return {
        "formatted_time": get_formatted_time(),
        "current_date": get_current_date(),
        "conversation": conversation,
        "agent_name": get_agent_name(),
        "skills": get_skills(text),
        "goals": get_goals(text),
        "tasks": get_tasks(text),
        "events": get_events(limit=12),
        "similar_events": get_similar_events(text),
        "personality": get_personality(text),
        "knowledge": get_knowledge(text),
    }

def get_conversation_history(limit=10):
    return messages_to_dialogue(
        collections["events"].get(where={"metadatas.type": "conversation"}, limit=limit)
    )

def get_similar_events(text, n_results=5):
    return get_formatted_collection_data("events", text, n_results)

def get_events(limit=12):
    events = events_to_stream(
        collections["events"].peek(limit=limit)
    )
    print("events", events)
    return events