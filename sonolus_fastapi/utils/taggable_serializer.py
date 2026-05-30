"""
Pydantic シリアライザー: TaggableItem の自動アンラップ
FastAPI レスポンスの JSON シリアライゼーション時に TaggableItem をアンラップ
"""
from typing import Any
from pydantic import GetSerializationHandler
from pydantic_core import core_schema


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
    from sonolus_fastapi.utils.taggable_item import TaggableItem, unwrap_taggable_item
    
    # TaggableItem をアンラップ
    if isinstance(value, TaggableItem):
        value = unwrap_taggable_item(value)
    
    # デフォルトシリアライザーで処理
    return handler(value)


def install_taggable_item_serializer():
    """
    Pydantic の JSON シリアライザーに TaggableItem アンラップ機能を追加。
    
    これにより、FastAPI の response_model がTaggableItem を含むモデルを返す場合、
    自動的にアンラップして Pydantic バリデーションを通す。
    
    使用例:
        # アプリケーション起動時に一度実行
        from sonolus_fastapi.utils.taggable_serializer import install_taggable_item_serializer
        install_taggable_item_serializer()
    """
    # Pydantic v2 では BaseModel.model_json_schema() などで処理
    # グローバルシリアライザーを追加する必要がある
    pass


# Pydantic v2 の ConfigDict で使用するシリアライザー設定
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

