import json
from typing import TypeVar, Generic, List, Optional
from sqlalchemy import create_engine, text

T = TypeVar("T")

class DatabaseItemStore(Generic[T]):
    def __init__(self, item_cls, url: str):
        self.item_cls = item_cls
        self.item_type = item_cls.__name__.lower()  # アイテムタイプを取得
        self.engine = create_engine(url, future=True)
        
        self._init_table()
        
    def _init_table(self):
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS items(
                    name TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    PRIMARY KEY (name, item_type)
                )
            """))
            conn.commit()
            
    def get(self, name: str) -> Optional[T]:
        with self.engine.connect() as conn:
            row = conn.execute(
                text("SELECT data FROM items WHERE name = :name AND item_type = :item_type"),
                {"name": name, "item_type": self.item_type}
            ).fetchone()
            
            if row is None:
                return None
            
            return self.item_cls.model_validate(json.loads(row[0]))
        
    def list(self, limit: int = 20, offset: int = 0) -> List[T]:
        if limit > 20:
            limit = 20  # 最大20件に制限
        
        with self.engine.begin() as conn:
            rows = conn.execute(
                text("SELECT data FROM items WHERE item_type = :item_type LIMIT :limit OFFSET :offset"),
                {"item_type": self.item_type, "limit": limit, "offset": offset}
            ).fetchall()

        return [
            self.item_cls.model_validate(json.loads(row[0]))
            for row in rows
        ]
        
    def add(self, item: T):
        data = json.dumps(item.model_dump(), ensure_ascii=False)

        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO items (name, item_type, data)
                    VALUES (:name, :item_type, :data)
                    ON CONFLICT(name, item_type) DO UPDATE SET data=:data
                """),
                {"name": item.name, "item_type": self.item_type, "data": data}
            )
            
    def delete(self, name: str):
        with self.engine.begin() as conn:
            conn.execute(
                text("DELETE FROM items WHERE name=:name AND item_type=:item_type"),
                {"name": name, "item_type": self.item_type}
            )
            
    def update(self, item: T):
        data = json.dumps(item.model_dump(), ensure_ascii=False)
        
        with self.engine.begin() as conn:
            conn.execute(
                text("UPDATE items SET data=:data WHERE name=:name AND item_type=:item_type"),
                {"name": item.name, "item_type": self.item_type, "data": data}
            )
        
    def map(self) -> dict[str, T]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                text("SELECT name, data FROM items WHERE item_type = :item_type"),
                {"item_type": self.item_type}
            ).fetchall()
            
        return {
            row[0]: self.item_cls.model_validate(json.loads(row[1]))
            for row in rows
        }
        
    def get_many(self, names: List[str]) -> List[T]:
        if not names:
            return []
            
        # IN句用にプレースホルダを作成
        placeholders = ",".join(f":name_{i}" for i in range(len(names)))
        params = {f"name_{i}": name for i, name in enumerate(names)}
        params["item_type"] = self.item_type
        
        with self.engine.connect() as conn:
            rows = conn.execute(
                text(f"SELECT name, data FROM items WHERE name IN ({placeholders}) AND item_type = :item_type"),
                params
            ).fetchall()
        
        items_dict = {
            row[0]: self.item_cls.model_validate(json.loads(row[1]))
            for row in rows
        }
        
        # 渡された順序でアイテムを返す
        return [items_dict[name] for name in names if name in items_dict]