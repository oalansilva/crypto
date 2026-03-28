from __future__ import annotations

"""Signal generation backed by Binance OHLCV.

This implementation uses deterministic heuristics until the LSTM + RandomForest
ensemble from Card #55 is available.
"""

import asyncio
import logging
import threading
import time
import uuid
from datetime import UTC, datetime
from statistics import mean, pstdev
from typing import Any

import httpx

from app.schemas.signal import (
    BollingerBandsPayload,
    ConfidenceBreakdown,
    RiskProfile,
    Signal,
    SignalIndicators,
    SignalListResponse,
    SignalType,
)

logger = logging.getLogger(__name__)

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
BINANCE_EXCHANGE_INFO_URL = "https://api.binance.com/api/v3/exchangeInfo"
CACHE_TTL_SECONDS = 300.0
KLINES_LIMIT = 120
KLINES_INTERVAL = "1h"
REQUEST_TIMEOUT_SECONDS = 8.0
MAX_RETRIES = 3
MAX_CONCURRENT_KLINES = 20
_KLINES_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENT_KLINES)

_CACHE_LOCK = threading.Lock()
_KLINES_CACHE: dict[tuple[str, str, int], dict[str, Any]] = {}
_SIGNAL_LOOKUP: dict[str, dict[str, Any]] = {}
_USDT_PAIRS_CACHE: dict[str, Any] = {}

_PROFILE_SETTINGS: dict[RiskProfile, dict[str, float]] = {
    RiskProfile.conservative: {
        "buy_rsi": 32.0,
        "sell_rsi": 68.0,
        "target_pct": 0.03,
        "stop_pct": 0.015,
        "default_confidence_min": 75.0,
    },
    RiskProfile.moderate: {
        "buy_rsi": 38.0,
        "sell_rsi": 64.0,
        "target_pct": 0.05,
        "stop_pct": 0.025,
        "default_confidence_min": 70.0,
    },
    RiskProfile.aggressive: {
        "buy_rsi": 45.0,
        "sell_rsi": 58.0,
        "target_pct": 0.08,
        "stop_pct": 0.04,
        "default_confidence_min": 60.0,
    },
}


def _utc_now() -> datetime:
    return datetime.now(UTC)


async def _fetch_all_usdt_pairs_from_binance() -> list[str]:
    """Fetch all USDT trading pairs from Binance exchangeInfo."""
    timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(BINANCE_EXCHANGE_INFO_URL)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else float(attempt)
                await asyncio.sleep(min(delay, 5.0))
                continue
            response.raise_for_status()
            payload = response.json()
            symbols = payload.get("symbols", [])
            usdt_pairs = [
                sym["symbol"]
                for sym in symbols
                if sym.get("status") == "TRADING"
                and sym.get("quoteAsset") == "USDT"
                and sym.get("isSpotTradingAllowed", False)
            ]
            return sorted(usdt_pairs)
        except (httpx.HTTPError, ValueError) as exc:
            if attempt >= MAX_RETRIES:
                raise RuntimeError(f"Unable to fetch Binance exchangeInfo: {exc}") from exc
            await asyncio.sleep(min(2 ** (attempt - 1), 4))
    return []


async def _get_all_usdt_pairs() -> list[str]:
    """Get all USDT pairs with 5-minute cache."""
    now = time.time()
    with _CACHE_LOCK:
        cached = _USDT_PAIRS_CACHE.get("usdt_pairs")
        if cached:
            expires_at = float(cached.get("expires_at") or 0)
            if expires_at > now:
                return list(cached.get("pairs") or [])
            _USDT_PAIRS_CACHE.pop("usdt_pairs", None)

    pairs = await _fetch_all_usdt_pairs_from_binance()
    with _CACHE_LOCK:
        _USDT_PAIRS_CACHE["usdt_pairs"] = {
            "pairs": pairs,
            "expires_at": time.time() + CACHE_TTL_SECONDS,
        }
    return pairs


def _normalize_asset(asset: str) -> str:
    normalized = str(asset or "").strip().upper()
    if not normalized:
        raise ValueError("Asset must not be empty")
    return normalized


async def _normalize_assets(asset: str | None) -> list[str]:
    if asset:
        return [_normalize_asset(asset)]
    return await _get_all_usdt_pairs()


