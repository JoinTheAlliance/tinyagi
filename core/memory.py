import chromadb
from seed_collections import seed_collections
from utils import write_debug_log

chroma_client = chromadb.Client()

collection_names = [
    "terminal_input_history",
    "skills",
    "personality",
    "goals",
    "events",
    "tasks",
    "knowledge",
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
    write_debug_log(f"Searching for similar " + collection_name + " to {query_text}")
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

def get_recent_terminal_input(query_text, n_results=10):
    collection_data = get_formatted_collection_data("terminal_input_history", query_text, n_results)
    collection_data = collection_data.split("\n")
    collection_data.reverse()
    collection_data = "\n".join(collection_data)
    return collection_data