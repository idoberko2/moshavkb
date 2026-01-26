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

        # S3 Configuration
        self.S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
        self.S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID", "minioadmin")
        self.S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin")
        self.S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "moshavkb")
        self.S3_REGION_NAME = os.getenv("S3_REGION_NAME", "us-east-1")


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
