import os
import logging
import opik
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from src.query_bot.handlers import start, handle_query
from dotenv import load_dotenv

# Load env vars
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    token = os.getenv("TELEGRAM_QUERY_BOT_TOKEN")
    if not token:
        logger.error("Error: TELEGRAM_QUERY_BOT_TOKEN not found in environment variables.")
        return
    
    # Initialize Opik (reads config from env vars: OPIK_API_KEY, OPIK_PROJECT_NAME, etc.)
    try:
        opik.configure(use_local=False)
        logger.info("Opik configured successfully.")
    except Exception as e:
        logger.warning(f"Failed to configure Opik: {e}")

    # Increase timeouts for stability
    application = ApplicationBuilder().token(token).read_timeout(60).write_timeout(60).connect_timeout(60).build()
    
    application.add_handler(CommandHandler("start", start))
    
    # Handle all text messages that are not commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))
    
    # Error handler
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

    application.add_error_handler(error_handler)
    
    logger.info("Query Bot is starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
