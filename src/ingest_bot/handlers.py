from telegram import Update
from telegram.ext import ContextTypes
from src.storage.local import LocalStorage
from src.config import config
import os

# Initialize storage
# In a larger app this would be dependency injected
storage = LocalStorage(config.DOCUMENT_DIR)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Moshav Knowledge Base Bot! 🏠\n"
        "Send me a PDF file and I will add it to the knowledge base."
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    
    if not document.mime_type or 'pdf' not in document.mime_type:
        await update.message.reply_text("Please send a PDF file.")
        return

    # Check file size (e.g. limit to 20MB)
    if document.file_size > 20 * 1024 * 1024:
         await update.message.reply_text("File is too large. Limit is 20MB.")
         return

    status_msg = await update.message.reply_text("Downloading file...")
    
    try:
        file = await context.bot.get_file(document.file_id)
        file_name = document.file_name
        
        # Determine unique filename to prevent overwrites or handle it in storage
        # For now, we trust the storage provider handles it or we overwrite
        # Ideally, prepend timestamp or uuid
        
        # Download to memory (bytearray)
        file_content = await file.download_as_bytearray()
        
        # Save using abstraction
        saved_path = storage.save_file(file_content, file_name)
        
        await status_msg.edit_text(f"File saved successfully! Processing started... 🚀\nID: {file_name}")
        
    except Exception as e:
        print(f"Error handling file: {e}")
        await status_msg.edit_text("An error occurred while saving the file.")
