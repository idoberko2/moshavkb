import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.LLM_PROVIDER = "azure"
        
        # Azure OpenAI Configuration
        self.AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
        self.AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME") # For Chat
        self.AZURE_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME") # For Embeddings
        
        self.CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma-db")
        self.CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
        self.DOCUMENT_DIR = os.getenv("DOCUMENT_DIR", "./data/documents")
        self.TENANT_NAME = os.getenv("TENANT_NAME", "moshavkb")
        self.COLLECTION_NAME = os.getenv("COLLECTION_NAME", "moshav_protocols")
        
        # Load whitelists once
        self.QUERY_ALLOWED_USERS = self._parse_id_list("QUERY_ALLOWED_USERS")
        self.QUERY_ALLOWED_GROUPS = self._parse_id_list("QUERY_ALLOWED_GROUPS")
        self.INGEST_ALLOWED_USERS = self._parse_id_list("INGEST_ALLOWED_USERS")
        self.INGEST_ALLOWED_GROUPS = self._parse_id_list("INGEST_ALLOWED_GROUPS")

        # Storage Provider
        self.STORAGE_PROVIDER = "azure"
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
