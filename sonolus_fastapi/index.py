from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any, Literal
from .model.items import (
    BackgroundItem,
    EffectItem,
    ParticleItem,
    SkinItem,
    EngineItem,
    LevelItem,
    PostItem
)
from .backend import StorageBackend, StoreFactory
from .model.ServerOption import ServerForm
from .search.registry import SearchRegistry
from .model.items import ItemType
from .utils.item_namespace import ItemNamespace
from .utils.server_namespace import ServerNamespace
from .utils.pack import set_pack_memory
from .utils.context import SonolusContext
from .utils.query import Query
from .utils.session import SessionStore, MemorySessionStore
from .router.sonolus_api import SonolusApi

class Sonolus:
    Kind = Literal["info", "list", "detail", "actions"]
    
    def __init__(
        self,
        address: str,
        port: int,
        dev: bool = False,
        session_store: Optional[SessionStore] = None,
        version: str = "1.0.2",
        enable_cors: bool = True,
        backend: StorageBackend = StorageBackend.MEMORY,
        **backend_options,
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
        factory = StoreFactory(backend, **backend_options)
        
        self.app = FastAPI()
        self.port = port
        self.address = address
        self.dev = dev
        self.version = version
        self.items = ItemStores(factory)
        
        self._handlers: dict[ItemType, dict[str, object]] = {}
        self._server_handlers: dict[str, object] = {}
        self._repository_paths: List[str] = []
        self._configuration_options: List[str] = []  # オプションのクエリ名を保存
        self._configuration_option_types: Dict[str, str] = {}  # オプションの型を保存
        
        self.server = ServerNamespace(self)
        self.level = ItemNamespace(self, ItemType.level)
        self.skin = ItemNamespace(self, ItemType.skin)
        self.engine = ItemNamespace(self, ItemType.engine)
        self.background = ItemNamespace(self, ItemType.background)  
        self.effect = ItemNamespace(self, ItemType.effect)
        self.particle = ItemNamespace(self, ItemType.particle)
        self.post = ItemNamespace(self, ItemType.post)
        self.replay = ItemNamespace(self, ItemType.replay)

        self.session_store = session_store or MemorySessionStore()
        self.search = SearchRegistry()
        
        # リポジトリファイルを提供するカスタムエンドポイントを先に追加
        self._setup_repository_handler()
        
        self.api = SonolusApi(self)
        self.api.register(self.app)

        @self.app.middleware('http')
        async def sonolus_version_middleware(request: Request, call_next):
            response = await call_next(request)
            
            if request.url.path.startswith('/sonolus'):
                response.headers['Sonolus-Version'] = self.version
            
            return response

        if enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
    def build_context(self, request: Request, request_body: Any = None) -> SonolusContext:
        # 設定されたオプションの値をクエリパラメータから取得し、型変換を行う
        options = {}
        for option_query in self._configuration_options:
            if option_query in request.query_params:
                raw_value = request.query_params.get(option_query)
                option_type = self._configuration_option_types.get(option_query)
                
                # 型に応じて変換
                if option_type == "toggle":
                    # toggleは "0" / "1" の文字列なのでbooleanに変換
                    options[option_query] = raw_value == "1" or raw_value.lower() == "true"
                elif option_type == "slider":
                    # sliderは数値なのでint/floatに変換を試行
                    try:
                        if '.' in raw_value:
                            options[option_query] = float(raw_value)
                        else:
                            options[option_query] = int(raw_value)
                    except ValueError:
                        options[option_query] = raw_value  # 変換失敗時は文字列のまま
                else:
                    # その他（text, textArea, select, file等）は文字列のまま
                    options[option_query] = raw_value
        
        return SonolusContext(
            user_session=request.headers.get("Sonolus-Session"),
            request=request_body,
            localization=request.query_params.get("localization"),
            options=options if options else None,
            is_dev=self.dev
        )
        
    def build_query(self, item_type, request):
        key = item_type.value
        form = self.search.get_form(key)
        model = self.search.get_query_model(key)

        raw = {
            k: v[0] if isinstance(v, list) else v
            for k, v in request.query_params.multi_items()
        }

        if model is None:
            return raw

        return model.model_validate(raw)

    def _register_handler(self, item_type: ItemType, kind: Kind, descriptor: object):
        self._handlers.setdefault(item_type, {})[kind] = descriptor
        
    def _register_server_handler(self, kind: str, descriptor: object):
        self._server_handlers[kind] = descriptor
        
    def get_handler(self, item_type: ItemType, kind: Kind):
        return self._handlers.get(item_type, {}).get(kind)
        
    def get_server_handler(self, kind: str):
        return self._server_handlers.get(kind)
    
    def register_configuration_options(self, options: List):
        """Configuration optionsを登録し、クエリ名を保存"""
        if options:
            for option in options:
                if hasattr(option, 'query'):
                    self._configuration_options.append(option.query)
                    # オプションの型を保存
                    if hasattr(option, 'type'):
                        self._configuration_option_types[option.query] = option.type
    
    def _setup_repository_handler(self):
        """リポジトリファイルを提供するハンドラーをセットアップ"""
        from fastapi import HTTPException
        from fastapi.responses import FileResponse
        import os
        
        @self.app.get("/sonolus/repository/{file_hash}")
        async def get_repository_file(file_hash: str):
            """リポジトリファイルを検索して提供"""
            # 各リポジトリパスでファイルを検索
            for repo_path in self._repository_paths:
                file_path = os.path.join(repo_path, file_hash)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    return FileResponse(file_path)
            
            # ファイルが見つからない場合は404エラー
            raise HTTPException(status_code=404, detail="File not found")
            
    def load(self, path: str):
        """
        Sonolus packでパックされたものを読み込みます。
        Load a pack packed with Sonolus pack.
        """
        import os
        repository_path = os.path.join(path, 'repository')
        db_path = os.path.join(path, 'db.json')
        set_pack_memory(db_path, self)
        
        if repository_path not in self._repository_paths:
            self._repository_paths.append(repository_path)
            
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
        import os
        from fastapi import HTTPException
        from fastapi.responses import FileResponse
        
        self.app.mount(
            "/static", StaticFiles(directory=self.path), name="static"
        )
        
        @self.app.get("/{full_path:path}")
        async def spa_handler(full_path: str):
            file_path = os.path.join(self.path, full_path)
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return FileResponse(file_path)
            
            fallback_path = os.path.join(self.path, self.fallback)
            if os.path.exists(fallback_path):
                return FileResponse(fallback_path)
            
            raise HTTPException(status_code=404, detail="File not found")
        
# -------------------------

class ItemStores:
    def __init__(self, factory: StoreFactory):
        self.post = factory.create(PostItem)
        self.level = factory.create(LevelItem)
        self.engine = factory.create(EngineItem)
        self.skin = factory.create(SkinItem)
        self.background = factory.create(BackgroundItem)
        self.effect = factory.create(EffectItem)
        self.particle = factory.create(ParticleItem)
    
    def override(self, **stores):
        for key, store in stores.items():
            setattr(self, key, store)