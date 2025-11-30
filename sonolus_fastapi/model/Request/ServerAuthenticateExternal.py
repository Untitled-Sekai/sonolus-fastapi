from pydantic import BaseModel, Field
from ..userprofile import ServiceUserProfile

class ServerAuthenticateExternalRequest(BaseModel):
    """
    サーバー外部認証リクエストモデル
    """
    type: str
    url: str
    time: int
    user_profile: ServiceUserProfile = Field(..., alias='userProfile')
    
    class Config:
        populate_by_name = True
        extra = 'ignore'
        validate_by_name = True