from pydantic import BaseModel
from typing import Optional, List
from ..base import SonolusResourceLocator
from ..common import Tag
from ..items import BaseItem, PackBaseItem
from ..items import LocalationText

SRL = SonolusResourceLocator

class BackgroundItem(BaseItem):
    """BackgroundItemは背景の情報を提供"""
    version: int = 2
    subtitle: str
    thumbnail: SRL
    data: SRL
    image: SRL
    configuration: SRL

class BackgroundPackItem(PackBaseItem):
    """BackgroundPackItemはパック内の背景の情報を提供"""
    version: int = 2
    subtitle: LocalationText
    thumbnail: SRL
    data: SRL
    image: SRL
    configuration: SRL