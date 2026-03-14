"""
sonolus-fastapi 総合サンプル

このファイルでは次の2パターンを同時に説明します。

1) FastAPI直利用（従来どおり）
2) APIRouter組み込み利用（今回の仕様変更）

実行モードは環境変数 `SONOLUS_EXAMPLE_MODE` で切り替え:

- standalone (デフォルト): `python example.py`
- router: `SONOLUS_EXAMPLE_MODE=router uvicorn example:app --reload`

router モードでは Sonolus 側に port/address の設定は不要です。
"""

from __future__ import annotations

import os
import time
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException

from sonolus_fastapi import Sonolus
from sonolus_fastapi.backend import StorageBackend
from sonolus_fastapi.pack import freepackpath
from sonolus_fastapi.utils.context import SonolusContext
from sonolus_fastapi.utils.generate import generate_random_string
from sonolus_fastapi.utils.session import MemorySessionStore
from sonolus_models import (
	BackgroundSection,
	PostItem,
	ServerAuthenticateRequest,
	ServerAuthenticateResponse,
	ServerInfoAuthenticationButton,
	ServerInfoConfigurationButton,
	ServerInfoItemButton,
	ServerItemDetails,
	ServerItemInfo,
	ServerItemList,
	ServerTextOption,
	ServerToggleOption,
	SonolusConfiguration,
	SonolusIcon,
	SonolusServerInfo,
	SonolusText,
)


def create_configuration_options() -> list:
	"""設定オプション定義（ctx.options で取得される）。"""
	return [
		ServerToggleOption(
			query="showFeatured",
			name="Show Featured",
			required=False,
			type="toggle",
			def_=True,
		),
		ServerTextOption(
			query="keywords",
			name=SonolusText.KEYWORDS,
			required=False,
			type="text",
			def_="",
			placeholder=SonolusText.KEYWORDS_PLACEHOLDER,
			limit=100,
			shortcuts=[],
		),
	]


def seed_data(sonolus: Sonolus):
	"""メモリストアへ最小限のサンプルデータを投入。"""
	now = int(time.time() * 1000)
	post_item = PostItem(
		name="example_post",
		title="Example Post",
		version=1,
		author="pim4n",
		tags=[],
		description="This is an example post item.",
		time=now,
		thumbnail=None,
	)
	sonolus.items.post.add(post_item)


def register_handlers(sonolus: Sonolus, config_options: list):
	"""サーバー/アイテムハンドラーを登録。"""

	@sonolus.server.server_info(SonolusServerInfo)
	async def get_server_info(ctx: SonolusContext):
		return SonolusServerInfo(
			title="Example Sonolus Server",
			description="FastAPI and APIRouter compatible example",
			buttons=[
				ServerInfoAuthenticationButton(type="authentication"),
				ServerInfoItemButton(type="post"),
				ServerInfoItemButton(type="background"),
				ServerInfoConfigurationButton(type="configuration"),
			],
			configuration=SonolusConfiguration(options=config_options),
			banner=None,
		)

	@sonolus.server.authenticate(ServerAuthenticateResponse)
	async def authenticate(ctx: SonolusContext[ServerAuthenticateRequest]):
		session = generate_random_string(16)
		expiration = int(time.time() * 1000) + 3600 * 1000
		sonolus.session_store.set(session, ctx.request)
		return ServerAuthenticateResponse(session=session, expiration=expiration)

	@sonolus.post.info(ServerItemInfo)
	async def get_post_info(ctx: SonolusContext):
		return ServerItemInfo(creates=[], searches=[], sections=[], banner=None)

	@sonolus.post.list(ServerItemList)
	async def get_post_list(ctx: SonolusContext, query: Any):
		keywords = (ctx.options or {}).get("keywords", "")
		items = sonolus.items.post.list()
		if keywords:
			items = [item for item in items if keywords.lower() in item.title.lower()]
		return ServerItemList(pageCount=1, items=items)

	@sonolus.post.detail(ServerItemDetails)
	async def get_post_detail(ctx: SonolusContext, name: str):
		post = sonolus.items.post.get(name)
		if post is None:
			raise HTTPException(404, "Post item not found")

		return ServerItemDetails(
			item=post,
			description="Detail page example",
			actions=[],
			hasCommunity=False,
			leaderboards=[],
			sections=[],
		)

	@sonolus.background.info(ServerItemInfo)
	async def get_background_info(ctx: SonolusContext):
		section = BackgroundSection(
			title=SonolusText.BACKGROUND,
			icon=SonolusIcon.Heart,
			items=sonolus.items.background.list(),
		)
		return ServerItemInfo(creates=[], searches=[], sections=[section], banner=None)

	@sonolus.background.list(ServerItemList)
	async def get_background_list(ctx: SonolusContext, query: Any):
		return ServerItemList(pageCount=1, items=sonolus.items.background.list())


def create_standalone_sonolus() -> Sonolus:
	"""
	1) FastAPI直利用モード

	- Sonolus が内部で FastAPI を持つ
	- `sonolus.run()` で起動可能
	- 従来互換
	"""
	sonolus = Sonolus(
		address="https://example.com",
		port=8000,
		enable_cors=True,
		dev=True,
		session_store=MemorySessionStore(),
		backend=StorageBackend.MEMORY,
	)

	config_options = create_configuration_options()
	sonolus.register_configuration_options(config_options)
	sonolus.load(freepackpath)
	seed_data(sonolus)
	register_handlers(sonolus, config_options)

	@sonolus.app.get("/health")
	async def health():
		return {"ok": True, "mode": "standalone"}

	return sonolus


def create_router_integration() -> tuple[FastAPI, Sonolus, APIRouter]:
	"""
	2) APIRouter組み込みモード（今回の仕様）

	- Sonolus を既存 FastAPI アプリへ router として統合
	- Sonolus 側の port/address 設定は不要（必要ならデフォルトをそのまま使用）
	"""
	app = FastAPI(title="Integrated App")
	api_router = APIRouter(prefix="/api")

	sonolus = Sonolus(
		router=api_router,
		dev=True,
		session_store=MemorySessionStore(),
		backend=StorageBackend.MEMORY,
	)

	config_options = create_configuration_options()
	sonolus.register_configuration_options(config_options)
	sonolus.load(freepackpath)
	seed_data(sonolus)
	register_handlers(sonolus, config_options)

	@app.get("/health")
	async def health():
		return {"ok": True, "mode": "router"}

	app.include_router(api_router)
	return app, sonolus, api_router


MODE = os.getenv("SONOLUS_EXAMPLE_MODE", "standalone").strip().lower()

if MODE == "router":
	app, sonolus, api_router = create_router_integration()
else:
	sonolus = create_standalone_sonolus()
	app = sonolus.app


if __name__ == "__main__":
	if MODE == "router":
		import uvicorn

		print("SONOLUS_EXAMPLE_MODE=router")
		print("Run: uvicorn example:app --reload")
		uvicorn.run(app, host="0.0.0.0", port=8000)
	else:
		print("SONOLUS_EXAMPLE_MODE=standalone")
		sonolus.run()
