from telegram import Update
from telegram.ext import ContextTypes
from src.storage.local import LocalStorage
from src.config import config
from src.ingest.parser import parse_pdf
from src.db.chroma import add_document
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

# Initialize storage
storage = LocalStorage(config.DOCUMENT_DIR)

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
        # In production this might be offloaded to a queue, but here we do it inline or in thread
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(None, process_document, saved_path)
        
        if success:
             await status_msg.edit_text(f"Successfully processed and indexed: {file_name} ✅")
        else:
             await status_msg.edit_text(f"Failed to process: {file_name} ❌")
        
    except Exception as e:
        logger.error(f"Error handling file: {e}")
        await status_msg.edit_text("An error occurred while handling the file.")

def process_document(filepath: str) -> bool:
    try:
        logger.info(f"Processing document: {filepath}")
        chunks = parse_pdf(filepath)
        if chunks:
            add_document(chunks)
            logger.info(f"Successfully processed {len(chunks)} chunks from: {filepath}")
            return True
        else:
            logger.warning(f"Empty or invalid document: {filepath}")
            return False
    except Exception as e:
        logger.error(f"Error processing document {filepath}: {e}")
        return False
