import json
import os
from typing import Dict, List, Optional
from sonolus_models import ItemType, ServerItemCommunityComment
from .result import ListResult

class JsonCommentStore:
    """JSONファイルでコメントを管理するストア"""
    
    def __init__(self, item_type: ItemType, item_name: str, base_path: str = "./data"):
        self.item_type = item_type
        self.item_name = item_name
        self.base_path = base_path
        
        # ディレクトリ構造: data/comments/{item_type}/{item_name}.json
        self.dir_path = os.path.join(base_path, "comments", item_type.value)
        os.makedirs(self.dir_path, exist_ok=True)
        
        self.file_path = os.path.join(self.dir_path, f"{item_name}.json")
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
    
    def get(self, comment_name: str) -> Optional[ServerItemCommunityComment]:
        raw = self._data.get(comment_name)
        if raw is None:
            return None
        return ServerItemCommunityComment.model_validate(raw)
    
    def list(self, limit: int = 10, offset: int = 0) -> ListResult[ServerItemCommunityComment]:
        if limit > 20:
            limit = 20
        
        all_comments = [
            ServerItemCommunityComment.model_validate(v)
            for v in self._data.values()
        ]
        # 時間でソート（新しい順）
        all_comments.sort(key=lambda x: x.time, reverse=True)
        total_count = len(all_comments)
        comments = all_comments[offset:offset + limit]
        
        return ListResult(
            items=comments,
            total_count=total_count,
            limit=limit,
            offset=offset
        )
    
    def add(self, comment: ServerItemCommunityComment):
        self._data[comment.name] = comment.model_dump()
        self._save()
    
    def delete(self, comment_name: str):
        if comment_name in self._data:
            del self._data[comment_name]
            self._save()
    
    def update(self, comment: ServerItemCommunityComment):
        self._data[comment.name] = comment.model_dump()
        self._save()
    
    def count(self) -> int:
        return len(self._data)
