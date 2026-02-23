import os
import sys
import logging
import argparse

# Ensure scripts/ is on path for tenant_config
sys.path.append(os.path.join(os.path.dirname(__file__)))
from tenant_config import apply_tenant, add_tenant_argument

# Parse args BEFORE importing src.config
parser = argparse.ArgumentParser(description="Delete a file from ChromaDB by filename.")
add_tenant_argument(parser)
parser.add_argument("filename", help="The exact filename to delete (as stored in metadata).")
args = parser.parse_args()
apply_tenant(args.tenant)

from src.db.chroma import get_collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_file(filename: str):
    try:
        collection = get_collection()
        # ChromaDB allows deleting by metadata filter
        collection.delete(
            where={"filename": filename}
        )
        logger.info(f"Successfully sent delete command for file: {filename}")
        
    except Exception as e:
        logger.error(f"Failed to delete file {filename}: {e}")

if __name__ == "__main__":
    delete_file(args.filename)
