import logging
import time
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from src.config import config
from io import BytesIO

logger = logging.getLogger(__name__)

class DocumentIntelligenceWrapper:
    def __init__(self):
        self.endpoint = config.AZURE_DOC_INTEL_ENDPOINT
        self.key = config.AZURE_DOC_INTEL_KEY
        self.client = None
        
        if self.endpoint and self.key:
            try:
                self.client = DocumentAnalysisClient(
                    endpoint=self.endpoint, 
                    credential=AzureKeyCredential(self.key)
                )
                logger.info("Azure Document Intelligence client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Document Intelligence client: {e}")
        else:
             logger.warning("Azure Document Intelligence credentials not configured.")

    def extract_text(self, file_stream) -> str:
        """
        Extracts text from a PDF/Image stream using Azure AI Document Intelligence (prebuilt-read model).
        """
        if not self.client:
            logger.error("Document Intelligence client not initialized")
            return ""

        try:
            logger.info("Starting layout analysis via Document Intelligence...")
            
            # Read flow requires seekable stream at 0
            if hasattr(file_stream, 'seek'):
                file_stream.seek(0)
            
            # Start the analysis
            # We use "prebuilt-read" which is optimized for text extraction.
            # "prebuilt-layout" is better for tables/structure but costlier.
            # Given the requirement for generic text, 'prebuilt-read' is excellent.
            # But the user mentioned "Layout" model is better for Hebrew. I will use "prebuilt-layout" per recommendation.
            poller = self.client.begin_analyze_document("prebuilt-layout", document=file_stream)
            
            # Wait for result
            result = poller.result()
            
            text_lines = []
            
            # Document Intelligence returns "content" which is the full text, 
            # but concatenating lines/paragraphs gives us more control if needed.
            # Using result.content is usually sufficient and preserves reading order.
            
            if result.content:
                 logger.info(f"Analysis completed. Extracted {len(result.content)} characters.")
                 return result.content
            
            # Fallback if content is empty but pages exist
            for page in result.pages:
                for line in page.lines:
                    text_lines.append(line.content)
            
            return "\n".join(text_lines)

        except Exception as e:
            logger.error(f"Document Intelligence analysis failed: {e}")
            return ""
