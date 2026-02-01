import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower() # openai or azure
        
        # Azure OpenAI Configuration
        self.AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
        self.AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME") # For Chat
        self.AZURE_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME") # For Embeddings
        
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

        # Storage Provider
        self.STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "s3").lower() # s3, azure
        self.AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "moshavkb")
        self.AZURE_BACKUP_CONTAINER_NAME = os.getenv("AZURE_BACKUP_CONTAINER_NAME", "moshavkb-backups")
        
        # Azure AI Document Intelligence
        self.AZURE_DOC_INTEL_ENDPOINT = os.getenv("AZURE_DOC_INTEL_ENDPOINT")
        self.AZURE_DOC_INTEL_KEY = os.getenv("AZURE_DOC_INTEL_KEY")
        
        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


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
