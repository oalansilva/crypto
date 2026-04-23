from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
import threading as _stdlib_threading
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI, Request
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from app.database import Base
from app.middleware.authMiddleware import get_current_user_optional
from app.models_signal_history import SignalHistory
from app.routes.signals import router as signals_router
from app.database import SessionLocal
from app.schemas.signal import (
    BollingerBandsPayload,
    RiskProfile,
    Signal,
    SignalIndicators,
    SignalType,
)
from app.routes import signals as signals_routes
from app.services import binance_service, sentiment_service


async def _dummy_latest_prices(assets: list[str]):
    return {asset: 100.0 for asset in assets}, datetime.now(UTC), False


@pytest.fixture(autouse=True)
def _reset_signal_caches(monkeypatch):
    binance_service.clear_signal_feed_snapshot_cache()
    binance_service.clear_signal_feed_snapshot_file()
    binance_service._SIGNAL_LOOKUP.clear()
    monkeypatch.setattr(binance_service, "get_latest_prices", _dummy_latest_prices)
    yield
    binance_service.clear_signal_feed_snapshot_cache()
    binance_service.clear_signal_feed_snapshot_file()
    binance_service._SIGNAL_LOOKUP.clear()


def _build_test_app() -> FastAPI:
    app = FastAPI()

    @app.middleware("http")
    async def add_signals_disclaimer_header(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/signals"):
            response.headers["X-Disclaimer"] = (
                "Isenção de responsabilidade: este não é advice financeiro."
            )
        return response

    app.include_router(signals_router)
    return app


def _make_signal(
    asset: str,
    signal_type: SignalType,
    confidence: int,
    risk_profile: RiskProfile,
    hours_ago: int = 0,
) -> Signal:
    created_at = datetime.now(UTC) - timedelta(hours=hours_ago)
    return Signal(
        id=str(uuid4()),
        asset=asset,
        type=signal_type,
        confidence=confidence,
        target_price=110.0 if signal_type != SignalType.SELL else 90.0,
        stop_loss=95.0 if signal_type != SignalType.SELL else 105.0,
        indicators=SignalIndicators(
            RSI=32.0,
            MACD="bullish",
            BollingerBands=BollingerBandsPayload(upper=110.0, middle=100.0, lower=90.0),
        ),
        created_at=created_at,
        risk_profile=risk_profile,
        entry_price=100.0,
    )


async def _dummy_klines(asset: str, interval: str = "1h", limit: int = 120):
    return {
        "candles": [{"open_time": datetime.now(UTC), "close": 100.0}],
        "cached_at": datetime.now(UTC),
        "is_stale": False,
    }


async def _dummy_pairs(*_args, **_kwargs):
    return ["BTCUSDT", "ETHUSDT", "SOLUSDT"]


async def _dummy_single_pair(*_args, **_kwargs):
    return ["BTCUSDT"]


async def _dummy_two_pairs(*_args, **_kwargs):
    return ["BTCUSDT", "ETHUSDT"]


async def test_signals_list_filters_threshold_and_adds_disclaimer(monkeypatch):
    app = _build_test_app()

    def _fake_build_signal(*, asset: str, risk_profile: RiskProfile, candles, sentiment_score=None):
        mapping = {
            "BTCUSDT": _make_signal(asset, SignalType.BUY, 88, risk_profile),
            "ETHUSDT": _make_signal(asset, SignalType.HOLD, 69, risk_profile),
            "SOLUSDT": _make_signal(asset, SignalType.SELL, 74, risk_profile),
        }
        return mapping[asset]

    monkeypatch.setattr(binance_service, "get_klines", _dummy_klines)
    monkeypatch.setattr(binance_service, "_build_signal", _fake_build_signal)
    monkeypatch.setattr(binance_service, "_get_all_usdt_pairs", _dummy_pairs)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/signals?confidence_min=70&risk_profile=moderate&limit=10")

    assert response.status_code == 200, response.text
    assert (
        response.headers["X-Disclaimer"]
        == "Isenção de responsabilidade: este não é advice financeiro."
    )

    payload = response.json()
    assert payload["total"] == 1
    assert [item["asset"] for item in payload["signals"]] == ["BTCUSDT"]
    assert all(item["confidence"] >= 70 for item in payload["signals"])


async def test_signals_latest_returns_only_high_confidence(monkeypatch):
    app = _build_test_app()

    def _fake_build_signal(*, asset: str, risk_profile: RiskProfile, candles, sentiment_score=None):
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
        return _make_signal(
            asset, SignalType.BUY, confidence_map[(asset, risk_profile)], risk_profile
        )

    monkeypatch.setattr(binance_service, "get_klines", _dummy_klines)
    monkeypatch.setattr(binance_service, "_build_signal", _fake_build_signal)
    monkeypatch.setattr(binance_service, "_get_all_usdt_pairs", _dummy_pairs)

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

    def _fake_build_signal(*, asset: str, risk_profile: RiskProfile, candles, sentiment_score=None):
        return _make_signal(asset, SignalType.BUY, 88, risk_profile)

    monkeypatch.setattr(binance_service, "get_klines", _dummy_klines)
    monkeypatch.setattr(binance_service, "_build_signal", _fake_build_signal)
    monkeypatch.setattr(binance_service, "_get_all_usdt_pairs", _dummy_single_pair)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        list_response = await client.get("/api/signals?confidence_min=0")
        signal_id = list_response.json()["signals"][0]["id"]
        detail_response = await client.get(f"/api/signals/{signal_id}")

    assert detail_response.status_code == 200, detail_response.text
    assert detail_response.json()["id"] == signal_id


async def test_signals_list_only_persists_history_for_authenticated_user(monkeypatch):
    app = _build_test_app()

    def _fake_build_signal(*, asset: str, risk_profile: RiskProfile, candles, sentiment_score=None):
        return _make_signal(asset, SignalType.BUY, 88, risk_profile)

    persisted_calls: list[tuple[str, str | None]] = []

    class _FakeThread(_stdlib_threading.Thread):
        def __init__(self, *args, **kwargs):
            if self.__class__ is not _FakeThread:
                super().__init__(*args, **kwargs)
                return

            self._target = kwargs.get("target")
            if args and len(args) > 1:
                self._args = args[1]
            else:
                self._args = kwargs.get("args", ())
            if not isinstance(self._args, tuple):
                self._args = tuple(self._args)

        def start(self):
            if self.__class__ is not _FakeThread:
                return super().start()

            signal = self._args[0]
            user_id = self._args[1] if len(self._args) > 1 else None
            persisted_calls.append((signal.id, user_id))

    monkeypatch.setattr(binance_service, "get_klines", _dummy_klines)
    monkeypatch.setattr(binance_service, "_build_signal", _fake_build_signal)
    monkeypatch.setattr(binance_service.threading, "Thread", _FakeThread)
    monkeypatch.setattr(binance_service, "_get_all_usdt_pairs", _dummy_two_pairs)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/signals?confidence_min=0&asset=BTCUSDT")

    assert response.status_code == 200, response.text
    assert persisted_calls == []

    app.dependency_overrides[get_current_user_optional] = lambda: "user-123"
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/api/signals?confidence_min=0&asset=ETHUSDT")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200, response.text
    assert len(persisted_calls) == 1
    assert persisted_calls[0][1] == "user-123"


async def test_signals_list_skips_low_quality_signals_for_history(monkeypatch):
    app = _build_test_app()

    def _fake_build_signal(*, asset: str, risk_profile: RiskProfile, candles, sentiment_score=None):
        return Signal(
            id=str(uuid4()),
            asset=asset,
            type=SignalType.BUY,
            confidence=62,
            target_price=103.0,
            stop_loss=98.0,
            indicators=SignalIndicators(
                RSI=42.0,
                MACD="neutral",
                BollingerBands=BollingerBandsPayload(upper=110.0, middle=100.0, lower=90.0),
            ),
            created_at=datetime.now(UTC),
            risk_profile=risk_profile,
            entry_price=100.0,
        )

    persisted_calls: list[tuple[str, str | None]] = []

    class _FakeThread(_stdlib_threading.Thread):
        def __init__(self, *args, **kwargs):
            if self.__class__ is not _FakeThread:
                super().__init__(*args, **kwargs)
                return

            self._target = kwargs.get("target")
            if args and len(args) > 1:
                self._args = args[1]
            else:
                self._args = kwargs.get("args", ())
            if not isinstance(self._args, tuple):
                self._args = tuple(self._args)

        def start(self):
            if self.__class__ is not _FakeThread:
                return super().start()

            if not self._args:
                return

            signal = self._args[0]
            user_id = self._args[1] if len(self._args) > 1 else None
            with SessionLocal() as db:
                if signals_routes._passes_history_quality_gate(signal, db):
                    persisted_calls.append((signal.id, user_id))

    monkeypatch.setattr(binance_service, "get_klines", _dummy_klines)
    monkeypatch.setattr(binance_service, "_build_signal", _fake_build_signal)
    monkeypatch.setattr(binance_service.threading, "Thread", _FakeThread)
    monkeypatch.setattr(binance_service, "_get_all_usdt_pairs", _dummy_single_pair)
    app.dependency_overrides[get_current_user_optional] = lambda: "user-123"

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/api/signals?confidence_min=0&asset=BTCUSDT")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200, response.text
    assert persisted_calls == []


async def test_signals_list_persists_only_when_new_calibrated_gate_passes(
    monkeypatch, tmp_path: Path
):
    app = _build_test_app()
    session_local = _session_factory(tmp_path)

    def _fake_build_signal(*, asset: str, risk_profile: RiskProfile, candles, sentiment_score=None):
        return Signal(
            id=str(uuid4()),
            asset=asset,
            type=SignalType.BUY,
            confidence=58,
            target_price=110.0,
            stop_loss=95.0,
            indicators=SignalIndicators(
                RSI=32.0,
                MACD="neutral",
                BollingerBands=BollingerBandsPayload(upper=110.0, middle=100.0, lower=90.0),
            ),
            created_at=datetime.now(UTC),
            risk_profile=RiskProfile.moderate,
            entry_price=100.0,
        )

    persisted_calls: list[tuple[str, str | None]] = []

    class _FakeThread(_stdlib_threading.Thread):
        def __init__(self, *args, **kwargs):
            if self.__class__ is not _FakeThread:
                super().__init__(*args, **kwargs)
                return

            self._target = kwargs.get("target")
            if args and len(args) > 1:
                self._args = args[1]
            else:
                self._args = kwargs.get("args", ())
            if not isinstance(self._args, tuple):
                self._args = tuple(self._args)

        def start(self):
            if self.__class__ is not _FakeThread:
                return super().start()

            if not self._args:
                return

            signal = self._args[0]
            user_id = self._args[1] if len(self._args) > 1 else None
            with session_local() as db:
                if signals_routes._passes_history_quality_gate(signal, db):
                    persisted_calls.append((signal.id, user_id))

    monkeypatch.setattr(binance_service, "get_klines", _dummy_klines)
    monkeypatch.setattr(binance_service, "_build_signal", _fake_build_signal)
    monkeypatch.setattr(binance_service.threading, "Thread", _FakeThread)
    monkeypatch.setattr(binance_service, "_get_all_usdt_pairs", _dummy_single_pair)
    app.dependency_overrides[get_current_user_optional] = lambda: "user-123"

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/api/signals?confidence_min=0&asset=BTCUSDT")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200, response.text
    assert len(persisted_calls) == 1


async def test_signals_list_uses_precomputed_snapshot_when_available(monkeypatch):
    app = _build_test_app()
    build_calls: list[str] = []

    def _fake_build_signal(*, asset: str, risk_profile: RiskProfile, candles, sentiment_score=None):
        build_calls.append(f"{risk_profile.value}:{asset}")
        return _make_signal(asset, SignalType.BUY, 88, risk_profile)

    async def _fake_sentiment():
        return sentiment_service.SentimentResult(
            score=55, components={"news": 55, "reddit": 55, "fear_greed": 55}, signal="neutral"
        )

    monkeypatch.setattr(binance_service, "get_klines", _dummy_klines)
    monkeypatch.setattr(binance_service, "_build_signal", _fake_build_signal)
    monkeypatch.setattr(binance_service, "_get_all_usdt_pairs", _dummy_pairs)
    monkeypatch.setattr(sentiment_service, "get_market_sentiment", _fake_sentiment)

    await binance_service.refresh_signal_feed_snapshots()
    initial_builds = list(build_calls)
    assert initial_builds

    async def _unexpected_klines(*args, **kwargs):
        raise AssertionError("endpoint should use precomputed snapshot")

    monkeypatch.setattr(binance_service, "get_klines", _unexpected_klines)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/signals?confidence_min=70&risk_profile=moderate&limit=10")

    assert response.status_code == 200, response.text
    assert build_calls == initial_builds


async def test_signal_snapshots_can_be_loaded_from_disk(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        binance_service, "SIGNAL_FEED_SNAPSHOT_FILE", tmp_path / "signals_snapshot.json"
    )

    def _fake_build_signal(*, asset: str, risk_profile: RiskProfile, candles, sentiment_score=None):
        return _make_signal(asset, SignalType.BUY, 88, risk_profile)

    async def _fake_sentiment():
        return sentiment_service.SentimentResult(
            score=55, components={"news": 55, "reddit": 55, "fear_greed": 55}, signal="neutral"
        )

    monkeypatch.setattr(binance_service, "get_klines", _dummy_klines)
    monkeypatch.setattr(binance_service, "_build_signal", _fake_build_signal)
    monkeypatch.setattr(binance_service, "_get_all_usdt_pairs", _dummy_pairs)
    monkeypatch.setattr(sentiment_service, "get_market_sentiment", _fake_sentiment)

    await binance_service.refresh_signal_feed_snapshots()
    binance_service.clear_signal_feed_snapshot_cache()

    assert binance_service.load_signal_feed_snapshots_from_disk() is True
    snapshot = binance_service.get_signal_feed_snapshot(RiskProfile.moderate)
    assert snapshot is not None
    assert len(snapshot.signals) == 3
    assert snapshot.available_assets == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]


