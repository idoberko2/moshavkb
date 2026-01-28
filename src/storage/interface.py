from abc import ABC, abstractmethod
from typing import Optional, List, BinaryIO

class StorageProvider(ABC):
    @abstractmethod
    def save_file(self, file_data: bytes, filename: str) -> str:
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
