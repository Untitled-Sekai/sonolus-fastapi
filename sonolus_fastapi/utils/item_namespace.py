from __future__ import annotations
from sonolus_models import ItemType
from .item_slot import InfoSlot, ListSlot, DetailSlot, ActionSlot, UploadSlot, ResultInfoSlot, ResultSubmitSlot, ResultUploadSlot
from .community_namespace import CommunityNamespace
from .leaderboard_namespace import LeaderboardNamespace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

class ItemNamespace:
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.info = InfoSlot(sonolus, item_type)
        self.list = ListSlot(sonolus, item_type)
        self.detail = DetailSlot(sonolus, item_type)
        self.actions = ActionSlot(sonolus, item_type)
        self.upload = UploadSlot(sonolus, item_type)
        self.result_info = ResultInfoSlot(sonolus, item_type)
        self.result_submit = ResultSubmitSlot(sonolus, item_type)
        self.result_upload = ResultUploadSlot(sonolus, item_type)
        self.community = CommunityNamespace(sonolus, item_type)
        self.leaderboard = LeaderboardNamespace(sonolus, item_type)