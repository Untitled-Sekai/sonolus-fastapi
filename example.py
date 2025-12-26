import time

from fastapi import HTTPException
from sonolus_fastapi import Sonolus, SonolusSpa
from sonolus_fastapi.backend import StorageBackend
from sonolus_fastapi.model.text import SonolusText
from sonolus_fastapi.model.icon import SonolusIcon
from sonolus_fastapi.utils.context import SonolusContext
from sonolus_fastapi.model.base import SonolusServerInfo, SonolusConfiguration, SonolusButton, SonolusButtonType
from sonolus_fastapi.model.items.post import PostItem
from sonolus_fastapi.model.ServerItemInfo import ServerItemInfo
from sonolus_fastapi.model.ServerItemList import ServerItemList
from sonolus_fastapi.model.sections import BackgroundSection
from sonolus_fastapi.model.ServerItemDetails import ServerItemDetails
from sonolus_fastapi.model.Request.authenticate import ServerAuthenticateRequest
from sonolus_fastapi.model.Response.authenticate import ServerAuthenticateResponse
from sonolus_fastapi.utils.generate import generate_random_string
from sonolus_fastapi.utils.session import MemorySessionStore
from sonolus_fastapi.utils.context import SonolusContext
from sonolus_fastapi.model.ServerOption import ServerToggleOption, ServerTextOption
from sonolus_fastapi.pack import freepackpath

# Sonolusインスタンスを作成 Create Sonolus instance

config_option = [
    ServerToggleOption(
        query="test",
        name="Test Option",
        required=False,
        type="toggle",
        def_=False
    ),
    ServerTextOption(
        query='keywords',
        name=SonolusText.KEYWORDS,
        required=False,
        type='text',
        def_='',
        placeholder=SonolusText.KEYWORDS_PLACEHOLDER,
        limit=100,
        shortcuts=[]
    ),
]

sonolus = Sonolus(
    address='https://example.com', # サーバーアドレスを指定してください Specify your server address
    port=8000, # サーバーポートを指定してください Specify your server port
    enable_cors=True, # CORSを有効にするかどうか Whether to enable CORS
    dev=True, # 開発モード Development mode
    session_store=MemorySessionStore(), # セッションストアを指定 Specify session store
    backend=StorageBackend.MEMORY, # ストレージバックエンドを指定 Specify storage backend
)

# Configuration optionsを登録
sonolus.register_configuration_options(config_option)

# ---------------------------------------- 

# PostItemの例 Example of PostItem


now = int(time.time() * 1000)

post_item = PostItem(
    name="example_post",
    title="Example Post",
    version=1,
    author="Author Name",
    tags=[],
    description="This is an example post item.",
    time=now,
    thumbnail=None,
)
sonolus.items.post.add(post_item)



# ---------------------------------------- 

# Sonolusパックを読み込む Load Sonolus pack
sonolus.load(freepackpath) # Sonolus packのパスを指定してください Specify the path to the Sonolus pack

# ---------------------------------------- 

# -- ハンドラーの登録 Register handlers

@sonolus.server.server_info(SonolusServerInfo) # サーバー情報ハンドラーを登録 Register server info handler
async def get_server_info(ctx: SonolusContext): # サーバー情報を取得 Get server info
    return SonolusServerInfo(
        title="Example Sonolus Server",
        description="This is an example Sonolus server.",
        buttons=[
            SonolusButton(type=SonolusButtonType.AUTHENTICATION),
            SonolusButton(type=SonolusButtonType.POST),
            SonolusButton(type=SonolusButtonType.LEVEL),
            SonolusButton(type=SonolusButtonType.SKIN),
            SonolusButton(type=SonolusButtonType.BACKGROUND),
            SonolusButton(type=SonolusButtonType.EFFECT),
            SonolusButton(type=SonolusButtonType.PARTICLE),
            SonolusButton(type=SonolusButtonType.ENGINE),
            SonolusButton(type=SonolusButtonType.CONFIGURATION)
        ],
        configuration=SonolusConfiguration(
            options=config_option
        ),
        banner=None,
    )
    
