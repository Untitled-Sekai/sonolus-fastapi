import time
from fastapi import HTTPException

from sonolus_fastapi import Sonolus
from sonolus_fastapi.model import ServerItemInfo, ServerItemList,ServerItemDetails, SonolusServerInfo, SonolusConfiguration, SonolusButton, SonolusButtonType
from sonolus_fastapi.model.text import SonolusText
from sonolus_fastapi.model.items import PostItem
from sonolus_fastapi.model.sections import PostSection

from example0search import post_search

# -------------------------
# Sonolus instance
# -------------------------

sonolus = Sonolus(
    address="http://localhost:8000",
    port=8000,
    dev=True,
)

# Search を登録
sonolus.search.post = post_search

# -------------------------
# Dummy data
# -------------------------

now = int(time.time() * 1000)

sonolus.items.post.add(
    PostItem(
        name="example-post-1",
        author="example-author",
        title="Example Post1",
        tags=[],
        description="This is an example post item.",
        time=now,
        thumbnail=None
    )
)

sonolus.items.post.add(
    PostItem(
        name="example-post-2",
        author="example-author",
        title="Example Post2",
        tags=[],
        description="This is an example post item.",
        time=now,
        thumbnail=None
    )
)

sonolus.items.post.add(
    PostItem(
        name="example-post-3",
        author="example-author",
        title="Example Post3",
        tags=[],
        description="This is an example post item.",
        time=now,
        thumbnail=None
    )
)

# -------------------------
# Info
# -------------------------

@sonolus.server.server_info(SonolusServerInfo)
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

@sonolus.post.info(ServerItemInfo)
async def post_info(ctx):
    # 検索フォームが正しく設定されているか確認
    search_forms = [sonolus.search.post] if sonolus.search.post else []
    
    return ServerItemInfo(
        creates=[],
        searches=search_forms,
        sections=[
            PostSection(
                title=SonolusText.POST,
                items=sonolus.items.post.list(),
            )
        ],
        banner=None,
    )

# -------------------------
# List (Search / Query 実演)
# -------------------------

@sonolus.post.list(ServerItemList)
async def post_list(ctx, query):
    """
    Post一覧を取得します
    キーワード検索に対応
    """
    items = sonolus.items.post.list()

    if isinstance(query, dict) and 'keywords' in query and query['keywords']:
        items = [
            i for i in items
            if query['keywords'].lower() in i.title.lower()
        ]
    elif hasattr(query, 'keywords') and query.keywords:
        items = [
            i for i in items
            if query.keywords.lower() in i.title.lower()
        ]

    return ServerItemList(
        pageCount=1,
        items=[i.model_dump() for i in items],
        searches=[sonolus.search.post]
    )

# -------------------------
# Detail
# -------------------------

@sonolus.post.detail(ServerItemDetails)
async def post_detail(ctx, name: str):
    post = sonolus.items.post.get(name)
    if post is None:
        raise HTTPException(404, "Post not found")
    
    return ServerItemDetails(
        item=post,
        description=post.description,
        actions=[],
        hasCommunity=False,
        leaderboards=[],
        sections=[]
    )
    

# -------------------------
# Run
# -------------------------

if __name__ == "__main__":
    sonolus.run()
