from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models_signal_history import SignalHistory
from app.routes import ai_dashboard
from app.schemas.signal import RiskProfile, Signal, SignalIndicators, SignalListResponse, SignalType
from app.services.sentiment_service import SentimentResult


def _session_factory(tmp_path: Path):
    db_file = tmp_path / "ai_dashboard_test.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def _make_signal(
    *,
    signal_id: str,
    user_id: str,
    asset: str,
    signal_type: str,
    confidence: int,
    created_at: datetime,
    rsi: float,
    macd: str,
    target_price: float,
    pnl: float | None = None,
    status: str = "ativo",
) -> SignalHistory:
    return SignalHistory(
        id=signal_id,
        user_id=user_id,
        asset=asset,
        type=signal_type,
        confidence=confidence,
        target_price=target_price,
        stop_loss=target_price * 0.95,
        indicators=(
            '{"RSI": %s, "MACD": "%s", "BollingerBands": {"upper": %s, "middle": %s, "lower": %s}}'
            % (rsi, macd, target_price * 1.03, target_price, target_price * 0.97)
        ),
        created_at=created_at,
        risk_profile="moderate",
        status=status,
        entry_price=target_price,
        pnl=pnl,
        archived="no",
    )


def test_ai_dashboard_is_dynamic_and_user_scoped(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    now = datetime.now(UTC)

    async def fake_news():
        published_at = now - timedelta(minutes=15)
        return [
            ai_dashboard.DashboardNewsItem(
                id="news-1",
                title="BTC lidera fluxo institucional",
                summary="Fluxo comprador institucional sustenta o ativo no curto prazo.",
                source="TestFeed",
                url="https://example.com/news-1",
                published_at=published_at,
                relative_time="Há 15 min",
                sentiment="bullish",
                related_asset="BTC/USDT",
            )
        ]

    async def fake_sentiment():
        return SentimentResult(
            score=68,
            components={"fear_greed": 74, "news": 70, "reddit": 60},
            signal="bullish",
        )

    async def fake_signal_feed(*args, **kwargs):
        return SignalListResponse(
            signals=[
                Signal(
                    id="live-btc",
                    asset="BTCUSDT",
                    type=SignalType.BUY,
                    confidence=88,
                    target_price=99000,
                    stop_loss=94000,
                    indicators=SignalIndicators.model_validate(
                        {
                            "RSI": 33.0,
                            "MACD": "bullish",
                            "BollingerBands": {"upper": 99500, "middle": 96500, "lower": 93500},
                        }
                    ),
                    created_at=now,
                    risk_profile=RiskProfile.moderate,
                    entry_price=97000,
                    current_price=97250,
                )
            ],
            total=1,
            cached_at=now,
            is_stale=False,
            available_assets=["BTCUSDT"],
        )

    async def fake_onchain_snapshot(*args, **kwargs):
        class Pair:
            symbol = "BTCUSDT"
            token = "BTC"
            chain = "ethereum"
            last_price = 97100.0

        class Result:
            signal = "BUY"
            confidence = 72

        return [(Pair(), Result())]

    monkeypatch.setattr(ai_dashboard, "_fetch_coingecko_news", fake_news)
    monkeypatch.setattr(ai_dashboard.sentiment_service, "get_market_sentiment", fake_sentiment)
    monkeypatch.setattr(ai_dashboard.binance_service, "build_signal_feed", fake_signal_feed)
    monkeypatch.setattr(
        ai_dashboard.binance_service, "build_signal_feed_for_assets", fake_signal_feed
    )
    monkeypatch.setattr(ai_dashboard, "build_onchain_snapshot", fake_onchain_snapshot)

    with SessionLocal() as db:
        db.add_all(
            [
                _make_signal(
                    signal_id="sig-a-1",
                    user_id="user-a",
                    asset="BTCUSDT",
                    signal_type="BUY",
                    confidence=91,
                    created_at=now - timedelta(minutes=5),
                    rsi=28.4,
                    macd="bullish",
                    target_price=98000,
                    pnl=500,
                    status="disparado",
                ),
                _make_signal(
                    signal_id="sig-a-2",
                    user_id="user-a",
                    asset="ETHUSDT",
                    signal_type="SELL",
                    confidence=77,
                    created_at=now - timedelta(minutes=30),
                    rsi=74.8,
                    macd="bearish",
                    target_price=3800,
                    pnl=-100,
                    status="disparado",
                ),
                _make_signal(
                    signal_id="sig-b-1",
                    user_id="user-b",
                    asset="SOLUSDT",
                    signal_type="BUY",
                    confidence=88,
                    created_at=now - timedelta(minutes=10),
                    rsi=31.0,
                    macd="bullish",
                    target_price=190,
                ),
            ]
        )
        db.commit()

        payload = asyncio.run(ai_dashboard.get_ai_dashboard(current_user_id="user-a", db=db))

    assert payload.stats.total_signals == 2
    assert payload.stats.hit_rate == 50
    assert {item.asset for item in payload.recent_signals} == {"BTC/USDT"}
    btc_signal = next(item for item in payload.recent_signals if item.asset == "BTC/USDT")
    assert btc_signal.action == "BUY"
    assert btc_signal.direction == "Compra forte"
    assert btc_signal.strength == 3
    assert btc_signal.total_sources == 3
    assert {source.source for source in btc_signal.sources} == {
        "AI Dashboard",
        "Signals",
        "On-chain",
    }
    assert all(source.criteria for source in btc_signal.sources)
    assert btc_signal.price == 97250
    assert all(
        reading.asset != "SOL/USDT" for card in payload.indicators for reading in card.readings
    )
    assert payload.fear_greed.value == 68
    assert payload.fear_greed.label == "Greed"
    assert payload.news[0].title == "BTC lidera fluxo institucional"
    assert (
        payload.news[0].summary == "Fluxo comprador institucional sustenta o ativo no curto prazo."
    )
    assert payload.insights[0].title == "Sinal mais forte: BUY"


def test_ai_dashboard_returns_empty_dynamic_state_without_history(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)

    async def failing_news():
        raise RuntimeError("news unavailable")

    async def neutral_sentiment():
        return SentimentResult(
            score=50,
            components={"fear_greed": 50, "news": 50, "reddit": 50},
            signal="neutral",
        )

    async def empty_signal_feed(*args, **kwargs):
        return SignalListResponse(
            signals=[], total=0, cached_at=None, is_stale=False, available_assets=[]
        )

    async def empty_onchain_snapshot(*args, **kwargs):
        return []

    monkeypatch.setattr(ai_dashboard, "_fetch_coingecko_news", failing_news)
    monkeypatch.setattr(ai_dashboard.sentiment_service, "get_market_sentiment", neutral_sentiment)
    monkeypatch.setattr(ai_dashboard.binance_service, "build_signal_feed", empty_signal_feed)
    monkeypatch.setattr(
        ai_dashboard.binance_service, "build_signal_feed_for_assets", empty_signal_feed
    )
    monkeypatch.setattr(ai_dashboard, "build_onchain_snapshot", empty_onchain_snapshot)

    with SessionLocal() as db:
        payload = asyncio.run(ai_dashboard.get_ai_dashboard(current_user_id="user-empty", db=db))

    assert payload.stats.total_signals == 0
    assert payload.indicators == []
    assert payload.recent_signals == []
    assert payload.news == []
    assert payload.insights[0].id == "empty-history"
    assert payload.section_errors["news"] == "CoinGecko indisponível no momento."


def test_ai_dashboard_hides_legacy_single_source_signals_when_no_unified_overlap(
    tmp_path: Path, monkeypatch
):
    SessionLocal = _session_factory(tmp_path)
    now = datetime.now(UTC)

    async def fake_news():
        return []

    async def fake_sentiment():
        return SentimentResult(
            score=50,
            components={"fear_greed": 50, "news": 50, "reddit": 50},
            signal="neutral",
        )

    async def empty_signal_feed(*args, **kwargs):
        return SignalListResponse(
            signals=[], total=0, cached_at=now, is_stale=False, available_assets=[]
        )

    async def empty_onchain_snapshot(*args, **kwargs):
        return []

    monkeypatch.setattr(ai_dashboard, "_fetch_coingecko_news", fake_news)
    monkeypatch.setattr(ai_dashboard.sentiment_service, "get_market_sentiment", fake_sentiment)
    monkeypatch.setattr(ai_dashboard.binance_service, "build_signal_feed", empty_signal_feed)
    monkeypatch.setattr(
        ai_dashboard.binance_service, "build_signal_feed_for_assets", empty_signal_feed
    )
    monkeypatch.setattr(ai_dashboard, "build_onchain_snapshot", empty_onchain_snapshot)

    with SessionLocal() as db:
        db.add(
            _make_signal(
                signal_id="legacy-ai-only",
                user_id="user-a",
                asset="USDPUSDT",
                signal_type="BUY",
                confidence=67,
                created_at=now - timedelta(minutes=5),
                rsi=33.3,
                macd="bullish",
                target_price=1.0,
            )
        )
        db.commit()

        payload = asyncio.run(ai_dashboard.get_ai_dashboard(current_user_id="user-a", db=db))

    assert payload.recent_signals == []
    assert "Nenhum sinal unificado disponível" in payload.section_errors["signals"]


def test_ai_dashboard_targets_history_assets_when_onchain_snapshot_is_empty(
    tmp_path: Path, monkeypatch
):
    SessionLocal = _session_factory(tmp_path)
    now = datetime.now(UTC)

    async def fake_news():
        return []

    async def fake_sentiment():
        return SentimentResult(
            score=58,
            components={"fear_greed": 58, "news": 58, "reddit": 58},
            signal="neutral",
        )

    async def targeted_signal_feed(*args, **kwargs):
        assert kwargs["assets"] == ["BTCUSDT"]
        return SignalListResponse(
            signals=[
                Signal(
                    id="live-btc-history-target",
                    asset="BTCUSDT",
                    type=SignalType.BUY,
                    confidence=84,
                    target_price=99500,
                    stop_loss=94000,
                    indicators=SignalIndicators.model_validate(
                        {
                            "RSI": 31.0,
                            "MACD": "bullish",
                            "BollingerBands": {"upper": 100200, "middle": 97000, "lower": 94000},
                        }
                    ),
                    created_at=now,
                    risk_profile=RiskProfile.moderate,
                    entry_price=97500,
                    current_price=97800,
                )
            ],
            total=1,
            cached_at=now,
            is_stale=False,
            available_assets=["BTCUSDT"],
        )

    async def empty_signal_feed(*args, **kwargs):
        return SignalListResponse(
            signals=[], total=0, cached_at=now, is_stale=False, available_assets=[]
        )

    async def empty_onchain_snapshot(*args, **kwargs):
        return []

    monkeypatch.setattr(ai_dashboard, "_fetch_coingecko_news", fake_news)
    monkeypatch.setattr(ai_dashboard.sentiment_service, "get_market_sentiment", fake_sentiment)
    monkeypatch.setattr(
        ai_dashboard.binance_service, "build_signal_feed_for_assets", targeted_signal_feed
    )
    monkeypatch.setattr(ai_dashboard.binance_service, "build_signal_feed", empty_signal_feed)
    monkeypatch.setattr(ai_dashboard, "build_onchain_snapshot", empty_onchain_snapshot)

    with SessionLocal() as db:
        db.add(
            _make_signal(
                signal_id="hist-btc-only",
                user_id="user-a",
                asset="BTCUSDT",
                signal_type="BUY",
                confidence=79,
                created_at=now - timedelta(minutes=6),
                rsi=29.4,
                macd="bullish",
                target_price=97200,
            )
        )
        db.commit()

        payload = asyncio.run(ai_dashboard.get_ai_dashboard(current_user_id="user-a", db=db))

    assert {item.asset for item in payload.recent_signals} == {"BTC/USDT"}
    btc_signal = payload.recent_signals[0]
    assert btc_signal.total_sources == 2
    assert {source.source for source in btc_signal.sources} == {"AI Dashboard", "Signals"}
    assert all(source.criteria for source in btc_signal.sources)


def test_ai_dashboard_falls_back_to_broad_signal_feed_when_targeted_fetch_fails(
    tmp_path: Path, monkeypatch
):
    SessionLocal = _session_factory(tmp_path)
    now = datetime.now(UTC)

    async def fake_news():
        return []

    async def fake_sentiment():
        return SentimentResult(
            score=61,
            components={"fear_greed": 61, "news": 61, "reddit": 61},
            signal="bullish",
        )

    async def failing_targeted_signal_feed(*args, **kwargs):
        raise RuntimeError("targeted feed unavailable")

    async def fallback_signal_feed(*args, **kwargs):
        return SignalListResponse(
            signals=[
                Signal(
                    id="live-btc-fallback",
                    asset="BTCUSDT",
                    type=SignalType.BUY,
                    confidence=83,
                    target_price=100000,
                    stop_loss=94500,
                    indicators=SignalIndicators.model_validate(
                        {
                            "RSI": 32.0,
                            "MACD": "bullish",
                            "BollingerBands": {"upper": 100500, "middle": 97200, "lower": 94400},
                        }
                    ),
                    created_at=now,
                    risk_profile=RiskProfile.moderate,
                    entry_price=97600,
                    current_price=97900,
                )
            ],
            total=1,
            cached_at=now,
            is_stale=False,
            available_assets=["BTCUSDT"],
        )

    async def fake_onchain_snapshot(*args, **kwargs):
        class Pair:
            symbol = "BTCUSDT"
            token = "BTC"
            chain = "ethereum"
            last_price = 97850.0

        class Result:
            signal = "BUY"
            confidence = 70

        return [(Pair(), Result())]

    monkeypatch.setattr(ai_dashboard, "_fetch_coingecko_news", fake_news)
    monkeypatch.setattr(ai_dashboard.sentiment_service, "get_market_sentiment", fake_sentiment)
    monkeypatch.setattr(
        ai_dashboard.binance_service, "build_signal_feed_for_assets", failing_targeted_signal_feed
    )
    monkeypatch.setattr(ai_dashboard.binance_service, "build_signal_feed", fallback_signal_feed)
    monkeypatch.setattr(ai_dashboard, "build_onchain_snapshot", fake_onchain_snapshot)

    with SessionLocal() as db:
        payload = asyncio.run(ai_dashboard.get_ai_dashboard(current_user_id="user-a", db=db))

    assert {item.asset for item in payload.recent_signals} == {"BTC/USDT"}
    btc_signal = payload.recent_signals[0]
    assert btc_signal.total_sources == 2
    assert {source.source for source in btc_signal.sources} == {"Signals", "On-chain"}
    assert all(source.criteria for source in btc_signal.sources)


def test_ai_dashboard_unified_signal_conflict_is_deterministic():
    recent = ai_dashboard._build_unified_signals(
        ai_rows=[],
        signal_feed=[
            Signal(
                id="sig-btc",
                asset="BTCUSDT",
                type=SignalType.BUY,
                confidence=82,
                target_price=99000,
                stop_loss=94000,
                indicators=SignalIndicators.model_validate(
                    {
                        "RSI": 33.0,
                        "MACD": "bullish",
                        "BollingerBands": {"upper": 99500, "middle": 96500, "lower": 93500},
                    }
                ),
                created_at=datetime.now(UTC),
                risk_profile=RiskProfile.moderate,
                current_price=97000,
            )
        ],
        onchain_snapshot=[
            (
                type(
                    "Pair",
                    (),
                    {
                        "symbol": "BTCUSDT",
                        "token": "BTC",
                        "chain": "ethereum",
                        "last_price": 96900.0,
                    },
                )(),
                type("Result", (), {"signal": "SELL", "confidence": 78})(),
            )
        ],
    )

    assert len(recent) == 1
    signal = recent[0]
    assert signal.asset == "BTC/USDT"
    assert signal.action == "HOLD"
    assert signal.direction == "Neutro"
    assert signal.strength == 0
    assert signal.total_sources == 2
    assert {source.status for source in signal.sources} == {"conflicting"}


def test_ai_dashboard_unified_signal_builder_handles_many_assets_quickly():
    ai_rows: list[SignalHistory] = []
    signal_feed: list[Signal] = []
    onchain_snapshot: list[tuple[object, object]] = []
    now = datetime.now(UTC)

    for index in range(200):
        asset = f"ASSET{index}USDT"
        ai_rows.append(
            _make_signal(
                signal_id=f"hist-{index}",
                user_id="perf-user",
                asset=asset,
                signal_type="BUY" if index % 2 == 0 else "SELL",
                confidence=70 + (index % 20),
                created_at=now - timedelta(minutes=index),
                rsi=29.0 if index % 2 == 0 else 72.0,
                macd="bullish" if index % 2 == 0 else "bearish",
                target_price=100 + index,
            )
        )
        signal_feed.append(
            Signal(
                id=f"live-{index}",
                asset=asset,
                type=SignalType.BUY if index % 2 == 0 else SignalType.SELL,
                confidence=65 + (index % 25),
                target_price=120 + index,
                stop_loss=90 + index,
                indicators=SignalIndicators.model_validate(
                    {
                        "RSI": 30.0 if index % 2 == 0 else 70.0,
                        "MACD": "bullish" if index % 2 == 0 else "bearish",
                        "BollingerBands": {
                            "upper": 125 + index,
                            "middle": 110 + index,
                            "lower": 95 + index,
                        },
                    }
                ),
                created_at=now,
                risk_profile=RiskProfile.moderate,
                current_price=110 + index,
            )
        )
        onchain_snapshot.append(
            (
                type(
                    "Pair",
                    (),
                    {
                        "symbol": asset,
                        "token": f"ASSET{index}",
                        "chain": "ethereum",
                        "last_price": 111 + index,
                    },
                )(),
                type(
                    "Result",
                    (),
                    {
                        "signal": "BUY" if index % 2 == 0 else "SELL",
                        "confidence": 60 + (index % 30),
                    },
                )(),
            )
        )

    started = time.perf_counter()
    recent = ai_dashboard._build_unified_signals(
        ai_rows=ai_rows,
        signal_feed=signal_feed,
        onchain_snapshot=onchain_snapshot,
    )
    elapsed = time.perf_counter() - started

    assert len(recent) == 8
    assert elapsed < 0.25
