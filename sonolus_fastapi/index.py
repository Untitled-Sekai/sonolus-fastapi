from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from .model.ServerOption import ServerForm
from .utils.pack import set_pack_memory

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
        version: str = "1.0.2",
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
        # self.sonolus_router = SonolusRouter(version=version)
        self.version = version
        
        self.headers = { "Sonolus-Version": self.version }

        if enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
    def setup_routes(self):
        """ルートをセットアップ"""
            
    def server_info_router(self):
        """
        サーバー情報ルーター
        This is the server info router.
        """     

    def info_router(self):
        """
        Typeごとのinfoルーター
        This is the info router for each type.
        """
        
    def list_router(self):
        """
        Typeごとのlistルーター
        This is the list router for each type.
        """
        
    def detail_router(self):
        """
        Typeごとのdetailルーター
        This is the detail router for each type.
        """
            
    def load(self, path: str):
        """
        Sonolus packでパックされたものを読み込みます。
        Load a pack packed with Sonolus pack.
        """
        import os
        repository_path = os.path.join(path, 'repository')
        db_path = os.path.join(path, 'db.json')
        set_pack_memory(db_path)
        self.app.mount('/sonolus/repository', StaticFiles(directory=repository_path), name="repository")
            
    def run(self):
        import uvicorn
        print(f"Starting Sonolus server on port {self.port}...")
        uvicorn.run(self.app, host='0.0.0.0', port=self.port)