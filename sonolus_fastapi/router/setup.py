from fastapi import APIRouter
from info import InfoRouter
from typing import Optional

class SetupRouter:
    """
    Sonolusの基礎的なAPIルートを設定するためのルータークラスです。
    Router class for setting up basic Sonolus API routes.
    """
    def __init__(self):
        """
        ルーターを初期化します。
        Initializes the router.
        """