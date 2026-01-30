import os
import sys
import shutil
import tarfile
import logging
import argparse
from src.storage.factory import StorageFactory
from src.config import config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def restore_chroma(backup_filename):
    # Paths
    chroma_data_dir = "/app/data/chroma_db"
    
    # Resolve remote path
    if "/" not in backup_filename:
        remote_path = f"backups/chroma/{backup_filename}"
    else:
        remote_path = backup_filename
        
    logger.info(f"Preparing to restore from {remote_path}...")

    # Initialize Storage Provider
    try:
        if config.STORAGE_PROVIDER == "azure":
             from src.storage.azure import AzureStorage
             storage = AzureStorage(container_name=config.AZURE_BACKUP_CONTAINER_NAME)
        else:
             storage = StorageFactory.get_storage_provider()
    except Exception as e:
        logger.error(f"Failed to initialize storage provider: {e}")
        return False

    try:
        # 1. Get Backup Stream
        logger.info(f"Downloading backup stream from {remote_path}...")
        file_stream = storage.get_file_stream(remote_path)
        
        if not file_stream:
            logger.error(f"Failed to retrieve backup file: {remote_path}")
            return False

        # 2. Clear existing data
        if os.path.exists(chroma_data_dir):
            logger.info(f"Removing existing data at {chroma_data_dir}...")
            shutil.rmtree(chroma_data_dir)
        
        # 3. Extract
        logger.info(f"Extracting to /app/data...")
        parent_dir = os.path.dirname(chroma_data_dir) # /app/data
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        # file_stream is a BytesIO object (or similar file-like object)
        with tarfile.open(fileobj=file_stream, mode="r:gz") as tar:
            tar.extractall(path=parent_dir)
            
        logger.info("Restoration complete.")
        return True

    except Exception as e:
        logger.error(f"Restoration failed: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore ChromaDB from backup.")
    parser.add_argument("filename", help="The filename of the backup (e.g. chroma_backup_20240101.tar.gz)")
    args = parser.parse_args()
    
    if restore_chroma(args.filename):
        sys.exit(0)
    else:
        sys.exit(1)
