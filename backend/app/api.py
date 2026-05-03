# file: backend/app/api.py
import os
import threading
import time
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query
import pandas as pd
from typing import Any, Dict, List, Tuple

from app.schemas.backtest import PresetResponse
from app.services.market_data_providers import (
    CCXT_SOURCE,
    get_market_data_provider,
)
from app.services.asset_classification import classify_asset_type
from app.services.preset_service import get_presets
from app.services.pandas_ta_inspector import get_all_indicators_metadata
from app.services.ohlcv_storage import MarketOhlcvRepository

router = APIRouter(prefix="/api")

_MARKET_TIMEFRAMES = {"1m", "5m", "15m", "1h", "4h", "1d"}
_DEFAULT_HISTORY_DAYS = {
    # Keep these windows small: the candles endpoint is for UI charts, not full-history backfills.
    "1m": 1,
    "5m": 3,
    "15m": 30,
    "1h": 180,
    "4h": 365,
    "1d": 400,
}
_CANDLES_CACHE_TTL_SECONDS = 120.0
_CANDLES_CACHE_LOCK = threading.Lock()
_CANDLES_CACHE: Dict[Tuple[str, str, int], Dict[str, Any]] = {}
_OHLCV_REPO = MarketOhlcvRepository()
_PERSISTED_CANDLES_MAX_LAG_SECONDS = {
    "1m": 10 * 60,
    "5m": 30 * 60,
    "15m": 2 * 60 * 60,
    "1h": 6 * 60 * 60,
    "4h": 24 * 60 * 60,
    "1d": 3 * 24 * 60 * 60,
}


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "crypto-backtester-api"}


@router.get("/presets", response_model=List[PresetResponse])
async def list_presets():
    """Get predefined backtest presets for Playground"""
    return get_presets()


@router.get("/exchanges/binance/symbols")
async def get_binance_symbols():
    """Get all available USDT trading pairs from Binance (excludes unsupported/delisted)."""
    from app.services.exchange_service import ExchangeService
    from app.services.opportunity_service import _is_unsupported_symbol

    service = ExchangeService()
    raw = service.fetch_binance_symbols()
    symbols = [s for s in raw if not _is_unsupported_symbol(s)]

    return {"symbols": symbols, "count": len(symbols)}


@router.get("/exchanges/binance/timeframes")
async def get_binance_timeframes():
    """Get supported timeframes for Binance (cached)."""
    from app.services.exchange_service import ExchangeService

    service = ExchangeService()
    tfs = service.fetch_binance_timeframes()
    return {"timeframes": tfs, "count": len(tfs)}


@router.get("/markets/us/nasdaq100")
async def get_us_nasdaq100_symbols():
    """Stocks are disabled while the MVP is crypto-only."""
    raise HTTPException(
        status_code=410,
        detail="US stocks are disabled for the crypto-only MVP. Use Binance crypto pairs.",
    )


@router.get("/strategies/metadata")
async def get_strategies_metadata():
    """Get metadata for all available TA-Lib indicators + custom strategies"""
    try:
        result = get_all_indicators_metadata()

        if "custom" not in result:
            result["custom"] = []

        result["custom"].append(
            {
                "id": "cruzamentomedias",
                "name": "CRUZAMENTOMEDIAS",
                "category": "custom",
                "description": "Moving Average Crossover Strategy (EMA + SMA)",
                "params": [
                    {"name": "media_curta", "type": "int", "default": 6},
                    {"name": "media_longa", "type": "int", "default": 38},
                    {"name": "media_inter", "type": "int", "default": 21},
                ],
            }
        )
        result["custom"].append(
            {
                "id": "emarsivolume",
                "name": "EMA 50/200 + RSI + Volume",
                "category": "custom",
                "description": "Trend following with EMA 200 filter, EMA 50 entries, RSI confirmation",
                "params": [
                    {"name": "ema_fast", "type": "int", "default": 50},
                    {"name": "ema_slow", "type": "int", "default": 200},
                    {"name": "rsi_period", "type": "int", "default": 14},
                    {"name": "rsi_min", "type": "int", "default": 40},
                    {"name": "rsi_max", "type": "int", "default": 50},
                ],
            }
        )
        result["custom"].append(
            {
                "id": "fibonacciema",
                "name": "Fibonacci (0.5 / 0.618) + EMA 200",
                "category": "custom",
                "description": "Fibonacci retracement with EMA 200 trend filter",
                "params": [
                    {"name": "ema_period", "type": "int", "default": 200},
                    {"name": "swing_lookback", "type": "int", "default": 20},
                    {"name": "fib_level_1", "type": "float", "default": 0.5},
                    {"name": "fib_level_2", "type": "float", "default": 0.618},
                    {"name": "level_tolerance", "type": "float", "default": 0.005},
                ],
            }
        )

        return result
    except Exception as e:
        raise HTTPException(500, f"Error getting metadata: {str(e)}")


