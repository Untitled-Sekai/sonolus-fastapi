from typing import Dict, List, Optional
from sonolus_models import ItemType, ServerItemLeaderboardRecord

class MemoryRecordStore:
    """メモリ上でleaderboard recordsを管理するストア"""
    
    def __init__(self, item_type: ItemType, item_name: str, leaderboard_name: str):
        self.item_type = item_type
        self.item_name = item_name
        self.leaderboard_name = leaderboard_name
        # record_name -> ServerItemLeaderboardRecord
        self._data: Dict[str, ServerItemLeaderboardRecord] = {}
    
    def get(self, record_name: str) -> Optional[ServerItemLeaderboardRecord]:
        return self._data.get(record_name)
    
    def list(self, limit: int = 10, offset: int = 0) -> List[ServerItemLeaderboardRecord]:
        if limit > 20:
            limit = 20
        
        items = list(self._data.values())
        # ランクでソート（数値として）
        items.sort(key=lambda x: int(x.rank) if x.rank.isdigit() else float('inf'))
        return items[offset:offset + limit]
    
    def add(self, record: ServerItemLeaderboardRecord):
        self._data[record.name] = record
    
    def delete(self, record_name: str):
        self._data.pop(record_name, None)
    
    def update(self, record: ServerItemLeaderboardRecord):
        self._data[record.name] = record
    
    def count(self) -> int:
        return len(self._data)
