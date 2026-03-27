from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
from fastapi import FastAPI, Request

from app.routes.signals import router as signals_router
from app.schemas.signal import BollingerBandsPayload, RiskProfile, Signal, SignalIndicators, SignalType
from app.services import binance_service


def _build_test_app() -> FastAPI:
    app = FastAPI()

    @app.middleware("http")
    async def add_signals_disclaimer_header(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/signals"):
            response.headers["X-Disclaimer"] = "Isenção de responsabilidade: este não é advice financeiro."
        return response

    app.include_router(signals_router)
    return app


def _make_signal(asset: str, signal_type: SignalType, confidence: int, risk_profile: RiskProfile, hours_ago: int = 0) -> Signal:
    created_at = datetime.now(UTC) - timedelta(hours=hours_ago)
    return Signal(
        id=str(uuid4()),
        asset=asset,
        type=signal_type,
        confidence=confidence,
        target_price=100.0,
        stop_loss=90.0,
        indicators=SignalIndicators(
            RSI=42.0,
            MACD="bullish",
            BollingerBands=BollingerBandsPayload(upper=110.0, middle=100.0, lower=90.0),
        ),
        created_at=created_at,
        risk_profile=risk_profile,
    )


async def _dummy_klines(asset: str, interval: str = "1h", limit: int = 120):
    return {"candles": [{"open_time": datetime.now(UTC), "close": 100.0}], "cached_at": datetime.now(UTC), "is_stale": False}


async def test_signals_list_filters_threshold_and_adds_disclaimer(monkeypatch):
    app = _build_test_app()

    def _fake_build_signal(*, asset: str, risk_profile: RiskProfile, candles):
        mapping = {
            "BTCUSDT": _make_signal(asset, SignalType.BUY, 88, risk_profile),
            "ETHUSDT": _make_signal(asset, SignalType.HOLD, 69, risk_profile),
            "SOLUSDT": _make_signal(asset, SignalType.SELL, 74, risk_profile),
        }
        return mapping[asset]

    monkeypatch.setattr(binance_service, "get_klines", _dummy_klines)
    monkeypatch.setattr(binance_service, "_build_signal", _fake_build_signal)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/signals?confidence_min=70&risk_profile=moderate&limit=10")

    assert response.status_code == 200, response.text
    assert response.headers["X-Disclaimer"] == "Isenção de responsabilidade: este não é advice financeiro."

    payload = response.json()
    assert payload["total"] == 2
    assert sorted(item["asset"] for item in payload["signals"]) == ["BTCUSDT", "SOLUSDT"]
    assert all(item["confidence"] >= 70 for item in payload["signals"])


async def test_signals_latest_returns_only_high_confidence(monkeypatch):
    app = _build_test_app()

    def _fake_build_signal(*, asset: str, risk_profile: RiskProfile, candles):
        confidence_map = {
            ("BTCUSDT", RiskProfile.conservative): 82,
            ("ETHUSDT", RiskProfile.conservative): 71,
            ("SOLUSDT", RiskProfile.conservative): 65,
            ("BTCUSDT", RiskProfile.moderate): 78,
            ("ETHUSDT", RiskProfile.moderate): 88,
            ("SOLUSDT", RiskProfile.moderate): 69,
            ("BTCUSDT", RiskProfile.aggressive): 90,
            ("ETHUSDT", RiskProfile.aggressive): 73,
            ("SOLUSDT", RiskProfile.aggressive): 55,
        }
        return _make_signal(asset, SignalType.BUY, confidence_map[(asset, risk_profile)], risk_profile)

    monkeypatch.setattr(binance_service, "get_klines", _dummy_klines)
    monkeypatch.setattr(binance_service, "_build_signal", _fake_build_signal)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/signals/latest")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 6
    assert len(payload["signals"]) == 5
    assert all(item["confidence"] >= 70 for item in payload["signals"])


async def test_signals_detail_returns_cached_signal(monkeypatch):
    app = _build_test_app()

    def _fake_build_signal(*, asset: str, risk_profile: RiskProfile, candles):
        return _make_signal(asset, SignalType.BUY, 88, risk_profile)

    monkeypatch.setattr(binance_service, "get_klines", _dummy_klines)
    monkeypatch.setattr(binance_service, "_build_signal", _fake_build_signal)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        list_response = await client.get("/api/signals?confidence_min=0")
        signal_id = list_response.json()["signals"][0]["id"]
        detail_response = await client.get(f"/api/signals/{signal_id}")

    assert detail_response.status_code == 200, detail_response.text
    assert detail_response.json()["id"] == signal_id
