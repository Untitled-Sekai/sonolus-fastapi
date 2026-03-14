from fastapi import APIRouter, Request, HTTPException, FastAPI
from typing import TYPE_CHECKING
from sonolus_models import SonolusSignaturePublicKey
from sonolus_models.items import ItemType
from typing import Literal
import json
import base64
import time as time_module
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

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
            
            # JWKから公開鍵を復元
            # x, y座標をBase64URLデコード
            x_bytes = base64.urlsafe_b64decode(self.SONOLUS_PUBLIC_KEY.x + '==')
            y_bytes = base64.urlsafe_b64decode(self.SONOLUS_PUBLIC_KEY.y + '==')
            
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
    
    async def _parse_request_body(self, request: Request, model_class=None):
        """リクエストボディを解析してモデルクラスのインスタンスを返す"""
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
    

    # -------------------------
    # handlers
    # -------------------------
    

    async def _authenticate(self, request: Request):
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
    
    async def _upload(self, item_type: ItemType, name: str, request: Request):
        from fastapi import File, UploadFile, Form
        from typing import List
        
        # Sonolus-Upload-Key ヘッダーを取得
        upload_key = request.headers.get("Sonolus-Upload-Key")
        
        # multipart/form-data からファイルを取得
        form = await request.form()
        files = form.getlist("files")
        
        ctx = self.sonolus.build_context(request)
        
        handler = self.sonolus.get_handler(item_type, "upload")
        if handler is None:
            raise HTTPException(404, "upload handler not implemented")
        
        result = await handler.call(ctx, name, upload_key, files)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    
    async def _result_info(self, item_type: ItemType, request: Request):
        # result info is only available for levels
        if item_type != ItemType.level:
            raise HTTPException(404, "result info is only available for levels")
        
        ctx = self.sonolus.build_context(request)
        
        handler = self.sonolus.get_handler(item_type, "result_info")
        if handler is None:
            raise HTTPException(404, "result info handler not implemented")
        
        result = await handler.call(ctx)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    
    async def _result_submit(self, item_type: ItemType, request: Request):
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
        
        handler = self.sonolus.get_handler(item_type, "result_submit")
        if handler is None:
            raise HTTPException(404, "result submit handler not implemented")
        
        result = await handler.call(ctx, submit_request)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)
    
    async def _result_upload(self, item_type: ItemType, request: Request):
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
        
        ctx = self.sonolus.build_context(request)
        
        handler = self.sonolus.get_handler(item_type, "result_upload")
        if handler is None:
            raise HTTPException(404, "result upload handler not implemented")
        
        result = await handler.call(ctx, upload_key, files)
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

    async def _leaderboard_detail(self, item_type: ItemType, name: str, leaderboard_name: str, request: Request):
        ctx = self.sonolus.build_context(request)

        handler = self.sonolus.get_leaderboard_handler(item_type, "detail")
        if handler is None:
            raise HTTPException(404, "leaderboard detail handler not implemented")

        result = await handler.call(ctx, name, leaderboard_name)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)

    async def _leaderboard_records(self, item_type: ItemType, name: str, leaderboard_name: str, request: Request):
        ctx = self.sonolus.build_context(request)
        query = self.sonolus.build_query(item_type, request)

        handler = self.sonolus.get_leaderboard_handler(item_type, "records")
        if handler is None:
            raise HTTPException(404, "leaderboard records handler not implemented")

        result = await handler.call(ctx, name, leaderboard_name, query)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)

    async def _leaderboard_record_detail(self, item_type: ItemType, name: str, leaderboard_name: str, record_name: str, request: Request):
        ctx = self.sonolus.build_context(request)

        handler = self.sonolus.get_leaderboard_handler(item_type, "record_detail")
        if handler is None:
            raise HTTPException(404, "leaderboard record detail handler not implemented")

        result = await handler.call(ctx, name, leaderboard_name, record_name)
        validated = handler.response_model.model_validate(result)
        return validated.model_dump(exclude_none=True, mode='json', by_alias=True)