def _read_cache(cache_key: tuple[str, str, int], *, allow_stale: bool = False) -> dict[str, Any] | None:
    now = time.time()
    with _CACHE_LOCK:
        cached = _KLINES_CACHE.get(cache_key)
        if not cached:
            return None
        expires_at = float(cached.get("expires_at") or 0)
        if expires_at > now:
            return {
                "candles": list(cached.get("candles") or []),
                "cached_at": cached.get("cached_at"),
                "is_stale": False,
            }
        if allow_stale:
            return {
                "candles": list(cached.get("candles") or []),
                "cached_at": cached.get("cached_at"),
                "is_stale": True,
            }
        _KLINES_CACHE.pop(cache_key, None)
        return None


def _write_cache(cache_key: tuple[str, str, int], candles: list[dict[str, Any]], cached_at: datetime) -> None:
    with _CACHE_LOCK:
        _KLINES_CACHE[cache_key] = {
            "candles": list(candles),
            "cached_at": cached_at,
            "expires_at": time.time() + CACHE_TTL_SECONDS,
        }


def _remember_signal(signal: Signal, cached_at: datetime | None, is_stale: bool) -> None:
    with _CACHE_LOCK:
        _SIGNAL_LOOKUP[signal.id] = {
            "signal": signal,
            "cached_at": cached_at,
            "is_stale": is_stale,
            "expires_at": time.time() + CACHE_TTL_SECONDS,
        }


def _get_remembered_signal(signal_id: str) -> tuple[Signal | None, datetime | None, bool]:
    now = time.time()
    with _CACHE_LOCK:
        entry = _SIGNAL_LOOKUP.get(signal_id)
        if not entry:
            return None, None, False
        if float(entry.get("expires_at") or 0) <= now:
            _SIGNAL_LOOKUP.pop(signal_id, None)
            return None, None, False
        return entry["signal"], entry.get("cached_at"), bool(entry.get("is_stale"))


async def _request_klines(asset: str, interval: str, limit: int) -> list[dict[str, Any]]:
    timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS)
    params = {"symbol": asset, "interval": interval, "limit": limit}

    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(BINANCE_KLINES_URL, params=params)

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else float(attempt)
                await asyncio.sleep(min(delay, 5.0))
                continue

            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise ValueError("Unexpected Binance klines payload")

            candles: list[dict[str, Any]] = []
            for row in payload:
                if not isinstance(row, list) or len(row) < 6:
                    continue
                candles.append(
                    {
                        "open_time": datetime.fromtimestamp(int(row[0]) / 1000, tz=UTC),
                        "open": float(row[1]),
                        "high": float(row[2]),
                        "low": float(row[3]),
                        "close": float(row[4]),
                        "volume": float(row[5]),
                    }
                )
            if not candles:
                raise ValueError(f"No candle data returned for {asset}")
            return candles
        except (httpx.HTTPError, ValueError) as exc:
            last_error = exc
            if attempt >= MAX_RETRIES:
                break
            await asyncio.sleep(min(2 ** (attempt - 1), 4))

    raise RuntimeError(f"Unable to fetch Binance klines for {asset}: {last_error}")


async def get_klines(asset: str, interval: str = KLINES_INTERVAL, limit: int = KLINES_LIMIT) -> dict[str, Any]:
    normalized_asset = _normalize_asset(asset)
    cache_key = (normalized_asset, interval, int(limit))
    cached = _read_cache(cache_key)
    if cached is not None:
        return cached

    try:
        candles = await _request_klines(normalized_asset, interval, limit)
    except Exception as exc:
        stale = _read_cache(cache_key, allow_stale=True)
        if stale is not None:
            logger.warning("Serving stale signal cache for %s after Binance failure: %s", normalized_asset, exc)
            return stale
        raise

    cached_at = _utc_now()
    _write_cache(cache_key, candles, cached_at)
    return {"candles": candles, "cached_at": cached_at, "is_stale": False}


def _simple_moving_average(values: list[float], window: int) -> float:
    sample = values[-window:]
    return mean(sample)


def _ema_series(values: list[float], window: int) -> list[float]:
    if len(values) < window:
        raise ValueError(f"Not enough values to compute EMA({window})")
    multiplier = 2 / (window + 1)
    ema_values: list[float] = [_simple_moving_average(values[:window], window)]
    for price in values[window:]:
        ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
    return ema_values


