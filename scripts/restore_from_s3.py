import os
import sys
import shutil
import boto3
import tarfile
import logging
import argparse
from botocore.exceptions import ClientError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def restore_chroma_from_s3(backup_filename):
    # Configuration
    s3_bucket = os.getenv("S3_BACKUP_BUCKET_NAME")
    s3_region = os.getenv("S3_REGION_NAME")
    s3_endpoint = os.getenv("S3_ENDPOINT_URL")
    s3_access_key = os.getenv("S3_ACCESS_KEY_ID")
    s3_secret_key = os.getenv("S3_SECRET_ACCESS_KEY")
    
    # Paths
    # We assume this runs in the ingest-bot container where ./data is mounted to /app/data
    # So the chroma db data (on host ./data/chroma_db) is at /app/data/chroma_db
    chroma_data_dir = "/app/data/chroma_db"
    
    # If the provided filename is just a name, assume it's in the standard path
    # If it's a full key, use it. But our backups are in backups/chroma/
    if "/" not in backup_filename:
        s3_key = f"backups/chroma/{backup_filename}"
    else:
        s3_key = backup_filename
        
    local_download_path = f"/tmp/{os.path.basename(backup_filename)}"

    if not all([s3_bucket, s3_access_key, s3_secret_key]):
        logger.error("Missing S3 configuration environment variables.")
        return False

    s3_client = boto3.client(
        's3',
        endpoint_url=s3_endpoint,
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        region_name=s3_region
    )

    try:
        # 1. Download
        logger.info(f"Downloading {s3_key} from bucket {s3_bucket}...")
        try:
            s3_client.download_file(s3_bucket, s3_key, local_download_path)
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                logger.error(f"Backup file {s3_key} not found in bucket {s3_bucket}.")
            else:
                logger.error(f"Download failed: {e}")
            return False

        logger.info("Download complete.")

        # 2. Clear existing data
        if os.path.exists(chroma_data_dir):
            logger.info(f"Removing existing data at {chroma_data_dir}...")
            shutil.rmtree(chroma_data_dir)
        
        # 3. Extract
        logger.info(f"Extracting {local_download_path} to /app/data...")
        # The tar was created with arcname=os.path.basename(chroma_data_dir) -> "chroma_db"
        # So extracting it to /app/data/ will create /app/data/chroma_db
        # We need to verify if the tar contains the directory wrapper or just files.
        # scripts/backup_to_s3.py: tar.add(chroma_data_dir, arcname=os.path.basename(chroma_data_dir))
        # This acts as `tar -czf ... chroma_db/` so it includes the top level folder `chroma_db`.
        # So extracting to `/app/data` is correct to restore `/app/data/chroma_db`.
        
        parent_dir = os.path.dirname(chroma_data_dir) # /app/data
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        with tarfile.open(local_download_path, "r:gz") as tar:
            tar.extractall(path=parent_dir)
            
        logger.info("Restoration complete.")

        # 4. Cleanup
        os.remove(local_download_path)
        logger.info("Cleanup complete.")
        return True

    except Exception as e:
        logger.error(f"Restoration failed: {e}")
        if os.path.exists(local_download_path):
            os.remove(local_download_path)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore ChromaDB from S3 backup.")
    parser.add_argument("filename", help="The filename of the backup (e.g. chroma_backup_20240101.tar.gz)")
    args = parser.parse_args()
    
    if restore_chroma_from_s3(args.filename):
        sys.exit(0)
    else:
        sys.exit(1)
