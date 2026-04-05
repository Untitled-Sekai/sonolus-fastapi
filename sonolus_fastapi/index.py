from fastapi import FastAPI, Request, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any, Literal
from sonolus_models import (
    BackgroundItem,
    EffectItem,
    ParticleItem,
    SkinItem,
    EngineItem,
    LevelItem,
    PostItem,
    UserItem,
    ReplayItem
)
from .backend import StorageBackend, StoreFactory
from sonolus_models import ServerForm
from .search.registry import SearchRegistry
from sonolus_models import ItemType
from .utils.item_namespace import ItemNamespace
from .utils.server_namespace import ServerNamespace
from .utils.pack import set_pack_memory
from .utils.context import SonolusContext
from .utils.query import Query
from .utils.session import SessionStore, MemorySessionStore
from .utils.source import override_source_fields
from .router.sonolus_api import SonolusApi
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .backend.memory import MemoryItemStore
    from .backend.json import JsonItemStore
    from .backend.database import DatabaseItemStore
    from .backend.community_accessor import ItemCommentAccessor
    from .backend.leaderboard_accessor import ItemLeaderboardAccessor

class Sonolus:
    Kind = Literal["info", "list", "detail", "actions", "upload", "result_info", "result_submit", "result_upload"]
    
    def __init__(
        self,
        address: str | None = None,
        port: int = 8000,
        dev: bool = False,
        session_store: Optional[SessionStore] = None,
        version: str = "1.1.1",
        enable_cors: bool = True,
        backend: StorageBackend = StorageBackend.MEMORY,
        app: Optional[FastAPI] = None,
        router: Optional[APIRouter] = None,
        target: Optional[FastAPI | APIRouter] = None,
        **backend_options,
    ):
        """
        
        Args:
            address: サーバーアドレス Server address
            port: サーバーポート Server port
            app: FastAPIインスタンス（指定時はこのappにもSonolusルートを登録）
            router: APIRouterインスタンス（指定時はこのrouterにSonolusルートを登録）
            target: FastAPIまたはAPIRouter（router/appより優先）
            level_search: レベル検索フォーム Level search form
            skin_search: スキン検索フォーム Skin search form
            background_search: 背景検索フォーム Background search form
            effect_search: エフェクト検索フォーム Effect search form
            particle_search: パーティクル検索フォーム Particle search form
            engine_search: エンジン検索フォーム Engine search form
            enable_cors: CORSを有効にするかどうか Whether to enable CORS
        """
        factory = StoreFactory(backend, **backend_options)
        
        if target is not None and router is not None and target is not router:
            raise ValueError("'target' and 'router' cannot be used together unless they point to the same object")

        self.app = app or FastAPI()
        self.router = APIRouter(prefix="/sonolus")
        self.port = port
        self.address = address
        self.dev = dev
        self.version = version
        self._enable_cors = enable_cors
        self._attached_targets: set[int] = set()
        self._version_header_middleware_apps: set[int] = set()
        self._cors_apps: set[int] = set()
        
        # コメントストアを作成
        from .backend import CommunityCommentStore, LeaderboardRecordStore
        self.community_comments = CommunityCommentStore(backend, **backend_options)
        self.leaderboard_records = LeaderboardRecordStore(backend, **backend_options)
        
        self.items = ItemStores(factory, self.community_comments, self.leaderboard_records)
        
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
        self.user = ItemNamespace(self, ItemType.user)

        self.session_store = session_store or MemorySessionStore()
        self.search = SearchRegistry()
        
        # リポジトリファイルを提供するカスタムエンドポイントを先に追加
        self._setup_repository_handler()
        
        self.api = SonolusApi(self, router=self.router)

        # デフォルトでは内部FastAPIに登録（従来互換）
        self.attach(self.app, enable_cors=enable_cors)

        # 外部のFastAPI/APIRouterにも必要に応じて登録
        effective_target = target or router
        if effective_target is not None and effective_target is not self.app:
            self.attach(
                effective_target,
                enable_cors=enable_cors if isinstance(effective_target, FastAPI) else None,
            )

    def attach(self, target: FastAPI | APIRouter, enable_cors: Optional[bool] = None):
        """SonolusルートをFastAPIまたはAPIRouterに登録します。"""
        target_id = id(target)
        if target_id not in self._attached_targets:
            self.api.register(target)
            self._attached_targets.add(target_id)

        if isinstance(target, FastAPI):
            self._setup_version_middleware(target)
            cors_enabled = self._enable_cors if enable_cors is None else enable_cors
            if cors_enabled:
                self._setup_cors(target)

    def _setup_version_middleware(self, app: FastAPI):
        app_id = id(app)
        if app_id in self._version_header_middleware_apps:
            return

        @app.middleware('http')
        async def sonolus_version_middleware(request: Request, call_next):
            response = await call_next(request)

            if request.url.path.startswith('/sonolus'):
                response.headers['Sonolus-Version'] = self.version

            return response

        self._version_header_middleware_apps.add(app_id)

    def _setup_cors(self, app: FastAPI):
        app_id = id(app)
        if app_id in self._cors_apps:
            return

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._cors_apps.add(app_id)

    def resolve_address(self, request: Request | None = None) -> str | None:
        """レスポンスへ埋め込む `source` 用のアドレスを解決します。"""
        if self.address:
            return self.address.rstrip("/")

        if request is not None:
            return str(request.base_url).rstrip("/")

        return None

    def apply_response_source(self, value: Any, request: Request | None = None) -> Any:
        """レスポンス内の `source` を現在の address で上書きします。"""
        return override_source_fields(value, self.resolve_address(request))
            
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

    def _register_handler(self, item_type: ItemType, kind: Kind, descriptor: object, filter_key: str | None = None):
        """ハンドラーを登録する
        
        Args:
            item_type: アイテムタイプ
            kind: ハンドラーの種類（info, list等）
            descriptor: ハンドラーディスクリプタ
            filter_key: フィルターキー（info_type, list_typeなど）。指定なしの場合はNone
        """
        if item_type not in self._handlers:
            self._handlers[item_type] = {}
        
        # filter_key が指定されている場合、内部では辞書構造にする
        if filter_key is not None:
            # 既に kind が登録されていない場合、辞書を作成
            if kind not in self._handlers[item_type]:
                self._handlers[item_type][kind] = {}
            # filter_key に対応するハンドラーを設定
            if not isinstance(self._handlers[item_type][kind], dict):
                # 既存のハンドラーがある場合、None キーで保存
                old_descriptor = self._handlers[item_type][kind]
                self._handlers[item_type][kind] = {None: old_descriptor}
            self._handlers[item_type][kind][filter_key] = descriptor
        else:
            # filter_key がない場合は通常通り
            self._handlers[item_type][kind] = descriptor
        
    def _register_server_handler(self, kind: str, descriptor: object):
        self._server_handlers[kind] = descriptor
    
    def _register_community_handler(self, item_type: ItemType, kind: str, descriptor: object):
        self._handlers.setdefault(item_type, {}).setdefault("community", {})[kind] = descriptor
    
    def _register_leaderboard_handler(self, item_type: ItemType, kind: str, descriptor: object):
        self._handlers.setdefault(item_type, {}).setdefault("leaderboard", {})[kind] = descriptor
        
    def get_handler(self, item_type: ItemType, kind: Kind, filter_key: str | None = None):
        """ハンドラーを取得する
        
        Args:
            item_type: アイテムタイプ
            kind: ハンドラーの種類（info, list等）
            filter_key: フィルターキー（info_type, list_typeなど）
            
        Returns:
            ハンドラーディスクリプタ、または存在しない場合はNone
        """
        handler = self._handlers.get(item_type, {}).get(kind)
        
        if handler is None:
            return None
        
        # ハンドラーが辞書の場合、filter_key で検索
        if isinstance(handler, dict):
            if filter_key is not None and filter_key in handler:
                return handler[filter_key]
            # filter_key が指定されていない場合、デフォルト（None）を返す
            elif filter_key is None and None in handler:
                return handler[None]
            else:
                return None
        
        # ハンドラーが辞書でない場合は直接返す（backward compatibility）
        return handler
        
    def get_server_handler(self, kind: str):
        return self._server_handlers.get(kind)
    
    def get_community_handler(self, item_type: ItemType, kind: str):
        return self._handlers.get(item_type, {}).get("community", {}).get(kind)
    
    def get_leaderboard_handler(self, item_type: ItemType, kind: str):
        return self._handlers.get(item_type, {}).get("leaderboard", {}).get(kind)
    
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
        
        @self.router.get("/repository/{file_hash}")
        async def get_repository_file(file_hash: str):
            """リポジトリファイルを検索して提供"""
            # 各リポジトリパスでファイルを検索
            for repo_path in self._repository_paths:
                file_path = os.path.join(repo_path, file_hash)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    return FileResponse(file_path)
            
            # ファイルが見つからない場合は404エラー
            raise HTTPException(status_code=404, detail="File not found")
            
    def load(self, path: str | List[str]):
        """
        Sonolus packでパックされたものを読み込みます。
        Load a pack packed with Sonolus pack.
        """
        import os
        
        # pathが配列の場合は各パスに対して再帰的にloadを呼び出す
        if isinstance(path, list):
            for p in path:
                self.load(p)
            return
        
        repository_path = os.path.join(path, 'repository')
        db_path = os.path.join(path, 'db.json')

        if not os.path.exists(db_path):
            raise FileNotFoundError(f"db.json not found in pack path: {path}")
        
        set_pack_memory(db_path, self)
        
        if repository_path not in self._repository_paths:
            self._repository_paths.append(repository_path)
    
    def add(self, path: str | List[str]):
        """
        追加のリポジトリディレクトリを監視対象に追加します。
        Add additional repository directories to watch.
        
        Args:
            path: リポジトリディレクトリのパス、または複数のパスのリスト
                  Repository directory path or list of paths
        """
        import os
        
        # pathが配列の場合は各パスに対して再帰的にaddを呼び出す
        if isinstance(path, list):
            for p in path:
                self.add(p)
            return
        
        # パスの存在確認
        if not os.path.exists(path):
            raise FileNotFoundError(f"Repository path not found: {path}")
        
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Path is not a directory: {path}")
        
        # 絶対パスに変換
        abs_path = os.path.abspath(path)
        
        # 重複チェックして追加
        if abs_path not in self._repository_paths:
            self._repository_paths.append(abs_path)
            
    def run(self):
        """
        サーバーを起動します。本番環境では、gunicornやuvicornを直接実行することを推奨します。
        
        Start the server. In production environments, we recommend running gunicorn or uvicorn directly.
        """
        import uvicorn
        print("----------------------------------------")
        print("This is recommended to be used in development only.")
        print("In production enviroments, we recommend using the FastAPI class in sonolus.app and running gunicorn or uvicorn directly.")
        print("----------------------------------------")
        print(f"Sonolus version: {self.version}")
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
    """アイテムストアのコレクション"""
    
    # 型ヒント用の属性定義
    post: "MemoryItemStore[PostItem] | JsonItemStore[PostItem] | DatabaseItemStore[PostItem]"
    level: "MemoryItemStore[LevelItem] | JsonItemStore[LevelItem] | DatabaseItemStore[LevelItem]"
    engine: "MemoryItemStore[EngineItem] | JsonItemStore[EngineItem] | DatabaseItemStore[EngineItem]"
    skin: "MemoryItemStore[SkinItem] | JsonItemStore[SkinItem] | DatabaseItemStore[SkinItem]"
    background: "MemoryItemStore[BackgroundItem] | JsonItemStore[BackgroundItem] | DatabaseItemStore[BackgroundItem]"
    effect: "MemoryItemStore[EffectItem] | JsonItemStore[EffectItem] | DatabaseItemStore[EffectItem]"
    particle: "MemoryItemStore[ParticleItem] | JsonItemStore[ParticleItem] | DatabaseItemStore[ParticleItem]"
    replay: "MemoryItemStore[ReplayItem] | JsonItemStore[ReplayItem] | DatabaseItemStore[ReplayItem]"
    user: "MemoryItemStore[UserItem] | JsonItemStore[UserItem] | DatabaseItemStore[UserItem]"
    
    # コメントアクセサ（オプショナル）
    level_comments: Optional["ItemCommentAccessor"]
    skin_comments: Optional["ItemCommentAccessor"]
    background_comments: Optional["ItemCommentAccessor"]
    effect_comments: Optional["ItemCommentAccessor"]
    particle_comments: Optional["ItemCommentAccessor"]
    engine_comments: Optional["ItemCommentAccessor"]
    post_comments: Optional["ItemCommentAccessor"]
    replay_comments: Optional["ItemCommentAccessor"]
    
    # リーダーボードアクセサ（オプショナル）
    level_leaderboards: Optional["ItemLeaderboardAccessor"]
    skin_leaderboards: Optional["ItemLeaderboardAccessor"]
    background_leaderboards: Optional["ItemLeaderboardAccessor"]
    effect_leaderboards: Optional["ItemLeaderboardAccessor"]
    particle_leaderboards: Optional["ItemLeaderboardAccessor"]
    engine_leaderboards: Optional["ItemLeaderboardAccessor"]
    post_leaderboards: Optional["ItemLeaderboardAccessor"]
    replay_leaderboards: Optional["ItemLeaderboardAccessor"]
    
    def __init__(self, factory: StoreFactory, comment_store=None, record_store=None):
        self.post = factory.create(PostItem)
        self.level = factory.create(LevelItem)
        self.engine = factory.create(EngineItem)
        self.skin = factory.create(SkinItem)
        self.background = factory.create(BackgroundItem)
        self.effect = factory.create(EffectItem)
        self.particle = factory.create(ParticleItem)
        self.replay = factory.create(ReplayItem)
        self.user = factory.create(UserItem)
        
        # コメントアクセサ
        if comment_store is not None:
            from .backend.community_accessor import ItemCommentAccessor
            self.level_comments = ItemCommentAccessor(ItemType.level, comment_store)
            self.skin_comments = ItemCommentAccessor(ItemType.skin, comment_store)
            self.background_comments = ItemCommentAccessor(ItemType.background, comment_store)
            self.effect_comments = ItemCommentAccessor(ItemType.effect, comment_store)
            self.particle_comments = ItemCommentAccessor(ItemType.particle, comment_store)
            self.engine_comments = ItemCommentAccessor(ItemType.engine, comment_store)
            self.post_comments = ItemCommentAccessor(ItemType.post, comment_store)
            self.replay_comments = ItemCommentAccessor(ItemType.replay, comment_store)
        
        # リーダーボードアクセサ
        if record_store is not None:
            from .backend.leaderboard_accessor import ItemLeaderboardAccessor
            self.level_leaderboards = ItemLeaderboardAccessor(ItemType.level, record_store)
            self.skin_leaderboards = ItemLeaderboardAccessor(ItemType.skin, record_store)
            self.background_leaderboards = ItemLeaderboardAccessor(ItemType.background, record_store)
            self.effect_leaderboards = ItemLeaderboardAccessor(ItemType.effect, record_store)
            self.particle_leaderboards = ItemLeaderboardAccessor(ItemType.particle, record_store)
            self.engine_leaderboards = ItemLeaderboardAccessor(ItemType.engine, record_store)
            self.post_leaderboards = ItemLeaderboardAccessor(ItemType.post, record_store)
            self.replay_leaderboards = ItemLeaderboardAccessor(ItemType.replay, record_store)
    
    def override(self, **stores):
        for key, store in stores.items():
            setattr(self, key, store)