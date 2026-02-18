# file: backend/app/api.py
from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.schemas.backtest import PresetResponse
from app.services.preset_service import get_presets
from app.services.pandas_ta_inspector import get_all_indicators_metadata

router = APIRouter(prefix="/api")


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
    symbol: str = "USDT/USDC",
    exchanges: str = Query("binance,okx,bybit", description="Lista de exchanges separadas por vírgula"),
    threshold: float = Query(0.0, description="Spread mínimo em %"),
):
    """Detecta spreads USDT/USDC entre exchanges via WebSocket (sem executar trades)."""
    from app.services.arbitrage_spread_service import get_spread_opportunities

    exchange_list = [e.strip() for e in exchanges.split(",") if e.strip()]
    try:
        result = await get_spread_opportunities(
            symbol=symbol,
            exchanges=exchange_list,
            threshold_pct=threshold,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "symbol": symbol,
        "threshold": threshold,
        "exchanges": exchange_list,
        "spreads": result["spreads"],
        "opportunities": result["opportunities"],
    }
