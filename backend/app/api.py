# file: backend/app/api.py
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
import pandas as pd
from typing import List

from app.schemas.backtest import PresetResponse
from app.services.market_data_providers import (
    CCXT_SOURCE,
    STOOQ_SOURCE,
    YahooMarketDataProvider,
    get_market_data_provider,
)
from app.services.preset_service import get_presets
from app.services.pandas_ta_inspector import get_all_indicators_metadata

router = APIRouter(prefix="/api")
NASDAQ100_VERSION = "2026-02-23"
NASDAQ100_CONFIG_PATH = (
    Path(__file__).resolve().parents[1]
    / "config"
    / f"nasdaq100_symbols.v{NASDAQ100_VERSION}.json"
)

_MARKET_TIMEFRAMES = {"15m", "1h", "4h", "1d"}
_DEFAULT_HISTORY_DAYS = {
    "15m": 30,
    "1h": 180,
    "4h": 365,
    "1d": 3650,
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

    return {
        "symbols": symbols,
        "count": len(symbols)
    }


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

        if 'custom' not in result:
            result['custom'] = []

        result['custom'].append({
            "id": "cruzamentomedias",
            "name": "CRUZAMENTOMEDIAS",
            "category": "custom",
            "description": "Moving Average Crossover Strategy (EMA + SMA)",
            "params": [
                {"name": "media_curta", "type": "int", "default": 6},
                {"name": "media_longa", "type": "int", "default": 38},
                {"name": "media_inter", "type": "int", "default": 21}
            ]
        })
        result['custom'].append({
            "id": "emarsivolume",
            "name": "EMA 50/200 + RSI + Volume",
            "category": "custom",
            "description": "Trend following with EMA 200 filter, EMA 50 entries, RSI confirmation",
            "params": [
                {"name": "ema_fast", "type": "int", "default": 50},
                {"name": "ema_slow", "type": "int", "default": 200},
                {"name": "rsi_period", "type": "int", "default": 14},
                {"name": "rsi_min", "type": "int", "default": 40},
                {"name": "rsi_max", "type": "int", "default": 50}
            ]
        })
        result['custom'].append({
            "id": "fibonacciema",
            "name": "Fibonacci (0.5 / 0.618) + EMA 200",
            "category": "custom",
            "description": "Fibonacci retracement with EMA 200 trend filter",
            "params": [
                {"name": "ema_period", "type": "int", "default": 200},
                {"name": "swing_lookback", "type": "int", "default": 20},
                {"name": "fib_level_1", "type": "float", "default": 0.5},
                {"name": "fib_level_2", "type": "float", "default": 0.618},
                {"name": "level_tolerance", "type": "float", "default": 0.005}
            ]
        })

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
            status_code=404,
            detail=f"Indicator '{strategy_name}' not found in pandas_ta library"
        )
    return schema


@router.get("/arbitrage/spreads")
async def get_arbitrage_spreads(
    symbols: str = Query(
        "USDT/USDC,USDT/DAI,USDC/DAI",
        description="Lista de símbolos separados por vírgula",
    ),
    exchanges: str = Query("binance,okx,bybit", description="Lista de exchanges separadas por vírgula"),
    threshold: float = Query(0.0, description="Spread mínimo em %"),
):
    """Detecta spreads entre exchanges via WebSocket (sem executar trades)."""
    from app.services.arbitrage_spread_service import get_spreads_for_symbols

    exchange_list = [e.strip() for e in exchanges.split(",") if e.strip()]
    symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
    try:
        results = await get_spreads_for_symbols(
            symbols=symbol_list,
            exchanges=exchange_list,
            threshold_pct=threshold,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "symbols": symbol_list,
        "threshold": threshold,
        "exchanges": exchange_list,
        "results": results,
    }


def _classify_asset(symbol: str) -> str:
    return "crypto" if "/" in symbol else "stock"


def _validate_market_timeframe(asset: str, timeframe: str) -> str:
    tf = str(timeframe or "").strip().lower()
    if tf not in _MARKET_TIMEFRAMES:
        supported = ", ".join(sorted(_MARKET_TIMEFRAMES))
        raise ValueError(f"Unsupported timeframe '{timeframe}' for {asset}. Supported: {supported}.")
    return tf


def _default_since_str(timeframe: str) -> str:
    days = _DEFAULT_HISTORY_DAYS.get(timeframe, 30)
    since = datetime.now(timezone.utc) - timedelta(days=days)
    return since.isoformat()


def _normalize_candles_frame(df, limit: int):
    if df is None:
        return []

    out = df.copy()
    if out.empty:
        return []
    if "timestamp_utc" not in out.columns:
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


@router.get("/market/candles")
async def get_market_candles(
    symbol: str = Query(..., description="Ticker or pair (e.g. NVDA or BTC/USDT)"),
    timeframe: str = Query("1h", description="One of: 15m, 1h, 4h, 1d"),
    limit: int = Query(300, ge=1, le=2000, description="Max candles to return"),
):
    raw_symbol = str(symbol or "").strip()
    if not raw_symbol:
        raise HTTPException(status_code=400, detail="Query param 'symbol' must not be empty.")

    try:
        asset_type = _classify_asset(raw_symbol)
        tf = _validate_market_timeframe(asset_type, timeframe)
        since_str = _default_since_str(tf)

        data_source = ""
        if asset_type == "crypto":
            data_source = CCXT_SOURCE
            provider = get_market_data_provider(data_source)
            df = provider.fetch_ohlcv(raw_symbol, tf, since_str=since_str, limit=limit)
        elif tf == "1d":
            # Prefer free Stooq EOD for stocks; fallback to Yahoo daily when needed.
            data_source = STOOQ_SOURCE
            provider = get_market_data_provider(data_source)
            try:
                df = provider.fetch_ohlcv(raw_symbol, tf, since_str=since_str, limit=limit)
            except Exception:
                data_source = "yahoo"
                df = YahooMarketDataProvider().fetch_ohlcv(raw_symbol, tf, since_str=since_str, limit=limit)
        else:
            data_source = "yahoo"
            df = YahooMarketDataProvider().fetch_ohlcv(raw_symbol, tf, since_str=since_str, limit=limit)

        candles = _normalize_candles_frame(df, limit=limit)
        return {
            "symbol": raw_symbol,
            "asset_type": asset_type,
            "timeframe": tf,
            "data_source": data_source,
            "limit": limit,
            "count": len(candles),
            "candles": candles,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed fetching candles for '{raw_symbol}': {exc}")
