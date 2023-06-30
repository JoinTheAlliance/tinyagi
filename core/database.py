import chromadb
import constants

chroma_client = chromadb.Client()

def get_client():
    return chroma_client

# dicitonary of collection names to collection objects
collections = {}

for collection in constants.collection_names:
    chroma_collection = chroma_client.get_or_create_collection(collection)
    collections[collection] = chroma_collection

def get_collections():
    return collections
