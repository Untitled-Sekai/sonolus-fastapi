from .backend import StorageBackend
from .memory import MemoryItemStore
from .json import JsonItemStore
from .database import DatabaseItemStore
from typing import TypeVar, Any, Type, Union

T = TypeVar("T")

class StoreFactory:
    """Factory for creating item stores with different backends."""
    
    def __init__(self, backend: StorageBackend, **options: Any) -> None:
        """Initialize StoreFactory.
        
        Args:
            backend: Storage backend type
            **options: Backend-specific options (e.g., path for JSON, url for DATABASE)
        """
        self.backend: StorageBackend = backend
        self.options: dict[str, Any] = options
        
    def create(self, item_cls: Type[T]) -> Union[MemoryItemStore, "JsonItemStore", "DatabaseItemStore"]:
        """Create an item store of the specified type.
        
        Args:
            item_cls: Item class to create store for
            
        Returns:
            Instance of MemoryItemStore, JsonItemStore, or DatabaseItemStore
            
        Raises:
            ValueError: If backend is not supported
        """
        if self.backend == StorageBackend.MEMORY:
            return MemoryItemStore(item_cls)
        elif self.backend == StorageBackend.JSON:
            return JsonItemStore(item_cls, path=self.options.get("path", "./data"))
        elif self.backend == StorageBackend.DATABASE:
            from .database import DatabaseItemStore

            return DatabaseItemStore(item_cls, url=self.options.get("url", "sqlite:///./data/database.db"))
        
        raise ValueError(f"Unsupported storage backend: {self.backend}")