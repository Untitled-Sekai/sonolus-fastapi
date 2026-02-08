import json
import os
from typing import Dict, List, Optional
from sonolus_models import ItemType, ServerItemLeaderboardRecord

class JsonRecordStore:
    """JSONファイルでleaderboard recordsを管理するストア"""
    
    def __init__(self, item_type: ItemType, item_name: str, leaderboard_name: str, base_path: str = "./data"):
        self.item_type = item_type
        self.item_name = item_name
        self.leaderboard_name = leaderboard_name
        self.base_path = base_path
        
        # ディレクトリ構造: data/leaderboards/{item_type}/{item_name}/{leaderboard_name}.json
        self.dir_path = os.path.join(base_path, "leaderboards", item_type.value, item_name)
        os.makedirs(self.dir_path, exist_ok=True)
        
        self.file_path = os.path.join(self.dir_path, f"{leaderboard_name}.json")
        self._data: Dict[str, dict] = {}
        
        self._load()
    
    def _load(self):
        """ファイルからデータを読み込む"""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
    
    def _save(self):
        """ファイルにデータを保存"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
    
    def get(self, record_name: str) -> Optional[ServerItemLeaderboardRecord]:
        raw = self._data.get(record_name)
        if raw is None:
            return None
        return ServerItemLeaderboardRecord.model_validate(raw)
    
    def list(self, limit: int = 10, offset: int = 0) -> List[ServerItemLeaderboardRecord]:
        if limit > 20:
            limit = 20
        
        records = [
            ServerItemLeaderboardRecord.model_validate(v)
            for v in self._data.values()
        ]
        # ランクでソート（数値として）
        records.sort(key=lambda x: int(x.rank) if x.rank.isdigit() else float('inf'))
        return records[offset:offset + limit]
    
    def add(self, record: ServerItemLeaderboardRecord):
        self._data[record.name] = record.model_dump()
        self._save()
    
    def delete(self, record_name: str):
        if record_name in self._data:
            del self._data[record_name]
            self._save()
    
    def update(self, record: ServerItemLeaderboardRecord):
        self._data[record.name] = record.model_dump()
        self._save()
    
    def count(self) -> int:
        return len(self._data)
