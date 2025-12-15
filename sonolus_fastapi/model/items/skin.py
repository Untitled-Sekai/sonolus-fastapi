from pydantic import BaseModel
from typing import Optional, List
from ..base import SonolusResourceLocator
from ..common import Tag
from ..items import BaseItem, PackBaseItem
from ..items import LocalationText

SRL = SonolusResourceLocator

class SkinItem(BaseItem):
    """SkinItemはスキンの情報を提供"""
    version: int = 4
    subtitle: str
    thumbnail: SRL
    data: SRL
    texture: SRL

class SkinPackItem(PackBaseItem):
    """SkinPackItemはパック内のスキンの情報を提供"""
    version: int = 4
    subtitle: LocalationText
    thumbnail: SRL
    data: SRL
    texture: SRL