import json
from typing import List, Optional
from sqlalchemy import create_engine, text
from sonolus_models import ItemType, ServerItemCommunityComment

class DatabaseCommentStore:
    """SQLデータベースでコメントを管理するストア"""
    
    def __init__(self, item_type: ItemType, item_name: str, url: str):
        self.item_type = item_type
        self.item_name = item_name
        self.engine = create_engine(url, future=True)
        
        self._init_table()
    
    def _init_table(self):
        """commentsテーブルを作成"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS comments(
                    comment_name TEXT NOT NULL,
                    parent_type TEXT NOT NULL,
                    parent_name TEXT NOT NULL,
                    author TEXT NOT NULL,
                    time INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    data TEXT NOT NULL,
                    PRIMARY KEY (comment_name, parent_type, parent_name)
                )
            """))
            
            # インデックスを追加（親アイテムごとのクエリを高速化）
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_comments_parent 
                ON comments(parent_type, parent_name, time DESC)
            """))
            conn.commit()
    
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
    
    def list(self, limit: int = 10, offset: int = 0) -> List[ServerItemCommunityComment]:
        if limit > 20:
            limit = 20
        
        with self.engine.connect() as conn:
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
        
        return [
            ServerItemCommunityComment.model_validate(json.loads(row[0]))
            for row in rows
        ]
    
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
