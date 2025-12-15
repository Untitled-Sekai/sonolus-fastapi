import time

from fastapi import HTTPException
from sonolus_fastapi import Sonolus
from sonolus_fastapi.model.base import SonolusServerInfo, SonolusConfiguration, SonolusButton, SonolusButtonType
from sonolus_fastapi.model.items.post import PostItem
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


# Sonolusパックを読み込む Load Sonolus pack
sonolus.load(freepackpath) # Sonolus packのパスを指定してください Specify the path to the Sonolus pack

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
    
    

@sonolus.app.get("/hoge") # ルートエンドポイントを追加 Add root endpoint
def huga():
    return {"message": "huga"}

if __name__ == "__main__":
    sonolus.run() # サーバーを起動します Start the server