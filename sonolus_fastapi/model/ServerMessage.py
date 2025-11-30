from pydantic import BaseModel

class ServerMessage(BaseModel):
    """
    サーバーメッセージモデル
    """
    message: str