def _session_factory(tmp_path: Path):
    engine = create_engine(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE system_preferences RESTART IDENTITY CASCADE"))
        connection.execute(text("TRUNCATE TABLE signal_history RESTART IDENTITY CASCADE"))
    return testing_session_local


def test_history_quality_gate_uses_defaults_when_system_preferences_table_is_missing():
    signal = _make_signal("BTCUSDT", SignalType.BUY, 88, RiskProfile.moderate)

    class _FailingQuery:
        def filter(self, *_args, **_kwargs):
            return self

        def first(self):
            raise OperationalError(
                "SELECT 1", (), Exception("relation system_preferences does not exist")
            )

    class _FailingSession:
        def query(self, *_args, **_kwargs):
            return _FailingQuery()

    assert signals_routes._passes_history_quality_gate(signal, _FailingSession()) is True


async def test_open_positions_returns_entry_current_price_and_pnl(monkeypatch, tmp_path: Path):
    app = _build_test_app()
    session_local = _session_factory(tmp_path)
    now = datetime.now(UTC)

    monkeypatch.setattr(signals_routes, "SessionLocal", session_local)

    async def _fake_latest_prices(assets: list[str]):
        assert assets == ["BTCUSDT"]
        return {"BTCUSDT": 110.0}, now, False

    monkeypatch.setattr(binance_service, "get_latest_prices", _fake_latest_prices)
    app.dependency_overrides[signals_routes.get_current_user] = lambda: "user-123"

    with session_local() as db:
        db.add(
            SignalHistory(
                id="sig-open-1",
                user_id="user-123",
                asset="BTCUSDT",
                type="BUY",
                confidence=88,
                target_price=120.0,
                stop_loss=95.0,
                indicators=None,
                created_at=now,
                risk_profile="moderate",
                status="ativo",
                entry_price=100.0,
                archived="no",
            )
        )
        db.commit()

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/api/signals/open-positions")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 1
    assert payload["positions"][0]["asset"] == "BTCUSDT"
    assert payload["positions"][0]["entry_price"] == 100.0
    assert payload["positions"][0]["current_price"] == 110.0
    assert payload["positions"][0]["pnl_percent"] == 10.0


async def test_signal_history_filters_best_signals_by_pnl_and_sort(monkeypatch, tmp_path: Path):
    app = _build_test_app()
    session_local = _session_factory(tmp_path)
    now = datetime.now(UTC)

    monkeypatch.setattr(signals_routes, "SessionLocal", session_local)
    app.dependency_overrides[signals_routes.get_current_user] = lambda: "user-123"

    with session_local() as db:
        db.add_all(
            [
                SignalHistory(
                    id="hist-1",
                    user_id="user-123",
                    asset="BTCUSDT",
                    type="BUY",
                    confidence=91,
                    target_price=120.0,
                    stop_loss=95.0,
                    indicators='{"RSI": 32.0, "MACD": "neutral", "BollingerBands": {"upper": 120.0, "middle": 100.0, "lower": 90.0}}',
                    created_at=now,
                    risk_profile="aggressive",
                    status="disparado",
                    entry_price=100.0,
                    exit_price=115.0,
                    pnl=15.0,
                    archived="no",
                ),
                SignalHistory(
                    id="hist-2",
                    user_id="user-123",
                    asset="ETHUSDT",
                    type="BUY",
                    confidence=82,
                    target_price=120.0,
                    stop_loss=95.0,
                    indicators='{"RSI": 33.0, "MACD": "neutral", "BollingerBands": {"upper": 120.0, "middle": 100.0, "lower": 90.0}}',
                    created_at=now,
                    risk_profile="aggressive",
                    status="disparado",
                    entry_price=100.0,
                    exit_price=108.0,
                    pnl=8.0,
                    archived="no",
                ),
                SignalHistory(
                    id="hist-3",
                    user_id="user-123",
                    asset="SOLUSDT",
                    type="BUY",
                    confidence=88,
                    target_price=120.0,
                    stop_loss=95.0,
                    indicators='{"RSI": 36.0, "MACD": "neutral", "BollingerBands": {"upper": 120.0, "middle": 100.0, "lower": 90.0}}',
                    created_at=now,
                    risk_profile="moderate",
                    status="disparado",
                    entry_price=100.0,
                    exit_price=97.0,
                    pnl=-3.0,
                    archived="no",
                ),
            ]
        )
        db.commit()

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/api/signals/history?status=disparado&risk_profile=aggressive&pnl_filter=positive&sort_by=pnl&sort_order=desc"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 2
    assert [item["asset"] for item in payload["signals"]] == ["BTCUSDT", "ETHUSDT"]
