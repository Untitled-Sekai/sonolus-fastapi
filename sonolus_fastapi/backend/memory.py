from typing import Generic, TypeVar, Dict, List, Optional, Union
from sonolus_fastapi.utils.source import strip_source_fields
from sonolus_fastapi.utils.taggable_item import TaggableItem, unwrap_taggable_item
from .result import ListResult

T = TypeVar("T")

class MemoryItemStore(Generic[T]):
    def __init__(self, item_cls):
        self.item_cls = item_cls
        self._data: Dict[str, T] = {}
        
    def get(self, name: str) -> Optional[Union[T, TaggableItem[T]]]:
        item = self._data.get(name)
        if item is None:
            return None
        return TaggableItem(item)
    
    def list(self, limit: int = 20, offset: int = 0) -> ListResult[T]:
        if limit > 20:
            limit = 20  # 最大20件に制限
        
        all_items = list(self._data.values())
        total_count = len(all_items)
        items = all_items[offset:offset + limit]
        
        # Wrap items with TaggableItem for consistency with get()
        wrapped_items = [TaggableItem(item) for item in items]
        
        return ListResult(
            items=wrapped_items,
            total_count=total_count,
            limit=limit,
            offset=offset
        )
    
    def add(self, item: T):
        item = unwrap_taggable_item(item)
        item = strip_source_fields(item)
        self._data[item.name] = item
    
    def delete(self, name: str):
        self._data.pop(name, None)
    
    def update(self, item: T):
        item = unwrap_taggable_item(item)
        item = strip_source_fields(item)
        self._data[item.name] = item
    
    def map(self) -> Dict[str, T]:
        # Wrap items with TaggableItem for consistency with get()
        return {name: TaggableItem(item) for name, item in self._data.items()}
    
    def get_many(self, names: List[str]) -> List[T]:
        result = []
        for name in names:
            if name in self._data:
                # Wrap items with TaggableItem for consistency with get()
                result.append(TaggableItem(self._data[name]))
        return result