from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models_signal_history import SignalHistory
from app.routes import ai_dashboard
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

    monkeypatch.setattr(ai_dashboard, "_fetch_coingecko_news", fake_news)
    monkeypatch.setattr(ai_dashboard.sentiment_service, "get_market_sentiment", fake_sentiment)

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
    assert {item.asset for item in payload.recent_signals} == {"BTC/USDT", "ETH/USDT"}
    assert all(reading.asset != "SOL/USDT" for card in payload.indicators for reading in card.readings)
    assert payload.fear_greed.value == 68
    assert payload.fear_greed.label == "Greed"
    assert payload.news[0].title == "BTC lidera fluxo institucional"
    assert payload.news[0].summary == "Fluxo comprador institucional sustenta o ativo no curto prazo."
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

    monkeypatch.setattr(ai_dashboard, "_fetch_coingecko_news", failing_news)
    monkeypatch.setattr(ai_dashboard.sentiment_service, "get_market_sentiment", neutral_sentiment)

    with SessionLocal() as db:
        payload = asyncio.run(ai_dashboard.get_ai_dashboard(current_user_id="user-empty", db=db))

    assert payload.stats.total_signals == 0
    assert payload.indicators == []
    assert payload.recent_signals == []
    assert payload.news == []
    assert payload.insights[0].id == "empty-history"
    assert payload.section_errors["news"] == "CoinGecko indisponível no momento."
