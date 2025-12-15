import time

from sonolus_fastapi import Sonolus, SonolusSpa
from sonolus_fastapi.model.items.post import PostItem
from sonolus_fastapi.model.ServerItemDetails import ServerItemDetails
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



@sonolus.post.detail(ServerItemDetails) # Postの詳細ハンドラーを登録 Register Post detail handler
async def get_post_detail(ctx, name: str): # Postの詳細を取得 Get Post details
    post = sonolus.ItemMemory.Post.get_name(name) # メモリからPostItemを取得 Get PostItem from memory
    if post is None: # 存在しない場合はNoneを返す If not found,
        return None # return None
    
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