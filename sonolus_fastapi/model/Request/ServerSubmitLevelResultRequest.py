from pydantic import BaseModel
from ..items.replay import ReplayItem

class ServerSubmitLevelResultRequest(BaseModel):
    """
    レベル結果提出リクエストモデル
    """
    replay: ReplayItem
    values: str