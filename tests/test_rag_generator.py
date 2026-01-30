
import pytest
from src.rag.generator import construct_system_prompt

def test_construct_system_prompt():
    context_chunks = [
        {
            'metadata': {'filename': 'file1.pdf'},
            'text': 'content from file1'
        },
        {
            'metadata': {'filename': 'file2.pdf'},
            'text': 'content from file2'
        },
        {
            'metadata': {'filename': 'file1.pdf'}, # Duplicate file
            'text': 'more content from file1'
        }
    ]

    prompt = construct_system_prompt(context_chunks)

    # Check valid filenames list
    assert "- file1.pdf" in prompt
    assert "- file2.pdf" in prompt
    
    # Check that it appears only once in the list section
    expected_list_part_1 = "- file1.pdf\n- file2.pdf"
    expected_list_part_2 = "- file2.pdf\n- file1.pdf"
    assert (expected_list_part_1 in prompt) or (expected_list_part_2 in prompt)

    # Check context content
    assert "מקור: file1.pdf" in prompt
    assert "תוכן: content from file1" in prompt
    assert "מקור: file2.pdf" in prompt
    assert "תוכן: content from file2" in prompt
    assert "תוכן: more content from file1" in prompt
    
    # Check placeholder replacement
    assert "{file_list}" not in prompt
    assert "{context}" not in prompt
