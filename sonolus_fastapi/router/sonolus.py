from fastapi import APIRouter
from typing import Optional

class SonolusRouter:
    def __init__ (self, prefix: str = '/sonolus', version: Optional[str] = None):
        """
        Sonolus APIのルーターを初期化します。
        Initializes the Sonolus API router.
        """
        self.router = APIRouter(prefix=prefix)
        self.version = version
        self.headers = { "Sonolus-Version": self.version } if self.version else {}
        self._setup_routes()
        
    def _setup_routes(self):
        """
        ルーターのセットアップを行います。
        Sets up the router routes.
        """