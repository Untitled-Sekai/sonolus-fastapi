from typing import Dict, List, Optional
from sonolus_models import ItemType, ServerItemCommunityComment

class MemoryCommentStore:
    """メモリ上でコメントを管理するストア"""
    
    def __init__(self, item_type: ItemType, item_name: str):
        self.item_type = item_type
        self.item_name = item_name
        # comment_name -> ServerItemCommunityComment
        self._data: Dict[str, ServerItemCommunityComment] = {}
    
    def get(self, comment_name: str) -> Optional[ServerItemCommunityComment]:
        return self._data.get(comment_name)
    
    def list(self, limit: int = 10, offset: int = 0) -> List[ServerItemCommunityComment]:
        if limit > 20:
            limit = 20
        
        items = list(self._data.values())
        # 時間でソート（新しい順）
        items.sort(key=lambda x: x.time, reverse=True)
        return items[offset:offset + limit]
    
    def add(self, comment: ServerItemCommunityComment):
        self._data[comment.name] = comment
    
    def delete(self, comment_name: str):
        self._data.pop(comment_name, None)
    
    def update(self, comment: ServerItemCommunityComment):
        self._data[comment.name] = comment
    
    def count(self) -> int:
        return len(self._data)
