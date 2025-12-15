from pydantic import BaseModel
from typing import Optional, List
from ..base import SonolusResourceLocator
from ..common import Tag
from ..items import BaseItem, PackBaseItem
from ..items import LocalationText

SRL = SonolusResourceLocator

class ParticleItem(BaseItem):
    """ParticleItemはパーティクルの情報を提供"""
    version: int = 3
    subtitle: str
    thumbnail: SRL
    data: SRL
    texture: SRL

class ParticlePackItem(PackBaseItem):
    """ParticlePackItemはパック内のパーティクルの情報を提供"""
    version: int = 3
    subtitle: LocalationText
    thumbnail: SRL
    data: SRL
    texture: SRL