@router.get("/indicator/{strategy_name}/schema")
async def get_indicator_schema_endpoint(strategy_name: str):
    """Get parameter schema for a specific indicator - dynamically generated from TA-Lib"""
    from app.schemas.dynamic_schema_generator import get_dynamic_indicator_schema

    schema = get_dynamic_indicator_schema(strategy_name)
    if not schema:
        raise HTTPException(
            status_code=404, detail=f"Indicator '{strategy_name}' not found in TA-Lib library"
        )
    return schema


def _validate_market_timeframe(asset: str, timeframe: str) -> str:
    tf = str(timeframe or "").strip().lower()
    if asset == "stock" and tf not in {"1d", "4h"}:
        raise ValueError("Stocks currently support only timeframe='1d' or '4h'.")
    if tf not in _MARKET_TIMEFRAMES:
        supported = ", ".join(sorted(_MARKET_TIMEFRAMES))
        raise ValueError(
            f"Unsupported timeframe '{timeframe}' for {asset}. Supported: {supported}."
        )
    return tf


def _ui_default_since_str(timeframe: str, limit: int) -> str:
    """Return a safe default `since` for UI chart candles.

    We intentionally avoid huge backfills (which can freeze the UI) and instead
    fetch a recent window sized for the requested number of candles.
    """

    tf = str(timeframe or "").strip().lower()
    base_days = int(_DEFAULT_HISTORY_DAYS.get(tf, 30))

    # Approximate days needed to cover `limit` candles.
    if tf == "1m":
        days_needed = max(1, int(limit / 1440) + 1)
    elif tf == "5m":
        days_needed = max(1, int(limit / 288) + 1)
    elif tf == "15m":
        days_needed = max(3, int(limit / 96) + 3)  # 96 candles/day
    elif tf == "1h":
        days_needed = max(7, int(limit / 24) + 7)
    elif tf == "4h":
        days_needed = max(30, int(limit / 6) + 30)
    else:  # 1d
        days_needed = max(60, int(limit) + 30)

    days = min(base_days, days_needed)
    since = datetime.now(timezone.utc) - timedelta(days=days)
    return since.isoformat()


def _normalize_candles_frame(df, limit: int):
    if df is None:
        return []

    out = df.copy()
    if out.empty:
        return []
    # Some providers (e.g., CCXT loader) may set timestamp_utc as the index name but not as a column.
    if "timestamp_utc" not in out.columns:
        if getattr(out.index, "name", None) == "timestamp_utc":
            out = out.reset_index()
        else:
            raise ValueError("Provider returned invalid candle payload (missing timestamp_utc).")

    out = out.reset_index(drop=True)
    out["timestamp_utc"] = pd.to_datetime(out["timestamp_utc"], utc=True, errors="coerce")
    out = out.dropna(subset=["timestamp_utc", "open", "high", "low", "close"])
    out = out.sort_values("timestamp_utc")
    out = out.tail(limit)

    candles = []
    for _, row in out.iterrows():
        ts = row["timestamp_utc"]
        candles.append(
            {
                "timestamp_utc": ts.isoformat(),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row.get("volume", 0.0) or 0.0),
            }
        )
    return candles


def _is_persisted_candles_fresh(candles: list[dict[str, Any]], timeframe: str) -> bool:
    if not candles:
        return False

    raw_timestamp = candles[-1].get("timestamp_utc")
    parsed = pd.to_datetime(raw_timestamp, utc=True, errors="coerce")
    if pd.isna(parsed):
        return False

    now = pd.Timestamp.now(tz=timezone.utc)
    lag_seconds = max(0.0, (now - parsed).total_seconds())
    max_lag_seconds = _PERSISTED_CANDLES_MAX_LAG_SECONDS.get(
        str(timeframe or "").strip().lower(),
        24 * 60 * 60,
    )
    return lag_seconds <= max_lag_seconds


def _persisted_candles_payload(
    *,
    raw_symbol: str,
    asset_type: str,
    timeframe: str,
    limit: int,
    candles: list[dict[str, Any]],
    data_source: str,
) -> dict[str, Any]:
    return {
        "symbol": raw_symbol,
        "asset_type": asset_type,
        "timeframe": timeframe,
        "data_source": data_source,
        "limit": limit,
        "count": len(candles),
        "candles": candles,
    }


