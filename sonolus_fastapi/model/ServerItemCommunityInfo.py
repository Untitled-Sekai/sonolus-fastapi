from pydantic import BaseModel
from .ServerItemCommunityComment import ServerItemCommunityComment
from .ServerOption import ServerForm

class ServerItemCommunityInfo(BaseModel):
    actions: list[ServerForm] = []
    topComments: list[ServerItemCommunityComment] = []