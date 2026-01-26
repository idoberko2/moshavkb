import sys
import os
import glob

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ingest.parser import parse_pdf
from src.db.chroma import add_document
from src.config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reindex_all():
    docs_dir = config.DOCUMENT_DIR
    logger.info(f"Scanning directory: {docs_dir}")
    
    pdf_files = glob.glob(os.path.join(docs_dir, "*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found.")
        return

    logger.info(f"Found {len(pdf_files)} PDFs. Starting re-indexing...")
    
    success_count = 0
    for filepath in pdf_files:
        try:
            logger.info(f"Processing: {filepath}")
            chunks = parse_pdf(filepath)
            if chunks:
                add_document(chunks)
                success_count += 1
            else:
                logger.warning(f"Failed to parse or empty: {filepath}")
        except Exception as e:
            logger.error(f"Error indexing {filepath}: {e}")

    logger.info(f"Re-indexing complete. Successfully indexed {success_count}/{len(pdf_files)} files.")

if __name__ == "__main__":
    reindex_all()
