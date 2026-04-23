from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.routes import user_credentials


def _session_factory(tmp_path: Path):
    db_file = tmp_path / "user_credentials_test.db"
    engine = create_engine(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def test_user_can_put_get_and_delete_binance_credentials(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        created = user_credentials.put_binance_credentials(
            user_credentials.BinanceCredentialPayload(
                api_key="abcd1234wxyz",
                api_secret="very-secret-value",
            ),
            current_user_id="user-a",
            db=db,
        )
        status = user_credentials.get_binance_credentials_status(current_user_id="user-a", db=db)
        deleted = user_credentials.delete_binance_credentials(current_user_id="user-a", db=db)
        empty = user_credentials.get_binance_credentials_status(current_user_id="user-a", db=db)

    assert created.configured is True
    assert created.api_key_masked is not None
    assert status.configured is True
    assert status.api_key_masked is not None
    assert deleted["message"] == "Binance credentials deleted"
    assert empty.configured is False
