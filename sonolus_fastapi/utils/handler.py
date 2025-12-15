from __future__ import annotations

from .context import SonolusContext
from .query import Query
from typing import Callable, Awaitable, Generic, TypeVar, Any
from pydantic import BaseModel

Ctx = SonolusContext

T = TypeVar("T", bound=BaseModel)

InfoFn = Callable[[Ctx], Awaitable[T]]
ListFn = Callable[[Ctx, Query], Awaitable[T]]
DetailFn = Callable[[Ctx, str], Awaitable[T]]

class ServerAuthenticateHandlerDescriptor(Generic[T]):
    def __init__(self, fn: InfoFn[T], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx) -> T:
        return await self.fn(ctx)

class ServerInfoHandlerDescriptor(Generic[T]):
    def __init__(self, fn: InfoFn[T], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx) -> T:
        return await self.fn(ctx)

class InfoHandlerDescriptor(Generic[T]):
    def __init__(self, fn: InfoFn[T], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx) -> T:
        return await self.fn(ctx)

class ListHandlerDescriptor(Generic[T]):
    def __init__(self, fn: ListFn[T], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, query: Query) -> T:
        return await self.fn(ctx, query)

class DetailHandlerDescriptor(Generic[T]):
    def __init__(self, fn: DetailFn[T], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, name: str) -> T:
        return await self.fn(ctx, name)
    
class HandlerDescriptor(Generic[T]):
    def __init__(
        self,
        fn: Callable[..., Awaitable[T]],
        response_model: type[T],
    ):
        self.fn = fn
        self.response_model: type[T] = response_model

    async def call(self, *args) -> T:
        return await self.fn(*args)