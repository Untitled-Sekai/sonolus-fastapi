from fastapi import APIRouter
from typing import Optional
from ..model.base import SonolusServerInfo, SonolusButton, SonolusButtonType, SonolusConfiguration, SonolusResourceLocator

router = APIRouter()

class InfoRouter:
    def __init__(self, title: str, description: str, buttons: list[SonolusButton], configuration: SonolusConfiguration, banner: Optional[SonolusResourceLocator] = None):
        self.router = APIRouter()
        self.title = title
        self.description = description
        self.buttons = buttons
        self.configuration = configuration
        self.banner = banner
        
    def setup_route(self):
        @self.router.get('/info', response_model=SonolusServerInfo)
        async def get_server_info():
            return SonolusServerInfo(
                title=self.title,
                description=self.description,
                buttons=self.buttons,
                configuration=self.configuration,
                banner=self.banner
            )