def _compute_rsi(closes: list[float], period: int = 14) -> float:
    if len(closes) <= period:
        raise ValueError("Not enough values to compute RSI")
    deltas = [current - previous for previous, current in zip(closes[:-1], closes[1:])]
    relevant = deltas[-period:]
    gains = [delta for delta in relevant if delta > 0]
    losses = [-delta for delta in relevant if delta < 0]
    avg_gain = sum(gains) / period if gains else 0.0
    avg_loss = sum(losses) / period if losses else 0.0
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _compute_macd(closes: list[float]) -> tuple[float, float, str]:
    ema12 = _ema_series(closes, 12)
    ema26 = _ema_series(closes, 26)
    offset = len(ema12) - len(ema26)
    macd_values = [ema12[idx + offset] - ema26[idx] for idx in range(len(ema26))]
    signal_series = _ema_series(macd_values, 9)
    macd_line = macd_values[-1]
    signal_line = signal_series[-1]
    histogram = macd_line - signal_line
    sentiment = "bullish" if histogram > 0.15 else "bearish" if histogram < -0.15 else "neutral"
    return macd_line, signal_line, sentiment


def _compute_bollinger_bands(closes: list[float], period: int = 20) -> BollingerBandsPayload:
    window = closes[-period:]
    middle = mean(window)
    deviation = pstdev(window) if len(window) > 1 else 0.0
    distance = deviation * 2
    return BollingerBandsPayload(upper=middle + distance, middle=middle, lower=middle - distance)


def _build_signal(
    *,
    asset: str,
    risk_profile: RiskProfile,
    candles: list[dict[str, Any]],
    sentiment_score: int | float | None = None,
) -> Signal:
    closes = [float(candle["close"]) for candle in candles]
    latest_close = closes[-1]
    latest_time = candles[-1]["open_time"]
    settings = _PROFILE_SETTINGS[risk_profile]
    rsi = round(_compute_rsi(closes), 2)
    _macd_line, _signal_line, macd_sentiment = _compute_macd(closes)
    bands = _compute_bollinger_bands(closes)

    buy_score = 0.0
    sell_score = 0.0

    if rsi <= settings["buy_rsi"]:
        buy_score += 34
    elif rsi <= settings["buy_rsi"] + 8:
        buy_score += 18

    if rsi >= settings["sell_rsi"]:
        sell_score += 34
    elif rsi >= settings["sell_rsi"] - 8:
        sell_score += 18

    if macd_sentiment == "bullish":
        buy_score += 24
    elif macd_sentiment == "bearish":
        sell_score += 24
    else:
        buy_score += 8
        sell_score += 8

    if latest_close <= bands.lower * 1.015:
        buy_score += 28
    elif latest_close <= bands.middle:
        buy_score += 12

    if latest_close >= bands.upper * 0.985:
        sell_score += 28
    elif latest_close >= bands.middle:
        sell_score += 12

    price_mid_delta = abs(latest_close - bands.middle) / max(bands.middle, 1e-9)
    hold_confidence = min(88, round(48 + (1 - min(price_mid_delta * 8, 1)) * 25))

    if buy_score >= sell_score and buy_score >= 50:
        signal_type = SignalType.BUY
        confidence = int(min(95, round(buy_score)))
        target_price = latest_close * (1 + settings["target_pct"])
        stop_loss = latest_close * (1 - settings["stop_pct"])
    elif sell_score > buy_score and sell_score >= 50:
        signal_type = SignalType.SELL
        confidence = int(min(95, round(sell_score)))
        target_price = latest_close * (1 - settings["target_pct"])
        stop_loss = latest_close * (1 + settings["stop_pct"])
    else:
        signal_type = SignalType.HOLD
        confidence = int(max(45, hold_confidence))
        target_price = latest_close * (1 + settings["target_pct"] / 2)
        stop_loss = latest_close * (1 - settings["stop_pct"] / 2)

    breakdown: ConfidenceBreakdown | None = None
    if sentiment_score is not None:
        normalized_sentiment = max(0.0, min(100.0, float(sentiment_score)))
        technical_confidence = max(0.0, min(100.0, float(confidence)))
        rsi_contribution = technical_confidence * 0.7 * 0.7
        macd_contribution = technical_confidence * 0.7 * 0.3
        sentiment_contribution = normalized_sentiment * 0.3
        display_total = rsi_contribution + macd_contribution + sentiment_contribution
        confidence = int(round(max(0.0, min(100.0, display_total))))
        breakdown = ConfidenceBreakdown(
            rsi_contribution=rsi_contribution,
            macd_contribution=macd_contribution,
            sentiment_contribution=sentiment_contribution,
            display_total=display_total,
        )

    signal_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"signal:{asset}:{risk_profile.value}:{latest_time.isoformat()}"))
    return Signal(
        id=signal_id,
        asset=asset,
        type=signal_type,
        confidence=confidence,
        target_price=round(target_price, 2),
        stop_loss=round(stop_loss, 2),
        indicators=SignalIndicators(
            RSI=round(rsi, 2),
            MACD=macd_sentiment,
            BollingerBands=bands,
        ),
        created_at=latest_time,
        risk_profile=risk_profile,
        breakdown=breakdown,
    )


