import time

from fastapi import HTTPException
from sonolus_fastapi import Sonolus
from sonolus_fastapi.model.base import SonolusServerInfo, SonolusConfiguration, SonolusButton, SonolusButtonType
from sonolus_fastapi.model.items.post import PostItem
from sonolus_fastapi.model.ServerItemInfo import ServerItemInfo
from sonolus_fastapi.model.ServerItemList import ServerItemList
from sonolus_fastapi.model.sections import BackgroundSection
from sonolus_fastapi.model.ServerItemDetails import ServerItemDetails
from sonolus_fastapi.model.Request.authenticate import ServerAuthenticateRequest
from sonolus_fastapi.model.Response.authenticate import ServerAuthenticateResponse
from sonolus_fastapi.utils.generate import generate_random_string
from sonolus_fastapi.pack import freepackpath

# Sonolusインスタンスを作成 Create Sonolus instance

sonolus = Sonolus(
    address='https://example.com', # サーバーアドレスを指定してください Specify your server address
    port=8000, # サーバーポートを指定してください Specify your server port
    enable_cors=True, # CORSを有効にするかどうか Whether to enable CORS
    dev=True, # 開発モード Development mode
)

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
sonolus.ItemMemory.Post.push(post_item) # メモリにPostItemを追加 Add PostItem to memory



# ---------------------------------------- 

# Sonolusパックを読み込む Load Sonolus pack
sonolus.load(freepackpath) # Sonolus packのパスを指定してください Specify the path to the Sonolus pack

# ---------------------------------------- 

# -- ハンドラーの登録 Register handlers

@sonolus.server.server_info(SonolusServerInfo) # サーバー情報ハンドラーを登録 Register server info handler
async def get_server_info(ctx):
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
            options=[]
        ),
        banner=None,
    )
    
@sonolus.server.authenticate(ServerAuthenticateResponse) # 認証ハンドラーを登録 Register authenticate handler
async def authenticate(ctx): # 認証処理 Authentication process
    session = generate_random_string(16) # セッションIDを生成 Generate session ID
    expiration = int(time.time() * 1000) + 3600 * 1000 # 有効期限を1時間後に設定 Set expiration to 1 hour later
    
    return ServerAuthenticateResponse( # 認証レスポンスを返す Return authentication response
        session=session, # セッションID Session ID
        expiration=expiration, # 有効期限 Expiration
    )

@sonolus.post.detail(ServerItemDetails) # Postの詳細ハンドラーを登録 Register Post detail handler
async def get_post_detail(ctx, name: str): # Postの詳細を取得 Get Post details
    post = sonolus.ItemMemory.Post.get_name(name) # メモリからPostItemを取得 Get PostItem from memory
    
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
async def get_background_info(ctx): # Backgroundの情報を取得 Get Background info
    
    background_section = BackgroundSection(
        title="Background",
        itemType="background", 
        items=sonolus.ItemMemory.Background.list_all() # メモリから全てのBackgroundItemを取得 Get all BackgroundItems from memory
    )
    
    return ServerItemInfo( # ServerItemInfoを返す Return ServerItemInfo
        creates=[], # 作成フォームのリスト List of create forms
        searches=[], # 検索フォームのリスト List of search forms
        sections=[background_section], # セクションのリスト List of sections
        banner=None, # バナー Banner
    )
    
@sonolus.background.list(ServerItemList) # Backgroundのリストハンドラーを登録 Register Background list handler
async def get_background_list(ctx, query): # Backgroundのリストを取得 Get Background list
    backgrounds = sonolus.ItemMemory.Background.list_all() # メモリから全てのBackgroundItemを取得 Get all BackgroundItems from memory
    
    # BackgroundItemオブジェクトを辞書に変換 Convert BackgroundItem objects to dictionaries
    background_dicts = [bg.model_dump() for bg in backgrounds]
    
    return ServerItemList( # ServerItemListを返す Return ServerItemList
        pageCount=1, # ページ数 Page count
        items=background_dicts, # BackgroundItemのリスト（辞書形式） List of BackgroundItems (as dictionaries)
    )
    
@sonolus.background.detail(ServerItemDetails) # Backgroundの詳細ハンドラーを登録 Register Background detail handler
async def get_background_detail(ctx, name: str): # Backgroundの詳細を取得 Get Background
    background = sonolus.ItemMemory.Background.get_name(name) # メモリからBackgroundItemを取得 Get BackgroundItem from memory
    
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

if __name__ == "__main__":
    sonolus.run() # サーバーを起動します Start the server