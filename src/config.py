import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma-db")
    CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
    DOCUMENT_DIR = os.getenv("DOCUMENT_DIR", "./data/documents")
    COLLECTION_NAME = "moshav_protocols"

config = Config()
