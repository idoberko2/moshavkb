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
async def process_query_logic(query_text: str) -> str:
    """
    Core logic for handling a query. Returns the final formatted response text.
    Wrapped with @track to ensure Opik captures the input and output.
    """
    # 1. Retrieve relevant chunks
    chunks = search_similar_docs(query_text, n_results=5)
    
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
            return response_data # Raw string
            
        answer_text = response_data
        sources = []
    else:
        answer_text = response_data.get("answer", "No answer generated.")
        sources = response_data.get("sources", [])
    
    # Escape the main answer text to ensure valid HTML
    import html
    answer_text = html.escape(answer_text)

    # 3. Process links
    if isinstance(sources, list) and sources:
        links_section = "\n\n📂 <b>קבצים רלוונטיים להורדה:</b>\n"
        added_links = False
        for filename in sources:
            link = storage.get_file_link(filename)
            if link:
                 clean_filename = html.escape(filename)
                 # Use double quotes for href
                 links_section += f'• <a href="{link}">{clean_filename}</a>\n'
                 added_links = True
        
        if added_links:
            answer_text += links_section
            
    return answer_text

@auth_required(AuthRole.QUERY)
async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text
    
    if not query_text:
        return

    # Notify user we are working
    status_msg = await update.message.reply_text("מחפש מידע... 🔍")
    
    try:
        # Run the tracked logic
        final_response = await process_query_logic(query_text)
        
        # 4. Reply with HTML parse mode
        from telegram.constants import ParseMode
        await status_msg.edit_text(final_response, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Error handling query: {e}")
        await status_msg.edit_text("מצטער, נתקלתי בבעיה בעת הניסיון לענות לבקשתך.")
