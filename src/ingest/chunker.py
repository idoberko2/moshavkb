import re

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Splits text into chunks using a recursive character splitting strategy.
    It tries to split by the most natural separators first (\n\n, \n, . , space).
    """
    separators = ["\n\n", "\n", ". ", " ", ""]
    raw_chunks = _split_text(text, chunk_size, overlap, separators)
    # Filter empty or whitespace-only chunks
    return [c for c in raw_chunks if c and c.strip()]

def _split_text(text: str, chunk_size: int, overlap: int, separators: list[str]) -> list[str]:
    final_chunks = []
    
    # Get the current separator
    separator = separators[0]
    next_separators = separators[1:] if len(separators) > 1 else []
    
    # Split text by the current separator
    if separator:
        splits = text.split(separator)
    else:
        splits = list(text) # Split by character if no separator left

    # Buffer to build the current chunk
    current_chunk = []
    current_length = 0
    
    for split in splits:
        # Re-attach separator if it's not the last split (approximation for reconstruction)
        # However, for splitting purposes, we usually just join later.
        # But split() removes the separator. We need to account for its length if we join.
        sep_len = len(separator) if separator else 0
        split_len = len(split)
        
        # If adding this split exceeds chunk size
        if current_length + split_len + (sep_len if current_chunk else 0) > chunk_size:
            # If buffer is not empty, save it
            if current_chunk:
                doc_chunk = separator.join(current_chunk)
                final_chunks.append(doc_chunk)
                
                # Handle overlap: keep ending items that fit within overlap
                # This is a simplified overlap strategy for recursive splitting
                overlap_buffer = []
                overlap_len = 0
                for item in reversed(current_chunk):
                    item_len = len(item)
                    if overlap_len + item_len + sep_len <= overlap:
                         overlap_buffer.insert(0, item)
                         overlap_len += item_len + sep_len
                    else:
                        break
                current_chunk = overlap_buffer
                current_length = overlap_len
            
            # Now check the current split again
            # If single split is still too large, verify if we can split it further
            if len(split) > chunk_size and next_separators:
                sub_chunks = _split_text(split, chunk_size, overlap, next_separators)
                final_chunks.extend(sub_chunks)
            else:
                # If cannot split further or fits now (unlikely if loop entered), add to buffer
                # Note: If > chunk_size and no separators, we force split (handled by list(text) case ideally, or accept oversized)
                current_chunk.append(split)
                current_length += len(split)
        else:
            current_chunk.append(split)
            current_length += split_len + (sep_len if current_chunk else 0)
            
    # Add remaining buffer
    if current_chunk:
        final_chunks.append(separator.join(current_chunk))
        
    return final_chunks
