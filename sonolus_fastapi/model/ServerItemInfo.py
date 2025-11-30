from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from .base import SonolusResourceLocator
from .ServerOption import ServerForm
from .sections import ServerItemSection

class ServerItemInfo(BaseModel):
    # https://wiki.sonolus.com/ja/custom-server-specs/endpoints/get-sonolus-type-info
    """
    サーバーのアイテム情報を定義
    """
    creates: List[ServerForm] = Field(default_factory=list)
    searches: List[ServerForm] = Field(default_factory=list)
    sections: List[ServerItemSection] = Field(default_factory=list) 
    banner: Optional[SonolusResourceLocator] = None