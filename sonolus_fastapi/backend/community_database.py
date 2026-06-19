import json
from threading import Lock
from typing import List, Optional
from weakref import WeakSet

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sonolus_models import ItemType, ServerItemCommunityComment
from .result import ListResult

_ENGINE_CACHE: dict[str, Engine] = {}
_ENGINE_CACHE_LOCK = Lock()
_INITIALIZED_ENGINES: WeakSet[Engine] = WeakSet()
_INIT_TABLE_LOCK = Lock()


def get_shared_community_engine(url: str) -> Engine:
    """Return one shared SQLAlchemy engine per database URL."""
    with _ENGINE_CACHE_LOCK:
        engine = _ENGINE_CACHE.get(url)
        if engine is None:
            engine = create_engine(url, future=True)
            _ENGINE_CACHE[url] = engine
        return engine


def init_comments_table(engine: Engine) -> None:
    """Create comments table and indexes once per engine."""
    with _INIT_TABLE_LOCK:
        if engine in _INITIALIZED_ENGINES:
            return

        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS comments(
                    comment_name TEXT NOT NULL,
                    parent_type TEXT NOT NULL,
                    parent_name TEXT NOT NULL,
                    author TEXT NOT NULL,
                    time BIGINT NOT NULL,
                    content TEXT NOT NULL,
                    data TEXT NOT NULL,
                    PRIMARY KEY (comment_name, parent_type, parent_name)
                )
            """))

            if conn.dialect.name == "postgresql":
                column_type = conn.execute(text("""
                    SELECT data_type
                    FROM information_schema.columns
                    WHERE table_schema = current_schema()
                      AND table_name = 'comments'
                      AND column_name = 'time'
                """)).scalar()

                if column_type and column_type.lower() != "bigint":
                    conn.execute(text("""
                        ALTER TABLE comments
                        ALTER COLUMN time TYPE BIGINT
                        USING time::bigint
                    """))
            
            # インデックスを追加（親アイテムごとのクエリを高速化）
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_comments_parent 
                ON comments(parent_type, parent_name, time DESC)
            """))
            conn.commit()

        _INITIALIZED_ENGINES.add(engine)


class DatabaseCommentStore:
    """SQLデータベースでコメントを管理するストア"""

    def __init__(
        self,
        item_type: ItemType,
        item_name: str,
        url: str | None = None,
        engine: Engine | None = None,
        init_table: bool = True,
    ):
        self.item_type = item_type
        self.item_name = item_name
        self.engine = engine or get_shared_community_engine(
            url or "sqlite:///./data/database.db"
        )

        if init_table:
            self._init_table()
    
    def _init_table(self):
        """commentsテーブルを作成"""
        init_comments_table(self.engine)
    
    def get(self, comment_name: str) -> Optional[ServerItemCommunityComment]:
        with self.engine.connect() as conn:
            row = conn.execute(
                text("""
                    SELECT data FROM comments 
                    WHERE comment_name = :name 
                    AND parent_type = :parent_type 
                    AND parent_name = :parent_name
                """),
                {
                    "name": comment_name,
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name
                }
            ).fetchone()
            
            if row is None:
                return None
            
            return ServerItemCommunityComment.model_validate(json.loads(row[0]))
    
    def list(self, limit: int = 10, offset: int = 0) -> ListResult[ServerItemCommunityComment]:
        if limit > 20:
            limit = 20
        
        with self.engine.connect() as conn:
            # totalcountを取得
            count_result = conn.execute(
                text("""
                    SELECT COUNT(*) FROM comments 
                    WHERE parent_type = :parent_type 
                    AND parent_name = :parent_name
                """),
                {
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name
                }
            ).fetchone()
            total_count = count_result[0] if count_result else 0
            
            # データを取得
            rows = conn.execute(
                text("""
                    SELECT data FROM comments 
                    WHERE parent_type = :parent_type 
                    AND parent_name = :parent_name
                    ORDER BY time DESC
                    LIMIT :limit OFFSET :offset
                """),
                {
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name,
                    "limit": limit,
                    "offset": offset
                }
            ).fetchall()
        
        items = [
            ServerItemCommunityComment.model_validate(json.loads(row[0]))
            for row in rows
        ]
        
        return ListResult(
            items=items,
            total_count=total_count,
            limit=limit,
            offset=offset
        )
    
    def add(self, comment: ServerItemCommunityComment):
        data = json.dumps(comment.model_dump(), ensure_ascii=False)
        
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO comments 
                    (comment_name, parent_type, parent_name, author, time, content, data)
                    VALUES (:name, :parent_type, :parent_name, :author, :time, :content, :data)
                    ON CONFLICT(comment_name, parent_type, parent_name) 
                    DO UPDATE SET data=:data, time=:time, content=:content
                """),
                {
                    "name": comment.name,
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name,
                    "author": comment.author,
                    "time": comment.time,
                    "content": comment.content,
                    "data": data
                }
            )
    
    def delete(self, comment_name: str):
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    DELETE FROM comments 
                    WHERE comment_name = :name 
                    AND parent_type = :parent_type 
                    AND parent_name = :parent_name
                """),
                {
                    "name": comment_name,
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name
                }
            )
    
    def update(self, comment: ServerItemCommunityComment):
        data = json.dumps(comment.model_dump(), ensure_ascii=False)
        
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE comments 
                    SET data = :data, time = :time, content = :content
                    WHERE comment_name = :name 
                    AND parent_type = :parent_type 
                    AND parent_name = :parent_name
                """),
                {
                    "name": comment.name,
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name,
                    "time": comment.time,
                    "content": comment.content,
                    "data": data
                }
            )
    
    def count(self) -> int:
        with self.engine.connect() as conn:
            row = conn.execute(
                text("""
                    SELECT COUNT(*) FROM comments 
                    WHERE parent_type = :parent_type 
                    AND parent_name = :parent_name
                """),
                {
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name
                }
            ).fetchone()
            return row[0] if row else 0
