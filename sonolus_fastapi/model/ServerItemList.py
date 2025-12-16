from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, TypeVar
from .ServerOption import ServerForm

T = TypeVar('T')

class ServerItemList(BaseModel):
    # https://wiki.sonolus.com/ja/custom-server-specs/endpoints/get-sonolus-type-list
    """
    サーバーのアイテムリストを定義
    """
    pageCount: int = Field(..., description="ページ数")
    items: List[T] = Field(default_factory=list, description="アイテムのリスト") # 一ページ20個まで
    searches: Optional[List[ServerForm]] = Field(None, description="検索フォームのリスト")