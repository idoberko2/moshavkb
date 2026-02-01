from openai import OpenAI, AzureOpenAI
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from src.config import config
import logging

logger = logging.getLogger(__name__)

class LLMFactory:
    @staticmethod
    def get_llm_client():
        """
        Returns an initialized OpenAI or AzureOpenAI client based on config.
        """
        # Always assume Azure OpenAI
        logger.info("Initializing Azure OpenAI Client")
        if not all([config.AZURE_OPENAI_API_KEY, config.AZURE_OPENAI_ENDPOINT, config.AZURE_OPENAI_API_VERSION]):
            raise ValueError("Azure OpenAI configuration missing (Key, Endpoint, or Version)")
            
        return AzureOpenAI(
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT
        )

    @staticmethod
    def get_embedding_function():
        """
        Returns the appropriate embedding function for ChromaDB.
        """
        # Always assume Azure OpenAI Embeddings
        logger.info("Initializing Azure OpenAI Embedding Function")
        if not all([config.AZURE_OPENAI_API_KEY, config.AZURE_OPENAI_ENDPOINT, config.AZURE_OPENAI_API_VERSION, config.AZURE_EMBEDDING_DEPLOYMENT_NAME]):
                raise ValueError("Azure OpenAI configuration missing for Embeddings (Key, Endpoint, Version, or Deployment Name)")

        return OpenAIEmbeddingFunction(
            api_key=config.AZURE_OPENAI_API_KEY,
            api_base=config.AZURE_OPENAI_ENDPOINT,
            api_type="azure",
            api_version=config.AZURE_OPENAI_API_VERSION,
            model_name=config.AZURE_EMBEDDING_DEPLOYMENT_NAME,
            deployment_id=config.AZURE_EMBEDDING_DEPLOYMENT_NAME
        )
