import json
from threading import Lock
from typing import List, Optional
from weakref import WeakSet

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sonolus_models import ItemType, ServerItemLeaderboardRecord
from .result import ListResult

_ENGINE_CACHE: dict[str, Engine] = {}
_ENGINE_CACHE_LOCK = Lock()
_INITIALIZED_ENGINES: WeakSet[Engine] = WeakSet()
_INIT_TABLE_LOCK = Lock()


def get_shared_leaderboard_engine(url: str) -> Engine:
    """Return one shared SQLAlchemy engine per database URL."""
    with _ENGINE_CACHE_LOCK:
        engine = _ENGINE_CACHE.get(url)
        if engine is None:
            engine = create_engine(url, future=True)
            _ENGINE_CACHE[url] = engine
        return engine


def init_leaderboard_records_table(engine: Engine) -> None:
    """Create leaderboard_records table and indexes once per engine."""
    with _INIT_TABLE_LOCK:
        if engine in _INITIALIZED_ENGINES:
            return

        with engine.connect() as conn:
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

        _INITIALIZED_ENGINES.add(engine)


class DatabaseRecordStore:
    """SQLデータベースでleaderboard recordsを管理するストア"""

    def __init__(
        self,
        item_type: ItemType,
        item_name: str,
        leaderboard_name: str,
        url: str | None = None,
        engine: Engine | None = None,
        init_table: bool = True,
    ):
        self.item_type = item_type
        self.item_name = item_name
        self.leaderboard_name = leaderboard_name
        self.engine = engine or get_shared_leaderboard_engine(
            url or "sqlite:///./data/database.db"
        )

        if init_table:
            self._init_table()

    def _init_table(self):
        """leaderboard_recordsテーブルを作成"""
        init_leaderboard_records_table(self.engine)

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
                    "leaderboard_name": self.leaderboard_name,
                },
            ).fetchone()

            if row is None:
                return None

            return ServerItemLeaderboardRecord.model_validate(json.loads(row[0]))

    def list(
        self, limit: int = 10, offset: int = 0
    ) -> ListResult[ServerItemLeaderboardRecord]:
        if limit > 20:
            limit = 20

        with self.engine.connect() as conn:
            # totalcountを取得
            count_result = conn.execute(
                text("""
                    SELECT COUNT(*) FROM leaderboard_records 
                    WHERE parent_type = :parent_type 
                    AND parent_name = :parent_name
                    AND leaderboard_name = :leaderboard_name
                """),
                {
                    "parent_type": self.item_type.value,
                    "parent_name": self.item_name,
                    "leaderboard_name": self.leaderboard_name,
                },
            ).fetchone()
            total_count = count_result[0] if count_result else 0

            # データを取得
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
                    "offset": offset,
                },
            ).fetchall()

        items = [
            ServerItemLeaderboardRecord.model_validate(json.loads(row[0]))
            for row in rows
        ]

        return ListResult(
            items=items, total_count=total_count, limit=limit, offset=offset
        )

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
                    "data": data,
                },
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
                    "leaderboard_name": self.leaderboard_name,
                },
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
                    "data": data,
                },
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
                    "leaderboard_name": self.leaderboard_name,
                },
            ).fetchone()
            return row[0] if row else 0
