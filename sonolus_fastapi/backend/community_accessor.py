from sonolus_models import ItemType
from .community import CommunityCommentStore

class ItemCommentAccessor:
    """アイテムタイプごとのコメントアクセサ"""
    
    def __init__(self, item_type: ItemType, comment_store: CommunityCommentStore):
        self.item_type = item_type
        self.comment_store = comment_store
    
    def for_item(self, item_name: str):
        """特定アイテムのコメントストアを返す"""
        return self.comment_store.get_store(self.item_type, item_name)
