from __future__ import annotations

"""Signal generation backed by Binance OHLCV.

This implementation uses deterministic heuristics until the LSTM + RandomForest
ensemble from Card #55 is available.
"""

import asyncio
import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
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
BINANCE_TICKER_PRICE_URL = "https://api.binance.com/api/v3/ticker/price"
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
_SNAPSHOT_CACHE_LOCK = threading.Lock()
_SIGNAL_FEED_SNAPSHOTS: dict["RiskProfile", "SignalFeedSnapshot"] = {}
_SIGNAL_FEED_REFRESH_TASK: asyncio.Task[None] | None = None
_SIGNAL_FEED_STOP_EVENT: asyncio.Event | None = None
SIGNAL_FEED_REFRESH_INTERVAL_SECONDS = 300.0
SIGNAL_FEED_SNAPSHOT_FILE = Path(__file__).resolve().parents[2] / "cache" / "signals_snapshot.json"

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


@dataclass
class SignalFeedSnapshot:
    risk_profile: RiskProfile
    signals: list[Signal]
    available_assets: list[str]
    cached_at: datetime | None
    is_stale: bool
    sentiment_score: int | float | None
    refreshed_at: datetime


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


async def _fetch_latest_price_from_binance(asset: str) -> float:
    timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(BINANCE_TICKER_PRICE_URL, params={"symbol": asset})
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else float(attempt)
                await asyncio.sleep(min(delay, 5.0))
                continue
            response.raise_for_status()
            payload = response.json()
            return float(payload["price"])
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            if attempt >= MAX_RETRIES:
                raise RuntimeError(f"Unable to fetch Binance ticker price for {asset}: {exc}") from exc
            await asyncio.sleep(min(2 ** (attempt - 1), 4))
    raise RuntimeError(f"Unable to fetch Binance ticker price for {asset}")


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


def _clone_snapshot(snapshot: SignalFeedSnapshot) -> SignalFeedSnapshot:
    return SignalFeedSnapshot(
        risk_profile=snapshot.risk_profile,
        signals=list(snapshot.signals),
        available_assets=list(snapshot.available_assets),
        cached_at=snapshot.cached_at,
        is_stale=snapshot.is_stale,
        sentiment_score=snapshot.sentiment_score,
        refreshed_at=snapshot.refreshed_at,
    )


def get_signal_feed_snapshot(risk_profile: RiskProfile) -> SignalFeedSnapshot | None:
    with _SNAPSHOT_CACHE_LOCK:
        snapshot = _SIGNAL_FEED_SNAPSHOTS.get(risk_profile)
        if snapshot is None:
            return None
        return _clone_snapshot(snapshot)


def clear_signal_feed_snapshot_cache() -> None:
    with _SNAPSHOT_CACHE_LOCK:
        _SIGNAL_FEED_SNAPSHOTS.clear()


def clear_signal_feed_snapshot_file() -> None:
    try:
        SIGNAL_FEED_SNAPSHOT_FILE.unlink(missing_ok=True)
    except Exception:
        return


def _snapshot_to_payload(snapshot: SignalFeedSnapshot) -> dict[str, Any]:
    return {
        "risk_profile": snapshot.risk_profile.value,
        "signals": [signal.model_dump(mode="json", by_alias=True) for signal in snapshot.signals],
        "available_assets": list(snapshot.available_assets),
        "cached_at": snapshot.cached_at.isoformat() if snapshot.cached_at else None,
        "is_stale": snapshot.is_stale,
        "sentiment_score": snapshot.sentiment_score,
        "refreshed_at": snapshot.refreshed_at.isoformat(),
    }


def _payload_to_snapshot(payload: dict[str, Any]) -> SignalFeedSnapshot:
    return SignalFeedSnapshot(
        risk_profile=RiskProfile(str(payload["risk_profile"])),
        signals=[Signal.model_validate(item) for item in payload.get("signals") or []],
        available_assets=list(payload.get("available_assets") or []),
        cached_at=datetime.fromisoformat(payload["cached_at"]) if payload.get("cached_at") else None,
        is_stale=bool(payload.get("is_stale")),
        sentiment_score=payload.get("sentiment_score"),
        refreshed_at=datetime.fromisoformat(payload["refreshed_at"]),
    )


