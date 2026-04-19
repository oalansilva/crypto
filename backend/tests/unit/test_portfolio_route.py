from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import PortfolioSnapshot
import app.routes.portfolio as portfolio_route


@pytest.fixture
def portfolio_db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def test_portfolio_helpers_cover_latest_snapshot_save_and_drawdown(
    monkeypatch, portfolio_db_session
):
    class FrozenDateTime(datetime):
        calls = 0

        @classmethod
        def now(cls, tz=None):
            cls.calls += 1
            return cls(2026, 4, 18, 12, 0, cls.calls)

    monkeypatch.setattr(portfolio_route, "datetime", FrozenDateTime)

    assert portfolio_route._get_latest_snapshot(portfolio_db_session, "user-1") is None
    assert portfolio_route._calculate_drawdown_30d([]) == (0.0, None)
    assert portfolio_route._calculate_drawdown_30d(
        [{"total_usd": 0, "recorded_at": "2026-04-18"}]
    ) == (
        0.0,
        None,
    )

    first_id = portfolio_route._save_snapshot(
        portfolio_db_session,
        total_usd=1000.0,
        btc_value=500.0,
        usdt_value=300.0,
        eth_value=100.0,
        other_usd=100.0,
        pnl_today_pct=1.2,
        drawdown_30d_pct=-2.5,
        drawdown_peak_date="2026-04-10",
        btc_change_24h_pct=3.1,
        user_id="user-1",
    )
    second_id = portfolio_route._save_snapshot(
        portfolio_db_session,
        total_usd=1200.0,
        btc_value=600.0,
        usdt_value=400.0,
        eth_value=100.0,
        other_usd=100.0,
        pnl_today_pct=2.5,
        drawdown_30d_pct=-1.0,
        drawdown_peak_date="2026-04-11",
        btc_change_24h_pct=4.0,
        user_id="user-2",
    )
    assert second_id == first_id + 1

    latest_user = portfolio_route._get_latest_snapshot(portfolio_db_session, "user-1")
    latest_any = portfolio_route._get_latest_snapshot(portfolio_db_session)
    assert latest_user["user_id"] == "user-1"
    assert latest_user["total_usd"] == 1000.0
    assert latest_any["user_id"] == "user-2"

    older = PortfolioSnapshot(
        recorded_at=datetime.now() - timedelta(days=5),
        total_usd=900.0,
        user_id="user-1",
    )
    newer = PortfolioSnapshot(
        recorded_at=datetime.now() - timedelta(days=1),
        total_usd=1100.0,
        user_id="user-1",
    )
    stale = PortfolioSnapshot(
        recorded_at=datetime.now() - timedelta(days=40),
        total_usd=800.0,
        user_id="user-1",
    )
    portfolio_db_session.add_all([older, newer, stale])
    portfolio_db_session.commit()

    recent = portfolio_route._get_30d_snapshots(portfolio_db_session, "user-1")
    assert len(recent) >= 2

    drawdown, peak_date = portfolio_route._calculate_drawdown_30d(
        [
            {"total_usd": 1000.0, "recorded_at": "2026-04-10T00:00:00"},
            {"total_usd": 1400.0, "recorded_at": datetime(2026, 4, 15, 0, 0, 0)},
            {"total_usd": 1050.0, "recorded_at": "2026-04-18T00:00:00"},
        ]
    )
    assert drawdown == -25.0
    assert peak_date == "2026-04-15"


@pytest.mark.asyncio
async def test_get_portfolio_kpi_covers_error_and_success_paths(monkeypatch, portfolio_db_session):
    class FakeAsyncResponse:
        def json(self):
            return {"symbol": "BTCUSDT", "priceChangePercent": "4.5"}

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params):
            assert "ticker/24hr" in url
            assert params == {"symbols": '["BTCUSDT"]'}
            return FakeAsyncResponse()

    monkeypatch.setattr(
        portfolio_route.httpx if hasattr(portfolio_route, "httpx") else __import__("httpx"),
        "AsyncClient",
        lambda timeout: FakeAsyncClient(),
    )

    monkeypatch.setattr(
        portfolio_route, "get_user_exchange_credential", lambda *args, **kwargs: None
    )
    with pytest.raises(HTTPException) as missing_cred_exc:
        await portfolio_route.get_portfolio_kpi("user-1", portfolio_db_session)
    assert missing_cred_exc.value.status_code == 503

    monkeypatch.setattr(
        portfolio_route,
        "get_user_exchange_credential",
        lambda *args, **kwargs: SimpleNamespace(api_key="key", api_secret="secret"),
    )
    monkeypatch.setattr(
        portfolio_route,
        "fetch_spot_balances_snapshot",
        lambda **kwargs: (_ for _ in ()).throw(portfolio_route.BinanceConfigError("missing")),
    )
    with pytest.raises(HTTPException) as config_exc:
        await portfolio_route.get_portfolio_kpi("user-1", portfolio_db_session)
    assert config_exc.value.status_code == 503

    monkeypatch.setattr(
        portfolio_route,
        "fetch_spot_balances_snapshot",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("binance unavailable")),
    )
    with pytest.raises(HTTPException) as gateway_exc:
        await portfolio_route.get_portfolio_kpi("user-1", portfolio_db_session)
    assert gateway_exc.value.status_code == 502

    yesterday_snapshot = PortfolioSnapshot(
        recorded_at=datetime.now() - timedelta(days=1),
        total_usd=1000.0,
        btc_value=600.0,
        usdt_value=200.0,
        eth_value=100.0,
        other_usd=100.0,
        user_id="user-1",
    )
    historical_peak = PortfolioSnapshot(
        recorded_at=datetime.now() - timedelta(days=10),
        total_usd=1500.0,
        btc_value=900.0,
        usdt_value=300.0,
        eth_value=150.0,
        other_usd=150.0,
        user_id="user-1",
    )
    portfolio_db_session.add_all([yesterday_snapshot, historical_peak])
    portfolio_db_session.commit()

    monkeypatch.setattr(
        portfolio_route,
        "fetch_spot_balances_snapshot",
        lambda **kwargs: {
            "balances": [
                {"asset": "BTC", "value_usd": 800.0},
                {"asset": "USDT", "value_usd": 300.0},
                {"asset": "ETH", "value_usd": 200.0},
                {"asset": "SOL", "value_usd": 100.0},
            ],
            "total_usd": 1400.0,
        },
    )
    saved_calls: list[dict] = []

    real_save_snapshot = portfolio_route._save_snapshot

    def tracked_save_snapshot(db, **kwargs):
        saved_calls.append(kwargs)
        return real_save_snapshot(db, **kwargs)

    monkeypatch.setattr(portfolio_route, "_save_snapshot", tracked_save_snapshot)

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: FakeAsyncClient())

    result = await portfolio_route.get_portfolio_kpi("user-1", portfolio_db_session)
    assert result["total_usd"] == 1400.0
    assert result["btc_value"] == 800.0
    assert result["usdt_value"] == 300.0
    assert result["eth_value"] == 200.0
    assert result["other_usd"] == 100.0
    assert result["btc_change_24h_pct"] == 4.5
    assert result["pnl_today_pct"] == 40.0
    assert result["pnl_today_vs_btc_pct"] == 35.5
    assert result["drawdown_30d_pct"] <= 0
    assert result["_history_insufficient"] is False
    assert saved_calls
    assert saved_calls[0]["total_usd"] == 1400.0

    saved = portfolio_route._get_latest_snapshot(portfolio_db_session, "user-1")
    assert saved is not None
    assert saved["total_usd"] == 1400.0
