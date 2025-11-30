from pydantic import BaseModel
from typing import Optional, List
from ..base import SonolusResourceLocator
from ..common import Tag
from ..items import BaseItem

SRL = SonolusResourceLocator

class ParticleItem(BaseItem):
    """ParticleItemはパーティクルの情報を提供"""
    version: int = 3
    subtitle: str
    thumbnail: SRL
    data: SRL
    texture: SRL
