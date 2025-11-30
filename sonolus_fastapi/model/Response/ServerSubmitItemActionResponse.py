from pydantic import BaseModel
from typing import Optional

class ServerSubmitItemActionResponse(BaseModel):
    key: str
    hashes: list[str]
    shouldUpdateItem: Optional[bool] = None
    shouldRemoveItem: Optional[bool] = None
    shouldNavigateToItem: Optional[str] = None
