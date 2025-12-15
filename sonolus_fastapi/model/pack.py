from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from .items.background import BackgroundPackItem
from .items.skin import SkinPackItem
from .items.effect import EffectPackItem
from .items.particle import ParticlePackItem
from .items.level import LevelPackItem
from .items.post import PostPackItem
from .items.playlist import PlaylistPackItem

class DbInfo(BaseModel):
    """
    packのinfoに相当するモデル
    """
    title: Dict[str, str]
    subtitle: Optional[Dict[str, str]] = None
    author: Optional[Dict[str, str]] = None
    description: Optional[Dict[str, str]] = None
    
class PackModel(BaseModel):
    """
    パックモデル
    """
    info: DbInfo
    skins: List[SkinPackItem] = []
    backgrounds: List[BackgroundPackItem] = []
    effects: List[EffectPackItem] = []
    particles: List[ParticlePackItem] = []
    levels: List[LevelPackItem] = []
    posts: List[PostPackItem] = []
    playlists: List[PlaylistPackItem] = []