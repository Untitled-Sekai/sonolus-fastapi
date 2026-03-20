from typing import Union
from sonolus_models import ItemType
from .leaderboard import LeaderboardRecordStore
from .leaderboard_memory import MemoryRecordStore
from .leaderboard_json import JsonRecordStore
from .leaderboard_database import DatabaseRecordStore

class ItemLeaderboardAccessor:
    """アイテムタイプごとのleaderboard recordsアクセサ"""
    
    def __init__(self, item_type: ItemType, record_store: LeaderboardRecordStore):
        self.item_type = item_type
        self.record_store = record_store
    
    def for_item(self, item_name: str, leaderboard_name: str) -> Union[MemoryRecordStore, JsonRecordStore, DatabaseRecordStore]:
        """特定アイテムのleaderboard recordsストアを返す"""
        return self.record_store.get_store(self.item_type, item_name, leaderboard_name)
