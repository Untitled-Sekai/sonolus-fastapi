from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar
from pydantic import BaseModel
from sonolus_models import ItemType

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

T = TypeVar("T", bound=BaseModel)

class LeaderboardDetailSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import LeaderboardDetailHandlerDescriptor
            desc = LeaderboardDetailHandlerDescriptor(fn, response_model)
            self.sonolus._register_leaderboard_handler(self.item_type, "detail", desc)
            return fn
        return decorator

class LeaderboardRecordsSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import LeaderboardRecordsHandlerDescriptor
            desc = LeaderboardRecordsHandlerDescriptor(fn, response_model)
            self.sonolus._register_leaderboard_handler(self.item_type, "records", desc)
            return fn
        return decorator

class LeaderboardRecordDetailSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import LeaderboardRecordDetailHandlerDescriptor
            desc = LeaderboardRecordDetailHandlerDescriptor(fn, response_model)
            self.sonolus._register_leaderboard_handler(self.item_type, "record_detail", desc)
            return fn
        return decorator
