from pydantic import BaseModel
from typing import Union

class ServerItemLeaderboardRecord(BaseModel):
    name: str
    rank: str
    player: str
    value: str