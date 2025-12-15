from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar
from pydantic import BaseModel
from sonolus_fastapi.model.items import ItemType
from .handler import (
    InfoHandlerDescriptor,
    ListHandlerDescriptor,
    DetailHandlerDescriptor,
)

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

T = TypeVar("T", bound=BaseModel)

class InfoSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            desc = InfoHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "info", desc)
            return fn
        return decorator

class ListSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            desc = ListHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "list", desc)
            return fn
        return decorator

class DetailSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            desc = DetailHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "detail", desc)
            return fn
        return decorator