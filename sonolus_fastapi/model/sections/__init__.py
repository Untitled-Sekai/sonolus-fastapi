from typing import Union
from ..sections.base import ServerItemSectionTyped
from ..items.post import PostItem
from ..items.playlist import PlaylistItem
from ..items.level import LevelItem
from ..items.skin import SkinItem
from ..items.background import BackgroundItem
from ..items.effect import EffectItem
from ..items.particle import ParticleItem
from ..items.engine import EngineItem
from ..items.replay import ReplayItem

# 各アイテムタイプ用のセクション定義
class PostSection(ServerItemSectionTyped[PostItem]):
    itemType: str = 'post'

class PlaylistSection(ServerItemSectionTyped[PlaylistItem]):
    itemType: str = 'playlist'

class LevelSection(ServerItemSectionTyped[LevelItem]):
    itemType: str = 'level'

class SkinSection(ServerItemSectionTyped[SkinItem]):
    itemType: str = 'skin'

class BackgroundSection(ServerItemSectionTyped[BackgroundItem]):
    itemType: str = 'background'

class EffectSection(ServerItemSectionTyped[EffectItem]):
    itemType: str = 'effect'

class ParticleSection(ServerItemSectionTyped[ParticleItem]):
    itemType: str = 'particle'

class EngineSection(ServerItemSectionTyped[EngineItem]):
    itemType: str = 'engine'

class ReplaySection(ServerItemSectionTyped[ReplayItem]):
    itemType: str = 'replay'

# Union型でServerItemSectionを定義
ServerItemSection = Union[
    PostSection,
    PlaylistSection,
    LevelSection,
    SkinSection,
    BackgroundSection,
    EffectSection,
    ParticleSection,
    EngineSection,
    ReplaySection
]
