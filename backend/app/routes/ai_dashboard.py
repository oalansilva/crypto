from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models_signal_history import SignalHistory

router = APIRouter(prefix="/api/ai", tags=["ai-dashboard"])

logger = logging.getLogger(__name__)

COINGECKO_NEWS_URL = "https://api.coingecko.com/api/v3/news"
REQUEST_TIMEOUT_SECONDS = 8.0


class AIInsight(BaseModel):
    id: str
    title: str
    description: str
    tone: str
    asset: str | None = None
    badge: str | None = None


class FearGreedPayload(BaseModel):
    value: int = Field(ge=0, le=100)
    label: str
    tone: str


class IndicatorReading(BaseModel):
    asset: str
    value: str
    status: str
    tone: str


class IndicatorCardPayload(BaseModel):
    id: str
    title: str
    subtitle: str
    readings: list[IndicatorReading]


class DashboardNewsItem(BaseModel):
    id: str
    title: str
    source: str
    url: str
    published_at: datetime
    relative_time: str
    sentiment: str
    related_asset: str | None = None


class DashboardSignalItem(BaseModel):
    id: str
    asset: str
    action: str
    confidence: int = Field(ge=0, le=100)
    reason: str


class DashboardStatsPayload(BaseModel):
    hit_rate: int = Field(ge=0, le=100)
    total_signals: int = Field(ge=0)
    avg_confidence: int = Field(ge=0, le=100)


class AIDashboardResponse(BaseModel):
    generated_at: datetime
    insights: list[AIInsight]
    fear_greed: FearGreedPayload
    indicators: list[IndicatorCardPayload]
    recent_signals: list[DashboardSignalItem]
    stats: DashboardStatsPayload
    news: list[DashboardNewsItem]
    section_errors: dict[str, str] = Field(default_factory=dict)


def _dt_ago(minutes: int) -> datetime:
    return datetime.now(UTC) - timedelta(minutes=minutes)


