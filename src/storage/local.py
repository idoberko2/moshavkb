import os
from typing import List
from .interface import StorageProvider

class LocalStorage(StorageProvider):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def save_file(self, file_data: bytes, filename: str) -> str:
        filepath = os.path.join(self.base_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(file_data)
        return filepath

    def list_files(self) -> List[str]:
        files = []
        for root, _, filenames in os.walk(self.base_dir):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files
