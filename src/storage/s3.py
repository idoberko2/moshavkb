import logging
import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError
from botocore.config import Config as BotoConfig
from src.storage.interface import StorageProvider
from src.config import config

logger = logging.getLogger(__name__)

class S3Storage(StorageProvider):
    def __init__(self):
        self.bucket_name = config.S3_BUCKET_NAME
        self.region_name = config.S3_REGION_NAME
        
        # Check for credentials
        if not config.S3_ACCESS_KEY_ID or not config.S3_SECRET_ACCESS_KEY:
             logger.warning("S3 credentials not fully configured.")
             self.s3_client = None
        else:
            try:
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=config.S3_ENDPOINT_URL,
                    aws_access_key_id=config.S3_ACCESS_KEY_ID,
                    aws_secret_access_key=config.S3_SECRET_ACCESS_KEY,
                    region_name=self.region_name,
                    config=BotoConfig(
                        signature_version='s3v4',
                        retries={
                            'max_attempts': 10,
                            'mode': 'adaptive'
                        }
                    )
                )
                
                print(f"DEBUG: Initialized S3 Storage provider with adaptive retries.")
                logger.info(f"Initialized S3 Storage provider with adaptive retries.")
                logger.info(f"DEBUG: Using S3 Access Key: {config.S3_ACCESS_KEY_ID[:4]}***")
                
                # Ensure bucket exists (helpful for local MinIO)
                try:
                    self.s3_client.head_bucket(Bucket=self.bucket_name)
                    logger.info(f"Bucket '{self.bucket_name}' exists.")
                except ClientError:
                    logger.info(f"Bucket '{self.bucket_name}' not found. Creating...")
                    try:
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                        logger.info(f"Bucket '{self.bucket_name}' created successfully.")
                    except Exception as e:
                        logger.error(f"Failed to create bucket '{self.bucket_name}': {e}")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                self.s3_client = None

    def save_file(self, file_data: bytes, filename: str) -> str:
        if not self.s3_client:
            logger.error("S3 client not initialized.")
            return ""

        try:
            logger.info(f"Uploading {filename} to S3 bucket {self.bucket_name}...")
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=file_data
            )
            return filename
        except NoCredentialsError:
            logger.error("Credentials not available for S3 upload.")
            return ""
        except Exception as e:
            logger.error(f"Failed to upload {filename} to S3: {e}")
            return ""

    def list_files(self) -> list[str]:
        if not self.s3_client:
            return []
            
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            logger.error(f"Failed to list files from S3: {e}")
            return []

    def get_file_stream(self, filename: str):
        """
        Returns a streaming body for the S3 object
        """
        if not self.s3_client:
            return None

        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=filename)
            return response['Body']
        except ClientError as e:
            logger.error(f"Error getting file stream for {filename}: {e}")
            return None
