from pydantic import BaseModel
from typing import Optional, List
from ..base import SonolusResourceLocator
from ..common import Tag

SRL = SonolusResourceLocator

class BaseItem(BaseModel):
    """全てのアイテムの基底クラス"""
    name: str
    source: Optional[str] = None
    title: str
    author: str
    tags: List[Tag] = []
    description: str = ""
