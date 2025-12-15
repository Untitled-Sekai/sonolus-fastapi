from __future__ import annotations
from .server_slot import ServerInfoSlot, ServerAuthenticateSlot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sonolus_fastapi.index import Sonolus

class ServerNamespace:
    def __init__(self, sonolus: "Sonolus"):
        self.server_info = ServerInfoSlot(sonolus)
        self.authenticate = ServerAuthenticateSlot(sonolus)