"""
Pydantic BaseModel のカスタムクラス
TaggableItem を自動的にアンラップするフィールドバリデーションを提供
"""

from typing import Any
from pydantic import BaseModel, model_validator
from sonolus_fastapi.utils.taggable_pydantic import unwrap_taggable_items


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

    @model_validator(mode="before")
    @classmethod
    def unwrap_taggable_items(cls, data: Any) -> Any:
        """
        モデル構築前に、すべての TaggableItem をアンラップする。

        Args:
            data: Pydantic に渡されるデータ

        Returns:
            アンラップされたデータ
        """
        return unwrap_taggable_items(data)

    @staticmethod
    def _unwrap_value(value: Any) -> Any:
        """
        値から TaggableItem をアンラップ（再帰的）。

        Args:
            value: 値

        Returns:
            アンラップされた値
        """
        return unwrap_taggable_items(value)


__all__ = ["SonolusModel"]
