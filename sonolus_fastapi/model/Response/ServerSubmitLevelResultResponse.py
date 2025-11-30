from pydantic import BaseModel

class ServerSubmitLevelResultResponse(BaseModel):
    """
    レベル結果提出レスポンスモデル
    """
    key: str
    hashes: list[str]