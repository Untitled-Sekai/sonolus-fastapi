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

    def __call__(self, response_model: type[T], info_type: str | None = None):
        def decorator(fn):
            desc = InfoHandlerDescriptor(fn, response_model, info_type=info_type)
            self.sonolus._register_handler(self.item_type, "info", desc, filter_key=info_type)
            return fn
        return decorator

class ListSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T], list_type: str | None = None):
        def decorator(fn):
            desc = ListHandlerDescriptor(fn, response_model, list_type=list_type)
            self.sonolus._register_handler(self.item_type, "list", desc, filter_key=list_type)
            return fn
        return decorator

class DetailSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T], detail_type: str | None = None):
        def decorator(fn):
            desc = DetailHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "detail", desc, filter_key=detail_type)
            return fn
        return decorator
    
class ActionSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T], action_type: str | None = None):
        def decorator(fn):
            from .handler import ActionHandlerDescriptor
            desc = ActionHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "actions", desc, filter_key=action_type)
            return fn
        return decorator

class UploadSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T], upload_type: str | None = None):
        def decorator(fn):
            from .handler import UploadHandlerDescriptor
            desc = UploadHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "upload", desc, filter_key=upload_type)
            return fn
        return decorator

class ResultInfoSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T], result_type: str | None = None):
        def decorator(fn):
            from .handler import ResultInfoHandlerDescriptor
            desc = ResultInfoHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "result_info", desc, filter_key=result_type)
            return fn
        return decorator

class ResultSubmitSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T], result_type: str | None = None):
        def decorator(fn):
            from .handler import ResultSubmitHandlerDescriptor
            desc = ResultSubmitHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "result_submit", desc, filter_key=result_type)
            return fn
        return decorator

class ResultUploadSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T], result_type: str | None = None):
        def decorator(fn):
            from .handler import ResultUploadHandlerDescriptor
            desc = ResultUploadHandlerDescriptor(fn, response_model)
            self.sonolus._register_handler(self.item_type, "result_upload", desc, filter_key=result_type)
            return fn
        return decorator