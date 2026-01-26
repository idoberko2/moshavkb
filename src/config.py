import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma-db")
        self.CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
        self.DOCUMENT_DIR = os.getenv("DOCUMENT_DIR", "./data/documents")
        self.COLLECTION_NAME = "moshav_protocols"
        
        # Load whitelists once
        self.QUERY_ALLOWED_USERS = self._parse_id_list("QUERY_ALLOWED_USERS")
        self.QUERY_ALLOWED_GROUPS = self._parse_id_list("QUERY_ALLOWED_GROUPS")
        self.INGEST_ALLOWED_USERS = self._parse_id_list("INGEST_ALLOWED_USERS")
        self.INGEST_ALLOWED_GROUPS = self._parse_id_list("INGEST_ALLOWED_GROUPS")

    @staticmethod
    def _parse_id_list(env_var_name: str) -> list[int]:
        raw = os.getenv(env_var_name, "")
        if not raw:
            return []
        try:
            return [int(x.strip()) for x in raw.split(",") if x.strip()]
        except ValueError:
            return []

config = Config()
