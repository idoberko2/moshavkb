import argparse
import sys
import os
import logging
import json

# Ensure src can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.chroma import get_collection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inspect_file(filename: str):
    print(f"Inspecting file: '{filename}'")
    
    collection = get_collection()
    
    # Fetch all chunks for this file
    results = collection.get(
        where={"filename": filename},
        include=["documents", "metadatas"]
    )
    
    if not results['ids']:
        print("No chunks found for this file.")
        return

    # Zip and sort by chunk_index
    chunks = []
    for i in range(len(results['ids'])):
        chunks.append({
            "id": results['ids'][i],
            "text": results['documents'][i],
            "metadata": results['metadatas'][i]
        })
    
    # Sort by chunk_index
    chunks.sort(key=lambda x: x['metadata'].get('chunk_index', 0))
    
    print(f"\nFound {len(chunks)} chunks:\n")
    
    for chunk in chunks:
        idx = chunk['metadata'].get('chunk_index', 'N/A')
        print(f"--- Chunk {idx} ---")
        print(f"Metadata: {json.dumps(chunk['metadata'], ensure_ascii=False)}")
        print(f"Text:\n{chunk['text']}")
        print("-" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dump all chunks for a specific file from ChromaDB.")
    parser.add_argument("filename", help="The exact filename to inspect.")
    args = parser.parse_args()
    
    inspect_file(args.filename)
