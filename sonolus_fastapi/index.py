from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any, Literal
from .memory import (
    BackgroundMemory,
    EffectMemory,
    ParticleMemory,
    SkinMemory,
    EngineMemory,
    LevelMemory,
    PostMemory
)
from .model.ServerOption import ServerForm
from .model.items import ItemType
from .utils.item_namespace import ItemNamespace
from .utils.pack import set_pack_memory
from .utils.context import SonolusContext
from .utils.query import Query
from .router.sonolus_api import SonolusApi

class Sonolus:
    Kind = Literal["info", "list", "detail"]
    
    def __init__(
        self,
        address: str,
        port: int,
        dev: bool = False,
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
        self.address = address
        self.dev = dev
        self.version = version
        self.headers = { "Sonolus-Version": self.version }
        
        self._handlers: dict[ItemType, dict[str, object]] = {}
        self.level = ItemNamespace(self, ItemType.level)
        self.skin = ItemNamespace(self, ItemType.skin)
        self.engine = ItemNamespace(self, ItemType.engine)
        self.background = ItemNamespace(self, ItemType.background)  
        self.effect = ItemNamespace(self, ItemType.effect)
        self.particle = ItemNamespace(self, ItemType.particle)
        self.post = ItemNamespace(self, ItemType.post)
        self.replay = ItemNamespace(self, ItemType.replay)

        # APIルーターを初期化・登録
        self.api = SonolusApi(self)
        self.api.register(self.app)

        if enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
    def build_context(self, request: Request) -> SonolusContext:
        # リクエストからコンテキストを構築
        return SonolusContext(
            user_handle=request.headers.get("Sonolus-User-Handle"),
            is_dev=self.dev
        )
    
    def build_query(self, item_type: ItemType, request: Request) -> Query:
        # クエリパラメータを取得してQueryオブジェクトを構築
        return Query(dict(request.query_params))

    def _register_handler(self, item_type: ItemType, kind: Kind, descriptor: object):
        self._handlers.setdefault(item_type, {})[kind] = descriptor
        
    def get_handler(self, item_type: ItemType, kind: Kind):
        return self._handlers.get(item_type, {}).get(kind)

    class ItemMemory:
        Background = BackgroundMemory
        Effect = EffectMemory
        Particle = ParticleMemory
        Skin = SkinMemory
        Engine = EngineMemory
        Level = LevelMemory
        Post = PostMemory
            
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


# -------------------------


class SonolusSpa:
    def __init__(
        self,
        app: FastAPI,
        path: str,
        mount: str = "/",
        fallback: str = "index.html"
    ):
        """
        SPA配信
        """

        self.app = app
        self.path = path
        self.mount = mount
        self.fallback = fallback

    def mount_spa(self):
        self.app.mount(
            self.mount, StaticFiles(directory=self.path, html=True), name="spa"
        )