def _relative_time(value: datetime) -> str:
    minutes = max(1, int((datetime.now(UTC) - value).total_seconds() // 60))
    if minutes < 60:
        return f"Há {minutes} min"
    hours = minutes // 60
    return f"Há {hours}h"


def _default_insights() -> list[AIInsight]:
    return [
        AIInsight(
            id="rsi-btc-oversold",
            title="RSI em sobrevenda",
            description="BTC/USDT com RSI em 28 sugere possível ponto de entrada se o momentum confirmar continuação.",
            tone="bullish",
            asset="BTC/USDT",
            badge="RSI 28",
        ),
        AIInsight(
            id="macd-btc-bullish",
            title="MACD bullish",
            description="MACD virou para alta em BTC/USDT e indica retomada de momentum comprador no curto prazo.",
            tone="bullish",
            asset="BTC/USDT",
            badge="4H",
        ),
        AIInsight(
            id="fear-greed-extreme-fear",
            title="Mercado em medo extremo",
            description="Fear & Greed em 22 aponta aversão a risco elevada e possível janela de acumulação gradual.",
            tone="warning",
            badge="22",
        ),
        AIInsight(
            id="rsi-eth-overbought",
            title="ETH em sobrecompra",
            description="ETH/USDT com RSI em 78 pede cautela com novas posições BUY e atenção a exaustão de preço.",
            tone="danger",
            asset="ETH/USDT",
            badge="RSI 78",
        ),
    ]


def _default_indicators() -> list[IndicatorCardPayload]:
    return [
        IndicatorCardPayload(
            id="rsi",
            title="RSI",
            subtitle="Momentum de compra e venda",
            readings=[
                IndicatorReading(asset="BTC/USDT", value="28", status="Oversold", tone="bullish"),
                IndicatorReading(asset="ETH/USDT", value="78", status="Overbought", tone="danger"),
            ],
        ),
        IndicatorCardPayload(
            id="macd",
            title="MACD",
            subtitle="Direção do cruzamento",
            readings=[
                IndicatorReading(asset="BTC/USDT", value="Bullish", status="Bullish", tone="bullish"),
                IndicatorReading(asset="ETH/USDT", value="Neutral", status="Neutral", tone="neutral"),
            ],
        ),
        IndicatorCardPayload(
            id="bollinger",
            title="Bollinger Bands",
            subtitle="Posição dentro das bandas",
            readings=[
                IndicatorReading(asset="BTC/USDT", value="Normal", status="Normal", tone="neutral"),
                IndicatorReading(asset="ETH/USDT", value="Normal", status="Normal", tone="neutral"),
            ],
        ),
    ]


def _default_recent_signals() -> list[DashboardSignalItem]:
    return [
        DashboardSignalItem(id="buy-btc", asset="BTC/USDT", action="BUY", confidence=92, reason="RSI sobrevenda + MACD bullish"),
        DashboardSignalItem(id="sell-eth", asset="ETH/USDT", action="SELL", confidence=78, reason="RSI sobrecompra"),
        DashboardSignalItem(id="hold-sol", asset="SOL/USDT", action="HOLD", confidence=65, reason="Sem confirmação de breakout"),
    ]


def _default_stats() -> DashboardStatsPayload:
    return DashboardStatsPayload(hit_rate=72, total_signals=150, avg_confidence=78)


def _default_news() -> list[DashboardNewsItem]:
    seeds = [
        ("btc-etf", "Bitcoin ultrapassa US$ 95.000 com influxo de ETFs acima de US$ 1 bi", "bullish", 12, "BTC/USDT"),
        ("eth-pectra", "Ethereum Foundation reforça atualização Pectra para escalar a rede", "bullish", 35, "ETH/USDT"),
        ("sol-etf", "SEC adia decisão sobre ETF de Solana e mantém mercado em compasso de espera", "neutral", 60, "SOL/USDT"),
        ("stablecoin-liquidity", "Volume de stablecoins em exchanges recua e pressiona liquidez do mercado", "bearish", 120, None),
        ("ada-roadmap", "Cardano divulga roadmap 2026 com Hydra e sidechains customizadas", "neutral", 180, "ADA/USDT"),
    ]
    items: list[DashboardNewsItem] = []
    for item_id, title, sentiment, minutes_ago, asset in seeds:
        published_at = _dt_ago(minutes_ago)
        items.append(
            DashboardNewsItem(
                id=item_id,
                title=title,
                source="CoinGecko",
                url="https://www.coingecko.com/",
                published_at=published_at,
                relative_time=_relative_time(published_at),
                sentiment=sentiment,
                related_asset=asset,
            )
        )
    return items


async def _fetch_coingecko_news() -> list[DashboardNewsItem]:
    """Fetch real crypto news from CoinGecko News API (aggregates multiple sources)."""
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(f"{COINGECKO_NEWS_URL}?per_page=5&page=1")
            response.raise_for_status()
            payload = response.json()
    except Exception as exc:
        logger.warning("CoinGecko news fetch failed for AI dashboard: %s", exc)
        raise

    data = payload.get("data", [])
    if not data:
        raise RuntimeError("CoinGecko returned no news")

    news_items: list[DashboardNewsItem] = []
    for item in data[:5]:
        title = str(item.get("title") or "")
        news_url = str(item.get("url") or item.get("news_site", ""))
        news_site = str(item.get("news_site") or "CoinGecko")
        crawled_at = item.get("crawled_at") or item.get("created_at")
        news_id = str(item.get("id", ""))

        # Convert Unix timestamp to datetime
        if crawled_at:
            published_at = datetime.fromtimestamp(crawled_at, tz=UTC)
        else:
            published_at = datetime.now(UTC)

        # Simple keyword-based sentiment
        title_lower = title.lower()
        if any(w in title_lower for w in ["surge", "soar", "bull", "rise", "gain", "up", "high", "record", "growth", "adoption"]):
            sentiment = "bullish"
        elif any(w in title_lower for w in ["fall", "drop", "bear", "loss", "crash", "decline", "risk", "fear", "sell"]):
            sentiment = "bearish"
        else:
            sentiment = "neutral"

        # Extract related asset from title if mentioned
        related_asset = None
        for pair in ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "DOT", "AVAX", "LINK", "MATIC"]:
            if pair in title.upper():
                related_asset = f"{pair}/USDT"
                break

        news_items.append(
            DashboardNewsItem(
                id=f"cg-news-{news_id}",
                title=title[:120],  # Limit title length
                source=news_site,
                url=news_url,
                published_at=published_at,
                relative_time=_relative_time(published_at),
                sentiment=sentiment,
                related_asset=related_asset,
            )
        )

    return news_items


def _load_stats_from_history() -> DashboardStatsPayload | None:
    db: Session = SessionLocal()
    try:
        rows = db.query(SignalHistory).filter(SignalHistory.archived == "no").all()
        if not rows:
            return None

        total = len(rows)
        avg_confidence = round(sum(row.confidence for row in rows) / total)
        triggered = [row for row in rows if row.status == "disparado"]
        winners = [row for row in triggered if row.pnl is not None and row.pnl > 0]
        hit_rate = round((len(winners) / len(triggered)) * 100) if triggered else 0

        return DashboardStatsPayload(
            hit_rate=hit_rate,
            total_signals=total,
            avg_confidence=avg_confidence,
        )
    except Exception as exc:
        logger.warning("Failed to load AI dashboard stats from signal history: %s", exc)
        return None
    finally:
        db.close()


@router.get(
    "/dashboard",
    response_model=AIDashboardResponse,
    summary="AI dashboard snapshot",
    description="Aggregates AI insights, sentiment, indicator cards, recent signals, performance metrics and CoinGecko-powered news into one frontend payload.",
)
async def get_ai_dashboard() -> AIDashboardResponse:
    section_errors: dict[str, str] = {}

    news = _default_news()
    stats = _default_stats()

    news_task = asyncio.create_task(_fetch_coingecko_news())
    stats_task = asyncio.create_task(asyncio.to_thread(_load_stats_from_history))

    news_result, stats_result = await asyncio.gather(news_task, stats_task, return_exceptions=True)

    if isinstance(news_result, Exception):
        section_errors["news"] = "CoinGecko indisponível, exibindo fallback local."
    else:
        news = news_result

    if isinstance(stats_result, Exception):
        section_errors["stats"] = "Não foi possível ler histórico de sinais, exibindo métricas padrão."
    elif stats_result is not None:
        stats = stats_result

    return AIDashboardResponse(
        generated_at=datetime.now(UTC),
        insights=_default_insights(),
        fear_greed=FearGreedPayload(value=22, label="Extreme Fear", tone="warning"),
        indicators=_default_indicators(),
        recent_signals=_default_recent_signals(),
        stats=stats,
        news=news,
        section_errors=section_errors,
    )
