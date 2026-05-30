"""
Pydantic BaseModel のカスタムクラス
TaggableItem を自動的にアンラップするフィールドバリデーションを提供
"""
from typing import Any
from pydantic import BaseModel, model_validator
from sonolus_fastapi.utils.taggable_item import TaggableItem


class SonolusModel(BaseModel):
    """
    TaggableItem を自動的にアンラップする Pydantic BaseModel。
    
    すべてのフィールドで、TaggableItem をそのまま渡しても
    自動的にアンラップされて検証されます。
    
    使用例:
        from sonolus_fastapi.utils.sonolus_model import SonolusModel
        from sonolus_models.items.level import LevelItem, EngineReference
        
        class CreateLevelRequest(SonolusModel):
            name: str
            engine: EngineReference  # TaggableItem[EngineReference] をそのまま渡せる
        
        # バックエンドから返された TaggableItem
        engine = sonolus.items.engine.get("engine_name")
        
        # そのまま渡せる！自動的にアンラップされる
        request = CreateLevelRequest(
            name="my_level",
            engine=engine  # TaggableItem[EngineReference]
        )
    """

    @model_validator(mode='before')
    @classmethod
    def unwrap_taggable_items(cls, data: Any) -> Any:
        """
        モデル構築前に、すべての TaggableItem をアンラップする。
        
        Args:
            data: Pydantic に渡されるデータ
            
        Returns:
            アンラップされたデータ
        """
        if not isinstance(data, dict):
            return data
        
        # すべてのフィールドで TaggableItem をアンラップ
        unwrapped_data = {}
        for key, value in data.items():
            unwrapped_data[key] = cls._unwrap_value(value)
        
        return unwrapped_data

    @staticmethod
    def _unwrap_value(value: Any) -> Any:
        """
        値から TaggableItem をアンラップ（再帰的）。
        
        Args:
            value: 値
            
        Returns:
            アンラップされた値
        """
        if value is None:
            return None
        
        # TaggableItem の場合はアンラップ
        if isinstance(value, TaggableItem):
            return object.__getattribute__(value, "_item")
        
        # リストの場合は再帰的にアンラップ
        if isinstance(value, list):
            return [SonolusModel._unwrap_value(item) for item in value]
        
        # 辞書の場合は再帰的にアンラップ
        if isinstance(value, dict):
            return {k: SonolusModel._unwrap_value(v) for k, v in value.items()}
        
        return value


__all__ = ["SonolusModel"]
