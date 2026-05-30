"""
FastAPI 統合: TaggableItem の自動シリアライゼーション
Pydantic モデルの JSON レスポンス時に TaggableItem を自動的にアンラップ
"""
from typing import Any
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder


def setup_taggable_item_support(app: FastAPI):
    """
    FastAPI アプリケーションに TaggableItem サポートを追加。
    
    レスポンスの JSON シリアライゼーション時に TaggableItem を自動的にアンラップする
    ミドルウェアを登録します。
    
    使用例:
        from fastapi import FastAPI
        from sonolus_fastapi.utils.taggable_fastapi_support import setup_taggable_item_support
        
        app = FastAPI()
        setup_taggable_item_support(app)
    """
    from sonolus_fastapi.utils.taggable_item import unwrap_taggable_item
    
    # 元の jsonable_encoder を保存
    original_jsonable_encoder = jsonable_encoder
    
    # カスタム jsonable_encoder
    def custom_jsonable_encoder(obj, *args, **kwargs):
        # TaggableItem をアンラップ
        obj = unwrap_taggable_item(obj)
        # 元の jsonable_encoder に委譲
        return original_jsonable_encoder(obj, *args, **kwargs)
    
    # FastAPI のデフォルト encoder をオーバーライド
    import fastapi.encoders
    fastapi.encoders.jsonable_encoder = custom_jsonable_encoder


def unwrap_taggable_items_in_model(data: Any) -> Any:
    """
    データ構造内のすべての TaggableItem をアンラップ。
    
    Args:
        data: アンラップするデータ（dict, list, TaggableItem, その他）
        
    Returns:
        アンラップされたデータ
    """
    from sonolus_fastapi.utils.taggable_item import TaggableItem, unwrap_taggable_item
    
    if isinstance(data, TaggableItem):
        return unwrap_taggable_items_in_model(unwrap_taggable_item(data))
    elif isinstance(data, dict):
        return {k: unwrap_taggable_items_in_model(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [unwrap_taggable_items_in_model(item) for item in data]
    else:
        return data


__all__ = ["setup_taggable_item_support", "unwrap_taggable_items_in_model"]
