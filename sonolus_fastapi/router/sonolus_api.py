from fastapi import APIRouter, Request, HTTPException, FastAPI
from typing import TYPE_CHECKING
from sonolus_models.items import ItemType
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

        
        # -------------------------
        # Sonolus Basic API
        # -------------------------


        self.router.post('/authenticate')(self._authenticate)
        self.router.get('/info')(self._server_info)
        self.router.get("/{item_type}/info")(self._info)
        self.router.get("/{item_type}/list")(self._list)
        self.router.get("/{item_type}/{name}")(self._detail)
        self.router.post("/{item_type}/{name}/submit")(self._actions)

        # -------------------------
        # Sonolus Extended API
        # -------------------------


        self.router.get("/{item_type}/{name}/community/info")(self._community_info)
        self.router.get("/{item_type}/{name}/community/comments/list")(self._community_comments)
        self.router.post("/{item_type}/{name}/community/submit")(self._community_actions)
        self.router.post("/{item_type}/{name}/community/upload")(self._community_upload)
        self.router.post("/{item_type}/{name}/community/comments/{comment_name}/submit")(self._community_comment_actions)
        self.router.post("/{item_type}/{name}/community/comments/{comment_name}/upload")(self._community_comment_upload)

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
        from sonolus_models import ServerAuthenticateRequest
        auth_request = await self._parse_request_body(request, ServerAuthenticateRequest)
        
        ctx = self.sonolus.build_context(request, auth_request)
        
        handler = self.sonolus.get_server_handler("authenticate")
        if handler is None:
            raise HTTPException(404, "authenticate handler not implemented")
        
        result = await handler.call(ctx)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    
    
    async def _server_info(self, request: Request):
        ctx = self.sonolus.build_context(request)
        
        handler = self.sonolus.get_server_handler("server_info")
        if handler is None:
            raise HTTPException(404, "server info handler not implemented")
        
        result = await handler.call(ctx)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    

    async def _info(self, item_type: ItemType, request: Request):
        ctx = self.sonolus.build_context(request)
        
        handler = self.sonolus.get_handler(item_type, "info")
        if handler is None:
            raise HTTPException(404, "info handler not implemented")
        
        result = await handler.call(ctx)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    

    async def _list(self, item_type: ItemType, request: Request):
        ctx = self.sonolus.build_context(request)
        query = self.sonolus.build_query(item_type, request)

        handler = self.sonolus.get_handler(item_type, "list")
        if handler is None:
            raise HTTPException(404, "list handler not implemented")
        
        result = await handler.call(ctx, query)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    

    async def _detail(self, item_type: ItemType, name: str, request: Request):
        ctx = self.sonolus.build_context(request)

        handler = self.sonolus.get_handler(item_type, "detail")
        if handler is None:
            raise HTTPException(404, "detail handler not implemented")

        result = await handler.call(ctx, name)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    

    async def _actions(self, item_type: ItemType, name: str, request: Request):
        ctx = self.sonolus.build_context(request)
        action_request = await self._parse_request_body(request)

        handler = self.sonolus.get_handler(item_type, "actions")
        if handler is None:
            raise HTTPException(404, "actions handler not implemented")

        result = await handler.call(ctx, name, action_request)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    

    async def _community_info(self, item_type: ItemType, name: str, request: Request):
        ctx = self.sonolus.build_context(request)

        handler = self.sonolus.get_community_handler(item_type, "info")
        if handler is None:
            raise HTTPException(404, "community info handler not implemented")

        result = await handler.call(ctx, name)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    

    async def _community_comments(self, item_type: ItemType, name: str, request: Request):
        ctx = self.sonolus.build_context(request)
        query = self.sonolus.build_query(item_type, request)

        handler = self.sonolus.get_community_handler(item_type, "comments")
        if handler is None:
            raise HTTPException(404, "community comments handler not implemented")

        result = await handler.call(ctx, name, query)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    

    async def _community_actions(self, item_type: ItemType, name: str, request: Request):
        ctx = self.sonolus.build_context(request)
        action_request = await self._parse_request_body(request)

        handler = self.sonolus.get_community_handler(item_type, "actions")
        if handler is None:
            raise HTTPException(404, "community actions handler not implemented")

        result = await handler.call(ctx, name, action_request)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    

    async def _community_upload(self, item_type: ItemType, name: str, request: Request):
        from fastapi import File, UploadFile, Form
        from typing import List
        
        # Sonolus-Upload-Key ヘッダーを取得
        upload_key = request.headers.get("Sonolus-Upload-Key")
        
        # multipart/form-data からファイルを取得
        form = await request.form()
        files = form.getlist("files")
        
        ctx = self.sonolus.build_context(request)
        
        handler = self.sonolus.get_community_handler(item_type, "upload")
        if handler is None:
            raise HTTPException(404, "community upload handler not implemented")
        
        result = await handler.call(ctx, name, upload_key, files)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    

    async def _community_comment_actions(self, item_type: ItemType, name: str, comment_name: str, request: Request):
        ctx = self.sonolus.build_context(request)
        action_request = await self._parse_request_body(request)

        handler = self.sonolus.get_community_handler(item_type, "comment_actions")
        if handler is None:
            raise HTTPException(404, "community comment actions handler not implemented")

        result = await handler.call(ctx, name, comment_name, action_request)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    

    async def _community_comment_upload(self, item_type: ItemType, name: str, comment_name: str, request: Request):
        from fastapi import File, UploadFile, Form
        from typing import List
        
        # Sonolus-Upload-Key ヘッダーを取得
        upload_key = request.headers.get("Sonolus-Upload-Key")
        
        # multipart/form-data からファイルを取得
        form = await request.form()
        files = form.getlist("files")
        
        ctx = self.sonolus.build_context(request)
        
        handler = self.sonolus.get_community_handler(item_type, "comment_upload")
        if handler is None:
            raise HTTPException(404, "community comment upload handler not implemented")
        
        result = await handler.call(ctx, name, comment_name, upload_key, files)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)