@sonolus.server.authenticate(ServerAuthenticateResponse) # 認証ハンドラーを登録 Register authenticate handler
async def authenticate(ctx: SonolusContext[ServerAuthenticateRequest]): # 認証処理 Authentication process
    session = generate_random_string(16) # セッションIDを生成 Generate session ID
    expiration = int(time.time() * 1000) + 3600 * 1000 # 有効期限を1時間後に設定 Set expiration to 1 hour later
    
    sonolus.session_store.set(session, ctx.request)
    
    return ServerAuthenticateResponse( # 認証レスポンスを返す Return authentication response
        session=session, # セッションID Session ID
        expiration=expiration, # 有効期限 Expiration
    )

@sonolus.post.detail(ServerItemDetails) # Postの詳細ハンドラーを登録 Register Post detail handler
async def get_post_detail(ctx: SonolusContext, name: str): # Postの詳細を取得 Get Post details
    post = sonolus.items.post.get(name) # メモリからPostItemを取得 Get PostItem from memory
    
    if post is None: # PostItemが見つからない場合 If PostItem not found
        raise HTTPException(404, "Post item not found") # 404エラーを返す Return 404 error
    
    return ServerItemDetails( # ServerItemDetailsを返す Return ServerItemDetails
        item=post, # PostItem
        description="This is the detail of the example post item.", # 詳細説明 Detail description
        actions=[], # アクションのリスト List of actions
        hasCommunity=False, # コミュニティがあるかどうか Whether there is a community
        leaderboards=[], # リーダーボードのリスト List of leaderboards
        sections=[], # セクションのリスト List of sections
    )

# ----------------------------------------     
 
# アイテムの一式のハンドラーを登録 Register item set handler 
    
    
@sonolus.background.info(ServerItemInfo)
async def get_background_info(ctx: SonolusContext): # Backgroundの情報を取得 Get Background info
    
    background_section = BackgroundSection(
        title=SonolusText.BACKGROUND,
        icon=SonolusIcon.Heart,
        items=sonolus.items.background.list() # メモリから全てのBackgroundItemを取得 Get all BackgroundItems from memory
    )
    
    return ServerItemInfo( # ServerItemInfoを返す Return ServerItemInfo
        creates=[], # 作成フォームのリスト List of create forms
        searches=[], # 検索フォームのリスト List of search forms
        sections=[background_section], # セクションのリスト List of sections
        banner=None, # バナー Banner
    )
    
@sonolus.background.list(ServerItemList) # Backgroundのリストハンドラーを登録 Register Background list handler
async def get_background_list(ctx: SonolusContext, query): # Backgroundのリストを取得 Get Background list
    backgrounds = sonolus.items.background.list() # メモリから全てのBackgroundItemを取得 Get all BackgroundItems from memory
    print(f"Localization: {ctx.localization}")  # "ja" が出力される
    print(f"Options: {ctx.options}")  # オプションの値を出力
    print(query)
    return ServerItemList( # ServerItemListを返す Return ServerItemList
        pageCount=1, # ページ数 Page count
        items=backgrounds, # BackgroundItemのリスト List of BackgroundItems
    )
    
@sonolus.background.detail(ServerItemDetails) # Backgroundの詳細ハンドラーを登録 Register Background detail handler
async def get_background_detail(ctx: SonolusContext, name: str): # Backgroundの詳細を取得 Get Background
    background = sonolus.items.background.get(name) # メモリからBackgroundItemを取得 Get BackgroundItem from memory
    
    if background is None: # BackgroundItemが見つからない場合 If BackgroundItem not found
        raise HTTPException(404, "Background item not found") # 404エラーを返す Return 404 error
    
    return ServerItemDetails( # ServerItemDetailsを返す Return ServerItemDetails
        item=background, # BackgroundItem
        description="This is the detail of the example background item.", # 詳細説明 Detail description
        actions=[], # アクションのリスト List of actions
        hasCommunity=False, # コミュニティがあるかどうか Whether there is a community
        leaderboards=[], # リーダーボードのリスト List of leaderboards
        sections=[], # セクションのリスト List of sections
    )
    
# ---------------------------------------- 
    
@sonolus.app.get("/hoge") # ルートエンドポイントを追加 Add root endpoint
def huga():
    return {"message": "huga"}

# ----------------------------------------

#  SPA配信

# spa = SonolusSpa(
#     sonolus.app,
#     path="./test", # SPAの静的ファイルのパス Path to SPA static files
#     mount="/" # マウントパス Mount path
# )

if __name__ == "__main__":
    # spa.mount_spa() # SPAをマウントします Mount the SPA
    sonolus.run() # サーバーを起動します Start the server