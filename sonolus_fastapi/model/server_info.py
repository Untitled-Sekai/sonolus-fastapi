from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from .text import LocalizationText

class ServerInfoButton(BaseModel):
    """サーバー情報ボタン - TypeScriptのServerInfoButtonに相当"""
    type: str


class ServerConfiguration(BaseModel):
    """サーバー設定情報"""
    options: Dict[str, Any] = {}


class ServerBanner(BaseModel):
    """サーバーバナー情報"""
    type: str = "ServerBanner"
    hash: str
    url: str


class ServerInfoSection(BaseModel):
    """サーバー情報セクション（レベル、スキンなど）"""
    items: List[Dict[str, Any]] = []
    search: Dict[str, Any] = {}


class ServerInfo(BaseModel):
    """Sonolusサーバー情報レスポンス - TypeScriptのServerInfoに相当"""
    title: LocalizationText
    description: Optional[LocalizationText] = None
    buttons: List[ServerInfoButton] = []
    banner: Optional[Dict[str, Any]] = None
    configuration: ServerConfiguration = ServerConfiguration()
    
    # 各アイテムタイプのセクション
    levels: Optional[ServerInfoSection] = None
    skins: Optional[ServerInfoSection] = None
    backgrounds: Optional[ServerInfoSection] = None
    effects: Optional[ServerInfoSection] = None
    particles: Optional[ServerInfoSection] = None
    engines: Optional[ServerInfoSection] = None
    replays: Optional[ServerInfoSection] = None
    posts: Optional[ServerInfoSection] = None
    playlists: Optional[ServerInfoSection] = None
    rooms: Optional[ServerInfoSection] = None