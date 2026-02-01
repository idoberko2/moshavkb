from telegram import Update
from telegram.ext import ContextTypes
from src.storage.factory import StorageFactory
from src.config import config
import asyncio
import hashlib
from src.db import chroma
from src.ingest.parser import parse_pdf, create_documents_from_chunks
from src.ocr.document_intelligence import DocumentIntelligenceWrapper
from src.ingest.chunker import chunk_text
from io import BytesIO
from datetime import datetime
import logging


logger = logging.getLogger(__name__)

# Initialize storage
storage = StorageFactory.get_storage_provider()
doc_intel_client = DocumentIntelligenceWrapper()  # New Client

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Moshav Knowledge Base Bot! 🏠\n"
        "Send me a PDF file and I will add it to the knowledge base."
    )

from src.auth import auth_required, AuthRole

@auth_required(AuthRole.INGEST)
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    
    if not document.mime_type or 'pdf' not in document.mime_type:
        await update.message.reply_text("Please send a PDF file.")
        return

    if document.file_size > 20 * 1024 * 1024:
         await update.message.reply_text("File is too large. Limit is 20MB.")
         return

    status_msg = await update.message.reply_text("מוריד קובץ...")
    
    try:
        file = await context.bot.get_file(document.file_id)
        file_name = document.file_name
        
        # converted to bytes in process_document or storage
        file_content = await file.download_as_bytearray()
        
        await status_msg.edit_text(f"מעבד... ⚙️")

        # Process document (sync wrapper)
        loop = asyncio.get_event_loop()
        # Pass file_content to avoid needing local file
        status, msg = await loop.run_in_executor(None, process_document, file_name, file_content)
        
        if status == "SUCCESS":
             await status_msg.edit_text(f"Successfully processed and indexed: {file_name} ✅")
        elif status == "DUPLICATE_SAME_NAME":
             await status_msg.edit_text(f"File '{file_name}' already exists! 🔄")
        elif status == "DUPLICATE_DIFF_NAME":
             await status_msg.edit_text(f"File content already exists as '{msg}'! 🔄")
        elif status == "NO_TEXT":
             await status_msg.edit_text(f"Could not extract text from: {file_name} ⚠️")
        else:
             await status_msg.edit_text(f"Failed to process: {file_name} ❌")
        
    except Exception as e:
        logger.error(f"Error handling file: {e}")
        await status_msg.edit_text("An error occurred while handling the file.")

def process_document(file_name, file_content):
    """
    Sync function to process the document:
    1. Calculate Hash
    2. Check Existence
    3. Save to S3 (if new)
    4. Parse & Index
    """
    try:
        # 1. Calculate MD5 Hash
        md5_hash = hashlib.md5(file_content).hexdigest()
        logger.info(f"Calculated hash for {file_name}: {md5_hash}")

        # 2. Check Deduplication
        existing_filename = chroma.check_file_exists_by_hash(md5_hash)
        
        if existing_filename:
            logger.info(f"Duplicate content detected. File previously uploaded as: {existing_filename}")
            if existing_filename == file_name:
                return "DUPLICATE_SAME_NAME", existing_filename
            else:
                return "DUPLICATE_DIFF_NAME", existing_filename

        # 3. Save file to storage (only if new)
        storage.save_file(file_content, file_name, content_type='application/pdf')
        
        # 4. Parse PDF
        # We pass the hash so it gets embedded in metadata
        chunks = parse_pdf(file_name, file_content=file_content, file_hash=md5_hash)
        
        if not chunks:
            logger.info(f"Normal parsing failed/empty for {file_name}. Checking OCR with Document Intelligence...")
            text = None
            
            # 4.2 Run OCR if needed
            if not text:
                logger.info("Running Azure AI Document Intelligence (Layout Model)...")
                text = doc_intel_client.extract_text(BytesIO(file_content))
                
                if text:
                    try: 
                        logger.info("OCR successful. Saving sidecar and updating metadata.")
                        storage.save_file(text.encode('utf-8'), f"{file_name}.txt", content_type='text/plain; charset=utf-8')
                        storage.update_metadata(file_name, {'ocr': 'true'})
                    except Exception as e:
                         logger.error(f"Failed to save OCR results: {e}")

            # 4.3 Process OCR text
            if text:
                text_chunks = chunk_text(text)
                base_metadata = {
                    "filename": file_name,
                    "created_at": datetime.now().isoformat(),
                    "page_count": 0,
                    "file_hash": md5_hash,
                    "ocr": "true"
                }
                
                chunks = create_documents_from_chunks(text_chunks, base_metadata, file_name)
            else:
                 logger.warning(f"No text extracted from {file_name} (OCR failed or empty)")
                 return "NO_TEXT", None
            
        # 5. Add to Chroma
        chroma.add_document(chunks)
        
        return "SUCCESS", None

    except Exception as e:
        logger.error(f"Error processing document {file_name}: {e}")
        return "ERROR", str(e)