async def build_signal_feed(
    *,
    signal_type: SignalType | None = None,
    confidence_min: int | None = None,
    asset: str | None = None,
    risk_profile: RiskProfile = RiskProfile.moderate,
    limit: int = 20,
    sentiment_score: int | float | None = None,
) -> SignalListResponse:
    assets = await _normalize_assets(asset)
    all_usdt_pairs = await _get_all_usdt_pairs()
    requested_limit = max(1, min(int(limit or 20), 50))
    threshold = int(confidence_min if confidence_min is not None else _PROFILE_SETTINGS[risk_profile]["default_confidence_min"])

    async def _get_klines_with_semaphore(item: str) -> dict[str, Any]:
        async with _KLINES_SEMAPHORE:
            return await get_klines(item)

    snapshots = await asyncio.gather(*(_get_klines_with_semaphore(item) for item in assets))
    cached_candidates = [item.get("cached_at") for item in snapshots if item.get("cached_at")]
    cached_at = max(cached_candidates) if cached_candidates else None
    is_stale = any(bool(item.get("is_stale")) for item in snapshots)

    signals = []
    for current_asset, snapshot in zip(assets, snapshots):
        try:
            signal = _build_signal(
                asset=current_asset,
                risk_profile=risk_profile,
                candles=snapshot["candles"],
                sentiment_score=sentiment_score,
            )
            signals.append(signal)
            # Save to history (fire-and-forget in background thread)
            from app.routes.signals import _save_signal_to_history
            threading.Thread(target=_save_signal_to_history, args=(signal,), daemon=True).start()
        except Exception as exc:
            logger.warning("Failed to build signal for %s: %s", current_asset, exc)
            continue

    if signal_type is not None:
        signals = [signal for signal in signals if signal.type == signal_type]
    signals = [signal for signal in signals if signal.confidence >= threshold]
    signals.sort(key=lambda item: (item.created_at, item.confidence), reverse=True)
    total = len(signals)
    signals = signals[:requested_limit]

    for signal in signals:
        _remember_signal(signal, cached_at, is_stale)

    return SignalListResponse(
        signals=signals,
        total=total,
        cached_at=cached_at,
        is_stale=is_stale,
        available_assets=all_usdt_pairs,
    )


async def get_signal_detail(signal_id: str) -> Signal:
    remembered, _cached_at, _is_stale = _get_remembered_signal(signal_id)
    if remembered is not None:
        return remembered

    all_pairs = await _get_all_usdt_pairs()
    signal_limit = min(100, len(all_pairs))
    for risk_profile in RiskProfile:
        feed = await build_signal_feed(risk_profile=risk_profile, confidence_min=0, limit=signal_limit)
        for signal in feed.signals:
            if signal.id == signal_id:
                return signal
    raise KeyError(signal_id)


async def get_latest_high_confidence_signals() -> SignalListResponse:
    all_pairs = await _get_all_usdt_pairs()
    signal_limit = min(150, len(all_pairs))
    feeds = await asyncio.gather(
        *(build_signal_feed(risk_profile=risk_profile, confidence_min=70, limit=signal_limit) for risk_profile in RiskProfile)
    )

    signals: list[Signal] = []
    cached_candidates: list[datetime] = []
    is_stale = False
    for feed in feeds:
        signals.extend(feed.signals)
        if feed.cached_at:
            cached_candidates.append(feed.cached_at)
        is_stale = is_stale or feed.is_stale

    signals = [signal for signal in signals if signal.confidence >= 70]
    signals.sort(key=lambda item: (item.created_at, item.confidence), reverse=True)
    total = len(signals)
    signals = signals[:5]

    latest_cached_at = max(cached_candidates) if cached_candidates else None
    for signal in signals:
        _remember_signal(signal, latest_cached_at, is_stale)

    return SignalListResponse(
        signals=signals,
        total=total,
        cached_at=latest_cached_at,
        is_stale=is_stale,
        available_assets=all_pairs,
    )
