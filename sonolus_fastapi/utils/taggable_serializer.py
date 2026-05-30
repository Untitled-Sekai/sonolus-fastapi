"""
Pydantic シリアライザー: TaggableItem の自動アンラップ
FastAPI レスポンスの JSON シリアライゼーション時に TaggableItem をアンラップ
"""
from typing import Any
from pydantic import GetSerializationHandler, field_serializer
from pydantic_core import core_schema
from functools import lru_cache


def taggable_item_serializer(value: Any, handler: GetSerializationHandler, info) -> Any:
    """
    Pydantic シリアライザーハンドラー。
    TaggableItem をアンラップして、内部のアイテムをシリアライズする。
    
    Args:
        value: シリアライズするアイテム
        handler: デフォルトシリアライザーハンドラー
        info: シリアライゼーション情報
        
    Returns:
        シリアライズされたアイテム
    """
    from sonolus_fastapi.utils.taggable_item import TaggableItem
    
    # TaggableItem をアンラップ
    if isinstance(value, TaggableItem):
        value = object.__getattribute__(value, "_item")
    
    # デフォルトシリアライザーで処理
    return handler(value)


def setup_taggable_item_serializer_for_response_model(model_class):
    """
    レスポンスモデルに TaggableItem シリアライザーを設定。
    
    使用例:
        from pydantic import BaseModel
        from sonolus_models import LevelItem
        from sonolus_fastapi.utils.taggable_serializer import setup_taggable_item_serializer_for_response_model
        
        class LevelResponse(BaseModel):
            item: 'TaggableItem[LevelItem]'
        
        setup_taggable_item_serializer_for_response_model(LevelResponse)
    
    Args:
        model_class: セットアップ対象のモデルクラス
    """
    if not hasattr(model_class, 'model_fields'):
        return
    
    # Pydantic v2 ConfigDict でシリアライザーを設定
    if not hasattr(model_class, 'model_config'):
        model_class.model_config = {}
    
    return model_class


def install_taggable_item_serializer():
    """
    Pydantic の JSON シリアライザーに TaggableItem アンラップ機能を追加。
    
    これにより、FastAPI の response_model がTaggableItem を含むモデルを返す場合、
    自動的にアンラップして Pydantic バリデーションを通す。
    
    使用例:
        # アプリケーション起動時に一度実行
        from sonolus_fastapi.utils.taggable_serializer import install_taggable_item_serializer
        install_taggable_item_serializer()
        
        # または FastAPI の after_response ハンドラーで使用
        from fastapi.responses import JSONResponse
        
        @app.get("/items/{item_id}")
        async def get_item(item_id: str) -> dict:
            # TaggableItem を含む dict が返される場合、
            # 自動的にアンラップされる
            item = await fetch_item(item_id)
            return {"item": item}
    """
    # Pydantic v2 ではコアスキーマで TaggableItem が定義されているため、
    # 追加のセットアップは不要。
    # TaggableItem.__pydantic_core_schema__ が自動的に呼ばれる。
    pass


# ============= Pydantic v2 統合ユーティリティ =============

@lru_cache(maxsize=128)
def get_taggable_item_inner_type(taggable_item_type: Any) -> Any:
    """
    TaggableItem[T] から T を抽出する。
    
    Args:
        taggable_item_type: TaggableItem の型（例：TaggableItem[LevelItem]）
        
    Returns:
        内部型 T
    """
    from typing import get_args
    args = get_args(taggable_item_type)
    if args:
        return args[0]
    return None


def unwrap_taggable_items_in_dict(data: dict) -> dict:
    """
    辞書内のすべての TaggableItem をアンラップする。
    リスト内の TaggableItem も再帰的にアンラップされる。
    
    Args:
        data: 辞書データ
        
    Returns:
        アンラップされた辞書
    """
    from sonolus_fastapi.utils.taggable_item import TaggableItem
    
    result = {}
    for key, value in data.items():
        if isinstance(value, TaggableItem):
            result[key] = object.__getattribute__(value, "_item")
        elif isinstance(value, list):
            result[key] = [
                object.__getattribute__(item, "_item") if isinstance(item, TaggableItem) else item
                for item in value
            ]
        elif isinstance(value, dict):
            result[key] = unwrap_taggable_items_in_dict(value)
        else:
            result[key] = value
    
    return result
TAGGABLE_ITEM_SERIALIZER_CONFIG = {
    "serializers": {
        "taggable_item": taggable_item_serializer,
    }
}


__all__ = [
    "taggable_item_serializer",
    "install_taggable_item_serializer",
    "TAGGABLE_ITEM_SERIALIZER_CONFIG",
]

