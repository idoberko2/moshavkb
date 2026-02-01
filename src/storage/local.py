import os
from typing import List
from .interface import StorageProvider

class LocalStorage(StorageProvider):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def save_file(self, file_data: bytes, filename: str, content_type: str = None) -> str:
        filepath = os.path.join(self.base_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(file_data)
        return filepath

    def list_files(self) -> List[str]:
        return [f for f in os.listdir(self.base_dir) if os.path.isfile(os.path.join(self.base_dir, f))]

    def get_file_stream(self, filename: str):
        filepath = os.path.join(self.base_dir, filename)
        if os.path.exists(filepath):
            return open(filepath, 'rb')
        return None

    def get_metadata(self, filename: str) -> dict:
        # Local storage doesn't support metadata in this simple implementation
        return {}

    def update_metadata(self, filename: str, metadata: dict) -> None:
        # Local storage doesn't support metadata
        pass
