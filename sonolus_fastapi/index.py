from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from .model.ServerOption import ServerForm

class Sonolus:
    def __init__(
        self,
        address: str,
        port: int,
        level_search: Optional[ServerForm] = None,
        skin_search: Optional[ServerForm] = None,
        background_search: Optional[ServerForm] = None,
        effect_search: Optional[ServerForm] = None,
        particle_search: Optional[ServerForm] = None,
        engine_search: Optional[ServerForm] = None,
        enable_cors: bool = True,
    ):
        """
        
        Args:
            address: サーバーアドレス Server address
            port: サーバーポート Server port
            level_search: レベル検索フォーム Level search form
            skin_search: スキン検索フォーム Skin search form
            background_search: 背景検索フォーム Background search form
            effect_search: エフェクト検索フォーム Effect search form
            particle_search: パーティクル検索フォーム Particle search form
            engine_search: エンジン検索フォーム Engine search form
            enable_cors: CORSを有効にするかどうか Whether to enable CORS
        """
        self.app = FastAPI()
        self.port = port
        
        if enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
    def run(self):
        import uvicorn
        uvicorn.run(self.app, host='0.0.0.0', port=self.port)