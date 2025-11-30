from pydantic import BaseModel
from typing import Optional, List
from ..base import SonolusResourceLocator
from ..common import Tag
from ..items import BaseItem
from ..items.level import LevelItem

SRL = SonolusResourceLocator

class ReplayItem(BaseItem):
    """ReplayItemはリプレイの情報を提供"""
    version: int = 1
    subtitle: str
    level: LevelItem
    data: SRL
    configuration: SRL
