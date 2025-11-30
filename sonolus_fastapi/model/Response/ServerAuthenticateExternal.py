from pydantic import BaseModel, Field

class ServerAuthenticateExternalResponse(BaseModel):
    """
    サーバー外部認証レスポンスモデル
    """
    message: str = Field(..., description="サーバーメッセージ")
    token: str = Field(..., description="認証トークン")
    secret: str = Field(..., description="認証シークレット")

    class Config:
        populate_by_name = True
        extra = 'ignore'
        validate_by_name = True