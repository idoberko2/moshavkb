from typing import Protocol, List

class StorageProvider(Protocol):
    def save_file(self, file_data: bytes, filename: str) -> str:
        """
        Saves a file and returns its path or reference.
        """
        ...
        
    def list_files(self) -> List[str]:
        """
        Lists available files in the storage.
        """
        ...
