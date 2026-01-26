import logging
from openai import OpenAI
from src.config import config
from opik import track

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=config.OPENAI_API_KEY)

import json

SYSTEM_PROMPT = """
אתה מזכיר מושב מקצועי, אדיב ויעיל. המטרה שלך היא לענות לשאלות של חברי המושב בהתבסס על המידע המסופק בפרוטוקולים ובמסמכים המצורפים.

הנחיות:
1. השתמש במידע מהמסמכים כדי לענות על השאלה. אם המידע לא מופיע במפורש, נסה להסיק מסקנות הגיוניות מההקשר (למשל: "תושבים" ו"חברי אגודה" הם קבוצות חופפות במושב).
2. אם התשובה לא נמצאת כלל במסמכים, ציין זאת ("לא מצאתי מידע על כך").
3. החזר את התשובה בפורמט JSON בלבד, במבנה הבא:
{{
  "answer": "טקסט התשובה המלא בעברית...",
  "sources": ["file1.pdf", "file2.pdf"]
}}
4. שדה 'answer': השתמש בשפה רשמית ומכובדת (עברית). צטט את שם הקובץ או תאריך הפרוטוקול עליו אתה מסתמך בגוף התשובה במידת הצורך. אם יש סתירה בין מסמכים, ציין זאת.
5. שדה 'sources': רשימת שמות הקבצים המדויקים עליהם התבססת. אל תמציא שמות.

מידע מהמסמכים:
{context}
"""

@track
def generate_answer(query: str, context_chunks: list) -> dict:
    """
    Generates an answer using OpenAI based on the query and context.
    Returns a dict with 'answer' (str) and 'sources' (list of str).
    """
    if not context_chunks:
        return {
            "answer": "לא מצאתי מידע רלוונטי במאגר הידע שלי כדי לענות על שאלתך.",
            "sources": []
        }

    # Prepare context string
    context_text = ""
    for chunk in context_chunks:
        source = chunk['metadata'].get('filename', 'Unknown Source')
        text = chunk['text']
        context_text += f"---\nמקור: {source}\nתוכן: {text}\n"

    # Fill system prompt
    formatted_system_prompt = SYSTEM_PROMPT.format(context=context_text)
    
    logger.info(f"Generating answer for query: '{query}' with {len(context_chunks)} chunks.")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": formatted_system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        return json.loads(content)

    except Exception as e:
        logger.error(f"Error generating answer with OpenAI: {e}")
        return {
            "answer": "מצטער, אירעה שגיאה בעת ניסיון ליצור את התשובה.",
            "sources": []
        }
