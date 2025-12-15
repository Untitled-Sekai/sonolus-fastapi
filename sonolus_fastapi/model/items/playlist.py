from pydantic import BaseModel
from typing import Optional, List, Any
from ..base import SonolusResourceLocator
from ..common import Tag
from ..items import BaseItem, PackBaseItem, LocalationText

SRL = SonolusResourceLocator

class PlaylistItem(BaseItem):
    """PlaylistItemはプレイリストの情報を提供"""
    version: int = 1
    subtitle: str
    levels: List[Any] = []  # LevelItemを参照、後で修正可能
    thumbnail: Optional[SRL] = None

class PlaylistPackItem(PackBaseItem):
    """PlaylistPackItemはパック内のプレイリストの情報を提供"""
    version: int = 1
    subtitle: LocalationText
    levels: List[str] = []  # level names
    thumbnail: Optional[SRL] = None
