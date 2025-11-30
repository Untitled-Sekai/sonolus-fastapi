# ここでベースとなるモデルの定義

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from .ServerOption import ServerOption

class SonolusResourceLocator(BaseModel):
    # https://wiki.sonolus.com/ja/custom-server-specs/misc/srl
    
    hash: str
    url: str


class SonolusButtonType(str, Enum):
    # https://wiki.sonolus.com/ja/custom-server-specs/endpoints/get-sonolus-info
    
    AUTHENTICATION = "authentication"
    POST = "post"
    LEVEL = "level"
    SKIN = "skin"
    BACKGROUND = "background"
    EFFECT = "effect"
    PARTICLE = "particle"
    ENGINE = "engine"
    CONFIGURATION = "configuration"

    
class SonolusButton(BaseModel):
    # ボタンの定義
    
    type: SonolusButtonType

    
class SonolusConfiguration(BaseModel):
    # サーバーの設定の情報
    options: List[ServerOption] = Field(default_factory=list)

    
class SonolusServerInfo(BaseModel):
    # サーバーの情報を定義
    # Sonolusのサーバーに入ったときの最初のメニュー
    
    title: str
    description: Optional[str] = None
    buttons: List[SonolusButton] = Field(default_factory=list)
    configuration: SonolusConfiguration = Field(default_factory=SonolusConfiguration)
    banner: Optional[SonolusResourceLocator] = None