"""
タグを動的に付与できるアイテムラッパー
"""
from typing import TypeVar, Generic, List, Any, Union, Optional, get_args, get_origin
from pydantic import BaseModel
from pydantic_core import core_schema, ValidationError
import sys

T = TypeVar("T", bound=BaseModel)


class TaggableItem(Generic[T]):
    """
    Pydanticモデルをラップして、タグを動的に付与するメソッドを提供します。
    
    使用例:
        item = sonolus.items.post.get("example")
        # タグをタイトル文字列で付与
        new_item = item.with_tags(["tag1", "tag2"])
        # または既存タグに追加
        new_item = item.add_tags(["tag3"])
    """

    def __init__(self, item: T):
        """
        アイテムをラップします。
        
        Args:
            item: Pydanticモデルのアイテム
        """
        object.__setattr__(self, "_item", item)

    def __getattr__(self, name: str) -> Any:
        """
        属性アクセスを内部アイテムに委譲します。
        これにより、TaggableItem を透過的にアクセス可能にします。
        
        Args:
            name: 属性名
            
        Returns:
            内部アイテムの属性値
            
        Raises:
            AttributeError: 属性が見つからない場合
        """
        if name in ("_item", "with_tags", "add_tags", "remove_tags", "clear_tags"):
            return object.__getattribute__(self, name)
        
        item = object.__getattribute__(self, "_item")
        return getattr(item, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        属性設定を内部アイテムに委譲します。
        
        Args:
            name: 属性名
            value: 設定する値
        """
        if name == "_item":
            object.__setattr__(self, name, value)
        else:
            item = object.__getattribute__(self, "_item")
            setattr(item, name, value)

    def __repr__(self) -> str:
        """文字列表現を返す"""
        item = object.__getattribute__(self, "_item")
        return f"TaggableItem({item!r})"

    def __str__(self) -> str:
        """文字列表現を返す"""
        item = object.__getattribute__(self, "_item")
        return str(item)

    def with_tags(self, tag_titles: List[str]) -> T:
        """
        タグを設定して、新しいアイテムを返します。
        既存のタグは上書きされます。
        タグタイトルから Tag オブジェクトが自動生成されます。
        
        Args:
            tag_titles: 設定するタグタイトルのリスト
            
        Returns:
            タグが設定された新しいアイテム
        """
        from sonolus_models import Tag
        item = object.__getattribute__(self, "_item")
        tags = [Tag(title=title) for title in tag_titles]
        return item.model_copy(update={"tags": tags})

    def add_tags(self, tag_titles: List[str]) -> T:
        """
        既存のタグにタグを追加して、新しいアイテムを返します。
        重複するタグタイトルは削除されます。
        
        Args:
            tag_titles: 追加するタグタイトルのリスト
            
        Returns:
            タグが追加された新しいアイテム
        """
        from sonolus_models import Tag
        item = object.__getattribute__(self, "_item")
        existing_tags = getattr(item, "tags", None) or []
        
        # 既存のタグタイトルを収集
        existing_titles = {tag.title for tag in existing_tags}
        
        # 新しいタグを追加（重複を避ける）
        new_tags = list(existing_tags)
        for title in tag_titles:
            if title not in existing_titles:
                new_tags.append(Tag(title=title))
                existing_titles.add(title)
        
        return item.model_copy(update={"tags": new_tags})

    def remove_tags(self, tag_titles: List[str]) -> T:
        """
        指定したタグを削除して、新しいアイテムを返します。
        
        Args:
            tag_titles: 削除するタグタイトルのリスト
            
        Returns:
            タグが削除された新しいアイテム
        """
        item = object.__getattribute__(self, "_item")
        existing_tags = getattr(item, "tags", None) or []
        titles_to_remove = set(tag_titles)
        
        new_tags = [tag for tag in existing_tags if tag.title not in titles_to_remove]
        return item.model_copy(update={"tags": new_tags})

    def clear_tags(self) -> T:
        """
        すべてのタグをクリアして、新しいアイテムを返します。
        
        Returns:
            タグがクリアされた新しいアイテム
        """
        item = object.__getattribute__(self, "_item")
        return item.model_copy(update={"tags": []})

    def get_tag_titles(self) -> List[str]:
        """
        現在のタグタイトルのリストを返します。
        
        Returns:
            タグタイトルのリスト
        """
        item = object.__getattribute__(self, "_item")
        tags = getattr(item, "tags", None) or []
        return [tag.title for tag in tags]

    # ラッパーの透過性を確保するためのメソッド
    def __getattr__(self, name: str) -> Any:
        """ラップされたアイテムの属性にアクセスします。"""
        item = object.__getattribute__(self, "_item")
        return getattr(item, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """ラップされたアイテムの属性を設定します。"""
        if name == "_item":
            object.__setattr__(self, name, value)
        else:
            item = object.__getattribute__(self, "_item")
            setattr(item, name, value)

    def __repr__(self) -> str:
        item = object.__getattribute__(self, "_item")
        return f"TaggableItem({item!r})"

    def __str__(self) -> str:
        item = object.__getattribute__(self, "_item")
        return str(item)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TaggableItem):
            item = object.__getattribute__(self, "_item")
            other_item = object.__getattribute__(other, "_item")
            return item == other_item
        item = object.__getattribute__(self, "_item")
        return item == other

    def __hash__(self) -> int:
        item = object.__getattribute__(self, "_item")
        return hash(item)

    def unwrap(self) -> T:
        """
        ラップされたアイテムを返します。タグメソッドと異なり、
        元のアイテムをそのまま返します（タグは保持されます）。
        
        Returns:
            ラップされたアイテム
        """
        return object.__getattribute__(self, "_item")

    # ============= Pydantic v2 バリデーション対応 =============

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> core_schema.CoreSchema:
        """
        Pydantic v2 のコアスキーマを定義。
        TaggableItem[T] を見た時、内部の T を検証対象にする。
        
        これにより、リクエスト時に TaggableItem を正しくバリデーションでき、
        レスポンス時に自動的にアンラップされる。
        """
        # 型引数 T を取得
        try:
            args = get_args(source_type)
            if args:
                inner_type = args[0]
            else:
                # 型引数がない場合は BaseModel を使用
                inner_type = BaseModel
        except Exception:
            inner_type = BaseModel

        # 内部型のスキーマを生成
        try:
            inner_schema = handler.generate_schema(inner_type)
        except Exception:
            # フォールバック：デフォルトスキーマを使用
            inner_schema = handler(inner_type)

        # TaggableItem でラップしたスキーマを定義
        # Python 側の検証と JSON シリアライゼーション
        return core_schema.with_info_before_validator_function(
            lambda value, info: cls._pydantic_validate(value),
            inner_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._pydantic_serialize,
                return_schema=inner_schema,
            ),
        )

    @staticmethod
    def _pydantic_validate(value: Any) -> Any:
        """
        Pydantic バリデーション時のコールバック。
        TaggableItem を受け取った場合、内部のアイテムを返す。
        
        Args:
            value: 検証対象の値（TaggableItem or タプル or T）
            
        Returns:
            内部のアイテム（T）
        """
        # すでに TaggableItem なら内部アイテムを返す
        if isinstance(value, TaggableItem):
            return object.__getattribute__(value, "_item")
        
        # タプル形式の場合（パース時）
        if isinstance(value, tuple) and len(value) == 1:
            inner = value[0]
            if isinstance(inner, TaggableItem):
                return object.__getattribute__(inner, "_item")
            return inner
        
        # その他はそのまま返す（Pydantic の検証に任せる）
        return value

    @staticmethod
    def _pydantic_serialize(value: Any) -> Any:
        """
        Pydantic シリアライゼーション時のコールバック。
        TaggableItem をアンラップして、内部のアイテムをシリアライズする。
        
        Args:
            value: シリアライズ対象の値（通常は T）
            
        Returns:
            シリアライズ対象の値
        """
        # TaggableItem の場合はアンラップ
        if isinstance(value, TaggableItem):
            return object.__getattribute__(value, "_item")
        return value


def unwrap_taggable_item(item: Any) -> Any:
    """
    TaggableItem を自動的にアンラップします。
    TaggableItem でない場合はそのまま返します。
    
    Args:
        item: アンラップするアイテム（TaggableItem or その他）
        
    Returns:
        アンラップされたアイテム、またはそのまま返されたアイテム
    """
    if item is None:
        return None
    if isinstance(item, TaggableItem):
        return object.__getattribute__(item, "_item")
    return item
