from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, Literal
from enum import Enum

class ItemType(str, Enum):
    """アイテムタイプの定義"""
    POST = "post"
    PLAYLIST = "playlist"
    LEVEL = "level"
    SKIN = "skin"
    BACKGROUND = "background"
    EFFECT = "effect"
    PARTICLE = "particle"
    ENGINE = "engine"
    REPLAY = "replay"
    ROOM = "room"

class SelectValue(BaseModel):
    """セレクト/マルチオプションの値"""
    name: str
    title: Union[str, Dict[str, Any]]  # Text型（多言語対応）またはstring

class ServerOptionBase(BaseModel):
    """全てのServerOptionの基底クラス"""
    query: str
    name: Union[str, Dict[str, Any]]  # Text型（多言語対応）またはstring
    description: Optional[str] = None
    required: bool

class ServerTextOption(ServerOptionBase):
    """テキスト入力オプション"""
    type: Literal["text"] = "text"
    def_: str = Field(alias="def")  # Pythonの予約語を回避
    placeholder: Union[str, Dict[str, Any]]
    limit: int
    shortcuts: List[str]
    class Config:
        populate_by_name = True

class ServerTextAreaOption(ServerOptionBase):
    """テキストエリア入力オプション"""
    type: Literal["textArea"] = "textArea"
    def_: str = Field(alias="def")
    placeholder: Union[str, Dict[str, Any]]
    limit: int
    shortcuts: List[str]
    class Config:
        populate_by_name = True

class ServerSliderOption(ServerOptionBase):
    """スライダー入力オプション"""
    type: Literal["slider"] = "slider"
    def_: float = Field(alias="def")
    min: float
    max: float
    step: float
    unit: Optional[Union[str, Dict[str, Any]]] = None
    class Config:
        populate_by_name = True

class ServerToggleOption(ServerOptionBase):
    """トグル（ON/OFF）オプション"""
    type: Literal["toggle"] = "toggle"
    def_: bool = Field(alias="def")
    class Config:
        populate_by_name = True

class ServerSelectOption(ServerOptionBase):
    """セレクト（単一選択）オプション"""
    type: Literal["select"] = "select"
    def_: str = Field(alias="def")
    values: List[SelectValue]
    class Config:
        populate_by_name = True

class ServerMultiOption(ServerOptionBase):
    """マルチ（複数選択）オプション"""
    type: Literal["multi"] = "multi"
    def_: List[bool] = Field(alias="def")
    values: List[SelectValue]
    class Config:
        populate_by_name = True

class ServerServerItemOption(ServerOptionBase):
    """サーバーアイテム（単一）オプション"""
    type: Literal["serverItem"] = "serverItem"
    item_type: ItemType = Field(alias="itemType")
    def_: Optional[str] = Field(alias="def")  # Sil型（簡略化してstringとする）
    allow_other_servers: bool = Field(alias="allowOtherServers")
    class Config:
        populate_by_name = True

class ServerServerItemsOption(ServerOptionBase):
    """サーバーアイテム（複数）オプション"""
    type: Literal["serverItems"] = "serverItems"
    item_type: ItemType = Field(alias="itemType")
    def_: List[str] = Field(alias="def")  # Sil[]型（簡略化してList[string]とする）
    allow_other_servers: bool = Field(alias="allowOtherServers")
    limit: int
    class Config:
        populate_by_name = True

class ServerCollectionItemOption(ServerOptionBase):
    """コレクションアイテムオプション"""
    type: Literal["collectionItem"] = "collectionItem"
    item_type: ItemType = Field(alias="itemType")
    class Config:
        populate_by_name = True
        
class ServerFileOption(ServerOptionBase):
    """ファイルオプション"""
    type: Literal["file"] = "file"
    def_: str = Field(alias="def")
    class Config:
        populate_by_name = True
        
# Union型でServerOptionを定義
ServerOption = Union[
    ServerTextOption,
    ServerTextAreaOption,
    ServerSliderOption,
    ServerToggleOption,
    ServerSelectOption,
    ServerMultiOption,
    ServerServerItemOption,
    ServerServerItemsOption,
    ServerCollectionItemOption,
    ServerFileOption
]

class ServerForm(BaseModel):
    """サーバーフォームの定義"""
    type: str
    title: Union[str, Dict[str, Any]]  # Text型（多言語対応）またはstring
    icon: Optional[Union[str, Dict[str, Any]]] = None  # Icon型（簡略化してstringまたはDict）
    description: Optional[str] = None
    help: Optional[str] = None
    require_confirmation: bool = Field(alias="requireConfirmation")
    options: List[ServerOption]
    
    class Config:
        validate_by_name = True
