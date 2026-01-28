from src.config import config
from src.storage.s3 import S3Storage
import logging

logger = logging.getLogger(__name__)

class StorageFactory:
    @staticmethod
    def get_storage_provider():
        """
        Returns the appropriate storage provider (S3 or Azure) based on config.
        """
        provider = getattr(config, "STORAGE_PROVIDER", "s3").lower()
        
        if provider == "azure":
            logger.info("Initializing Azure Native Storage Provider")
            from src.storage.azure import AzureStorage
            return AzureStorage()
        else:
            logger.info("Initializing S3 Storage Provider (Default)")
            return S3Storage()
