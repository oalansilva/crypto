from __future__ import annotations

import asyncio
import json
import logging
from collections import OrderedDict
from datetime import UTC, datetime
from typing import Any

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.models_signal_history import SignalHistory
from app.schemas.signal import RiskProfile, Signal
from app.services import binance_service, sentiment_service
from app.services.news_localization_service import (
    get_cached_localized_news,
    schedule_news_localization_refresh,
)

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
    summary: str
    source: str
    url: str
    published_at: datetime
    relative_time: str
    sentiment: str
    related_asset: str | None = None


class DashboardSignalCriterion(BaseModel):
    label: str
    score: float | None = None
    value: str | None = None


class DashboardSignalSource(BaseModel):
    source: str
    action: str
    confidence: int = Field(ge=0, le=100)
    direction: str | None = None
    status: str | None = None
    reason: str | None = None
    price: float | None = None
    criteria: list[DashboardSignalCriterion] = Field(default_factory=list)


class DashboardSignalItem(BaseModel):
    id: str
    asset: str
    action: str
    confidence: int = Field(ge=0, le=100)
    reason: str
    direction: str = "Neutro"
    strength: int = Field(default=0, ge=0, le=3)
    total_sources: int = Field(default=0, ge=0, le=3)
    price: float | None = None
    sources: list[DashboardSignalSource] = Field(default_factory=list)


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


