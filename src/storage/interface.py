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

    def get_file_stream(self, filename: str):
        """
        Returns a file-like object (stream) for the file, or None if not found.
        The caller is responsible for closing the stream.
        """
        ...
