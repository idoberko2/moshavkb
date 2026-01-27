import os
import shutil
import datetime
import boto3
import tarfile
import logging
from botocore.exceptions import ClientError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_chroma_to_s3():
    # Configuration
    s3_bucket = os.getenv("S3_BACKUP_BUCKET_NAME")
    s3_region = os.getenv("S3_REGION_NAME")
    s3_endpoint = os.getenv("S3_ENDPOINT_URL")
    s3_access_key = os.getenv("S3_ACCESS_KEY_ID")
    s3_secret_key = os.getenv("S3_SECRET_ACCESS_KEY")
    
    # ChromaDB data path (mounted in container)
    # The docker-compose mounts ./data/chroma_db:/data, but the bots mount ./data:/app/data
    # However, the bots do NOT have access to the chroma-db volume content directly unless we mount it.
    # The plan says: "run via docker compose run ... ingest-bot".
    # ingest-bot mounts `./data:/app/data`.
    # And chroma-db mounts `./data/chroma_db:/data`.
    # So from the perspective of ingest-bot running inside the container:
    # `/app/data/chroma_db` is where the data should be visible IF the host directory is shared.
    # Let's verify the mount paths in docker-compose.prod.yml:
    # ingest-bot: ./data:/app/data
    # chroma-db: ./data/chroma_db:/data
    # So yes, inside ingest-bot, /app/data/chroma_db corresponds to the chroma data.
    
    chroma_data_dir = "/app/data/chroma_db"
    backup_filename = f"chroma_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
    local_backup_path = f"/tmp/{backup_filename}"
    s3_backup_key = f"backups/chroma/{backup_filename}"

    if not all([s3_bucket, s3_access_key, s3_secret_key]):
        logger.error("Missing S3 configuration environment variables.")
        return

    # Check if directory exists
    if not os.path.exists(chroma_data_dir):
        logger.error(f"Chroma data directory not found at {chroma_data_dir}")
        return

    try:
        # 1. Compress the directory
        logger.info(f"Compressing {chroma_data_dir} to {local_backup_path}...")
        with tarfile.open(local_backup_path, "w:gz") as tar:
            tar.add(chroma_data_dir, arcname=os.path.basename(chroma_data_dir))
        
        # 2. Upload to S3
        logger.info(f"Uploading to S3 bucket {s3_bucket} key {s3_backup_key}...")
        
        s3_client = boto3.client(
            's3',
            endpoint_url=s3_endpoint,
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key,
            region_name=s3_region
        )
        
        s3_client.upload_file(local_backup_path, s3_bucket, s3_backup_key)
        logger.info("Backup uploaded successfully.")

        # 3. Cleanup
        os.remove(local_backup_path)
        logger.info("Local backup file removed.")

    except Exception as e:
        logger.error(f"Backup failed: {e}")
        # Try to cleanup if failed
        if os.path.exists(local_backup_path):
            os.remove(local_backup_path)

if __name__ == "__main__":
    backup_chroma_to_s3()
