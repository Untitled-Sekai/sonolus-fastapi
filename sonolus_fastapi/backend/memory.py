from typing import Generic, TypeVar, Dict, List, Optional
from sonolus_fastapi.utils.source import strip_source_fields

T = TypeVar("T")

class MemoryItemStore(Generic[T]):
    def __init__(self, item_cls):
        self.item_cls = item_cls
        self._data: Dict[str, T] = {}
        
    def get(self, name: str) -> Optional[T]:
        return self._data.get(name)
    
    def list(self, limit: int = 20, offset: int = 0) -> List[T]:
        if limit > 20:
            limit = 20  # 最大20件に制限
            
        items = list(self._data.values())
        return items[offset:offset + limit]
    
    def add(self, item: T):
        item = strip_source_fields(item)
        self._data[item.name] = item
    
    def delete(self, name: str):
        self._data.pop(name, None)
    
    def update(self, item: T):
        item = strip_source_fields(item)
        self._data[item.name] = item
    
    def map(self) -> Dict[str, T]:
        return self._data.copy()
    
    def get_many(self, names: List[str]) -> List[T]:
        result = []
        for name in names:
            if name in self._data:
                result.append(self._data[name])
        return result