def _relative_time(value: datetime) -> str:
    minutes = max(1, int((datetime.now(UTC) - value).total_seconds() // 60))
    if minutes < 60:
        return f"Há {minutes} min"
    hours = minutes // 60
    return f"Há {hours}h"


async def _fetch_coingecko_news() -> list[DashboardNewsItem]:
    """Fetch real crypto news from CoinGecko without blocking on MiniMax localization."""
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
    raw_news_for_localization: list[dict[str, str | None]] = []
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
        if any(
            w in title_lower
            for w in [
                "surge",
                "soar",
                "bull",
                "rise",
                "gain",
                "up",
                "high",
                "record",
                "growth",
                "adoption",
            ]
        ):
            sentiment = "bullish"
        elif any(
            w in title_lower
            for w in ["fall", "drop", "bear", "loss", "crash", "decline", "risk", "fear", "sell"]
        ):
            sentiment = "bearish"
        else:
            sentiment = "neutral"

        # Extract related asset from title if mentioned
        related_asset = None
        for pair in ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "DOT", "AVAX", "LINK", "MATIC"]:
            if pair in title.upper():
                related_asset = f"{pair}/USDT"
                break

        news_item_id = f"cg-news-{news_id}"
        raw_news_for_localization.append(
            {
                "id": news_item_id,
                "title": title[:120],
                "source": news_site,
                "sentiment": sentiment,
                "related_asset": related_asset,
            }
        )
        news_items.append(
            DashboardNewsItem(
                id=news_item_id,
                title=title[:120],  # Limit title length
                summary="Resumo indisponível no momento.",
                source=news_site,
                url=news_url,
                published_at=published_at,
                relative_time=_relative_time(published_at),
                sentiment=sentiment,
                related_asset=related_asset,
            )
        )

    localized_by_id, _is_fresh = get_cached_localized_news(raw_news_for_localization)
    for item in news_items:
        localized = localized_by_id.get(item.id) or {}
        item.title = str(localized.get("title_pt") or item.title)
        item.summary = str(localized.get("summary_pt") or item.summary)

    schedule_news_localization_refresh(raw_news_for_localization)
    return news_items


def _empty_stats() -> DashboardStatsPayload:
    return DashboardStatsPayload(hit_rate=0, total_signals=0, avg_confidence=0)


def _normalize_asset(asset: str | None) -> str:
    raw = str(asset or "").strip().upper()
    if not raw:
        return "ATIVO"
    if "/" in raw:
        return raw
    for suffix in ("USDT", "USDC", "BTC", "ETH", "BRL"):
        if raw.endswith(suffix) and len(raw) > len(suffix):
            return f"{raw[:-len(suffix)]}/{suffix}"
    return raw


def _symbol_key(asset: str | None) -> str:
    return str(asset or "").strip().upper().replace("/", "").replace("-", "")


def _collect_target_assets(ai_rows: list[SignalHistory]) -> list[str]:
    target_assets: list[str] = []
    seen_assets: set[str] = set()

    for row in ai_rows:
        key = _symbol_key(row.asset)
        if not key or key in seen_assets:
            continue
        seen_assets.add(key)
        target_assets.append(key)

    return target_assets


def _parse_indicators(row: SignalHistory) -> dict | None:
    if not row.indicators:
        return None
    try:
        parsed = json.loads(row.indicators)
    except Exception:
        return None
    return parsed if isinstance(parsed, dict) else None


def _rsi_status(value: float) -> tuple[str, str]:
    if value <= 30:
        return "Oversold", "bullish"
    if value >= 70:
        return "Overbought", "danger"
    return "Neutral", "neutral"


def _macd_status(value: str) -> tuple[str, str]:
    normalized = str(value or "").strip().lower()
    if normalized == "bullish":
        return "Bullish", "bullish"
    if normalized == "bearish":
        return "Bearish", "danger"
    return "Neutral", "neutral"


def _bollinger_status(price: float | None, bands: dict | None) -> tuple[str, str]:
    if not isinstance(bands, dict):
        return "Indisponível", "neutral"

    try:
        lower = float(bands.get("lower"))
        upper = float(bands.get("upper"))
        middle = float(bands.get("middle"))
    except Exception:
        return "Indisponível", "neutral"

    base_price = price if price is not None else middle
    if base_price <= lower:
        return "Banda inferior", "bullish"
    if base_price >= upper:
        return "Banda superior", "danger"
    return "Faixa média", "neutral"


def _fear_greed_label(value: int) -> tuple[str, str]:
    if value <= 20:
        return "Extreme Fear", "warning"
    if value <= 40:
        return "Fear", "warning"
    if value < 60:
        return "Neutral", "neutral"
    if value < 80:
        return "Greed", "bullish"
    return "Extreme Greed", "bullish"


def _load_user_history(db: Session, current_user_id: str, limit: int = 50) -> list[SignalHistory]:
    return (
        db.query(SignalHistory)
        .filter(
            SignalHistory.archived == "no",
            SignalHistory.user_id == current_user_id,
        )
        .order_by(SignalHistory.created_at.desc())
        .limit(limit)
        .all()
    )


def _load_stats_from_history(db: Session, current_user_id: str) -> DashboardStatsPayload:
    rows = (
        db.query(SignalHistory)
        .filter(
            SignalHistory.archived == "no",
            SignalHistory.user_id == current_user_id,
        )
        .all()
    )
    if not rows:
        return _empty_stats()

    total = len(rows)
    avg_confidence = round(sum(row.confidence for row in rows) / total)
    closed = [row for row in rows if row.status == "disparado" and row.pnl is not None]
    winners = [row for row in closed if (row.pnl or 0) > 0]
    hit_rate = round((len(winners) / len(closed)) * 100) if closed else 0
    return DashboardStatsPayload(
        hit_rate=hit_rate,
        total_signals=total,
        avg_confidence=avg_confidence,
    )


def _build_signal_reason(row: SignalHistory, indicators: dict | None) -> str:
    reasons: list[str] = []
    if indicators:
        rsi_value = indicators.get("RSI")
        if isinstance(rsi_value, (int, float)):
            status, _tone = _rsi_status(float(rsi_value))
            if status == "Oversold":
                reasons.append(f"RSI {float(rsi_value):.1f} em sobrevenda")
            elif status == "Overbought":
                reasons.append(f"RSI {float(rsi_value):.1f} em sobrecompra")
            else:
                reasons.append(f"RSI {float(rsi_value):.1f} neutro")

        macd_value = indicators.get("MACD")
        if macd_value is not None:
            status, _tone = _macd_status(str(macd_value))
            reasons.append(f"MACD {status.lower()}")

        bollinger = indicators.get("BollingerBands")
        price_reference = row.entry_price or row.trigger_price or row.target_price
        bollinger_status, _tone = _bollinger_status(
            price_reference, bollinger if isinstance(bollinger, dict) else None
        )
        if bollinger_status != "Indisponível":
            reasons.append(f"Bollinger em {bollinger_status.lower()}")

    if not reasons:
        return f"{row.type} com {row.confidence}% de confiança"
    return " + ".join(reasons[:3])


def _load_recent_signals_from_history(rows: list[SignalHistory]) -> list[DashboardSignalItem]:
    items: list[DashboardSignalItem] = []
    for row in rows[:5]:
        indicators = _parse_indicators(row)
        items.append(
            DashboardSignalItem(
                id=row.id,
                asset=_normalize_asset(row.asset),
                action=row.type,
                confidence=row.confidence,
                reason=_build_signal_reason(row, indicators),
            )
        )
    return items


def _source_score(action: str | None) -> int:
    normalized = str(action or "").strip().upper()
    if normalized == "BUY":
        return 1
    if normalized == "SELL":
        return -1
    return 0


def _direction_label(action: str, strength: int, opposing_sources: int) -> str:
    normalized = str(action).upper()
    if normalized == "BUY":
        return "Compra forte" if strength >= 2 and opposing_sources == 0 else "Compra"
    if normalized == "SELL":
        return "Venda forte" if strength >= 2 and opposing_sources == 0 else "Venda"
    return "Neutro"


def _coerce_price(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _clamp_score(value: float) -> float:
    return round(max(-100.0, min(100.0, float(value))), 1)


def _compact_number(value: float | int | None, *, currency: bool = False) -> str | None:
    if value is None:
        return None

    amount = float(value)
    absolute = abs(amount)
    suffix = ""
    divisor = 1.0
    if absolute >= 1_000_000_000:
        suffix = "B"
        divisor = 1_000_000_000
    elif absolute >= 1_000_000:
        suffix = "M"
        divisor = 1_000_000
    elif absolute >= 1_000:
        suffix = "K"
        divisor = 1_000

    formatted = f"{amount / divisor:.1f}{suffix}" if suffix else f"{amount:.1f}"
    if currency:
        return f"${formatted}"
    return formatted


def _score_macd_status(value: str | None) -> float:
    normalized = str(value or "").strip().lower()
    if normalized == "bullish":
        return 100.0
    if normalized == "bearish":
        return 0.0
    return 50.0


def _score_bollinger_status(value: str) -> float:
    if value == "Banda inferior":
        return 100.0
    if value == "Banda superior":
        return 0.0
    return 50.0


def _build_ai_source_criteria(
    row: SignalHistory, indicators: dict | None
) -> list[DashboardSignalCriterion]:
    if not indicators:
        return []

    criteria: list[DashboardSignalCriterion] = []
    rsi_value = indicators.get("RSI")
    if isinstance(rsi_value, (int, float)):
        status, _tone = _rsi_status(float(rsi_value))
        criteria.append(
            DashboardSignalCriterion(
                label="RSI",
                score=_clamp_score(float(rsi_value)),
                value=f"{float(rsi_value):.1f} · {status.lower()}",
            )
        )

    macd_value = indicators.get("MACD")
    if macd_value is not None:
        status, _tone = _macd_status(str(macd_value))
        criteria.append(
            DashboardSignalCriterion(
                label="MACD",
                score=_score_macd_status(str(macd_value)),
                value=status,
            )
        )

    bollinger = indicators.get("BollingerBands")
    if isinstance(bollinger, dict):
        price_reference = row.entry_price or row.trigger_price or row.target_price
        status, _tone = _bollinger_status(price_reference, bollinger)
        if status != "Indisponível":
            criteria.append(
                DashboardSignalCriterion(
                    label="Bollinger",
                    score=_score_bollinger_status(status),
                    value=status,
                )
            )

    return criteria


def _build_signals_source_criteria(signal: Signal) -> list[DashboardSignalCriterion]:
    if signal.breakdown:
        return [
            DashboardSignalCriterion(
                label="RSI",
                score=_clamp_score(signal.breakdown.rsi_contribution),
                value="Contribuição",
            ),
            DashboardSignalCriterion(
                label="MACD",
                score=_clamp_score(signal.breakdown.macd_contribution),
                value="Contribuição",
            ),
            DashboardSignalCriterion(
                label="Sentimento",
                score=_clamp_score(signal.breakdown.sentiment_contribution),
                value="Ajuste",
            ),
        ]

    return [
        DashboardSignalCriterion(
            label="RSI",
            score=_clamp_score(signal.indicators.rsi),
            value=f"{signal.indicators.rsi:.1f}",
        ),
        DashboardSignalCriterion(
            label="MACD",
            score=_score_macd_status(signal.indicators.macd),
            value=signal.indicators.macd.capitalize(),
        ),
    ]


def _source_direction(action: str | None) -> str:
    normalized = str(action or "").strip().upper()
    if normalized == "BUY":
        return "Compra"
    if normalized == "SELL":
        return "Venda"
    return "Neutro"


def _build_unified_reason(
    final_action: str,
    supporting_sources: list[dict[str, Any]],
    opposing_sources: list[dict[str, Any]],
) -> str:
    if not supporting_sources and not opposing_sources:
        return "Nenhuma fonte disponível para consolidar."

    support_names = ", ".join(source["source"] for source in supporting_sources) or "nenhuma"
    oppose_names = ", ".join(source["source"] for source in opposing_sources)

    if final_action == "HOLD":
        if supporting_sources:
            return (
                f"Sinal neutro por ausência de maioria direcional. Fontes neutras: {support_names}."
            )
        if opposing_sources:
            return f"Sinal neutro por conflito entre fontes: {oppose_names}."
        return "Sinal neutro por falta de confirmação direcional."

    verb = "compra" if final_action == "BUY" else "venda"
    if opposing_sources:
        return f"Consolidação em {verb}: apoio de {support_names}; conflito com {oppose_names}."
    return f"Consolidação em {verb}: apoio de {support_names}."


def _make_unified_signal(
    *,
    asset_key: str,
    display_asset: str,
    entries: list[dict[str, Any]],
) -> DashboardSignalItem:
    directional_entries = [entry for entry in entries if _source_score(entry.get("action")) != 0]
    weighted_score = sum(
        _source_score(entry.get("action")) * (int(entry.get("confidence") or 0) / 100)
        for entry in entries
    )

    if directional_entries and abs(weighted_score) >= 0.35:
        final_action = "BUY" if weighted_score > 0 else "SELL"
    else:
        final_action = "HOLD"

    supporting_sources = [
        entry
        for entry in entries
        if _source_score(entry.get("action")) == _source_score(final_action)
    ]
    opposing_sources = [
        entry
        for entry in entries
        if _source_score(entry.get("action")) == -_source_score(final_action)
        and _source_score(final_action) != 0
    ]
    neutral_sources = [entry for entry in entries if _source_score(entry.get("action")) == 0]

    if final_action == "HOLD":
        supporting_sources = neutral_sources

    strength = len(supporting_sources)
    confidence = (
        round(
            sum(int(entry.get("confidence") or 0) for entry in supporting_sources)
            / len(supporting_sources)
        )
        if supporting_sources
        else 0
    )
    direction = _direction_label(final_action, strength, len(opposing_sources))
    price = None
    for preferred_source in ("Signals", "AI Dashboard"):
        price = next(
            (
                _coerce_price(entry.get("price"))
                for entry in entries
                if entry.get("source") == preferred_source
                and _coerce_price(entry.get("price")) is not None
            ),
            None,
        )
        if price is not None:
            break
    reason = _build_unified_reason(
        final_action,
        supporting_sources,
        opposing_sources if final_action != "HOLD" else directional_entries,
    )

    ordered_sources = sorted(
        entries, key=lambda entry: int(entry.get("confidence") or 0), reverse=True
    )
    enriched_sources: list[dict[str, Any]] = []
    for entry in ordered_sources:
        entry_score = _source_score(entry.get("action"))
        if final_action == "HOLD":
            status = "neutral" if entry_score == 0 else "conflicting"
        elif entry_score == _source_score(final_action):
            status = "supporting"
        elif entry_score == 0:
            status = "neutral"
        else:
            status = "conflicting"
        enriched_sources.append(
            {
                **entry,
                "direction": _source_direction(entry.get("action")),
                "status": status,
            }
        )
    signal_id = f"unified-{asset_key.lower()}"
    return DashboardSignalItem(
        id=signal_id,
        asset=display_asset,
        action=final_action,
        confidence=confidence,
        reason=reason,
        direction=direction,
        strength=strength,
        total_sources=len(entries),
        price=price,
        sources=enriched_sources,
    )


def _unified_signal_rank(entries: list[dict[str, Any]]) -> tuple[int, int]:
    weighted_score = sum(
        _source_score(entry.get("action")) * (int(entry.get("confidence") or 0) / 100)
        for entry in entries
    )
    has_directional_entry = any(_source_score(entry.get("action")) != 0 for entry in entries)
    if has_directional_entry and abs(weighted_score) >= 0.35:
        final_action = "BUY" if weighted_score > 0 else "SELL"
    else:
        final_action = "HOLD"

    final_score = _source_score(final_action)
    if final_action == "HOLD":
        supporting_sources = [entry for entry in entries if _source_score(entry.get("action")) == 0]
    else:
        supporting_sources = [
            entry for entry in entries if _source_score(entry.get("action")) == final_score
        ]

    strength = len(supporting_sources)
    confidence = (
        round(
            sum(int(entry.get("confidence") or 0) for entry in supporting_sources)
            / len(supporting_sources)
        )
        if supporting_sources
        else 0
    )
    return strength, confidence


def _materialize_unified_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    materialized: list[dict[str, Any]] = []
    for entry in entries:
        if entry.get("source") == "AI Dashboard":
            row = entry["row"]
            indicators = _parse_indicators(row)
            materialized.append(
                {
                    "source": "AI Dashboard",
                    "action": entry["action"],
                    "confidence": entry["confidence"],
                    "reason": _build_signal_reason(row, indicators),
                    "price": _coerce_price(
                        row.entry_price or row.trigger_price or row.target_price
                    ),
                    "criteria": _build_ai_source_criteria(row, indicators),
                }
            )
            continue

        signal = entry["signal"]
        breakdown_summary = None
        if signal.breakdown:
            breakdown_summary = f"RSI {signal.breakdown.rsi_contribution:.0f}% · MACD {signal.breakdown.macd_contribution:.0f}% · Sentimento {signal.breakdown.sentiment_contribution:.0f}%"
        materialized.append(
            {
                "source": "Signals",
                "action": entry["action"],
                "confidence": entry["confidence"],
                "reason": breakdown_summary
                or f"Sinal {signal.type.value} com perfil {signal.risk_profile.value}.",
                "price": _coerce_price(signal.current_price or signal.entry_price),
                "criteria": _build_signals_source_criteria(signal),
            }
        )
    return materialized


def _build_unified_signals(
    *,
    ai_rows: list[SignalHistory],
    signal_feed: list[Signal],
) -> list[DashboardSignalItem]:
    grouped: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def ensure_group(asset: str | None) -> dict[str, Any] | None:
        key = _symbol_key(asset)
        if not key:
            return None
        if key not in grouped:
            grouped[key] = {
                "asset": _normalize_asset(asset or key),
                "entries": [],
            }
        return grouped[key]

    seen_ai_assets: set[str] = set()
    for row in ai_rows:
        key = _symbol_key(row.asset)
        if not key or key in seen_ai_assets:
            continue
        seen_ai_assets.add(key)
        group = ensure_group(row.asset)
        if not group:
            continue
        group["entries"].append(
            {
                "source": "AI Dashboard",
                "action": str(row.type).upper(),
                "confidence": int(row.confidence),
                "row": row,
            }
        )

    seen_signal_assets: set[str] = set()
    for signal in signal_feed:
        key = _symbol_key(signal.asset)
        if not key or key in seen_signal_assets:
            continue
        seen_signal_assets.add(key)
        group = ensure_group(signal.asset)
        if not group:
            continue
        group["entries"].append(
            {
                "source": "Signals",
                "action": signal.type.value,
                "confidence": int(signal.confidence),
                "signal": signal,
            }
        )

    ranked_groups = [
        (_unified_signal_rank(data["entries"]), asset_key, data)
        for asset_key, data in grouped.items()
        if len(data["entries"]) >= 2
    ]
    ranked_groups.sort(key=lambda item: item[0], reverse=True)

    return [
        _make_unified_signal(
            asset_key=asset_key,
            display_asset=str(data["asset"]),
            entries=_materialize_unified_entries(data["entries"]),
        )
        for _, asset_key, data in ranked_groups[:8]
    ]


def _build_indicator_cards(rows: list[SignalHistory]) -> list[IndicatorCardPayload]:
    latest_by_asset: OrderedDict[str, tuple[SignalHistory, dict]] = OrderedDict()
    for row in rows:
        asset = _normalize_asset(row.asset)
        if asset in latest_by_asset:
            continue
        indicators = _parse_indicators(row)
        if indicators:
            latest_by_asset[asset] = (row, indicators)
        if len(latest_by_asset) >= 3:
            break

    rsi_readings: list[IndicatorReading] = []
    macd_readings: list[IndicatorReading] = []
    bollinger_readings: list[IndicatorReading] = []

    for asset, (row, indicators) in latest_by_asset.items():
        rsi_value = indicators.get("RSI")
        if isinstance(rsi_value, (int, float)):
            status, tone = _rsi_status(float(rsi_value))
            rsi_readings.append(
                IndicatorReading(
                    asset=asset,
                    value=f"{float(rsi_value):.1f}",
                    status=status,
                    tone=tone,
                )
            )

        macd_value = indicators.get("MACD")
        if macd_value is not None:
            status, tone = _macd_status(str(macd_value))
            macd_readings.append(
                IndicatorReading(
                    asset=asset,
                    value=status,
                    status=status,
                    tone=tone,
                )
            )

        bollinger = indicators.get("BollingerBands")
        if isinstance(bollinger, dict):
            price_reference = row.entry_price or row.trigger_price or row.target_price
            status, tone = _bollinger_status(price_reference, bollinger)
            bollinger_readings.append(
                IndicatorReading(
                    asset=asset,
                    value=status,
                    status=status,
                    tone=tone,
                )
            )

    cards: list[IndicatorCardPayload] = []
    if rsi_readings:
        cards.append(
            IndicatorCardPayload(
                id="rsi",
                title="RSI",
                subtitle="Leitura mais recente por ativo monitorado",
                readings=rsi_readings,
            )
        )
    if macd_readings:
        cards.append(
            IndicatorCardPayload(
                id="macd",
                title="MACD",
                subtitle="Direção do momentum nas últimas entradas",
                readings=macd_readings,
            )
        )
    if bollinger_readings:
        cards.append(
            IndicatorCardPayload(
                id="bollinger",
                title="Bollinger Bands",
                subtitle="Posição do preço dentro do canal",
                readings=bollinger_readings,
            )
        )
    return cards


def _build_dynamic_insights(
    *,
    stats: DashboardStatsPayload,
    fear_greed: FearGreedPayload,
    indicators: list[IndicatorCardPayload],
    recent_signals: list[DashboardSignalItem],
    news: list[DashboardNewsItem],
) -> list[AIInsight]:
    insights: list[AIInsight] = []

    if stats.total_signals == 0:
        return [
            AIInsight(
                id="empty-history",
                title="Sem histórico suficiente",
                description="A dashboard está online, mas esta conta ainda não tem sinais salvos para gerar leituras técnicas personalizadas.",
                tone="neutral",
                badge="0 sinais",
            )
        ]

    if recent_signals:
        top_signal = max(recent_signals, key=lambda item: item.confidence)
        insights.append(
            AIInsight(
                id=f"signal-{top_signal.id}",
                title=f"Sinal mais forte: {top_signal.action}",
                description=f"{top_signal.asset} lidera a fila com {top_signal.confidence}% de confiança. Motivo: {top_signal.reason}.",
                tone=(
                    "bullish"
                    if top_signal.action == "BUY"
                    else "danger" if top_signal.action == "SELL" else "warning"
                ),
                asset=top_signal.asset,
                badge=f"{top_signal.confidence}%",
            )
        )

    for card in indicators:
        extreme = next(
            (
                reading
                for reading in card.readings
                if reading.status
                in {
                    "Oversold",
                    "Overbought",
                    "Bullish",
                    "Bearish",
                    "Banda inferior",
                    "Banda superior",
                }
            ),
            None,
        )
        if not extreme:
            continue
        insights.append(
            AIInsight(
                id=f"{card.id}-{extreme.asset.lower().replace('/', '-')}",
                title=f"{card.title} em destaque",
                description=f"{extreme.asset} aparece com leitura {extreme.status.lower()} em {card.title}, com valor atual {extreme.value}.",
                tone=extreme.tone,
                asset=extreme.asset,
                badge=extreme.value,
            )
        )
        break

    insights.append(
        AIInsight(
            id="fear-greed-live",
            title=f"Sentimento agregado: {fear_greed.label}",
            description=f"O índice atual está em {fear_greed.value}, refletindo o pulso consolidado de fear & greed, notícias e sentimento social.",
            tone=fear_greed.tone,
            badge=str(fear_greed.value),
        )
    )

    if news:
        headline = news[0]
        insights.append(
            AIInsight(
                id=f"news-{headline.id}",
                title="Notícia mais recente",
                description=f"{headline.title} Fonte: {headline.source}, publicada {headline.relative_time.lower()}.",
                tone=(
                    headline.sentiment
                    if headline.sentiment in {"bullish", "bearish"}
                    else "neutral"
                ),
                asset=headline.related_asset,
                badge=headline.source,
            )
        )

    return insights[:4]


@router.get(
    "/dashboard",
    response_model=AIDashboardResponse,
    summary="AI dashboard snapshot",
    description="Aggregates AI insights, sentiment, indicator cards, recent signals, performance metrics and CoinGecko-powered news into one frontend payload.",
)
async def get_ai_dashboard(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AIDashboardResponse:
    section_errors: dict[str, str] = {}
    news: list[DashboardNewsItem] = []
    stats = _empty_stats()
    fear_greed = FearGreedPayload(value=50, label="Neutral", tone="neutral")
    history_rows = _load_user_history(db, current_user_id)
    indicators = _build_indicator_cards(history_rows)
    news_task = asyncio.create_task(_fetch_coingecko_news())
    sentiment_task = asyncio.create_task(sentiment_service.get_market_sentiment())

    news_result, sentiment_result = await asyncio.gather(
        news_task,
        sentiment_task,
        return_exceptions=True,
    )

    if isinstance(news_result, Exception):
        section_errors["news"] = "CoinGecko indisponível no momento."
    else:
        news = news_result

    try:
        stats = _load_stats_from_history(db, current_user_id)
    except Exception as exc:
        logger.warning("Failed to load AI dashboard stats from signal history: %s", exc)
        section_errors["stats"] = "Não foi possível consolidar o histórico de sinais."

    if isinstance(sentiment_result, Exception):
        logger.warning("Failed to load AI dashboard sentiment: %s", sentiment_result)
        section_errors["fear_greed"] = "Não foi possível atualizar o radar de sentimento."
        sentiment_score = None
    else:
        fear_greed_value = int(sentiment_result.score)
        sentiment_score = sentiment_result.score
        fear_greed_label, fear_greed_tone = _fear_greed_label(fear_greed_value)
        fear_greed = FearGreedPayload(
            value=fear_greed_value,
            label=fear_greed_label,
            tone=fear_greed_tone,
        )

    candidate_assets = _collect_target_assets(history_rows)
    signal_feed: list[Signal] = []

    if candidate_assets:
        try:
            signal_feed_result = await binance_service.build_signal_feed_for_assets(
                assets=candidate_assets,
                risk_profile=RiskProfile.moderate,
                confidence_min=40,
                limit=20,
                sentiment_score=sentiment_score,
                user_id=None,
                include_neutral=True,
            )
            signal_feed = list(signal_feed_result.signals)
        except Exception as exc:
            logger.warning(
                "Failed to load targeted live signal feed for unified AI dashboard: %s", exc
            )

    if not signal_feed:
        try:
            fallback_feed_result = await binance_service.build_signal_feed(
                limit=20,
                risk_profile=RiskProfile.moderate,
                user_id=None,
                confidence_min=40,
                sentiment_score=sentiment_score,
            )
            signal_feed = list(fallback_feed_result.signals)
        except Exception as exc:
            logger.warning("Failed to load fallback live signal feed for AI dashboard: %s", exc)
            section_errors["signals"] = "Não foi possível atualizar os sinais técnicos."
            signal_feed = []

    recent_signals = _build_unified_signals(
        ai_rows=history_rows,
        signal_feed=signal_feed,
    )

    if not recent_signals:
        section_errors["signals"] = (
            section_errors.get("signals")
            or "Nenhum sinal unificado disponível com convergência suficiente entre as fontes."
        )

    insights = _build_dynamic_insights(
        stats=stats,
        fear_greed=fear_greed,
        indicators=indicators,
        recent_signals=recent_signals,
        news=news,
    )

    return AIDashboardResponse(
        generated_at=datetime.now(UTC),
        insights=insights,
        fear_greed=fear_greed,
        indicators=indicators,
        recent_signals=recent_signals,
        stats=stats,
        news=news,
        section_errors=section_errors,
    )
