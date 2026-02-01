import fitz  # PyMuPDF
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from src.ingest.chunker import chunk_text

def parse_pdf(filepath: str, file_content: bytes = None, file_hash: str = None):
    """
    Extracts text and metadata from a PDF file.
    If file_content is provided, parses from memory stream.
    Returns a LIST of chunk dictionaries.
    """
    try:
        if file_content:
            doc = fitz.open(stream=file_content, filetype="pdf")
            # For stream, use current time as created_at
            created_at = datetime.now().isoformat()
        else:
            doc = fitz.open(filepath)
            created_at = datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
            
            # If hash not provided and reading from file, calculate it (optional backup)
            # But the caller should usually provide it.

        text = ""
        for page in doc:
            text += page.get_text() + "\n"
            
        base_metadata = {
            "filename": os.path.basename(filepath),
            "created_at": created_at,
            "page_count": len(doc)
        }
        
        if file_hash:
            base_metadata["file_hash"] = file_hash
        
        # Chunk the text
        text_chunks = chunk_text(text)
        
        return create_documents_from_chunks(text_chunks, base_metadata, os.path.basename(filepath))

    except Exception as e:
        logger.error(f"Error parsing {filepath}: {e}")
        return []

def create_documents_from_chunks(chunks: list[str], base_metadata: dict, filename: str) -> list[dict]:
    """
    Helper to format text chunks into document objects.
    """
    documents = []
    for i, chunk in enumerate(chunks):
        doc_id = f"{filename}_part_{i}"
        chunk_metadata = base_metadata.copy()
        chunk_metadata["chunk_index"] = i
        
        documents.append({
            "text": chunk,
            "metadata": chunk_metadata,
            "id": doc_id
        })
    return documents
