from fastapi import APIRouter, Request, HTTPException, FastAPI
from typing import TYPE_CHECKING
from sonolus_fastapi.model.items import ItemType
from typing import Literal

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

class SonolusApi:
    def __init__(self, sonolus: "Sonolus"):
        self.sonolus = sonolus
        self.router = APIRouter(prefix="/sonolus")
        self._register_routes()

    def register(self, app: FastAPI):
        app.include_router(self.router)

    # -------------------------
    # route definitions
    # -------------------------

    def _register_routes(self):
        self.router.post('/authenticate')(self._authenticate)
        self.router.get('/info')(self._server_info)
        self.router.get("/{item_type}/info")(self._info)
        self.router.get("/{item_type}/list")(self._list)
        self.router.get("/{item_type}/{name}")(self._detail)
        self.router.post("/{item_type}/{name}/submit")(self._actions)

    # -------------------------
    # utility methods
    # -------------------------
    
    async def _parse_request_body(self, request: Request, model_class=None):
        """リクエストボディを解析してモデルクラスのインスタンスを返す"""
        try:
            body = await request.json()
            if model_class:
                return model_class.model_validate(body)
            return body
        except Exception:
            return None

    # -------------------------
    # handlers
    # -------------------------
    
    async def _authenticate(self, request: Request):
        from sonolus_fastapi.model.Request.authenticate import ServerAuthenticateRequest
        auth_request = await self._parse_request_body(request, ServerAuthenticateRequest)
        
        ctx = self.sonolus.build_context(request, auth_request)
        
        handler = self.sonolus.get_server_handler("authenticate")
        if handler is None:
            raise HTTPException(404, "authenticate handler not implemented")
        
        result = await handler.call(ctx)
        return handler.response_model.model_validate(result)
    
    async def _server_info(self, request: Request):
        ctx = self.sonolus.build_context(request)
        
        handler = self.sonolus.get_server_handler("server_info")
        if handler is None:
            raise HTTPException(404, "server info handler not implemented")
        
        result = await handler.call(ctx)
        return handler.response_model.model_validate(result)

    async def _info(self, item_type: ItemType, request: Request):
        ctx = self.sonolus.build_context(request)
        
        handler = self.sonolus.get_handler(item_type, "info")
        if handler is None:
            raise HTTPException(404, "info handler not implemented")
        
        result = await handler.call(ctx)
        return handler.response_model.model_validate(result)

    async def _list(self, item_type: ItemType, request: Request):
        ctx = self.sonolus.build_context(request)
        query = self.sonolus.build_query(item_type, request)

        handler = self.sonolus.get_handler(item_type, "list")
        if handler is None:
            raise HTTPException(404, "list handler not implemented")
        
        result = await handler.call(ctx, query)

        return handler.response_model.model_validate(result)

    async def _detail(self, item_type: ItemType, name: str, request: Request):
        ctx = self.sonolus.build_context(request)

        handler = self.sonolus.get_handler(item_type, "detail")
        if handler is None:
            raise HTTPException(404, "detail handler not implemented")

        result = await handler.call(ctx, name)
        return handler.response_model.model_validate(result)

    async def _actions(self, item_type: ItemType, name: str, request: Request):
        ctx = self.sonolus.build_context(request)
        action_request = await self._parse_request_body(request)

        handler = self.sonolus.get_handler(item_type, "actions")
        if handler is None:
            raise HTTPException(404, "actions handler not implemented")

        result = await handler.call(ctx, name, action_request)
        return handler.response_model.model_validate(result)