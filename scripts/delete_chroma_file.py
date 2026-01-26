import logging
import argparse
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
    parser = argparse.ArgumentParser(description="Delete a file from ChromaDB by filename.")
    parser.add_argument("filename", help="The exact filename to delete (as stored in metadata).")
    args = parser.parse_args()
    
    delete_file(args.filename)
