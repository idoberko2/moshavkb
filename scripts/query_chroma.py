import argparse
import sys
import os
import logging
import json

# Ensure src can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock opik if not installed (for local usage outside container)
try:
    import opik
except ImportError:
    import sys
    from unittest.mock import MagicMock
    
    # Create a mock module
    mock_opik = MagicMock()
    # Configure the 'track' decorator to be a pass-through
    def mock_track(func):
        return func
    mock_opik.track = mock_track
    
    sys.modules["opik"] = mock_opik

from src.rag.search import search_similar_docs
from src.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def query_chroma(query_text: str, n_results: int = 5):
    print(f"Searching for: '{query_text}' (n={n_results})")
    
    chunks = search_similar_docs(query_text, n_results)
    
    print(f"\nFound {len(chunks)} chunks:\n")
    
    for i, chunk in enumerate(chunks):
        metadata = chunk.get('metadata', {})
        score = "N/A" # Search similar docs doesn't currently return scores in the dict
        filename = metadata.get('filename', 'Unknown')
        page = metadata.get('page_count', 'Unknown')
        
        print(f"--- Result {i+1} ---")
        print(f"File: {filename}")
        print(f"Metadata: {json.dumps(metadata, ensure_ascii=False)}")
        print(f"Content Preview: {chunk['text'][:200]}...")
        print("-" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query ChromaDB using the bot's search logic.")
    parser.add_argument("query", help="The text query to search for.")
    parser.add_argument("-n", "--n_results", type=int, default=5, help="Number of results to retrieve (default: 5)")
    
    args = parser.parse_args()
    
    query_chroma(args.query, args.n_results)
