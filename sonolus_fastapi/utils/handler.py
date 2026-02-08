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

class ActionHandlerDescriptor(Generic[T]):
    def __init__(
        self,
        fn: Callable[[Ctx, str, Any], Awaitable[T]],
        response_model: type[T],
    ):
        self.fn = fn
        self.response_model: type[T] = response_model

    async def call(self, ctx: Ctx, name: str, action_request: type[T]) -> T:
        return await self.fn(ctx, name, action_request)

class UploadHandlerDescriptor(Generic[T]):
    def __init__(self, fn: Callable[[Ctx, str, str, list], Awaitable[T]], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, name: str, upload_key: str, files: list) -> T:
        return await self.fn(ctx, name, upload_key, files)

class ResultInfoHandlerDescriptor(Generic[T]):
    def __init__(self, fn: InfoFn[T], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx) -> T:
        return await self.fn(ctx)

class ResultSubmitHandlerDescriptor(Generic[T]):
    def __init__(self, fn: Callable[[Ctx, Any], Awaitable[T]], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, submit_request: Any) -> T:
        return await self.fn(ctx, submit_request)

class ResultUploadHandlerDescriptor(Generic[T]):
    def __init__(self, fn: Callable[[Ctx, str, list], Awaitable[T]], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, upload_key: str, files: list) -> T:
        return await self.fn(ctx, upload_key, files)

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

# Community Handlers
class CommunityInfoHandlerDescriptor(Generic[T]):
    def __init__(self, fn: Callable[[Ctx, str], Awaitable[T]], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, item_name: str) -> T:
        return await self.fn(ctx, item_name)

class CommunityCommentsHandlerDescriptor(Generic[T]):
    def __init__(self, fn: Callable[[Ctx, str, Query], Awaitable[T]], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, item_name: str, query: Query) -> T:
        return await self.fn(ctx, item_name, query)

class CommunityActionsHandlerDescriptor(Generic[T]):
    def __init__(self, fn: Callable[[Ctx, str, Any], Awaitable[T]], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, item_name: str, action_request: Any) -> T:
        return await self.fn(ctx, item_name, action_request)

class CommunityUploadHandlerDescriptor(Generic[T]):
    def __init__(self, fn: Callable[[Ctx, str, str, list], Awaitable[T]], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, item_name: str, upload_key: str, files: list) -> T:
        return await self.fn(ctx, item_name, upload_key, files)

class CommunityCommentActionsHandlerDescriptor(Generic[T]):
    def __init__(self, fn: Callable[[Ctx, str, str, Any], Awaitable[T]], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, item_name: str, comment_name: str, action_request: Any) -> T:
        return await self.fn(ctx, item_name, comment_name, action_request)

class CommunityCommentUploadHandlerDescriptor(Generic[T]):
    def __init__(self, fn: Callable[[Ctx, str, str, str, list], Awaitable[T]], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, item_name: str, comment_name: str, upload_key: str, files: list) -> T:
        return await self.fn(ctx, item_name, comment_name, upload_key, files)

# Leaderboard Handlers
class LeaderboardDetailHandlerDescriptor(Generic[T]):
    def __init__(self, fn: Callable[[Ctx, str, str], Awaitable[T]], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, item_name: str, leaderboard_name: str) -> T:
        return await self.fn(ctx, item_name, leaderboard_name)

class LeaderboardRecordsHandlerDescriptor(Generic[T]):
    def __init__(self, fn: Callable[[Ctx, str, str, Query], Awaitable[T]], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, item_name: str, leaderboard_name: str, query: Query) -> T:
        return await self.fn(ctx, item_name, leaderboard_name, query)

class LeaderboardRecordDetailHandlerDescriptor(Generic[T]):
    def __init__(self, fn: Callable[[Ctx, str, str, str], Awaitable[T]], response_model: type[T]):
        self.fn = fn
        self.response_model = response_model

    async def call(self, ctx: Ctx, item_name: str, leaderboard_name: str, record_name: str) -> T:
        return await self.fn(ctx, item_name, leaderboard_name, record_name)