def _read_candles_cache(symbol: str, timeframe: str, limit: int) -> Dict[str, Any] | None:
    now = time.time()
    key = (symbol, timeframe, limit)
    with _CANDLES_CACHE_LOCK:
        cached = _CANDLES_CACHE.get(key)
        if not cached:
            return None
        if float(cached.get("expires_at") or 0) <= now:
            _CANDLES_CACHE.pop(key, None)
            return None
        return dict(cached.get("payload") or {})


def _write_candles_cache(symbol: str, timeframe: str, limit: int, payload: Dict[str, Any]) -> None:
    key = (symbol, timeframe, limit)
    with _CANDLES_CACHE_LOCK:
        _CANDLES_CACHE[key] = {
            "payload": dict(payload),
            "expires_at": time.time() + _CANDLES_CACHE_TTL_SECONDS,
        }


@router.get("/market/candles")
async def get_market_candles(
    symbol: str = Query(..., description="Ticker or pair (e.g. NVDA or BTC/USDT)"),
    timeframe: str = Query("1d", description="One of: 1m, 5m, 15m, 1h, 4h, 1d"),
    limit: int = Query(200, ge=1, le=2000, description="Max candles to return"),
):
    raw_symbol = str(symbol or "").strip()
    if not raw_symbol:
        raise HTTPException(status_code=400, detail="Query param 'symbol' must not be empty.")

    try:
        asset_type = classify_asset_type(raw_symbol)
        if asset_type != "crypto":
            raise ValueError("The MVP supports only crypto pairs such as BTC/USDT.")
        tf = _validate_market_timeframe(asset_type, timeframe)
        cached = _read_candles_cache(raw_symbol, tf, limit)
        if cached is not None:
            return cached

        stale_persisted: list[dict[str, Any]] = []
        if _OHLCV_REPO.enabled:
            try:
                persisted = _OHLCV_REPO.read_recent_candles(raw_symbol, tf, limit)
            except Exception:
                persisted = []
            if persisted and _is_persisted_candles_fresh(persisted, tf):
                payload = _persisted_candles_payload(
                    raw_symbol=raw_symbol,
                    asset_type=asset_type,
                    timeframe=tf,
                    limit=limit,
                    candles=persisted,
                    data_source="timescaledb",
                )
                _write_candles_cache(raw_symbol, tf, limit, payload)
                return payload
            stale_persisted = persisted

        since_str = _ui_default_since_str(tf, limit=limit)

        data_source = ""
        df = None
        if asset_type == "crypto":
            data_source = CCXT_SOURCE
            provider = get_market_data_provider(data_source)
            # For UI candles, never trigger full-history download when cache is empty.
            # Some test fakes/providers may not support this kwarg.
            try:
                df = provider.fetch_ohlcv(
                    raw_symbol,
                    tf,
                    since_str=since_str,
                    limit=limit,
                    full_history_if_empty=False,
                )
            except TypeError:
                df = provider.fetch_ohlcv(raw_symbol, tf, since_str=since_str, limit=limit)
            except Exception:
                if stale_persisted:
                    payload = _persisted_candles_payload(
                        raw_symbol=raw_symbol,
                        asset_type=asset_type,
                        timeframe=tf,
                        limit=limit,
                        candles=stale_persisted,
                        data_source="timescaledb-stale",
                    )
                    _write_candles_cache(raw_symbol, tf, limit, payload)
                    return payload
                raise
        candles = _normalize_candles_frame(df, limit=limit)
        if not candles and stale_persisted:
            payload = _persisted_candles_payload(
                raw_symbol=raw_symbol,
                asset_type=asset_type,
                timeframe=tf,
                limit=limit,
                candles=stale_persisted,
                data_source="timescaledb-stale",
            )
            _write_candles_cache(raw_symbol, tf, limit, payload)
            return payload
        payload = {
            "symbol": raw_symbol,
            "asset_type": asset_type,
            "timeframe": tf,
            "data_source": data_source,
            "limit": limit,
            "count": len(candles),
            "candles": candles,
        }
        if _OHLCV_REPO.enabled and candles:
            try:
                _OHLCV_REPO.write_candles(raw_symbol, tf, data_source, df)
            except Exception:
                pass
        _write_candles_cache(raw_symbol, tf, limit, payload)
        return payload
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed fetching candles for '{raw_symbol}': {exc}"
        )


@router.get("/market/candles/metrics")
async def get_market_candles_metrics():
    payload = _OHLCV_REPO.get_metrics()
    return {
        "source": "market_ohlcv" if _OHLCV_REPO.enabled else "disabled",
        "metrics": payload,
    }
