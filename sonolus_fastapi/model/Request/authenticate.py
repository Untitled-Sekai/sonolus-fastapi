from pydantic import BaseModel, Field
from typing import Optional
from ..userprofile import ServiceUserProfile

class ServerAuthenticateRequest(BaseModel):
    """
    サーバー認証リクエストモデル
    """
    type: str
    address: str  
    time: int
    user_profile: ServiceUserProfile = Field(..., alias='userProfile')
    
    class Config:
        populate_by_name = True
        extra = 'ignore'
        validate_by_name = True