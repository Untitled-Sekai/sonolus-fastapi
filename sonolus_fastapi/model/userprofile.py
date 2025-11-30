from pydantic import BaseModel, Field
from typing import List, NewType

ServiceUserId = NewType('ServiceUserId', str)

class ServiceUserProfile(BaseModel):
    """
    サービスユーザープロファイルのデータモデル
    """
    id: ServiceUserId
    handle: str
    name: str
    avatar_type: str = Field(..., alias='avatarType')
    avatar_foreground_type: str = Field(..., alias='avatarForegroundType')
    avatar_foreground_color: str = Field(..., alias='avatarForegroundColor')
    avatar_background_type: str = Field(..., alias='avatarBackgroundType')
    avatar_background_color: str = Field(..., alias='avatarBackgroundColor')
    banner_type: str = Field(..., alias='bannerType')
    about_me: str = Field(..., alias='aboutMe')
    favorites: List[str]
    
    class Config:
        validate_by_name = True
        populate_by_name = True