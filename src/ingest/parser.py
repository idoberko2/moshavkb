import fitz  # PyMuPDF
import os
from datetime import datetime

def parse_pdf(filepath: str):
    """
    Extracts text and metadata from a PDF file.
    
    Args:
        filepath (str): Path to the PDF file.
        
    Returns:
        dict: A dictionary containing 'text', 'metadata', and 'filename'.
    """
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
            
        metadata = {
            "filename": os.path.basename(filepath),
            "created_at": datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
            "page_count": len(doc)
        }
        
        return {
            "text": text,
            "metadata": metadata,
            "id": os.path.basename(filepath) # Using filename as ID for now
        }
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None