def _persist_signal_feed_snapshots(snapshots: dict[RiskProfile, SignalFeedSnapshot]) -> None:
    try:
        SIGNAL_FEED_SNAPSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "profiles": {risk_profile.value: _snapshot_to_payload(snapshot) for risk_profile, snapshot in snapshots.items()},
            "saved_at": _utc_now().isoformat(),
        }
        SIGNAL_FEED_SNAPSHOT_FILE.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    except Exception as exc:
        logger.warning("Failed to persist signal feed snapshots: %s", exc)


def load_signal_feed_snapshots_from_disk() -> bool:
    try:
        if not SIGNAL_FEED_SNAPSHOT_FILE.exists():
            return False
        payload = json.loads(SIGNAL_FEED_SNAPSHOT_FILE.read_text(encoding="utf-8"))
        profiles_payload = payload.get("profiles") or {}
        loaded = {
            RiskProfile(profile_name): _payload_to_snapshot(snapshot_payload)
            for profile_name, snapshot_payload in profiles_payload.items()
        }
    except Exception as exc:
        logger.warning("Failed to load signal feed snapshots from disk: %s", exc)
        return False

    if not loaded:
        return False

    with _SNAPSHOT_CACHE_LOCK:
        _SIGNAL_FEED_SNAPSHOTS.clear()
        _SIGNAL_FEED_SNAPSHOTS.update({key: _clone_snapshot(value) for key, value in loaded.items()})
    return True


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


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _compute_macd(closes: list[float]) -> tuple[float, float, float, str]:
    ema12 = _ema_series(closes, 12)
    ema26 = _ema_series(closes, 26)
    offset = len(ema12) - len(ema26)
    macd_values = [ema12[idx + offset] - ema26[idx] for idx in range(len(ema26))]
    signal_series = _ema_series(macd_values, 9)
    macd_line = macd_values[-1]
    signal_line = signal_series[-1]
    histogram = macd_line - signal_line
    scale = max(abs(signal_line), abs(macd_line), 1e-9)
    normalized_histogram = histogram / scale
    sentiment = "bullish" if normalized_histogram > 0.08 else "bearish" if normalized_histogram < -0.08 else "neutral"
    return macd_line, signal_line, histogram, sentiment


def _compute_bollinger_bands(closes: list[float], period: int = 20) -> BollingerBandsPayload:
    window = closes[-period:]
    middle = mean(window)
    deviation = pstdev(window) if len(window) > 1 else 0.0
    distance = deviation * 2
    return BollingerBandsPayload(upper=middle + distance, middle=middle, lower=middle - distance)


def _round_price(value: float) -> float:
    if value >= 1000:
        return round(value, 2)
    if value >= 1:
        return round(value, 4)
    if value >= 0.01:
        return round(value, 6)
    return round(value, 8)


def _load_open_buy_positions(user_id: str | None) -> set[tuple[str, str]]:
    if not user_id:
        return set()

    from app.database import SessionLocal
    from app.models_signal_history import SignalHistory

    db = SessionLocal()
    try:
        rows = (
            db.query(SignalHistory.asset, SignalHistory.risk_profile)
            .filter(
                SignalHistory.user_id == user_id,
                SignalHistory.archived == "no",
                SignalHistory.type == "BUY",
                SignalHistory.status == "ativo",
            )
            .distinct()
            .all()
        )
        return {(str(asset), str(risk_profile)) for asset, risk_profile in rows}
    finally:
        db.close()


def _load_open_buy_position_entries(user_id: str | None) -> dict[tuple[str, str], float]:
    if not user_id:
        return {}

    from app.database import SessionLocal
    from app.models_signal_history import SignalHistory

    db = SessionLocal()
    try:
        rows = (
            db.query(
                SignalHistory.asset,
                SignalHistory.risk_profile,
                SignalHistory.entry_price,
            )
            .filter(
                SignalHistory.user_id == user_id,
                SignalHistory.archived == "no",
                SignalHistory.type == "BUY",
                SignalHistory.status == "ativo",
                SignalHistory.entry_price.isnot(None),
            )
            .order_by(SignalHistory.created_at.desc())
            .all()
        )
        entries: dict[tuple[str, str], float] = {}
        for asset, risk_profile, entry_price in rows:
            key = (str(asset), str(risk_profile))
            if key in entries:
                continue
            entries[key] = float(entry_price)
        return entries
    finally:
        db.close()


