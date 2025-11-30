from pydantic import BaseModel
from typing import Optional
from .ServerItemCommunityComment import ServerItemCommunityComment

class ServerItemCommunityCommentList(BaseModel):
    pageCount: int
    cursor: Optional[str] = None
    comments: list[ServerItemCommunityComment]