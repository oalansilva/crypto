from __future__ import annotations

import os


def _env_enabled(name: str, default: str = "0") -> bool:
    value = os.getenv(name, default).strip().lower()
    return value not in {"", "0", "false", "no", "off"}


def canonical_candles_enabled() -> bool:
    return _env_enabled("CRYPTO_CANDLES_CANONICAL_MODE", "1")


def direct_binance_candle_fetch_allowed() -> bool:
    return _env_enabled("CRYPTO_CANDLES_DIRECT_FETCH_FALLBACK", "0") or candle_writer_enabled()


def candle_writer_enabled() -> bool:
    return _env_enabled("CRYPTO_CANDLES_WRITER_ENABLED", "0")


def canonical_empty_payload(
    *,
    raw_symbol: str,
    asset_type: str,
    timeframe: str,
    limit: int,
    full_history: bool = False,
    backfill_job_id: str | None = None,
) -> dict:
    payload = {
        "symbol": raw_symbol,
        "asset_type": asset_type,
        "timeframe": timeframe,
        "data_source": "market_ohlcv-empty",
        "limit": limit,
        "count": 0,
        "candles": [],
        "canonical_candles": True,
        "direct_fetch_skipped": True,
    }
    if full_history and backfill_job_id:
        payload["backfill_job_id"] = backfill_job_id
        payload["backfill_status"] = "scheduled"
    return payload
