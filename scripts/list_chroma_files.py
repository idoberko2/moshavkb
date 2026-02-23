import sys
import os
import argparse

# Ensure scripts/ is on path for tenant_config
sys.path.append(os.path.join(os.path.dirname(__file__)))
from tenant_config import apply_tenant, add_tenant_argument

# Parse args BEFORE importing src.config
parser = argparse.ArgumentParser(description="List all files stored in ChromaDB.")
add_tenant_argument(parser)
args = parser.parse_args()
apply_tenant(args.tenant)

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.db.chroma import get_collection
from src.config import config
import logging

# Configure logging to show only errors to keep output clean
logging.basicConfig(level=logging.ERROR)

def list_files():
    try:
        collection = get_collection()
        # Get all metadatas
        # Note: For very large collections, this should be paginated or optimized
        result = collection.get(include=['metadatas'])
        
        if not result or not result['metadatas']:
            print("No documents found in ChromaDB.")
            return

        unique_files = set()
        total_chunks = len(result['metadatas'])
        
        for meta in result['metadatas']:
            if meta and 'filename' in meta:
                unique_files.add(meta['filename'])
        
        print(f"Tenant: {args.tenant}")
        print(f"Collection: {config.COLLECTION_NAME}")
        print(f"Total Chunks: {total_chunks}")
        print(f"Unique Files ({len(unique_files)}):")
        print("-" * 30)
        for filename in sorted(unique_files):
            print(f"- {filename}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_files()
