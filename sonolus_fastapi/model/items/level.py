from pydantic import BaseModel
from typing import Optional, List, Union, Any
from ..base import SonolusResourceLocator
from ..common import Tag
from ..items import BaseItem, PackBaseItem, LocalationText
from ..items.engine import EngineItem
from ..items.skin import SkinItem
from ..items.background import BackgroundItem
from ..items.effect import EffectItem
from ..items.particle import ParticleItem

SRL = SonolusResourceLocator

class LevelItem(BaseItem):
    """LevelItemはレベルの情報を提供"""
    version: int = 1
    rating: float
    artists: str
    engine: EngineItem
    useSkin: Any  # Union[UseItemDefault, UseItemCustom[SkinItem]]
    useBackground: Any  # Union[UseItemDefault, UseItemCustom[BackgroundItem]]
    useEffect: Any  # Union[UseItemDefault, UseItemCustom[EffectItem]]
    useParticle: Any  # Union[UseItemDefault, UseItemCustom[ParticleItem]]
    cover: SRL
    bgm: SRL
    preview: Optional[SRL] = None
    data: SRL

class LevelPackItem(PackBaseItem):
    """LevelPackItemはパック内のレベルの情報を提供"""
    version: int = 1
    rating: float
    artists: LocalationText
    engine: str  # engine name
    useSkin: Any
    useBackground: Any
    useEffect: Any
    useParticle: Any
    cover: SRL
    bgm: SRL
    preview: Optional[SRL] = None
    data: SRL
