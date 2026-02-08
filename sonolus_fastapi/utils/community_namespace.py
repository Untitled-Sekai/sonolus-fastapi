from __future__ import annotations
from sonolus_models import ItemType
from .community_slot import CommunityInfoSlot, CommunityCommentsSlot, CommunityActionsSlot, CommunityUploadSlot, CommunityCommentActionsSlot, CommunityCommentUploadSlot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

class CommunityNamespace:
    def __init__(self, sonolus: "Sonolus", item_type: ItemType):
        self.info = CommunityInfoSlot(sonolus, item_type)
        self.comments = CommunityCommentsSlot(sonolus, item_type)
        self.actions = CommunityActionsSlot(sonolus, item_type)
        self.upload = CommunityUploadSlot(sonolus, item_type)
        self.comment_actions = CommunityCommentActionsSlot(sonolus, item_type)
        self.comment_upload = CommunityCommentUploadSlot(sonolus, item_type)
