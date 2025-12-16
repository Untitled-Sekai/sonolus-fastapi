from ..model.userprofile import ServiceUserProfile
from typing import Optional, Protocol

class SessionData:
    def __init__(self, session: str, expiretion: int, profile: ServiceUserProfile):
        self.session = session
        self.expiretion = expiretion
        self.profile = profile
        
class SessionStore(Protocol):
    def get(self, session: str) -> Optional[SessionData]:
        ...
    
    def set(self, session: str, data: SessionData) -> None:
        ...
    
    def delete(self, session: str) -> None:
        ...
        
class MemorySessionStore:
    def __init__(self):
        self._store: dict[str, SessionData] = {}

    def get(self, session: str):
        return self._store.get(session)

    def set(self, session: str, data: SessionData):
        self._store[session] = data

    def delete(self, session: str):
        self._store.pop(session, None)
