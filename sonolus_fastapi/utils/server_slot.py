from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar
from pydantic import BaseModel
from .handler import ServerInfoHandlerDescriptor

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

T = TypeVar("T", bound=BaseModel)

class ServerInfoSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus"):
        self.sonolus = sonolus
        
    def __call__(self, response_model: type[T]):
        def decorator(fn):
            desc = ServerInfoHandlerDescriptor(fn, response_model)
            self.sonolus._register_server_handler("server_info", desc)
            return fn
        return decorator

class ServerAuthenticateSlot(Generic[T]):
    def __init__(self, sonolus: "Sonolus"):
        self.sonolus = sonolus
        
    def __call__(self, response_model: type[T]):
        def decorator(fn):
            from .handler import ServerAuthenticateHandlerDescriptor
            desc = ServerAuthenticateHandlerDescriptor(fn, response_model)
            self.sonolus._register_server_handler("authenticate", desc)
            return fn
        return decorator