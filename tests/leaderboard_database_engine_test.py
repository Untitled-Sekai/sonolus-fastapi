from sonolus_models import ItemType

from sonolus_fastapi.backend.backend import StorageBackend
from sonolus_fastapi.backend.leaderboard import LeaderboardRecordStore
from sonolus_fastapi.backend.leaderboard_database import DatabaseRecordStore


def test_database_leaderboard_stores_share_one_engine(monkeypatch):
    created_engines = []
    initialized_engines = []

    def create_engine(url, future):
        engine = object()
        created_engines.append((url, future, engine))
        return engine

    def init_table(engine):
        initialized_engines.append(engine)

    monkeypatch.setattr(
        "sonolus_fastapi.backend.leaderboard_database.create_engine",
        create_engine,
    )
    monkeypatch.setattr(
        "sonolus_fastapi.backend.leaderboard.init_leaderboard_records_table",
        init_table,
    )
    monkeypatch.setattr(
        "sonolus_fastapi.backend.leaderboard_database.init_leaderboard_records_table",
        init_table,
    )

    store = LeaderboardRecordStore(
        StorageBackend.DATABASE,
        url="postgresql+psycopg://example/db",
    )

    first = store.get_store(ItemType.level, "level-1", "score")
    second = store.get_store(ItemType.level, "level-2", "score")

    assert isinstance(first, DatabaseRecordStore)
    assert isinstance(second, DatabaseRecordStore)
    assert first.engine is second.engine
    assert len(created_engines) == 1
    assert initialized_engines == [first.engine]


def test_database_leaderboard_store_accepts_external_engine(monkeypatch):
    engine = object()

    def create_engine(url, future):
        raise AssertionError("create_engine should not be called")

    monkeypatch.setattr(
        "sonolus_fastapi.backend.leaderboard_database.create_engine",
        create_engine,
    )
    monkeypatch.setattr(
        "sonolus_fastapi.backend.leaderboard.init_leaderboard_records_table",
        lambda table_engine: None,
    )

    store = LeaderboardRecordStore(StorageBackend.DATABASE, engine=engine)

    record_store = store.get_store(ItemType.level, "level", "score")

    assert record_store.engine is engine
