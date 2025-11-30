from pydantic import BaseModel
from .ServerOption import ServerForm

class ServerItemCommunityComment(BaseModel):
    name: str
    author: str
    time: int
    content: str
    actions: list[ServerForm] = []