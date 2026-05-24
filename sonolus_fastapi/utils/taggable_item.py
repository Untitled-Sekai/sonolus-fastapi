"""
タグを動的に付与できるアイテムラッパー
"""
from typing import TypeVar, Generic, List, Any, Union, Optional
from pydantic import BaseModel

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
