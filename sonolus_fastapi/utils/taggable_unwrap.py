"""
TaggableItem のアンラップおよび Pydantic 統合
"""
from typing import Any, Optional
from sonolus_fastapi.utils.taggable_item import TaggableItem


def unwrap_taggable_item(item: Any) -> Any:
    """
    TaggableItem をアンラップして、内部の実際のアイテムを返す。
    
    Args:
        item: TaggableItem またはその他のアイテム
        
    Returns:
        アンラップされた実際のアイテム、または元のアイテム
    """
    if item is None:
        return None
    
    if isinstance(item, TaggableItem):
        return object.__getattribute__(item, "_item")
    
    return item


def is_taggable_item(item: Any) -> bool:
    """
    指定されたアイテムが TaggableItem であるかチェック。
    
    Args:
        item: チェック対象のアイテム
        
    Returns:
        True if TaggableItem, False otherwise
    """
    return isinstance(item, TaggableItem)


__all__ = ["unwrap_taggable_item", "is_taggable_item"]
