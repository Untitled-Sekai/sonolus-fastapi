from pydantic import BaseModel, Field
from typing import Optional, Union, TypeVar, Generic, Annotated
from .base import SonolusResourceLocator

Text = Annotated[str, Field(description="テキスト型")]

Icon = Annotated[str, Field(description="アイコン型")]

class Tag(BaseModel):
    """タグ情報を提供"""
    title: str
    icon: Optional[str] = None

T = TypeVar('T')

class UseItemDefault(BaseModel):
    """デフォルトアイテムを使用"""
    useDefault: bool = True

class UseItemCustom(BaseModel, Generic[T]):
    """カスタムアイテムを使用"""
    useDefault: bool = False
    item: T

def UseItem(item_type: T) -> Union[UseItemDefault, UseItemCustom[T]]:
    """UseItem型のファクトリー関数"""
    return Union[UseItemDefault, UseItemCustom[item_type]]
