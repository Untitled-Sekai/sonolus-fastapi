from fastapi import APIRouter, Request, HTTPException, FastAPI
from typing import TYPE_CHECKING, Any, Optional, TypeVar, Union
from sonolus_models import SonolusSignaturePublicKey
from sonolus_models.items import ItemType
from typing import Literal
import json
import base64
import time as time_module
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.hazmat.backends import default_backend

T = TypeVar('T')

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

class SonolusApi:
    # Sonolus公開鍵（JWK形式）
    SONOLUS_PUBLIC_KEY = SonolusSignaturePublicKey(
        x="d2B14ZAn-zDsqY42rHofst8rw3XB90-a5lT80NFdXo0",
        y="Hxzi9DHrlJ4CVSJVRnydxFWBZAgkFxZXbyxPSa8SJQw"
    )
    
    def __init__(self, sonolus: "Sonolus", router: APIRouter | None = None):
        self.sonolus = sonolus
        self.router = router or APIRouter(prefix="/sonolus")
        self._register_routes()

    def register(self, target: FastAPI | APIRouter):
        target.include_router(self.router)

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
        
        # Result API (only for levels) - Must be before generic routes
        self.router.get("/{item_type}/result/info")(self._result_info)
        self.router.post("/{item_type}/result/submit")(self._result_submit)
        self.router.post("/{item_type}/result/upload")(self._result_upload)

        # Rooms Create API (only for rooms) - Must be before generic routes
        self.router.post("/{item_type}/create")(self._room_create)
        
        # Generic item routes
        self.router.get("/{item_type}/{name}")(self._detail)
        self.router.post("/{item_type}/{name}/submit")(self._actions)
        self.router.post("/{item_type}/{name}/upload")(self._upload)

        # -------------------------
        # Sonolus Extended API
        # -------------------------

        # Community API
        self.router.get("/{item_type}/{name}/community/info")(self._community_info)
        self.router.get("/{item_type}/{name}/community/comments/list")(self._community_comments)
        self.router.post("/{item_type}/{name}/community/submit")(self._community_actions)
        self.router.post("/{item_type}/{name}/community/upload")(self._community_upload)
        self.router.post("/{item_type}/{name}/community/comments/{comment_name}/submit")(self._community_comment_actions)
        self.router.post("/{item_type}/{name}/community/comments/{comment_name}/upload")(self._community_comment_upload)

        # Leaderboard API
        self.router.get("/{item_type}/{name}/leaderboards/{leaderboard_name}")(self._leaderboard_detail)
        self.router.get("/{item_type}/{name}/leaderboards/{leaderboard_name}/records/list")(self._leaderboard_records)
        self.router.get("/{item_type}/{name}/leaderboards/{leaderboard_name}/records/{record_name}")(self._leaderboard_record_detail)


    # -------------------------
    # utility methods
    # -------------------------

    def _verify_sonolus_signature(self, message: bytes, signature_b64: str) -> bool:
        """Sonolus-Signatureを検証する
        
        Args:
            message: 検証するメッセージ（署名対象のデータ）
            signature_b64: Base64エンコードされた署名
            
        Returns:
            署名が有効な場合True、無効な場合False
        """
        try:
            # Base64デコードされた署名を取得
            signature = base64.b64decode(signature_b64)

            # Sonolusクライアントからは raw 64-byte (r||s) 形式で来る場合がある。
            # cryptography の ECDSA verify は DER 形式を期待するため変換する。
            if len(signature) == 64:
                r = int.from_bytes(signature[:32], byteorder='big')
                s = int.from_bytes(signature[32:], byteorder='big')
                signature = encode_dss_signature(r, s)
            
            # JWKから公開鍵を復元
            # x, y座標をBase64URLデコード
            x_padding = '=' * (-len(self.SONOLUS_PUBLIC_KEY.x) % 4)
            y_padding = '=' * (-len(self.SONOLUS_PUBLIC_KEY.y) % 4)
            x_bytes = base64.urlsafe_b64decode(self.SONOLUS_PUBLIC_KEY.x + x_padding)
            y_bytes = base64.urlsafe_b64decode(self.SONOLUS_PUBLIC_KEY.y + y_padding)
            
            # x, yから整数を作成
            x = int.from_bytes(x_bytes, byteorder='big')
            y = int.from_bytes(y_bytes, byteorder='big')
            
            # EC公開鍵を作成
            public_numbers = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1())
            public_key = public_numbers.public_key(default_backend())
            
            # 署名を検証
            public_key.verify(
                signature,
                message,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False
    
    async def _parse_request_body(self, request: Request, model_class: Optional[type[T]] = None) -> Union[dict[str, Any], T]:
        """Parse request body and return model instance or dict.
        
        Args:
            request: FastAPI request object
            model_class: Optional Pydantic model class to validate against
            
        Returns:
            Validated model instance if model_class is provided, otherwise raw dict
            
        Raises:
            HTTPException: If request body parsing fails
        """
        try:
            body = await request.json()
            if model_class:
                return model_class.model_validate(body)
            return body
        except Exception as e:
            import traceback
            print(f"Error parsing request body: {e}")
            print(traceback.format_exc())
            raise HTTPException(400, f"Invalid request body: {str(e)}")

    def _build_response(self, handler: Any, result: Any, request: Request) -> dict[str, Any]:
        """Build response by applying source fields and validating with response model.
        
        Args:
            handler: Handler descriptor with response_model
            result: Raw result from handler
            request: FastAPI request object
            
        Returns:
            Validated response dict ready for JSON serialization
        """
        result = self.sonolus.apply_response_source(result, request)
        validated = handler.response_model.model_validate(result)
        validated = self.sonolus.apply_response_source(validated, request)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    

    # -------------------------
    # handlers
    # -------------------------
    

    async def _authenticate(self, request: Request) -> dict[str, Any]:
        """Handle server authentication."""
        from sonolus_models import ServerAuthenticateRequest
        
        # Sonolus-Signatureヘッダーを取得
        signature = request.headers.get("Sonolus-Signature")
        if not signature:
            raise HTTPException(401, "Sonolus-Signature header is required")
        
        # リクエストボディを取得（JSON文字列として）
        body_bytes = await request.body()
        
        # 署名を検証
        if not self._verify_sonolus_signature(body_bytes, signature):
            raise HTTPException(401, "Invalid signature")
        
        # リクエストボディをパース
        try:
            body = json.loads(body_bytes)
            auth_request = ServerAuthenticateRequest.model_validate(body)
        except Exception as e:
            raise HTTPException(400, f"Invalid request body: {str(e)}")
        
        # typeを検証
        if auth_request.type != "authenticateServer":
            raise HTTPException(401, f"Invalid type: expected 'authenticateServer', got '{auth_request.type}'")
        
        # timeを検証（5分以内か）
        current_time = int(time_module.time() * 1000)  # ミリ秒
        time_diff = abs(current_time - auth_request.time)
        if time_diff > 5 * 60 * 1000:  # 5分
            raise HTTPException(401, f"Request time is too old or too far in the future")
        
        ctx = self.sonolus.build_context(request, auth_request)
        
        handler = self.sonolus.get_server_handler("authenticate")
        if handler is None:
            raise HTTPException(404, "authenticate handler not implemented")
        
        result = await handler.call(ctx)
        return self._build_response(handler, result, request)
    
    
    async def _server_info(self, request: Request) -> dict[str, Any]:
        """Get server information."""
        ctx = self.sonolus.build_context(request)
        
        handler = self.sonolus.get_server_handler("server_info")
        if handler is None:
            raise HTTPException(404, "server info handler not implemented")
        
        result = await handler.call(ctx)
        return self._build_response(handler, result, request)
    

    async def _info(self, item_type: ItemType, request: Request) -> dict[str, Any]:
        """Get item type information."""
        ctx = self.sonolus.build_context(request)
        
        # クエリパラメータから type を取得（info_type用）
        info_type = request.query_params.get("type")
        
        handler = self.sonolus.get_handler(item_type, "info", filter_key=info_type)
        if handler is None:
            raise HTTPException(404, "info handler not implemented")
        
        result = await handler.call(ctx)
        return self._build_response(handler, result, request)
    

    async def _list(self, item_type: ItemType, request: Request) -> dict[str, Any]:
        """Get list of items."""
        ctx = self.sonolus.build_context(request)
        query = self.sonolus.build_query(item_type, request)
        
        # クエリパラメータから type を取得（list_type用）
        list_type = request.query_params.get("type")

        handler = self.sonolus.get_handler(item_type, "list", filter_key=list_type)
        if handler is None:
            raise HTTPException(404, "list handler not implemented")
        
        result = await handler.call(ctx, query)
        return self._build_response(handler, result, request)
    

    async def _detail(self, item_type: ItemType, name: str, request: Request) -> dict[str, Any]:
        """Get item detail."""
        ctx = self.sonolus.build_context(request)
        
        # クエリパラメータから type を取得（detail_type用）
        detail_type = request.query_params.get("type")

        handler = self.sonolus.get_handler(item_type, "detail", filter_key=detail_type)
        if handler is None:
            raise HTTPException(404, "detail handler not implemented")

        result = await handler.call(ctx, name)
        return self._build_response(handler, result, request)
    

    async def _actions(self, item_type: ItemType, name: str, request: Request) -> dict[str, Any]:
        """Handle item actions."""
        ctx = self.sonolus.build_context(request)
        action_request = await self._parse_request_body(request)
        
        # クエリパラメータから type を取得（action_type用）
        action_type = request.query_params.get("type")

        handler = self.sonolus.get_handler(item_type, "actions", filter_key=action_type)
        if handler is None:
            raise HTTPException(404, "actions handler not implemented")

        result = await handler.call(ctx, name, action_request)
        return self._build_response(handler, result, request)
    
    async def _upload(self, item_type: ItemType, name: str, request: Request) -> dict[str, Any]:
        """Handle item upload."""
        from fastapi import File, UploadFile, Form
        from typing import List
        
        # Sonolus-Upload-Key ヘッダーを取得
        upload_key = request.headers.get("Sonolus-Upload-Key")
        
        # multipart/form-data からファイルを取得
        form = await request.form()
        files = form.getlist("files")
        
        # クエリパラメータから type を取得（upload_type用）
        upload_type = request.query_params.get("type")
        
        ctx = self.sonolus.build_context(request)
        
        handler = self.sonolus.get_handler(item_type, "upload", filter_key=upload_type)
        if handler is None:
            raise HTTPException(404, "upload handler not implemented")
        
        result = await handler.call(ctx, name, upload_key, files)
        return self._build_response(handler, result, request)
    
    async def _result_info(self, item_type: ItemType, request: Request) -> dict[str, Any]:
        """Get result information (levels only)."""
        # result info is only available for levels
        if item_type != ItemType.level:
            raise HTTPException(404, "result info is only available for levels")
        
        ctx = self.sonolus.build_context(request)
        
        # クエリパラメータから type を取得（result_type用）
        result_type = request.query_params.get("type")
        
        handler = self.sonolus.get_handler(item_type, "result_info", filter_key=result_type)
        if handler is None:
            raise HTTPException(404, "result info handler not implemented")
        
        result = await handler.call(ctx)
        return self._build_response(handler, result, request)
    
    async def _result_submit(self, item_type: ItemType, request: Request) -> dict[str, Any]:
        """Submit result (levels only)."""
        # result submit is only available for levels
        if item_type != ItemType.level:
            raise HTTPException(404, "result submit is only available for levels")
        
        from sonolus_models import ServerSubmitLevelResultRequest
        from sonolus_fastapi.utils.replay import normalize_replay_item
        
        ctx = self.sonolus.build_context(request)
        
        # Get raw request body first
        try:
            body = await request.json()
        except Exception as e:
            import traceback
            print(f"Error parsing request body: {e}")
            print(traceback.format_exc())
            raise HTTPException(400, f"Invalid request body: {str(e)}")
        
        # Normalize replay item descriptions BEFORE validation
        if body and 'replay' in body and body['replay']:
            body['replay'] = normalize_replay_item(body['replay'])
        
        # Now validate with normalized data
        try:
            submit_request = ServerSubmitLevelResultRequest.model_validate(body)
        except Exception as e:
            import traceback
            print(f"Error validating request body: {e}")
            print(traceback.format_exc())
            raise HTTPException(400, f"Invalid request body: {str(e)}")
        
        # クエリパラメータから type を取得（result_type用）
        result_type = request.query_params.get("type")
        
        handler = self.sonolus.get_handler(item_type, "result_submit", filter_key=result_type)
        if handler is None:
            raise HTTPException(404, "result submit handler not implemented")
        
        result = await handler.call(ctx, submit_request)
        return self._build_response(handler, result, request)
    
    async def _result_upload(self, item_type: ItemType, request: Request) -> dict[str, Any]:
        """Upload result (levels only)."""
        # result upload is only available for levels
        if item_type != ItemType.level:
            raise HTTPException(404, "result upload is only available for levels")
        
        from fastapi import File, UploadFile, Form
        from typing import List
        
        # Sonolus-Upload-Key ヘッダーを取得
        upload_key = request.headers.get("Sonolus-Upload-Key")
        
        # multipart/form-data からファイルを取得
        form = await request.form()
        files = form.getlist("files")
        
        # クエリパラメータから type を取得（result_type用）
        result_type = request.query_params.get("type")
        
        ctx = self.sonolus.build_context(request)
        
        handler = self.sonolus.get_handler(item_type, "result_upload", filter_key=result_type)
        if handler is None:
            raise HTTPException(404, "result upload handler not implemented")
        
        result = await handler.call(ctx, upload_key, files)
        return self._build_response(handler, result, request)

    async def _room_create(self, item_type: ItemType, request: Request) -> dict[str, Any]:
        """Create a room (rooms only)."""
        from sonolus_models import ServerCreateRoomRequest
        if item_type != ItemType.room:
            raise HTTPException(404, "room create API is only available for rooms")
        
        ctx = self.sonolus.build_context(request)
        
        # リクエストボディをパース
        body_bytes = await request.body()
        try:
            body = json.loads(body_bytes) if body_bytes else {}
            room_request = ServerCreateRoomRequest.model_validate(body)
        except Exception as e:
            raise HTTPException(400, f"Invalid request body: {str(e)}")
        
        handler = self.sonolus.get_room_handler("create")
        if handler is None:
            raise HTTPException(404, "room create handler not implemented")
        
        result = await handler.call(ctx)
        return self._build_response(handler, result, request)

    async def _community_info(self, item_type: ItemType, name: str, request: Request) -> dict[str, Any]:
        """Get community information for an item."""
        ctx = self.sonolus.build_context(request)

        handler = self.sonolus.get_community_handler(item_type, "info")
        if handler is None:
            raise HTTPException(404, "community info handler not implemented")

        result = await handler.call(ctx, name)
        return self._build_response(handler, result, request)
    

    async def _community_comments(self, item_type: ItemType, name: str, request: Request) -> dict[str, Any]:
        """Get community comments for an item."""
        ctx = self.sonolus.build_context(request)
        query = self.sonolus.build_query(item_type, request)

        handler = self.sonolus.get_community_handler(item_type, "comments")
        if handler is None:
            raise HTTPException(404, "community comments handler not implemented")

        result = await handler.call(ctx, name, query)
        return self._build_response(handler, result, request)
    

    async def _community_actions(self, item_type: ItemType, name: str, request: Request) -> dict[str, Any]:
        """Handle community actions for an item."""
        ctx = self.sonolus.build_context(request)
        action_request = await self._parse_request_body(request)

        handler = self.sonolus.get_community_handler(item_type, "actions")
        if handler is None:
            raise HTTPException(404, "community actions handler not implemented")

        result = await handler.call(ctx, name, action_request)
        return self._build_response(handler, result, request)
    

    async def _community_upload(self, item_type: ItemType, name: str, request: Request) -> dict[str, Any]:
        """Handle community upload for an item."""
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
        return self._build_response(handler, result, request)
    

    async def _community_comment_actions(self, item_type: ItemType, name: str, comment_name: str, request: Request) -> dict[str, Any]:
        """Handle community comment actions."""
        ctx = self.sonolus.build_context(request)
        action_request = await self._parse_request_body(request)

        handler = self.sonolus.get_community_handler(item_type, "comment_actions")
        if handler is None:
            raise HTTPException(404, "community comment actions handler not implemented")

        result = await handler.call(ctx, name, comment_name, action_request)
        return self._build_response(handler, result, request)
    

    async def _community_comment_upload(self, item_type: ItemType, name: str, comment_name: str, request: Request) -> dict[str, Any]:
        """Handle community comment upload."""
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
        return self._build_response(handler, result, request)

    async def _leaderboard_detail(self, item_type: ItemType, name: str, leaderboard_name: str, request: Request) -> dict[str, Any]:
        """Get leaderboard details."""
        ctx = self.sonolus.build_context(request)

        handler = self.sonolus.get_leaderboard_handler(item_type, "detail")
        if handler is None:
            raise HTTPException(404, "leaderboard detail handler not implemented")

        result = await handler.call(ctx, name, leaderboard_name)
        return self._build_response(handler, result, request)

    async def _leaderboard_records(self, item_type: ItemType, name: str, leaderboard_name: str, request: Request) -> dict[str, Any]:
        """Get leaderboard records."""
        ctx = self.sonolus.build_context(request)
        query = self.sonolus.build_query(item_type, request)

        handler = self.sonolus.get_leaderboard_handler(item_type, "records")
        if handler is None:
            raise HTTPException(404, "leaderboard records handler not implemented")

        result = await handler.call(ctx, name, leaderboard_name, query)
        return self._build_response(handler, result, request)

    async def _leaderboard_record_detail(self, item_type: ItemType, name: str, leaderboard_name: str, record_name: str, request: Request) -> dict[str, Any]:
        """Get leaderboard record details."""
        ctx = self.sonolus.build_context(request)

        handler = self.sonolus.get_leaderboard_handler(item_type, "record_detail")
        if handler is None:
            raise HTTPException(404, "leaderboard record detail handler not implemented")

        result = await handler.call(ctx, name, leaderboard_name, record_name)
        return self._build_response(handler, result, request)