def _build_signal(
    *,
    asset: str,
    risk_profile: RiskProfile,
    candles: list[dict[str, Any]],
    sentiment_score: int | float | None = None,
) -> Signal:
    closes = [float(candle["close"]) for candle in candles]
    latest_close = closes[-1]
    entry_price = latest_close
    latest_time = candles[-1]["open_time"]
    settings = _PROFILE_SETTINGS[risk_profile]
    rsi = round(_compute_rsi(closes), 2)
    macd_line, signal_line, histogram, macd_sentiment = _compute_macd(closes)
    bands = _compute_bollinger_bands(closes)

    buy_score = 0.0
    sell_score = 0.0

    rsi_buy_strength = _clamp((settings["buy_rsi"] + 12 - rsi) / 18, 0.0, 1.0)
    rsi_sell_strength = _clamp((rsi - (settings["sell_rsi"] - 12)) / 18, 0.0, 1.0)
    buy_score += rsi_buy_strength * 34
    sell_score += rsi_sell_strength * 34

    macd_scale = max(abs(signal_line), abs(macd_line), latest_close * 0.002, 1e-9)
    macd_bias = _clamp(histogram / macd_scale, -1.0, 1.0)
    buy_score += max(0.0, macd_bias) * 24
    sell_score += max(0.0, -macd_bias) * 24
    if abs(macd_bias) < 0.12:
        neutrality_bonus = (0.12 - abs(macd_bias)) / 0.12 * 6
        buy_score += neutrality_bonus
        sell_score += neutrality_bonus

    band_span = max(bands.upper - bands.lower, latest_close * 0.01, 1e-9)
    band_position = _clamp((latest_close - bands.lower) / band_span, 0.0, 1.0)
    buy_score += (1.0 - band_position) * 28
    sell_score += band_position * 28

    price_mid_delta = abs(latest_close - bands.middle) / max(bands.middle, 1e-9)
    hold_confidence = min(88, round(48 + (1 - min(price_mid_delta * 8, 1)) * 25))

    if buy_score >= sell_score and buy_score >= 50:
        signal_type = SignalType.BUY
        confidence = int(round(_clamp(buy_score, 0.0, 95.0)))
        target_price = latest_close * (1 + settings["target_pct"])
        stop_loss = latest_close * (1 - settings["stop_pct"])
    elif sell_score > buy_score and sell_score >= 50:
        signal_type = SignalType.SELL
        confidence = int(round(_clamp(sell_score, 0.0, 95.0)))
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
        rsi_contribution = technical_confidence * 0.7
        macd_contribution = technical_confidence * 0.3
        # Sentiment should bias the technical signal, not wipe it out for mildly bearish days.
        sentiment_contribution = (normalized_sentiment - 50.0) * 0.15
        display_total = technical_confidence + sentiment_contribution
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
        target_price=_round_price(target_price),
        stop_loss=_round_price(stop_loss),
        indicators=SignalIndicators(
            RSI=round(rsi, 2),
            MACD=macd_sentiment,
            BollingerBands=bands,
        ),
        created_at=latest_time,
        risk_profile=risk_profile,
        entry_price=entry_price,
        current_price=latest_close,
        pnl_percent=0.0 if signal_type == SignalType.BUY else None,
        breakdown=breakdown,
    )


