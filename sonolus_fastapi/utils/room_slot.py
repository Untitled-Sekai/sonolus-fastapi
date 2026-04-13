from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar
from pydantic import BaseModel

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

T = TypeVar("T", bound=BaseModel)

class RoomCreateSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus"):
        self.sonolus = sonolus

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import RoomCreateHandlerDescriptor
            desc = RoomCreateHandlerDescriptor(fn, response_model)
            self.sonolus._register_room_handler("create", desc)
            return fn
        return decorator
