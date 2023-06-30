import chromadb
import constants

chroma_client = chromadb.Client()

collection_names = ["user_terminal_input", "people", "skills", "goals", "events", "tasks"]

collections = {}


def get_client():
    return chroma_client


for collection_name in constants.collection_names:
    collection = chroma_client.get_or_create_collection(collection_name)
    collections[collection_name] = collection


def get_collections():
    return collections
