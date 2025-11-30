from pydantic import BaseModel
from typing import Optional, List
from ..base import SonolusResourceLocator
from ..common import Tag
from ..items import BaseItem
from ..items.skin import SkinItem
from ..items.background import BackgroundItem
from ..items.effect import EffectItem
from ..items.particle import ParticleItem

SRL = SonolusResourceLocator

class EngineItem(BaseItem):
    """EngineItemはエンジンの情報を提供"""
    version: int = 13
    subtitle: str
    skin: SkinItem  # エンジンで使用するデフォルトスキン
    background: BackgroundItem  # エンジンで使用するデフォルト背景
    effect: EffectItem  # エンジンで使用するデフォルトエフェクト
    particle: ParticleItem  # エンジンで使用するデフォルトパーティクル
    thumbnail: SRL
    playData: SRL
    watchData: SRL
    previewData: SRL
    tutorialData: SRL
    rom: Optional[SRL] = None
    configuration: SRL
