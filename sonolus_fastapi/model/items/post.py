from pydantic import BaseModel
from typing import Optional, List
from ..base import SonolusResourceLocator
from ..common import Tag
from ..items import BaseItem, PackBaseItem

SRL = SonolusResourceLocator

class PostItem(BaseItem):
    """PostItemはポストの情報を提供"""
    version: int = 1
    time: int  # タイムスタンプ
    thumbnail: Optional[SRL] = None

class PostPackItem(PackBaseItem):
    """PostPackItemはパック内のポストの情報を提供"""
    version: int = 1
    time: int
    thumbnail: Optional[SRL] = None
