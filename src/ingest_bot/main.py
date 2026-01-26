import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from src.ingest_bot.handlers import start, handle_document
from dotenv import load_dotenv

# Load env vars if not already loaded (though config usually does it)
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    token = os.getenv("TELEGRAM_INGESTION_BOT_TOKEN")
    if not token:
        logging.error("Error: TELEGRAM_INGESTION_BOT_TOKEN not found in environment variables.")
        return

    # Increase timeouts for stability
    application = ApplicationBuilder().token(token).read_timeout(60).write_timeout(60).connect_timeout(60).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    
    # Debug handler
    async def debug_msg(update: Update, context):
        logging.debug(f"DEBUG: Received message: {update.message}")
        if update.message.document:
             logging.debug(f"DEBUG: Document: {update.message.document}")
             logging.debug(f"DEBUG: Mime: {update.message.document.mime_type}")

    application.add_handler(MessageHandler(filters.ALL, debug_msg))
    
    # Error handler
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.error(msg="Exception while handling an update:", exc_info=context.error)

    application.add_error_handler(error_handler)
    
    logging.info("Bot is starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
