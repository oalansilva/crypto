from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.routes import system_preferences


def _session_factory(tmp_path: Path):
    db_file = tmp_path / "system_preferences_test.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def test_admin_can_put_get_and_delete_system_preferences(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        created = system_preferences.put_system_preferences(
            system_preferences.MinimaxApiKeyPayload(minimax_api_key="minimax-secret-key-12345"),
            admin_user_id="admin-user",
            db=db,
        )
        status = system_preferences.get_system_preferences(_admin_user_id="admin-user", db=db)
        deleted = system_preferences.delete_system_preferences(_admin_user_id="admin-user", db=db)
        empty = system_preferences.get_system_preferences(_admin_user_id="admin-user", db=db)

    assert created.minimax_api_key_configured is True
    assert created.minimax_api_key_masked is not None
    assert status.minimax_api_key_configured is True
    assert status.minimax_api_key_masked is not None
    assert deleted["message"] == "System preferences cleared"
    assert empty.minimax_api_key_configured is False
    assert empty.minimax_api_key_masked is None
