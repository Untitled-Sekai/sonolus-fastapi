from pydantic import BaseModel
from typing import List
from .ServerItemLeaderboardRecord import ServerItemLeaderboardRecord

class ServerItemLeaderboardDetails(BaseModel):
    topRecords: List[ServerItemLeaderboardRecord]