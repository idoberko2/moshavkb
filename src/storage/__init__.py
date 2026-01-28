from src.storage.factory import StorageFactory

# Backwards compatibility: exposes 's3_client' (which is actually a provider now)
# Ideally consumers should call StorageFactory.get_storage_provider()
# But let's check current usages.
# Existing consumers likely import 's3' or 'S3Storage'.

storage_provider = StorageFactory.get_storage_provider()
