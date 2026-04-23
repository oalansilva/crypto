from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.routes import monitor_preferences
from app.services.user_exchange_credentials import BINANCE_PROVIDER, upsert_user_exchange_credential


def _session_factory(tmp_path: Path):
    db_file = tmp_path / "monitor_prefs_test.db"
    engine = create_engine(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE monitor_preferences RESTART IDENTITY CASCADE"))
        connection.execute(text("TRUNCATE TABLE user_exchange_credentials RESTART IDENTITY CASCADE"))
    return TestingSessionLocal


def test_monitor_preferences_defaults_to_empty_map(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        response = monitor_preferences.list_monitor_preferences(current_user_id="user-a", db=db)
    assert response == {}


def test_monitor_preferences_put_and_get_roundtrip(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        put_response = monitor_preferences.update_monitor_preferences(
            payload=monitor_preferences.MonitorPreferenceUpdate(
                in_portfolio=True,
                card_mode="strategy",
                price_timeframe="4h",
            ),
            symbol="BTC/USDT",
            current_user_id="user-a",
            db=db,
        )
        get_response = monitor_preferences.list_monitor_preferences(current_user_id="user-a", db=db)

    assert put_response == {
        "in_portfolio": True,
        "card_mode": "strategy",
        "price_timeframe": "4h",
        "theme": "dark-green",
    }
    assert get_response == {
        "BTC/USDT": {
            "in_portfolio": True,
            "card_mode": "strategy",
            "price_timeframe": "4h",
            "theme": "dark-green",
        },
    }


def test_monitor_preferences_put_partial_update_keeps_defaults(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        first = monitor_preferences.update_monitor_preferences(
            payload=monitor_preferences.MonitorPreferenceUpdate(in_portfolio=True),
            symbol="NVDA",
            current_user_id="user-a",
            db=db,
        )
        second = monitor_preferences.update_monitor_preferences(
            payload=monitor_preferences.MonitorPreferenceUpdate(card_mode="strategy"),
            symbol="NVDA",
            current_user_id="user-a",
            db=db,
        )
        final = monitor_preferences.list_monitor_preferences(current_user_id="user-a", db=db)

    assert first == {
        "in_portfolio": True,
        "card_mode": "price",
        "price_timeframe": "1d",
        "theme": "dark-green",
    }
    assert second == {
        "in_portfolio": True,
        "card_mode": "strategy",
        "price_timeframe": "1d",
        "theme": "dark-green",
    }
    assert final == {
        "NVDA": {
            "in_portfolio": True,
            "card_mode": "strategy",
            "price_timeframe": "1d",
            "theme": "dark-green",
        },
    }


def test_monitor_preferences_put_requires_at_least_one_field(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        with pytest.raises(HTTPException) as exc:
            monitor_preferences.update_monitor_preferences(
                payload=monitor_preferences.MonitorPreferenceUpdate(),
                symbol="NVDA",
                current_user_id="user-a",
                db=db,
            )
    assert "At least one field must be provided" in str(exc.value.detail)


def test_monitor_preferences_price_timeframe_persists_for_crypto(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        first = monitor_preferences.update_monitor_preferences(
            payload=monitor_preferences.MonitorPreferenceUpdate(price_timeframe="15m"),
            symbol="BTC/USDT",
            current_user_id="user-a",
            db=db,
        )
        second = monitor_preferences.list_monitor_preferences(current_user_id="user-a", db=db)

    assert first == {
        "in_portfolio": False,
        "card_mode": "price",
        "price_timeframe": "15m",
        "theme": "dark-green",
    }
    assert second["BTC/USDT"]["price_timeframe"] == "15m"
    assert second["BTC/USDT"]["theme"] == "dark-green"


def test_monitor_preferences_rejects_intraday_timeframe_for_stock(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        with pytest.raises(HTTPException) as exc:
            monitor_preferences.update_monitor_preferences(
                payload=monitor_preferences.MonitorPreferenceUpdate(price_timeframe="4h"),
                symbol="NVDA",
                current_user_id="user-a",
                db=db,
            )
    assert "Stocks currently support only timeframe='1d'" in str(exc.value.detail)


def test_monitor_preferences_are_scoped_per_user(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        first = monitor_preferences.update_monitor_preferences(
            payload=monitor_preferences.MonitorPreferenceUpdate(
                in_portfolio=True,
                card_mode="strategy",
                price_timeframe="4h",
            ),
            symbol="BTC/USDT",
            current_user_id="user-a",
            db=db,
        )
        second = monitor_preferences.list_monitor_preferences(current_user_id="user-b", db=db)
        third = monitor_preferences.update_monitor_preferences(
            payload=monitor_preferences.MonitorPreferenceUpdate(
                in_portfolio=False,
                card_mode="price",
                price_timeframe="15m",
            ),
            symbol="BTC/USDT",
            current_user_id="user-b",
            db=db,
        )
        first_user = monitor_preferences.list_monitor_preferences(current_user_id="user-a", db=db)

    assert first["card_mode"] == "strategy"
    assert second == {}
    assert third["price_timeframe"] == "15m"
    assert first_user == {
        "BTC/USDT": {
            "in_portfolio": True,
            "card_mode": "strategy",
            "price_timeframe": "4h",
            "theme": "dark-green",
        },
    }


def test_monitor_preferences_reject_manual_portfolio_override_for_crypto_with_binance(
    tmp_path: Path,
):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        upsert_user_exchange_credential(
            db,
            user_id="user-a",
            provider=BINANCE_PROVIDER,
            api_key="test-api-key",
            api_secret="test-api-secret-123",
        )
        with pytest.raises(HTTPException) as exc:
            monitor_preferences.update_monitor_preferences(
                payload=monitor_preferences.MonitorPreferenceUpdate(in_portfolio=True),
                symbol="BTC/USDT",
                current_user_id="user-a",
                db=db,
            )

    assert exc.value.status_code == 409
    assert "cannot be changed manually" in str(exc.value.detail)


def test_monitor_preferences_allows_manual_portfolio_override_for_stock_with_binance(
    tmp_path: Path,
):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        upsert_user_exchange_credential(
            db,
            user_id="user-a",
            provider=BINANCE_PROVIDER,
            api_key="test-api-key",
            api_secret="test-api-secret-123",
        )
        response = monitor_preferences.update_monitor_preferences(
            payload=monitor_preferences.MonitorPreferenceUpdate(in_portfolio=True),
            symbol="NVDA",
            current_user_id="user-a",
            db=db,
        )

    assert response == {
        "in_portfolio": True,
        "card_mode": "price",
        "price_timeframe": "1d",
        "theme": "dark-green",
    }


def test_monitor_preferences_allows_non_portfolio_updates_for_crypto_with_binance(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        upsert_user_exchange_credential(
            db,
            user_id="user-a",
            provider=BINANCE_PROVIDER,
            api_key="test-api-key",
            api_secret="test-api-secret-123",
        )
        response = monitor_preferences.update_monitor_preferences(
            payload=monitor_preferences.MonitorPreferenceUpdate(
                card_mode="strategy", price_timeframe="4h"
            ),
            symbol="BTC/USDT",
            current_user_id="user-a",
            db=db,
        )

    assert response == {
        "in_portfolio": False,
        "card_mode": "strategy",
        "price_timeframe": "4h",
        "theme": "dark-green",
    }
