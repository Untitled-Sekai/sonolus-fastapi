from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from .items.background import BackgroundPackItem
from .items.skin import SkinPackItem
from .items.effect import EffectPackItem
from .items.particle import ParticlePackItem

class DbInfo(BaseModel):
    """
    packのinfoに相当するモデル
    """
    title: str
    
class PackModel(BaseModel):
    """
    パックモデル
    """
    info: DbInfo
    skins: List[SkinPackItem] = []
    backgrounds: List[BackgroundPackItem] = []
    effects: List[EffectPackItem] = []
    particles: List[ParticlePackItem] = []