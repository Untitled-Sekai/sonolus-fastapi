# example2.py

import time
from sonolus_fastapi import Sonolus
from sonolus_fastapi.backend import StorageBackend
from sonolus_fastapi.model.text import SonolusText
from sonolus_fastapi.model.icon import SonolusIcon

from sonolus_fastapi.model.items import PostItem
from sonolus_fastapi.model.sections import PostSection

from sonolus_fastapi.model import ServerItemInfo, ServerItemList, ServerItemDetails, SonolusServerInfo, SonolusConfiguration, SonolusButton, SonolusButtonType

from sonolus_fastapi.pack import freepackpath

sonolus = Sonolus(
    address="https://example.com",
    port=8000,
    dev=False,
    enable_cors=True,
    backend=StorageBackend.DATABASE, 
    backend_options={"url": "sqlite:////data/sonolus.db"}
)

sonolus.load(freepackpath)

# Create New Item
now = int(time.time() * 1000) # to milliseconds
new_post = PostItem(
    name="example-post-1",
    author="example-author",
    title="Example Post",
    tags=[],
    description="This is an example post item.",
    time=now,
    thumbnail=None
)
sonolus.items.post.add(new_post)

# Server Info

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

# Define Handlers

@sonolus.post.info(ServerItemInfo)
async def get_post_info(ctx) -> ServerItemInfo:
    posts = sonolus.items.post.list()
    
    section = PostSection(
        title=SonolusText.POST,
        icon=SonolusIcon.Post,
        items=posts
    )
    return ServerItemInfo(
        creates=[],
        sections=[section],
        searches=[],
        banner=None,
    )
    
@sonolus.post.list(ServerItemList)
async def list_post(ctx, query) -> ServerItemList:
    posts = sonolus.items.post.list()
    
    return ServerItemList(
        pagecount=1,
        items=posts
    )
    
@sonolus.post.detail(ServerItemDetails)
async def detail_post(ctx, name: str) -> ServerItemDetails:
    post = sonolus.items.post.get(name)
    return ServerItemDetails(
        item=post,
        description="Example post detail",
        hasCommunity=False,
        sections=[],
        actions=[],
        leaderboards=[]
    )

if __name__ == "__main__":
    sonolus.run()