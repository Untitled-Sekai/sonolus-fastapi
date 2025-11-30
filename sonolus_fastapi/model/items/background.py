from pydantic import BaseModel
from typing import Optional, List
from ..base import SonolusResourceLocator
from ..common import Tag
from ..items import BaseItem

SRL = SonolusResourceLocator

class BackgroundItem(BaseItem):
    """BackgroundItemは背景の情報を提供"""
    version: int = 2
    subtitle: str
    thumbnail: SRL
    data: SRL
    image: SRL
    configuration: SRL
