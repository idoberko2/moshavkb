import os
import shutil
import datetime
import tarfile
import logging
from src.config import config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_chroma():
    # ChromaDB data path (mounted in container at /app/data/chroma_db)
    # Ensure this matches docker-compose mount
    chroma_data_dir = "/app/data/chroma_db"
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"chroma_backup_{timestamp}.tar.gz"
    local_archive_path = f"/tmp/{backup_filename}"
    
    # Remote path (folder/filename)
    remote_path = f"backups/chroma/{backup_filename}"

    # Initialize Storage Provider
    try:
        # use Azure Storage
        from src.storage.azure import AzureStorage
        storage = AzureStorage(container_name=config.AZURE_BACKUP_CONTAINER_NAME)
    except Exception as e:
        logger.error(f"Failed to initialize storage provider: {e}")
        return

    # Check if directory exists
    if not os.path.exists(chroma_data_dir):
        logger.error(f"Chroma data directory not found at {chroma_data_dir}")
        return

    try:
        # 1. Compress the directory
        logger.info(f"Compressing {chroma_data_dir} to {local_archive_path}...")
        with tarfile.open(local_archive_path, "w:gz") as tar:
            tar.add(chroma_data_dir, arcname=os.path.basename(chroma_data_dir))
        
        # 2. Read and Upload
        logger.info(f"Uploading to Azure storage at {remote_path}...")
        
        # Note: Reading entire file into memory. 
        # For very large backups, we should extend StorageProvider to support file_path upload.
        with open(local_archive_path, "rb") as f:
            file_data = f.read()
            
        # The save_file method in our interface takes specific filename, 
        # but for Azure/S3 it often treats it as a key.
        # Let's verify if 'save_file' implementation handles paths.
        # Azure: blob_client = container_client.get_blob_client(filename) -> handles paths ok.
        # S3: s3_client.put_object(..., Key=filename) -> handles paths ok.
        
        storage.save_file(file_data, remote_path)
        logger.info(f"Backup uploaded successfully to {remote_path}")

        # 3. Cleanup
        if os.path.exists(local_archive_path):
            os.remove(local_archive_path)
            logger.info("Local backup file removed.")

    except Exception as e:
        logger.error(f"Backup failed: {e}")
        # Try to cleanup if failed
        if os.path.exists(local_archive_path):
            os.remove(local_archive_path)

if __name__ == "__main__":
    backup_chroma()
