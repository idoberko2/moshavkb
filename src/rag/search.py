import logging
from src.db.chroma import get_collection
from src.config import config
from opik import track

logger = logging.getLogger(__name__)

@track
def search_similar_docs(query_text: str, n_results: int = 5):
    """
    Searches for documents in ChromaDB similar to the query text.
    
    Args:
        query_text (str): The question or query to search for.
        n_results (int): Number of chunks to retrieve.
        
    Returns:
        list: A list of dictionaries containing 'text', 'metadata', and 'id'.
    """
    try:
        collection = get_collection()
        
        # Query ChromaDB
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # Format results
        # Chroma returns lists of lists (one list per query)
        if not results['documents'] or not results['documents'][0]:
            logging.info(f"No results found for query: {query_text}")
            return []
            
        formatted_results = []
        for i, doc_text in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i] if results['metadatas'] else {}
            doc_id = results['ids'][0][i] if results['ids'] else "unknown"
            
            # Optional: Filter by distance if available and needed
            # distance = results['distances'][0][i] if 'distances' in results else 0
            
            formatted_results.append({
                "text": doc_text,
                "metadata": metadata,
                "id": doc_id
            })
            
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error searching ChromaDB: {e}")
        return []
