from pydantic import BaseModel
from typing import Optional, List
from ..base import SonolusResourceLocator
from ..common import Tag
from ..items import BaseItem

SRL = SonolusResourceLocator

class PostItem(BaseItem):
    """PostItemはポストの情報を提供"""
    version: int = 1
    time: int  # タイムスタンプ
    thumbnail: Optional[SRL] = None
