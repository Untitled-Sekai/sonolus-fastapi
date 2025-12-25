import json
import os
from typing import TypeVar, Generic, Dict, List, Optional

T = TypeVar("T")

class JsonItemStore(Generic[T]):
    def __init__(self, item_cls, path: str = "./data"):
        self.item_cls = item_cls
        self.path = path
        os.makedirs(self.path, exist_ok=True)
        
        self.file = os.path.join(path, f"{item_cls.__name__.lower()}.json")
        self._data: Dict[str, dict] = {}
        
        self._load()
        
    def _load(self):
        if os.path.exists(self.file):
            with open(self.file, "r", encoding="utf-8") as f:
                self._data = json.load(f)
                
    def _save(self):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
                
    def get(self, name: str) -> Optional[T]:
        raw = self._data.get(name)
        if raw is None:
            return None
        
        return self.item_cls.model_validate(raw)
    
    def list(self, limit: int = 20, offset: int = 0) -> List[T]:
        items = [
            self.item_cls.model_validate(v)
            for v in self._data.values()
        ]
        return items[offset:offset + limit]
        
    def add(self, item: T):
        self._data[item.name] = item.model_dump()
        self._save()
        
    def delete(self, name: str):
        if name in self._data:
            del self._data[name]
            self._save()
        else:
            pass
    
    def update(self, item: T):
        self._data[item.name] = item.model_dump()
        self._save()
    
    def map(self) -> Dict[str, T]:
        return {
            name: self.item_cls.model_validate(data)
            for name, data in self._data.items()
        }
    
    def get_many(self, names: List[str]) -> List[T]:
        result = []
        for name in names:
            if name in self._data:
                result.append(self.item_cls.model_validate(self._data[name]))
        return result