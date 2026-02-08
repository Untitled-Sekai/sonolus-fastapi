from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar
from pydantic import BaseModel
from sonolus_models import ItemType

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

T = TypeVar("T", bound=BaseModel)

class CommunityInfoSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import CommunityInfoHandlerDescriptor
            desc = CommunityInfoHandlerDescriptor(fn, response_model)
            self.sonolus._register_community_handler(self.item_type, "info", desc)
            return fn
        return decorator

class CommunityCommentsSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import CommunityCommentsHandlerDescriptor
            desc = CommunityCommentsHandlerDescriptor(fn, response_model)
            self.sonolus._register_community_handler(self.item_type, "comments", desc)
            return fn
        return decorator

class CommunityActionsSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import CommunityActionsHandlerDescriptor
            desc = CommunityActionsHandlerDescriptor(fn, response_model)
            self.sonolus._register_community_handler(self.item_type, "actions", desc)
            return fn
        return decorator

class CommunityUploadSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import CommunityUploadHandlerDescriptor
            desc = CommunityUploadHandlerDescriptor(fn, response_model)
            self.sonolus._register_community_handler(self.item_type, "upload", desc)
            return fn
        return decorator

class CommunityCommentActionsSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import CommunityCommentActionsHandlerDescriptor
            desc = CommunityCommentActionsHandlerDescriptor(fn, response_model)
            self.sonolus._register_community_handler(self.item_type, "comment_actions", desc)
            return fn
        return decorator

class CommunityCommentUploadSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.sonolus = sonolus
        self.item_type = item_type

    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import CommunityCommentUploadHandlerDescriptor
            desc = CommunityCommentUploadHandlerDescriptor(fn, response_model)
            self.sonolus._register_community_handler(self.item_type, "comment_upload", desc)
            return fn
        return decorator