async def _fetch_market_snapshots(assets: list[str]) -> tuple[dict[str, dict[str, Any]], datetime | None, bool]:
    async def _get_klines_with_semaphore(item: str) -> dict[str, Any]:
        async with _KLINES_SEMAPHORE:
            return await get_klines(item)

    raw_snapshots = await asyncio.gather(
        *(_get_klines_with_semaphore(item) for item in assets),
        return_exceptions=True,
    )
    collected_snapshots: list[tuple[str, dict[str, Any] | None, Exception | None]] = []
    for item, raw_snapshot in zip(assets, raw_snapshots):
        if isinstance(raw_snapshot, Exception):
            logger.warning("Failed to fetch klines for %s while building snapshot: %s", item, raw_snapshot)
            collected_snapshots.append((item, None, raw_snapshot))
            continue
        collected_snapshots.append((item, raw_snapshot, None))

    snapshots_by_asset = {
        item: snapshot
        for item, snapshot, error in collected_snapshots
        if snapshot is not None
    }
    if not snapshots_by_asset:
        raise RuntimeError("Unable to fetch klines for any requested asset")

    cached_candidates = [
        item_snapshot.get("cached_at")
        for _, item_snapshot, _ in collected_snapshots
        if item_snapshot is not None and item_snapshot.get("cached_at")
    ]
    cached_at = max(cached_candidates) if cached_candidates else None
    is_stale = any(
        bool(item_snapshot.get("is_stale"))
        for _, item_snapshot, _ in collected_snapshots
        if item_snapshot is not None
    )
    return snapshots_by_asset, cached_at, is_stale


async def get_latest_prices(assets: list[str]) -> tuple[dict[str, float], datetime | None, bool]:
    normalized_assets = [_normalize_asset(asset) for asset in assets if str(asset or "").strip()]
    if not normalized_assets:
        return {}, None, False

    async def _get_price(asset: str) -> tuple[str, float | None]:
        try:
            return asset, await _fetch_latest_price_from_binance(asset)
        except Exception as exc:
            logger.warning("Failed to fetch latest Binance ticker price for %s: %s", asset, exc)
            return asset, None

    raw_prices = await asyncio.gather(*(_get_price(asset) for asset in normalized_assets))
    prices: dict[str, float] = {}
    for asset, price in raw_prices:
        if price is None:
            continue
        prices[asset] = price

    if len(prices) == len(normalized_assets):
        return prices, _utc_now(), False

    snapshots_by_asset, cached_at, is_stale = await _fetch_market_snapshots(normalized_assets)
    for asset, snapshot in snapshots_by_asset.items():
        if asset in prices:
            continue
        candles = snapshot.get("candles") or []
        if not candles:
            continue
        try:
            prices[asset] = float(candles[-1]["close"])
        except (TypeError, ValueError, KeyError):
            continue
    return prices, cached_at, True if prices else is_stale


def _build_signals_for_profile(
    *,
    risk_profile: RiskProfile,
    snapshots_by_asset: dict[str, dict[str, Any]],
    sentiment_score: int | float | None,
) -> list[Signal]:
    signals: list[Signal] = []
    for asset, snapshot in snapshots_by_asset.items():
        try:
            signal = _build_signal(
                asset=asset,
                risk_profile=risk_profile,
                candles=snapshot["candles"],
                sentiment_score=sentiment_score,
            )
            signals.append(signal)
        except Exception as exc:
            logger.warning("Failed to build signal for %s: %s", asset, exc)
    signals.sort(key=lambda item: (item.created_at, item.confidence), reverse=True)
    return signals


async def _compute_signal_feed_snapshots() -> dict[RiskProfile, SignalFeedSnapshot]:
    all_usdt_pairs = await _get_all_usdt_pairs()
    sentiment_score = None
    try:
        from app.services import sentiment_service

        sentiment_score = (await sentiment_service.get_market_sentiment()).score
    except Exception as exc:
        logger.warning("Failed to refresh market sentiment for signals snapshot: %s", exc)

    snapshots_by_asset, cached_at, is_stale = await _fetch_market_snapshots(all_usdt_pairs)
    refreshed_at = _utc_now()
    return {
        risk_profile: SignalFeedSnapshot(
            risk_profile=risk_profile,
            signals=_build_signals_for_profile(
                risk_profile=risk_profile,
                snapshots_by_asset=snapshots_by_asset,
                sentiment_score=sentiment_score,
            ),
            available_assets=list(all_usdt_pairs),
            cached_at=cached_at,
            is_stale=is_stale,
            sentiment_score=sentiment_score,
            refreshed_at=refreshed_at,
        )
        for risk_profile in RiskProfile
    }


async def refresh_signal_feed_snapshots() -> dict[RiskProfile, SignalFeedSnapshot]:
    computed = await _compute_signal_feed_snapshots()
    with _SNAPSHOT_CACHE_LOCK:
        _SIGNAL_FEED_SNAPSHOTS.clear()
        _SIGNAL_FEED_SNAPSHOTS.update({key: _clone_snapshot(value) for key, value in computed.items()})
    _persist_signal_feed_snapshots(computed)
    return computed


