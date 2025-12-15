from __future__ import annotations
from sonolus_fastapi.model.items import ItemType
from .item_slot import InfoSlot, ListSlot, DetailSlot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

class ItemNamespace:
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.info = InfoSlot(sonolus, item_type)
        self.list = ListSlot(sonolus, item_type)
        self.detail = DetailSlot(sonolus, item_type)