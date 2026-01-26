from telegram import Update
from telegram.ext import ContextTypes
from src.rag.search import search_similar_docs
from src.rag.generator import generate_answer
from opik import track
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "שלום! אני הבוט של המושב. 🚜\n"
        "אתה מוזמן לשאול אותי כל שאלה לגבי הפרוטוקולים וההחלטות במושב, ואנסה לענות על בסיס המידע הקיים."
    )

from src.storage.s3 import S3Storage
from src.auth import auth_required, AuthRole

# Initialize storage (dynamic based on config)
storage = S3Storage()



@track
async def process_query_logic(query_text: str) -> dict:
    """
    Core logic for handling a query. Returns a dict containing 'answer' and 'sources' list.
    """
    # 1. Retrieve relevant chunks
    chunks = search_similar_docs(query_text, n_results=20)
    
    logger.debug(f"DEBUG: Retrieved {len(chunks)} chunks.")
    
    # 2. Generate answer
    response_data = generate_answer(query_text, chunks)
    
    logger.debug(f"response_data type: {type(response_data)}")
    logger.debug(f"response_data content: {response_data}")
    
    if isinstance(response_data, str):
        # Fallback
        import json
        try:
            response_data = json.loads(response_data)
        except:
             return {"answer": response_data, "sources": []}
            
    return response_data

@auth_required(AuthRole.QUERY)
async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text
    
    if not query_text:
        return

    # Notify user we are working
    status_msg = await update.message.reply_text("מחפש מידע... 🔍")
    
    try:
        # Run the tracked logic
        result = await process_query_logic(query_text)
        answer_text = result.get("answer", "No answer.")
        sources = result.get("sources", [])
        
        # 3. Reply with text
        # Escape HTML chars for safety
        import html
        answer_text = html.escape(answer_text)
        
        from telegram.constants import ParseMode
        await status_msg.edit_text(answer_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        
        # 4. Send Files
        if sources:
            await update.message.reply_text("📂 **קבצים מצורפים:**", parse_mode='Markdown')
            for filename in sources:
                try:
                    file_stream = storage.get_file_stream(filename)
                    if file_stream:
                        await update.message.reply_document(document=file_stream, filename=filename)
                    else:
                        await update.message.reply_text(f"⚠️ לא ניתן היה לאתר את הקובץ: {filename}")
                except Exception as e:
                     logger.error(f"Failed to send file {filename}: {e}")
                     await update.message.reply_text(f"⚠️ שגיאה בשליחת הקובץ: {filename}")
        
    except Exception as e:
        logger.error(f"Error handling query: {e}")
        await status_msg.edit_text("מצטער, נתקלתי בבעיה בעת הניסיון לענות לבקשתך.")
