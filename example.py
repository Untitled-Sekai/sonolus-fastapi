import time

from sonolus_fastapi import Sonolus
from sonolus_fastapi.model.items.post import PostItem
from sonolus_fastapi.pack import freepackpath

sonolus = Sonolus(
    address='https://example.com', # サーバーアドレスを指定してください Specify your server address
    port=8000, # サーバーポートを指定してください Specify your server port
    enable_cors=True, # CORSを有効にするかどうか Whether to enable CORS
)

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

sonolus.load(freepackpath) # Sonolus packのパスを指定してください Specify the path to the Sonolus pack

@sonolus.app.get("/hoge") # ルートエンドポイントを追加 Add root endpoint
def huga():
    return {"message": "huga"}

if __name__ == "__main__":
    sonolus.run() # サーバーを起動します Start the server