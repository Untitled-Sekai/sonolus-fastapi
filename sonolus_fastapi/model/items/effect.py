from pydantic import BaseModel
from typing import Optional, List
from ..base import SonolusResourceLocator
from ..common import Tag
from ..items import BaseItem

SRL = SonolusResourceLocator

class EffectItem(BaseItem):
    """EffectItemはエフェクトの情報を提供"""
    version: int = 5
    subtitle: str
    thumbnail: SRL
    data: SRL
    audio: SRL
