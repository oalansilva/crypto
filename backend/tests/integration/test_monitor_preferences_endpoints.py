from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.routes import monitor_preferences


def _build_test_app(tmp_path: Path) -> FastAPI:
    db_file = tmp_path / "monitor_prefs_test.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def _get_db_override():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(monitor_preferences.router)
    app.dependency_overrides[get_db] = _get_db_override
    return app


async def test_monitor_preferences_defaults_to_empty_map(tmp_path: Path):
    app = _build_test_app(tmp_path)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/monitor/preferences")

    assert response.status_code == 200, response.text
    assert response.json() == {}


async def test_monitor_preferences_put_and_get_roundtrip(tmp_path: Path):
    app = _build_test_app(tmp_path)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        put_response = await client.put(
            "/api/monitor/preferences/BTC/USDT",
            json={"in_portfolio": True, "card_mode": "strategy", "price_timeframe": "4h"},
        )
        get_response = await client.get("/api/monitor/preferences")

    assert put_response.status_code == 200, put_response.text
    assert put_response.json() == {"in_portfolio": True, "card_mode": "strategy", "price_timeframe": "4h"}

    assert get_response.status_code == 200, get_response.text
    assert get_response.json() == {
        "BTC/USDT": {"in_portfolio": True, "card_mode": "strategy", "price_timeframe": "4h"},
    }


async def test_monitor_preferences_put_partial_update_keeps_defaults(tmp_path: Path):
    app = _build_test_app(tmp_path)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        first = await client.put(
            "/api/monitor/preferences/NVDA",
            json={"in_portfolio": True},
        )
        second = await client.put(
            "/api/monitor/preferences/NVDA",
            json={"card_mode": "strategy"},
        )
        final = await client.get("/api/monitor/preferences")

    assert first.status_code == 200, first.text
    assert first.json() == {"in_portfolio": True, "card_mode": "price", "price_timeframe": "1d"}

    assert second.status_code == 200, second.text
    assert second.json() == {"in_portfolio": True, "card_mode": "strategy", "price_timeframe": "1d"}

    assert final.status_code == 200, final.text
    assert final.json() == {
        "NVDA": {"in_portfolio": True, "card_mode": "strategy", "price_timeframe": "1d"},
    }


async def test_monitor_preferences_put_requires_at_least_one_field(tmp_path: Path):
    app = _build_test_app(tmp_path)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.put("/api/monitor/preferences/NVDA", json={})

    assert response.status_code == 400, response.text
    assert "At least one field must be provided" in response.json()["detail"]


async def test_monitor_preferences_price_timeframe_persists_for_crypto(tmp_path: Path):
    app = _build_test_app(tmp_path)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        first = await client.put(
            "/api/monitor/preferences/BTC/USDT",
            json={"price_timeframe": "15m"},
        )
        second = await client.get("/api/monitor/preferences")

    assert first.status_code == 200, first.text
    assert first.json() == {"in_portfolio": False, "card_mode": "price", "price_timeframe": "15m"}
    assert second.status_code == 200, second.text
    assert second.json()["BTC/USDT"]["price_timeframe"] == "15m"


async def test_monitor_preferences_rejects_intraday_timeframe_for_stock(tmp_path: Path):
    app = _build_test_app(tmp_path)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.put(
            "/api/monitor/preferences/NVDA",
            json={"price_timeframe": "4h"},
        )

    assert response.status_code == 400, response.text
    assert "Stocks currently support only timeframe='1d'" in response.json()["detail"]
