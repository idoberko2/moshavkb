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

from src.auth import auth_required, AuthRole

@auth_required(AuthRole.QUERY)
@track
async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text
    
    if not query_text:
        return

    # Notify user we are working
    status_msg = await update.message.reply_text("מחפש מידע... 🔍")
    
    try:
        # 1. Retrieve relevant chunks
        chunks = search_similar_docs(query_text, n_results=5)
        
        # 2. Generate answer
        answer = generate_answer(query_text, chunks)
        
        # 3. Reply
        await status_msg.edit_text(answer)
        
    except Exception as e:
        logger.error(f"Error handling query: {e}")
        await status_msg.edit_text("מצטער, נתקלתי בבעיה בעת הניסיון לענות לבקשתך.")
