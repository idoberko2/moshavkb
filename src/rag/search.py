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
            
            # Context Expansion: Fetch neighbors
            expanded_text = doc_text
            try:
                chunk_index = metadata.get('chunk_index')
                filename = metadata.get('filename')
                
                print(f"DEBUG: Processing doc_id={doc_id}, index={chunk_index}, file={filename}")

                if chunk_index is not None and filename is not None:
                    # Construct neighbor IDs
                    prev_id = f"{filename}_part_{int(chunk_index) - 1}"
                    next_id = f"{filename}_part_{int(chunk_index) + 1}"
                    
                    print(f"DEBUG: Fetching neighbors: {prev_id}, {next_id}")
                    
                    # Fetch them
                    neighbors = collection.get(ids=[prev_id, next_id])
                    print(f"DEBUG: Got neighbors result ids: {neighbors.get('ids')}")
                    
                    neighbor_map = {}
                    if neighbors['ids']:
                        for j, nid in enumerate(neighbors['ids']):
                            neighbor_map[nid] = neighbors['documents'][j]
                            
                    # Merge text
                    if prev_id in neighbor_map:
                        expanded_text = neighbor_map[prev_id] + "\n" + expanded_text
                        print(f"DEBUG: Merged prev chunk")
                        
                    if next_id in neighbor_map:
                        expanded_text = expanded_text + "\n" + neighbor_map[next_id]
                        print(f"DEBUG: Merged next chunk")
                        
            except Exception as e:
                print(f"Failed to fetch neighbors for {doc_id}: {e}")
            
            formatted_results.append({
                "text": expanded_text,
                "metadata": metadata,
                "id": doc_id
            })
            
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error searching ChromaDB: {e}")
        return []
