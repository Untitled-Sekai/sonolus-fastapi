from typing import Dict, Tuple
from sonolus_models import ItemType
from .backend import StorageBackend
from .leaderboard_memory import MemoryRecordStore
from .leaderboard_json import JsonRecordStore
from .leaderboard_database import DatabaseRecordStore

class LeaderboardRecordStore:
    """アイテムごとのleaderboard recordsを管理する統合ストア"""
    
    def __init__(self, backend: StorageBackend, **options):
        self.backend = backend
        self.options = options
        
        # Memory バックエンドの場合、全データをここに保持
        if backend == StorageBackend.MEMORY:
            self._memory_data: Dict[Tuple[ItemType, str, str], MemoryRecordStore] = {}
        else:
            self._stores: Dict[Tuple[ItemType, str, str], object] = {}
    
    def get_store(self, item_type: ItemType, item_name: str, leaderboard_name: str):
        """特定アイテムのleaderboard recordsストアを取得"""
        key = (item_type, item_name, leaderboard_name)
        
        if self.backend == StorageBackend.MEMORY:
            if key not in self._memory_data:
                self._memory_data[key] = MemoryRecordStore(item_type, item_name, leaderboard_name)
            return self._memory_data[key]
        
        # JSON/Database の場合、都度作成（軽量なので問題ない）
        if key not in self._stores:
            self._stores[key] = self._create_store(item_type, item_name, leaderboard_name)
        return self._stores[key]
    
    def _create_store(self, item_type: ItemType, item_name: str, leaderboard_name: str):
        if self.backend == StorageBackend.JSON:
            path = self.options.get("path", "./data")
            return JsonRecordStore(item_type, item_name, leaderboard_name, path)
        elif self.backend == StorageBackend.DATABASE:
            url = self.options.get("url", "sqlite:///./data/database.db")
            return DatabaseRecordStore(item_type, item_name, leaderboard_name, url)
        
        raise ValueError(f"Unsupported backend: {self.backend}")
