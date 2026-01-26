import chromadb
from chromadb.config import Settings
from src.config import config
import os
import logging

logger = logging.getLogger(__name__)

def get_client():
    """
    Returns a ChromaDB client. 
    If running locally without docker, it might fall back to local mode if host is set, 
    but primarily properly configured for Docker.
    """
    # Check if we are running inside docker or locally
    # For now, we assume simple http client if host is set, otherwise local persistence
    
    try:
        return chromadb.HttpClient(host=config.CHROMA_HOST, port=config.CHROMA_PORT)
    except Exception:
        logger.warning("Could not connect to Chroma HTTP Server, falling back to local persistence (for testing only).")
        return chromadb.PersistentClient(path="./data/chroma_persist")

from chromadb.utils import embedding_functions

def get_collection():
    client = get_client()
    # verify connection
    try:
        client.heartbeat()
        logger.info("Connected to ChromaDB")
    except Exception as e:
        logger.warning(f"Warning: Could not connect to ChromaDB: {e}")

    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=config.OPENAI_API_KEY,
        model_name="text-embedding-3-small"
    )

    return client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=openai_ef
    )

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
    logger.info(f"Added document: {doc_data['id']}")
