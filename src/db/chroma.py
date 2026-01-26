import chromadb
from chromadb.config import Settings
from src.config import config
import os

def get_client():
    """
    Returns a ChromaDB client. 
    If running locally without docker, it might fall back to local mode if host not found, 
    but primarily properly configured for Docker.
    """
    # Check if we are running inside docker or locally
    # For now, we assume simple http client if host is set, otherwise local persistence
    
    try:
        return chromadb.HttpClient(host=config.CHROMA_HOST, port=config.CHROMA_PORT)
    except Exception:
        print("Could not connect to Chroma HTTP Server, falling back to local persistence (for testing only).")
        return chromadb.PersistentClient(path="./data/chroma_persist")

def get_collection():
    client = get_client()
    # verify connection
    try:
        client.heartbeat()
        print("Connected to ChromaDB")
    except Exception as e:
        print(f"Warning: Could not connect to ChromaDB: {e}")

    return client.get_or_create_collection(name=config.COLLECTION_NAME)

def add_document(doc_data):
    """
    Adds a document to the collection.
    doc_data expected: {'text': str, 'metadata': dict, 'id': str}
    """
    collection = get_collection()
    
    if not doc_data or not doc_data['text']:
        return

    collection.upsert(
        documents=[doc_data['text']],
        metadatas=[doc_data['metadata']],
        ids=[doc_data['id']]
    )
    print(f"Added document: {doc_data['id']}")
