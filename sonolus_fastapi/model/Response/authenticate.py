from pydantic import BaseModel

class ServerAuthenticateResponse(BaseModel):
    """
    サーバー認証レスポンスモデル
    """
    session: str
    expiration: int