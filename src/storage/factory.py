from src.config import config
from src.storage.azure import AzureStorage
import logging

logger = logging.getLogger(__name__)

class StorageFactory:
    @staticmethod
    def get_storage_provider():
        """
        Returns the appropriate storage provider (Azure).
        """
        # Hardcoded to Azure as we removed S3 support
        logger.info("Initializing Azure Native Storage Provider")
        return AzureStorage()
