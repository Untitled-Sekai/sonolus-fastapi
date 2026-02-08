from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar
from pydantic import BaseModel
from sonolus_models import ItemType
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
    
class ActionSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import ActionHandlerDescriptor
            desc = ActionHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "actions", desc)
            return fn
        return decorator

class UploadSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import UploadHandlerDescriptor
            desc = UploadHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "upload", desc)
            return fn
        return decorator

class ResultInfoSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import ResultInfoHandlerDescriptor
            desc = ResultInfoHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "result_info", desc)
            return fn
        return decorator

class ResultSubmitSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import ResultSubmitHandlerDescriptor
            desc = ResultSubmitHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "result_submit", desc)
            return fn
        return decorator

class ResultUploadSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import ResultUploadHandlerDescriptor
            desc = ResultUploadHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "result_upload", desc)
            return fn
        return decorator