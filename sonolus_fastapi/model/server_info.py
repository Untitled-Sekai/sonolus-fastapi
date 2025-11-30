from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from .text import LocalizationText
from .base import SonolusResourceLocator


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
    """Sonolusサーバー情報レスポンス"""
    title: LocalizationText
    description: Optional[LocalizationText] = None
    banner: Optional[ServerBanner] = None
    configuration: ServerConfiguration = ServerConfiguration()
    
    # 各アイテムタイプのセクション
    levels: ServerInfoSection = ServerInfoSection()
    skins: ServerInfoSection = ServerInfoSection() 
    backgrounds: ServerInfoSection = ServerInfoSection()
    effects: ServerInfoSection = ServerInfoSection()
    particles: ServerInfoSection = ServerInfoSection()
    engines: ServerInfoSection = ServerInfoSection()
    replays: Optional[ServerInfoSection] = None
    posts: Optional[ServerInfoSection] = None
    playlists: Optional[ServerInfoSection] = None
    rooms: Optional[ServerInfoSection] = None