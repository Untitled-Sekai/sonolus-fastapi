"""
sonolus-fastapi 総合サンプル

このファイルは、`sonolus-fastapi` の基本的な使い方を一通りまとめたサンプルです。

主に次の内容を含みます。

1. `FastAPI` 直利用モード
	- `Sonolus` インスタンスが内部で `FastAPI` を持つ従来の使い方
	- `sonolus.run()` でそのまま起動できます

2. `APIRouter` 組み込みモード
	- 既存の `FastAPI` アプリへ `Sonolus` を router として組み込む使い方
	- 今回追加した仕様です
	- このモードでは `Sonolus` 側に `port` や `address` を必須で持たせる必要はありません

3. ハンドラー登録の流れ
	- `server_info`
	- `authenticate`
	- `post.info/list/detail`
	- `background.info/list`

4. `source` の扱い
	- 各アイテムの `source` は保存時にはDB/JSON/メモリへ保持しません
	- 返却時にだけ `Sonolus.address` または現在のリクエストURLで動的に上書きされます
	- そのため、開発環境/本番環境/リバースプロキシ配下で柔軟に切り替えできます

実行モードは環境変数 `SONOLUS_EXAMPLE_MODE` で切り替えます。

- standalone (デフォルト): `python example.py`
- router: `SONOLUS_EXAMPLE_MODE=router uvicorn example:app --reload`

ルーティング例:

- standalone: `/sonolus/...`
- router: `/api/sonolus/...`
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
	"""
	設定オプション定義。

	ここで登録した option は、各ハンドラーの `ctx.options` から参照できます。
	たとえば `keywords` は `post.list` 内で簡易フィルタに使っています。
	"""
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
	"""
	メモリストアへ最小限のサンプルデータを投入。

	このサンプルでは `PostItem` だけを手動で追加しています。
	`source` はここで指定しなくても、レスポンス返却時に自動で補われます。
	"""
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
	"""
	サーバー/アイテムハンドラーを登録。

	この関数は `standalone` / `router` の両モードで共通利用しています。
	つまり、利用モードが変わってもハンドラーの書き方自体は同じです。
	"""

	@sonolus.server.server_info(SonolusServerInfo)
	async def get_server_info(ctx: SonolusContext):
		# Sonolus アプリ起動時に最初に参照されることが多い基本情報。
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
		# 認証の最小例。ここではランダムなセッションIDを発行しています。
		session = generate_random_string(16)
		expiration = int(time.time() * 1000) + 3600 * 1000
		sonolus.session_store.set(session, ctx.request)
		return ServerAuthenticateResponse(session=session, expiration=expiration)

	@sonolus.post.info(ServerItemInfo)
	async def get_post_info(ctx: SonolusContext):
		# Post 一覧のメタ情報。
		return ServerItemInfo(creates=[], searches=[], sections=[], banner=None)

	@sonolus.post.list(ServerItemList)
	async def get_post_list(ctx: SonolusContext, query: Any):
		# 設定オプションから値を受け取り、簡易フィルタしています。
		keywords = (ctx.options or {}).get("keywords", "")
		items = sonolus.items.post.list()
		if keywords:
			items = [item for item in items if keywords.lower() in item.title.lower()]
		return ServerItemList(pageCount=1, items=items)

	@sonolus.post.detail(ServerItemDetails)
	async def get_post_detail(ctx: SonolusContext, name: str):
		# 詳細レスポンスでも item.source は返却時に自動上書きされます。
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
		# pack から読み込んだ background をセクション表示する例。
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
	- `address` を固定しているので、返却される `source` もこの値になります
	"""
	# `address` を明示すると、全レスポンスの `source` はこのURL基準になります。
	# 本番で固定URLが決まっている場合はこちらが分かりやすいです。
	sonolus = Sonolus(
		address="https://example.com",
		port=8000,
		enable_cors=True,
		dev=True,
		session_store=MemorySessionStore(),
		backend=StorageBackend.MEMORY,
	)

	config_options = create_configuration_options()
	# Configuration option を登録すると `ctx.options` から参照できます。
	sonolus.register_configuration_options(config_options)
	# Sonolus pack を読み込みます。repository 配信も自動で有効になります。
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
	- Sonolus 側の port/address 設定は不要
	- `address=None` のままなら、返却時の `source` は現在のリクエストURLから自動解決されます
	- たとえば `/api` 配下へ組み込んでもハンドラーの書き方は変わりません
	"""
	app = FastAPI(title="Integrated App")
	api_router = APIRouter(prefix="/api")

	# `router=api_router` を渡すと Sonolus ルートがこの router に登録されます。
	# このとき Sonolus 内部の app とは別に、既存 FastAPI アプリへ自然に統合できます。
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

	# ここで既存アプリへ router を組み込みます。
	# 実際の Sonolus API は `/api/sonolus/...` に生えます。
	app.include_router(api_router)
	return app, sonolus, api_router


MODE = os.getenv("SONOLUS_EXAMPLE_MODE", "standalone").strip().lower()

if MODE == "router":
	# router モード:
	#   FastAPI アプリへ Sonolus router を統合した `app` を公開します。
	app, sonolus, api_router = create_router_integration()
else:
	# standalone モード:
	#   Sonolus が内部で持つ FastAPI アプリをそのまま使います。
	sonolus = create_standalone_sonolus()
	app = sonolus.app


if __name__ == "__main__":
	if MODE == "router":
		import uvicorn

		print("SONOLUS_EXAMPLE_MODE=router")
		print("Run: uvicorn example:app --reload")
		print("Sonolus endpoints: /api/sonolus/...")
		uvicorn.run(app, host="0.0.0.0", port=8000)
	else:
		print("SONOLUS_EXAMPLE_MODE=standalone")
		print("Sonolus endpoints: /sonolus/...")
		sonolus.run()
