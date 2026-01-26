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
                    config=BotoConfig(signature_version='s3v4')
                )
                
                # Separate client for signing URLs (using public endpoint)
                # This works because generating presigned URLs is an offline operation
                self.signing_client = boto3.client(
                    's3',
                    endpoint_url=config.S3_PUBLIC_ENDPOINT_URL,
                    aws_access_key_id=config.S3_ACCESS_KEY_ID,
                    aws_secret_access_key=config.S3_SECRET_ACCESS_KEY,
                    region_name=self.region_name,
                    config=BotoConfig(signature_version='s3v4')
                )

                print(f"DEBUG: Initialized S3 Storage provider.")
                print(f"DEBUG: Internal Endpoint: {config.S3_ENDPOINT_URL}")
                print(f"DEBUG: Public Endpoint (for links): {config.S3_PUBLIC_ENDPOINT_URL}")
                
                logger.info(f"Initialized S3 Storage provider.")
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

    def get_file_link(self, filename: str, expiration=3600) -> str | None:
        """
        Generate a presigned URL to share an S3 object
        """
        # Use signing_client if available, else fallback to standard client
        client = getattr(self, 'signing_client', self.s3_client)
        
        if not client:
            return None

        try:
            url = client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name, 
                    'Key': filename
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL for {filename}: {e}")
            return None
