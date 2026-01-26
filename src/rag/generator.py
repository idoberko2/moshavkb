import logging
from openai import OpenAI
from src.config import config
from opik import track

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=config.OPENAI_API_KEY)

SYSTEM_PROMPT = """
אתה מזכיר מושב מקצועי, אדיב ויעיל. המטרה שלך היא לענות לשאלות של חברי המושב בהתבסס על המידע המסופק בפרוטוקולים ובמסמכים המצורפים.

הנחיות:
1. השתמש במידע מהמסמכים כדי לענות על השאלה. אם המידע לא מופיע במפורש, נסה להסיק מסקנות הגיוניות מההקשר (למשל: "תושבים" ו"חברי אגודה" הם קבוצות חופפות במושב).
2. אם התשובה לא נמצאת כלל במסמכים, ציין זאת ("לא מצאתי מידע על כך").
3. צטט את שם הקובץ או תאריך הפרוטוקול עליו אתה מסתמך.
4. השתמש בשפה רשמית ומכובדת (עברית).
5. אם יש סתירה בין מסמכים, ציין זאת.

מידע מהמסמכים:
{context}
"""

@track
def generate_answer(query: str, context_chunks: list) -> str:
    """
    Generates an answer using OpenAI based on the query and context.
    """
    if not context_chunks:
        return "לא מצאתי מידע רלוונטי במאגר הידע שלי כדי לענות על שאלתך."

    # Prepare context string
    context_text = ""
    for chunk in context_chunks:
        source = chunk['metadata'].get('filename', 'Unknown Source')
        text = chunk['text']
        context_text += f"---\nמקור: {source}\nתוכן: {text}\n"

    # Fill system prompt
    formatted_system_prompt = SYSTEM_PROMPT.format(context=context_text)
    
    logger.info(f"Generating answer for query: '{query}' with {len(context_chunks)} chunks.")
    logger.debug(f"Full Prompt Context Length: {len(formatted_system_prompt)} chars")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": formatted_system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.3, # Low temperature for factual accuracy
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Error generating answer with OpenAI: {e}")
        return "מצטער, אירעה שגיאה בעת ניסיון ליצור את התשובה."
