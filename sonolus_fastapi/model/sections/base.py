from pydantic import BaseModel
from typing import Optional, List, Union, Literal, TypeVar, Generic
from ..common import Text, Icon
from ..ServerOption import ServerForm

T = TypeVar('T')

class ServerItemSectionTyped(BaseModel, Generic[T]):
    """ServerItemSectionTypedはアイテムセクションの情報を提供"""
    title: str
    icon: Optional[str] = None
    description: Optional[str] = None
    help: Optional[str] = None
    itemType: str
    items: List[T] = []
    search: Optional[ServerForm] = None
    searchValues: Optional[str] = None
