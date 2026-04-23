from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.routes import monitor_preferences


def _session_factory(tmp_path: Path):
    db_file = tmp_path / "monitor_theme_test.db"
    engine = create_engine(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def test_monitor_theme_field_roundtrips_on_preference(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        put_response = monitor_preferences.update_monitor_preferences(
            payload=monitor_preferences.MonitorPreferenceUpdate(theme="dark-green"),
            symbol="BTC/USDT",
            current_user_id="user-a",
            db=db,
        )
        get_response = monitor_preferences.list_monitor_preferences(current_user_id="user-a", db=db)

    assert put_response["theme"] == "dark-green"
    assert get_response["BTC/USDT"]["theme"] == "dark-green"