async def get_or_refresh_signal_feed_snapshot(risk_profile: RiskProfile) -> SignalFeedSnapshot:
    snapshot = get_signal_feed_snapshot(risk_profile)
    if snapshot is not None:
        return snapshot
    computed = await refresh_signal_feed_snapshots()
    return _clone_snapshot(computed[risk_profile])


async def _signal_feed_refresh_loop() -> None:
    assert _SIGNAL_FEED_STOP_EVENT is not None
    while not _SIGNAL_FEED_STOP_EVENT.is_set():
        try:
            await refresh_signal_feed_snapshots()
        except Exception as exc:
            logger.warning("Signal feed refresh loop failed: %s", exc)
        try:
            await asyncio.wait_for(
                _SIGNAL_FEED_STOP_EVENT.wait(),
                timeout=SIGNAL_FEED_REFRESH_INTERVAL_SECONDS,
            )
        except TimeoutError:
            continue


async def start_signal_feed_snapshot_worker() -> None:
    global _SIGNAL_FEED_REFRESH_TASK, _SIGNAL_FEED_STOP_EVENT

    if _SIGNAL_FEED_REFRESH_TASK and not _SIGNAL_FEED_REFRESH_TASK.done():
        return

    _SIGNAL_FEED_STOP_EVENT = asyncio.Event()
    load_signal_feed_snapshots_from_disk()
    _SIGNAL_FEED_REFRESH_TASK = asyncio.create_task(_signal_feed_refresh_loop())


async def stop_signal_feed_snapshot_worker() -> None:
    global _SIGNAL_FEED_REFRESH_TASK, _SIGNAL_FEED_STOP_EVENT

    stop_event = _SIGNAL_FEED_STOP_EVENT
    task = _SIGNAL_FEED_REFRESH_TASK
    _SIGNAL_FEED_STOP_EVENT = None
    _SIGNAL_FEED_REFRESH_TASK = None

    if stop_event is not None:
        stop_event.set()
    if task is not None:
        await task


async def build_signal_feed(
    *,
    signal_type: SignalType | None = None,
    confidence_min: int | None = None,
    asset: str | None = None,
    risk_profile: RiskProfile = RiskProfile.moderate,
    limit: int = 20,
    sentiment_score: int | float | None = None,
    user_id: str | None = None,
) -> SignalListResponse:
    requested_limit = max(1, min(int(limit or 20), 50))
    threshold = int(confidence_min if confidence_min is not None else _PROFILE_SETTINGS[risk_profile]["default_confidence_min"])
    signals: list[Signal]
    available_assets: list[str]
    cached_at: datetime | None
    is_stale: bool

    snapshot = get_signal_feed_snapshot(risk_profile)
    if snapshot is None and asset is None and sentiment_score is None:
        snapshot = await get_or_refresh_signal_feed_snapshot(risk_profile)

    if snapshot is not None and sentiment_score is None:
        signals = list(snapshot.signals)
        available_assets = list(snapshot.available_assets)
        cached_at = snapshot.cached_at
        is_stale = snapshot.is_stale
    else:
        assets = await _normalize_assets(asset)
        available_assets = await _get_all_usdt_pairs()
        market_snapshots, cached_at, is_stale = await _fetch_market_snapshots(assets)
        signals = _build_signals_for_profile(
            risk_profile=risk_profile,
            snapshots_by_asset=market_snapshots,
            sentiment_score=sentiment_score,
        )

    if asset:
        normalized_asset = _normalize_asset(asset)
        signals = [signal for signal in signals if signal.asset == normalized_asset]

    if signal_type is not None:
        signals = [signal for signal in signals if signal.type == signal_type]

    latest_prices, latest_prices_cached_at, latest_prices_stale = await get_latest_prices([signal.asset for signal in signals])
    if latest_prices:
        cached_at = latest_prices_cached_at or cached_at
        is_stale = is_stale or latest_prices_stale
        signals = [
            signal.model_copy(update={"current_price": latest_prices.get(signal.asset, signal.current_price)})
            for signal in signals
        ]

    open_positions = _load_open_buy_positions(user_id)
    open_position_entries = _load_open_buy_position_entries(user_id)
    actionable_signals: list[Signal] = []
    for signal in signals:
        position_key = (signal.asset, signal.risk_profile.value)
        if signal.type == SignalType.HOLD:
            continue
        if signal.type == SignalType.SELL and position_key not in open_positions:
            continue
        tracked_entry = open_position_entries.get(position_key)
        if tracked_entry is not None:
            current_price = signal.current_price or signal.entry_price
            pnl_percent = None
            if current_price is not None and tracked_entry > 0:
                pnl_percent = round(((current_price - tracked_entry) / tracked_entry) * 100, 4)
            signal = signal.model_copy(
                update={
                    "entry_price": tracked_entry,
                    "current_price": current_price,
                    "pnl_percent": pnl_percent,
                    "is_open_position": True,
                }
            )
        actionable_signals.append(signal)

    signals = actionable_signals
    signals = [signal for signal in signals if signal.confidence >= threshold]
    signals.sort(key=lambda item: (item.created_at, item.confidence), reverse=True)
    total = len(signals)
    signals = signals[:requested_limit]

    if user_id:
        from app.routes.signals import _save_signal_to_history

        for signal in signals:
            threading.Thread(target=_save_signal_to_history, args=(signal, user_id), daemon=True).start()

    for signal in signals:
        _remember_signal(signal, cached_at, is_stale)

    return SignalListResponse(
        signals=signals,
        total=total,
        cached_at=cached_at,
        is_stale=is_stale,
        available_assets=available_assets,
    )


