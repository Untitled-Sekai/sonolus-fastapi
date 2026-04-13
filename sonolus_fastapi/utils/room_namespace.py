from __future__ import annotations
from .room_slot import RoomCreateSlot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

class RoomNamespace:
    def __init__(self, sonolus: "Sonolus"):
        self.create = RoomCreateSlot(sonolus)
