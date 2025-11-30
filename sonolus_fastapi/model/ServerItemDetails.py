from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List, Union
from .ServerOption import ServerForm
from .sections import ServerItemSection

T = TypeVar('T')

class ServerItemLeaderboard(BaseModel):
    name: str
    title: str
    description: Optional[str] = None

class ServerItemDetails(BaseModel, Generic[T]):
    item: T
    description: Optional[str] = None
    actions: List[ServerForm] = Field(default_factory=list)
    hasCommunity: bool
    leaderboards: List[ServerItemLeaderboard] = Field(default_factory=list)
    sections: List[ServerItemSection] = Field(default_factory=list)