async def build_signal_feed_for_assets(
    *,
    assets: list[str],
    risk_profile: RiskProfile = RiskProfile.moderate,
    confidence_min: int | None = None,
    limit: int = 20,
    sentiment_score: int | float | None = None,
    user_id: str | None = None,
    include_neutral: bool = True,
) -> SignalListResponse:
    requested_limit = max(1, min(int(limit or 20), 50))
    threshold = int(confidence_min if confidence_min is not None else _PROFILE_SETTINGS[risk_profile]["default_confidence_min"])

    normalized_assets = []
    seen_assets: set[str] = set()
    for asset in assets:
        try:
            normalized = _normalize_asset(asset)
        except Exception:
            continue
        if normalized in seen_assets:
            continue
        seen_assets.add(normalized)
        normalized_assets.append(normalized)

    if not normalized_assets:
        return SignalListResponse(
            signals=[],
            total=0,
            cached_at=None,
            is_stale=False,
            available_assets=[],
        )

    snapshots_by_asset, cached_at, is_stale = await _fetch_market_snapshots(normalized_assets)
    signals = _build_signals_for_profile(
        risk_profile=risk_profile,
        snapshots_by_asset=snapshots_by_asset,
        sentiment_score=sentiment_score,
    )

    latest_prices, latest_prices_cached_at, latest_prices_stale = await get_latest_prices([signal.asset for signal in signals])
    if latest_prices:
        cached_at = latest_prices_cached_at or cached_at
        is_stale = is_stale or latest_prices_stale
        signals = [
            signal.model_copy(update={"current_price": latest_prices.get(signal.asset, signal.current_price)})
            for signal in signals
        ]

    open_positions = _load_open_buy_positions(user_id) if user_id else set()
    open_position_entries = _load_open_buy_position_entries(user_id) if user_id else {}
    actionable_signals: list[Signal] = []
    for signal in signals:
        if not include_neutral and signal.type == SignalType.HOLD:
            continue
        if user_id and signal.type == SignalType.SELL:
            position_key = (signal.asset, signal.risk_profile.value)
            if position_key not in open_positions:
                continue
        if user_id:
            tracked_entry = open_position_entries.get((signal.asset, signal.risk_profile.value))
            if tracked_entry is not None:
                current_price = signal.current_price or signal.entry_price
                pnl_percent = None
                if current_price is not None and tracked_entry > 0:
                    pnl_percent = round(((current_price - tracked_entry) / tracked_entry) * 100, 4)
                signal = signal.model_copy(
                    update={
                        "entry_price": tracked_entry,
                        "current_price": current_price,
                        "pnl_percent": pnl_percent,
                        "is_open_position": True,
                    }
                )
        actionable_signals.append(signal)

    signals = [signal for signal in actionable_signals if signal.confidence >= threshold]
    signals.sort(key=lambda item: (item.created_at, item.confidence), reverse=True)
    total = len(signals)
    signals = signals[:requested_limit]

    if user_id:
        for signal in signals:
            _remember_signal(signal, cached_at, is_stale)

    return SignalListResponse(
        signals=signals,
        total=total,
        cached_at=cached_at,
        is_stale=is_stale,
        available_assets=normalized_assets,
    )


