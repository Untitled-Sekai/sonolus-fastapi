from dataclasses import dataclass
from typing import List, TypeVar, Generic

T = TypeVar('T')

@dataclass
class ListResult(Generic[T]):
    """リスト取得結果"""
    items: List[T]
    total_count: int
    limit: int
    offset: int
    
    def __class_getitem__(cls, item_type):
        # ジェネリクスの型パラメータを正しく処理
        return cls
