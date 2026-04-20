# file: backend/app/api.py
import json
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
import pandas as pd
from typing import Any, Dict, List, Tuple

from app.schemas.backtest import PresetResponse
from app.services.market_data_providers import (
    CCXT_SOURCE,
    STOOQ_SOURCE,
    YahooMarketDataProvider,
    get_market_data_provider,
)
from app.services.asset_classification import classify_asset_type
from app.services.preset_service import get_presets
from app.services.pandas_ta_inspector import get_all_indicators_metadata

router = APIRouter(prefix="/api")
NASDAQ100_VERSION = "2026-02-23"
NASDAQ100_CONFIG_PATH = (
    Path(__file__).resolve().parents[1] / "config" / f"nasdaq100_symbols.v{NASDAQ100_VERSION}.json"
)

_MARKET_TIMEFRAMES = {"15m", "1h", "4h", "1d"}
_DEFAULT_HISTORY_DAYS = {
    # Keep these windows small: the candles endpoint is for UI charts, not full-history backfills.
    "15m": 30,
    "1h": 180,
    "4h": 365,
    "1d": 400,
}
_CANDLES_CACHE_TTL_SECONDS = 120.0
_CANDLES_CACHE_LOCK = threading.Lock()
_CANDLES_CACHE: Dict[Tuple[str, str, int], Dict[str, Any]] = {}


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
    """Get versioned NASDAQ-100 ticker universe (plain US tickers)."""
    try:
        with NASDAQ100_CONFIG_PATH.open("r", encoding="utf-8") as f:
            symbols = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="NASDAQ-100 config not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid NASDAQ-100 config format")

    if not isinstance(symbols, list) or not all(isinstance(s, str) and s.strip() for s in symbols):
        raise HTTPException(status_code=500, detail="Invalid NASDAQ-100 symbols payload")

    ordered = [str(s).strip().upper() for s in symbols]
    return {
        "market": "us-stocks",
        "universe": "nasdaq-100",
        "version": NASDAQ100_VERSION,
        "symbols": ordered,
        "count": len(ordered),
    }


@router.get("/strategies/metadata")
async def get_strategies_metadata():
    """Get metadata for all available pandas-ta indicators + custom strategies"""
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
    """Get parameter schema for a specific indicator - dynamically generated from pandas_ta"""
    from app.schemas.dynamic_schema_generator import get_dynamic_indicator_schema

    schema = get_dynamic_indicator_schema(strategy_name)
    if not schema:
        raise HTTPException(
            status_code=404, detail=f"Indicator '{strategy_name}' not found in pandas_ta library"
        )
    return schema


def _validate_market_timeframe(asset: str, timeframe: str) -> str:
    tf = str(timeframe or "").strip().lower()
    if asset == "stock" and tf != "1d":
        raise ValueError("Stocks currently support only timeframe='1d'.")
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
    if tf == "15m":
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
    timeframe: str = Query("1d", description="One of: 15m, 1h, 4h, 1d"),
    limit: int = Query(200, ge=1, le=2000, description="Max candles to return"),
):
    raw_symbol = str(symbol or "").strip()
    if not raw_symbol:
        raise HTTPException(status_code=400, detail="Query param 'symbol' must not be empty.")

    try:
        asset_type = classify_asset_type(raw_symbol)
        tf = _validate_market_timeframe(asset_type, timeframe)
        cached = _read_candles_cache(raw_symbol, tf, limit)
        if cached is not None:
            return cached
        since_str = _ui_default_since_str(tf, limit=limit)

        data_source = ""
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
        elif tf == "1d":
            # Prefer free Stooq EOD for stocks; fallback to Yahoo daily when needed.
            data_source = STOOQ_SOURCE
            provider = get_market_data_provider(data_source)
            try:
                df = provider.fetch_ohlcv(raw_symbol, tf, since_str=since_str, limit=limit)
            except Exception:
                data_source = "yahoo"
                df = YahooMarketDataProvider().fetch_ohlcv(
                    raw_symbol, tf, since_str=since_str, limit=limit
                )
        else:
            raise ValueError("Stocks currently support only timeframe='1d'.")

        candles = _normalize_candles_frame(df, limit=limit)
        payload = {
            "symbol": raw_symbol,
            "asset_type": asset_type,
            "timeframe": tf,
            "data_source": data_source,
            "limit": limit,
            "count": len(candles),
            "candles": candles,
        }
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
