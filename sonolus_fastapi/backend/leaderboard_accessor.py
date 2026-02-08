from sonolus_models import ItemType
from .leaderboard import LeaderboardRecordStore

class ItemLeaderboardAccessor:
    """アイテムタイプごとのleaderboard recordsアクセサ"""
    
    def __init__(self, item_type: ItemType, record_store: LeaderboardRecordStore):
        self.item_type = item_type
        self.record_store = record_store
    
    def for_item(self, item_name: str, leaderboard_name: str):
        """特定アイテムのleaderboard recordsストアを返す"""
        return self.record_store.get_store(self.item_type, item_name, leaderboard_name)
