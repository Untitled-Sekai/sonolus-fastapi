from __future__ import annotations
from sonolus_models import ItemType
from .leaderboard_slot import LeaderboardDetailSlot, LeaderboardRecordsSlot, LeaderboardRecordDetailSlot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

class LeaderboardNamespace:
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.detail = LeaderboardDetailSlot(sonolus, item_type)
        self.records = LeaderboardRecordsSlot(sonolus, item_type)
        self.record_detail = LeaderboardRecordDetailSlot(sonolus, item_type)
