from pydantic import BaseModel
from typing import List, Optional

class ServerSubmitItemCommunityActionResponse(BaseModel):
    key: str
    hashes: List[str]
    shouldUpdateCommunity: Optional[bool] = None
    shouldUpdateComments: Optional[bool] = None
    shouldNavigateCommentsToPage: Optional[int] = None