import fitz  # PyMuPDF
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from src.ingest.chunker import chunk_text

def parse_pdf(filepath: str):
    """
    Extracts text and metadata from a PDF file.
    Returns a LIST of chunk dictionaries.
    """
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
            
        base_metadata = {
            "filename": os.path.basename(filepath),
            "created_at": datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
            "page_count": len(doc)
        }
        
        # Chunk the text
        text_chunks = chunk_text(text)
        
        documents = []
        for i, chunk in enumerate(text_chunks):
            doc_id = f"{os.path.basename(filepath)}_part_{i}"
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_index"] = i
            
            documents.append({
                "text": chunk,
                "metadata": chunk_metadata,
                "id": doc_id
            })
            
        return documents

    except Exception as e:
        logger.error(f"Error parsing {filepath}: {e}")
        return []
