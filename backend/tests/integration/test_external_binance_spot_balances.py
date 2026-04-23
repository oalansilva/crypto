from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.routes import external_balances
from app.routes import user_credentials


def _session_factory(tmp_path: Path):
    db_file = tmp_path / "external_balances_test.db"
    engine = create_engine(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def test_external_balances_requires_user_scoped_credentials(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        with pytest.raises(HTTPException) as exc:
            external_balances.get_binance_spot_balances(current_user_id="user-a", db=db)
    assert exc.value.status_code == 503
    assert "not configured for this user" in str(exc.value.detail)


def test_external_balances_uses_current_user_credentials(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)

    captured: dict[str, str | float | None] = {
        "api_key": None,
        "api_secret": None,
        "min_usd": None,
    }

    def _fake_fetch_spot_balances_snapshot(
        *, lookback_days=None, min_usd=None, api_key=None, api_secret=None, base_url=None
    ):
        captured["api_key"] = api_key
        captured["api_secret"] = api_secret
        captured["min_usd"] = min_usd
        return {"balances": [], "total_usd": 0.0, "as_of": "2026-03-31T00:00:00Z"}

    monkeypatch.setattr(
        external_balances, "fetch_spot_balances_snapshot", _fake_fetch_spot_balances_snapshot
    )

    with SessionLocal() as db:
        user_credentials.put_binance_credentials(
            user_credentials.BinanceCredentialPayload(
                api_key="user-a-key", api_secret="user-a-secret-123"
            ),
            current_user_id="user-a",
            db=db,
        )
        user_credentials.put_binance_credentials(
            user_credentials.BinanceCredentialPayload(
                api_key="user-b-key", api_secret="user-b-secret-123"
            ),
            current_user_id="user-b",
            db=db,
        )

        external_balances.get_binance_spot_balances(current_user_id="user-b", db=db, min_usd=5)

    assert captured["api_key"] == "user-b-key"
    assert captured["api_secret"] == "user-b-secret-123"
    assert captured["min_usd"] == 5
