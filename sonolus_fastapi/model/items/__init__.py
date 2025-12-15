from pydantic import BaseModel
from typing import Optional, List
from ..base import SonolusResourceLocator
from ..common import Tag
from enum import Enum

SRL = SonolusResourceLocator

class LocalationText(BaseModel):
    ja: Optional[str] = None
    en: Optional[str] = None
    zh: Optional[str] = None

class BaseItem(BaseModel):
    """全てのアイテムの基底クラス"""
    name: str
    source: Optional[str] = None
    title: str
    author: str
    tags: List[Tag] = []
    description: str = ""

class PackBaseItem(BaseItem):
    """パック内の全てのアイテムの基底クラス"""
    name: str
    source: Optional[SRL] = None
    title: LocalationText
    author: LocalationText
    tags: List[Tag] = []
    description: LocalationText = LocalationText()

class ItemType(str, Enum):
    background = "backgrounds"
    effect = "effects"
    engine = "engines"
    level = "levels"
    particle = "particles"
    post = "posts"
    replay = "replays"
    skin = "skins"