async def get_signal_detail(signal_id: str) -> Signal:
    remembered, _cached_at, _is_stale = _get_remembered_signal(signal_id)
    if remembered is not None:
        return remembered

    for risk_profile in RiskProfile:
        snapshot = get_signal_feed_snapshot(risk_profile)
        if snapshot is None:
            continue
        for signal in snapshot.signals:
            if signal.id == signal_id:
                return signal

    all_pairs = await _get_all_usdt_pairs()
    signal_limit = min(100, len(all_pairs))
    for risk_profile in RiskProfile:
        feed = await build_signal_feed(risk_profile=risk_profile, confidence_min=0, limit=signal_limit)
        for signal in feed.signals:
            if signal.id == signal_id:
                return signal
    raise KeyError(signal_id)


async def get_latest_high_confidence_signals(user_id: str | None = None) -> SignalListResponse:
    signals: list[Signal] = []
    cached_candidates: list[datetime] = []
    is_stale = False
    available_assets: list[str] = []
    latest_cached_at: datetime | None = None

    snapshots = await asyncio.gather(*(get_or_refresh_signal_feed_snapshot(risk_profile) for risk_profile in RiskProfile))
    for snapshot in snapshots:
        signals.extend(snapshot.signals)
        if snapshot.cached_at:
            cached_candidates.append(snapshot.cached_at)
        is_stale = is_stale or snapshot.is_stale
        if not available_assets:
            available_assets = list(snapshot.available_assets)

    signals = [signal for signal in signals if signal.confidence >= 70]

    latest_prices, latest_prices_cached_at, latest_prices_stale = await get_latest_prices([signal.asset for signal in signals])
    if latest_prices:
        latest_cached_at = latest_prices_cached_at
        is_stale = is_stale or latest_prices_stale
        signals = [
            signal.model_copy(update={"current_price": latest_prices.get(signal.asset, signal.current_price)})
            for signal in signals
        ]

    open_positions = _load_open_buy_positions(user_id)
    open_position_entries = _load_open_buy_position_entries(user_id)
    if user_id:
        filtered: list[Signal] = []
        for signal in signals:
            position_key = (signal.asset, signal.risk_profile.value)
            if signal.type == SignalType.HOLD:
                continue
            if signal.type == SignalType.SELL and position_key not in open_positions:
                continue
            tracked_entry = open_position_entries.get(position_key)
            if tracked_entry is not None:
                current_price = signal.current_price or signal.entry_price
                pnl_percent = None
                if current_price is not None and tracked_entry > 0:
                    pnl_percent = round(((current_price - tracked_entry) / tracked_entry) * 100, 4)
                signal = signal.model_copy(
                    update={
                        "entry_price": tracked_entry,
                        "current_price": current_price,
                        "pnl_percent": pnl_percent,
                        "is_open_position": True,
                    }
                )
            filtered.append(signal)
        signals = filtered

    signals.sort(key=lambda item: (item.created_at, item.confidence), reverse=True)
    total = len(signals)
    signals = signals[:5]

    if latest_cached_at is None:
        latest_cached_at = max(cached_candidates) if cached_candidates else None
    for signal in signals:
        _remember_signal(signal, latest_cached_at, is_stale)
    if user_id:
        from app.routes.signals import _save_signal_to_history

        for signal in signals:
            threading.Thread(target=_save_signal_to_history, args=(signal, user_id), daemon=True).start()

    return SignalListResponse(
        signals=signals,
        total=total,
        cached_at=latest_cached_at,
        is_stale=is_stale,
        available_assets=available_assets,
    )
