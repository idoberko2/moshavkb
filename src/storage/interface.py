from abc import ABC, abstractmethod
from typing import Optional, List, BinaryIO

class StorageProvider(ABC):
    @abstractmethod
    def save_file(self, file_data: bytes, filename: str, content_type: str = None) -> str:
        """Saves a file and returns its identifier/key"""
        pass

    @abstractmethod
    def list_files(self) -> List[str]:
        """Returns a list of file keys in storage"""
        pass
    
    @abstractmethod
    def get_file_stream(self, filename: str) -> Optional[BinaryIO]:
        """Returns a stream of the file content"""
        pass

    @abstractmethod
    def get_metadata(self, filename: str) -> dict:
        """Returns the metadata of the file"""
        pass

    @abstractmethod
    def update_metadata(self, filename: str, metadata: dict) -> None:
        """Updates the metadata of the file"""
        pass
