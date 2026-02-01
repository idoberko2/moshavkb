import logging
from openai import OpenAI
from src.config import config
from opik import track
from src.llm.factory import LLMFactory

logger = logging.getLogger(__name__)

# Initialize OpenAI/Azure client lazily
_client = None

def get_client():
    global _client
    if _client is None:
        _client = LLMFactory.get_llm_client()
    return _client

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
4. שדה 'answer': השתמש בשפה רשמית ומכובדת (עברית). צטט את שם הקובץ או תאריך הפרוטוקול עליו אתה מסתמך בגוף התשובה במידת הצורך. אם יש סתירה בין מסמכים, ציין זאת. הבא ציטוטים רלוונטיים מתוך המקורות במידת האפשר.
5. שדה 'sources': רשימת שמות הקבצים המדויקים עליהם התבססת. עליך לבחור אך ורק מתוך הרשימה הבאה:
{file_list}

אל תמציא שמות ואל תשנה אותם (כולל רווחים).

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

    # Construct system prompt
    formatted_system_prompt = construct_system_prompt(context_chunks)
    
    logger.info(f"Generating answer for query: '{query}' with {len(context_chunks)} chunks.")
    
    try:
        response = call_llm(formatted_system_prompt, query)
        
        content = response.choices[0].message.content.strip()
        return json.loads(content)

    except Exception as e:
        logger.error(f"Error generating answer with OpenAI: {e}")
        return {
            "answer": "מצטער, אירעה שגיאה בעת ניסיון ליצור את התשובה.",
            "sources": []
        }

@track
def construct_system_prompt(context_chunks: list) -> str:
    """
    Constructs the system prompt with context and a list of valid filenames.
    """
    context_text = ""
    filenames = set()

    for chunk in context_chunks:
        source = chunk['metadata'].get('filename', 'Unknown Source')
        filenames.add(source)
        text = chunk['text']
        context_text += f"---\nמקור: {source}\nתוכן: {text}\n"

    # Create a clean list of filenames for the prompt
    file_list_str = "\n".join([f"- {f}" for f in sorted(list(filenames))])

    # Fill system prompt
    return SYSTEM_PROMPT.format(file_list=file_list_str, context=context_text)


@track
def call_llm(system_prompt: str, query: str) -> dict:
    client = get_client()
    return client.chat.completions.create(
        model=config.AZURE_DEPLOYMENT_NAME if config.LLM_PROVIDER == "azure" else "gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.3,
        max_tokens=2000,
        response_format={"type": "json_object"}
    )
