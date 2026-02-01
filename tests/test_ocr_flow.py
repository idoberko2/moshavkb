import unittest
from unittest.mock import MagicMock, patch, ANY
import sys
import os
from io import BytesIO

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock telegram modules that might be missing
sys.modules["telegram"] = MagicMock()
sys.modules["telegram.ext"] = MagicMock()
sys.modules["dotenv"] = MagicMock()
sys.modules["azure"] = MagicMock()
sys.modules["msrest"] = MagicMock()
sys.modules["msrest.authentication"] = MagicMock()
sys.modules["azure.core"] = MagicMock()
sys.modules["azure.core.exceptions"] = MagicMock()
sys.modules["azure.storage"] = MagicMock()
sys.modules["azure.storage.blob"] = MagicMock()
sys.modules["azure.ai"] = MagicMock()
sys.modules["azure.ai.formrecognizer"] = MagicMock()
sys.modules["boto3"] = MagicMock()
sys.modules["botocore"] = MagicMock()
sys.modules["botocore.exceptions"] = MagicMock()
sys.modules["botocore.config"] = MagicMock()

from src.ingest_bot.handlers import process_document

class TestOCRFlow(unittest.TestCase):
    @patch('src.ingest_bot.handlers.create_documents_from_chunks')
    @patch('src.ingest_bot.handlers.chunk_text')
    @patch('src.ingest_bot.handlers.storage')
    @patch('src.ingest_bot.handlers.doc_intel_client')
    @patch('src.ingest_bot.handlers.chroma')
    @patch('src.ingest_bot.handlers.parse_pdf')
    def test_ocr_fallback(self, mock_parse_pdf, mock_chroma, mock_doc_intel, mock_storage, mock_chunk_text, mock_create_docs):
        # Setup
        file_name = "scanned.pdf"
        file_content = b"fake_pdf_content"
        
        # Mock Check Existence (New file)
        mock_chroma.check_file_exists_by_hash.return_value = None
        
        # Mock Parse PDF (Returns empty - triggering OCR)
        mock_parse_pdf.return_value = []
        
        # Mock Metadata Check (No OCR yet)
        mock_storage.get_metadata.return_value = {}
        
        # Mock Document Intelligence (Returns text)
        mock_doc_intel.extract_text.return_value = "Extracted Hebrew Text"

        # Mock Chunker
        mock_chunk_text.return_value = ["Extracted Hebrew Text"]
        
        # Mock Create Docs
        mock_create_docs.return_value = [{
            'text': "Extracted Hebrew Text",
            'metadata': {'ocr': 'true'},
            'id': 'doc_1'
        }]
        
        # Run
        status, msg = process_document(file_name, file_content)
        
        # Verify
        self.assertEqual(status, "SUCCESS")
        
        # Verify Doc Intel API called
        mock_doc_intel.extract_text.assert_called_once()
        
        # Verify Sidecar Saved
        mock_storage.save_file.assert_any_call(b"Extracted Hebrew Text", "scanned.pdf.txt")
        
        # Verify Metadata Updated
        mock_storage.update_metadata.assert_called_with("scanned.pdf", {'ocr': 'true'})
        
        # Verify Chroma Indexing
        mock_chroma.add_document.assert_called_once()
        args = mock_chroma.add_document.call_args[0][0]
        self.assertEqual(args[0]['text'], "Extracted Hebrew Text")
        self.assertEqual(args[0]['metadata']['ocr'], "true")


if __name__ == '__main__':
    unittest.main()
