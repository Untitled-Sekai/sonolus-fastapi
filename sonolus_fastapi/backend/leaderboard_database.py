import json
from typing import List, Optional
from sqlalchemy import create_engine, text
from sonolus_models import ItemType, ServerItemLeaderboardRecord

class DatabaseRecordStore:
    """SQLデータベースでleaderboard recordsを管理するストア"""
    
    def __init__(self, item_type: ItemType, item_name: str, leaderboard_name: str, url: str):
        self.item_type = item_type
        self.item_name = item_name
        self.leaderboard_name = leaderboard_name
        self.engine = create_engine(url, future=True)
        
        self._init_table()
    
    def _init_table(self):
        """leaderboard_recordsテーブルを作成"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS leaderboard_records(
                    record_name TEXT NOT NULL,
                    parent_type TEXT NOT NULL,
                    parent_name TEXT NOT NULL,
                    leaderboard_name TEXT NOT NULL,
                    rank TEXT NOT NULL,
                    player TEXT NOT NULL,
                    value TEXT NOT NULL,
                    data TEXT NOT NULL,
                    PRIMARY KEY (record_name, parent_type, parent_name, leaderboard_name)
                )
            """))
            
            # インデックスを追加（親アイテム+リーダーボードごとのクエリを高速化）
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_leaderboard_records_parent 
                ON leaderboard_records(parent_type, parent_name, leaderboard_name, rank)
            """))
            conn.commit()
    
    def get(self, record_name: str) -> Optional[ServerItemLeaderboardRecord]:
        with self.engine.connect() as conn:
            row = conn.execute(
                text("""
                    SELECT data FROM leaderboard_records 
                    WHERE record_name = :name 
                    AND parent_type = :parent_type 
                    AND parent_name = :parent_name
                    AND leaderboard_name = :leaderboard_name
                """),
                {
                    "name": record_name,
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name,
                    "leaderboard_name": self.leaderboard_name
                }
            ).fetchone()
            
            if row is None:
                return None
            
            return ServerItemLeaderboardRecord.model_validate(json.loads(row[0]))
    
    def list(self, limit: int = 10, offset: int = 0) -> List[ServerItemLeaderboardRecord]:
        if limit > 20:
            limit = 20
        
        with self.engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT data FROM leaderboard_records 
                    WHERE parent_type = :parent_type 
                    AND parent_name = :parent_name
                    AND leaderboard_name = :leaderboard_name
                    ORDER BY CAST(rank AS INTEGER)
                    LIMIT :limit OFFSET :offset
                """),
                {
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name,
                    "leaderboard_name": self.leaderboard_name,
                    "limit": limit,
                    "offset": offset
                }
            ).fetchall()
        
        return [
            ServerItemLeaderboardRecord.model_validate(json.loads(row[0]))
            for row in rows
        ]
    
    def add(self, record: ServerItemLeaderboardRecord):
        data = json.dumps(record.model_dump(), ensure_ascii=False)
        
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO leaderboard_records 
                    (record_name, parent_type, parent_name, leaderboard_name, rank, player, value, data)
                    VALUES (:name, :parent_type, :parent_name, :leaderboard_name, :rank, :player, :value, :data)
                    ON CONFLICT(record_name, parent_type, parent_name, leaderboard_name) 
                    DO UPDATE SET data=:data, rank=:rank, player=:player, value=:value
                """),
                {
                    "name": record.name,
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name,
                    "leaderboard_name": self.leaderboard_name,
                    "rank": record.rank,
                    "player": record.player,
                    "value": record.value,
                    "data": data
                }
            )
    
    def delete(self, record_name: str):
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    DELETE FROM leaderboard_records 
                    WHERE record_name = :name 
                    AND parent_type = :parent_type 
                    AND parent_name = :parent_name
                    AND leaderboard_name = :leaderboard_name
                """),
                {
                    "name": record_name,
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name,
                    "leaderboard_name": self.leaderboard_name
                }
            )
    
    def update(self, record: ServerItemLeaderboardRecord):
        data = json.dumps(record.model_dump(), ensure_ascii=False)
        
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE leaderboard_records 
                    SET data = :data, rank = :rank, player = :player, value = :value
                    WHERE record_name = :name 
                    AND parent_type = :parent_type 
                    AND parent_name = :parent_name
                    AND leaderboard_name = :leaderboard_name
                """),
                {
                    "name": record.name,
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name,
                    "leaderboard_name": self.leaderboard_name,
                    "rank": record.rank,
                    "player": record.player,
                    "value": record.value,
                    "data": data
                }
            )
    
    def count(self) -> int:
        with self.engine.connect() as conn:
            row = conn.execute(
                text("""
                    SELECT COUNT(*) FROM leaderboard_records 
                    WHERE parent_type = :parent_type 
                    AND parent_name = :parent_name
                    AND leaderboard_name = :leaderboard_name
                """),
                {
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name,
                    "leaderboard_name": self.leaderboard_name
                }
            ).fetchone()
            return row[0] if row else 0
