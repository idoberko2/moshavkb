from src.config import config
from src.storage.interface import StorageProvider
import logging
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from io import BytesIO

logger = logging.getLogger(__name__)

class AzureStorage(StorageProvider):
    def __init__(self):
        self.connection_string = config.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = config.AZURE_CONTAINER_NAME
        
        self.blob_service_client = None
        self.container_client = None

        if not self.connection_string:
            logger.warning("Azure Storage Connection String not configured.")
            return

        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Ensure container exists
            try:
                self.container_client.create_container()
                logger.info(f"Container '{self.container_name}' created.")
            except ResourceExistsError:
                logger.info(f"Container '{self.container_name}' exists.")
                
            logger.info("Initialized Azure Storage Provider.")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure Storage: {e}")
            self.blob_service_client = None

    def save_file(self, file_data: bytes, filename: str) -> str:
        if not self.container_client:
            logger.error("Azure container client not initialized.")
            return ""

        try:
            # Convert bytearray to bytes if needed, or wrap in BytesIO
            if isinstance(file_data, bytearray):
                file_data = bytes(file_data)
            
            blob_client = self.container_client.get_blob_client(filename)
            logger.info(f"Uploading {filename} to Azure container {self.container_name}...")
            blob_client.upload_blob(file_data, overwrite=True)
            return filename
        except Exception as e:
            logger.error(f"Failed to upload {filename} to Azure: {e}")
            raise e

    def list_files(self) -> list[str]:
        if not self.container_client:
            return []
            
        try:
            blob_list = self.container_client.list_blobs()
            return [blob.name for blob in blob_list]
        except Exception as e:
            logger.error(f"Failed to list files from Azure: {e}")
            return []

    def get_file_stream(self, filename: str):
        if not self.container_client:
            return None
        
        try:
             blob_client = self.container_client.get_blob_client(filename)
             data = blob_client.download_blob().readall()
             return BytesIO(data)
        except Exception as e:
            logger.error(f"Error getting file stream for {filename}: {e}")
            return None
