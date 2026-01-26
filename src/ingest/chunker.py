def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200):
    """
    Splits text into smaller chunks with overlap.
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    
    return chunks
