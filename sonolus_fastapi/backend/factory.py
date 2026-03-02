from .backend import StorageBackend
from .memory import MemoryItemStore
from .json import JsonItemStore
from typing import TypeVar

T = TypeVar("T")

class StoreFactory:
    def __init__(self, backend: StorageBackend, **options):
        """
        Args:
            backend: ストレージバックエンド Storage backend
        """
        self.backend = backend
        self.options = options
        
    def create(self, item_cls: T) -> T:
        if self.backend == StorageBackend.MEMORY:
            return MemoryItemStore(item_cls)
        elif self.backend == StorageBackend.JSON:
            return JsonItemStore(item_cls, path=self.options.get("path", "./data"))
        elif self.backend == StorageBackend.DATABASE:
            from .database import DatabaseItemStore

            return DatabaseItemStore(item_cls, url=self.options.get("url", "sqlite:///./data/database.db"))
        
        raise ValueError(f"Unsupported storage backend: {self.backend}")