from telegram import Update
from telegram.ext import ContextTypes
from src.storage.s3 import S3Storage
from src.config import config
import asyncio
import hashlib
from src.db import chroma
from src.ingest.parser import parse_pdf
import logging


logger = logging.getLogger(__name__)

# Initialize storage
storage = S3Storage()

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

    status_msg = await update.message.reply_text("Downloading file...")
    
    try:
        file = await context.bot.get_file(document.file_id)
        file_name = document.file_name
        
        file_content = await file.download_as_bytearray()
        saved_path = storage.save_file(file_content, file_name)
        
        await status_msg.edit_text(f"File saved! Processing... ⚙️")

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
        storage.save_file(file_content, file_name)
        
        # 4. Parse PDF
        # We pass the hash so it gets embedded in metadata
        chunks = parse_pdf(file_name, file_content=file_content, file_hash=md5_hash)
        
        if not chunks:
            logger.warning(f"No text extracted from {file_name}")
            return "NO_TEXT", None
            
        # 5. Add to Chroma
        chroma.add_document(chunks)
        
        return "SUCCESS", None

    except Exception as e:
        logger.error(f"Error processing document {file_name}: {e}")
        return "ERROR", str(e)
