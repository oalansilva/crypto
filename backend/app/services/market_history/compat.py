"""Leituras e escritas no formato antigo ``(símbolo, timeframe, fonte)`` (card #1118).

``MarketOhlcvRepository`` (escritor de cripto, rotas e indicadores) mantém a sua
interface; com ``MARKET_HISTORY_UNIFIED=1`` ela passa por aqui e grava/lê as
séries ``binance_spot`` da autoridade nova. Fontes legadas (Stooq, Yahoo) viram
séries próprias e não se misturam com a Binance.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
from sqlalchemy import text

from app.services.market_history import store
from app.services.market_history.model import (
    SeriesSpec,
    crypto_spec,
    legacy_spec,
    legacy_source_label,
    SOURCE_SPOT,
)

_BINANCE_ALIASES = {"", "ccxt", "binance", "crypto", "default", "binance_spot"}


def spec_for_legacy(symbol: str, timeframe: str, source: str | None) -> SeriesSpec:
    src = str(source or "").strip().lower()
    if src in _BINANCE_ALIASES and "/" in str(symbol):
        return crypto_spec(symbol, timeframe)
    return legacy_spec(symbol, timeframe, src or "ccxt")


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return (
        value.replace(tzinfo=timezone.utc)
        if value.tzinfo is None
        else value.astimezone(timezone.utc)
    )


def _series_id(engine, symbol: str, timeframe: str, source: str | None = None) -> int | None:
    spec = spec_for_legacy(symbol, timeframe, source)
    with engine.connect() as conn:
        found = store.find_series(conn, spec)
    return found.series_id if found else None


def latest_candle_time(engine, symbol: str, timeframe: str) -> datetime | None:
    sid = _series_id(engine, symbol, timeframe)
    if sid is None:
        return None
    with engine.connect() as conn:
        _, last, _ = store.stored_extent(conn, sid)
    return _aware(last)


def earliest_candle_time(engine, symbol: str, timeframe: str) -> datetime | None:
    sid = _series_id(engine, symbol, timeframe)
    if sid is None:
        return None
    with engine.connect() as conn:
        first, _, _ = store.stored_extent(conn, sid)
    return _aware(first)


def _rows_to_dicts(frame: pd.DataFrame, source: str) -> list[dict[str, Any]]:
    return [
        {
            "timestamp_utc": ts.isoformat(),
            "open": float(r.open),
            "high": float(r.high),
            "low": float(r.low),
            "close": float(r.close),
            "volume": float(r.volume or 0.0),
            "source": source,
        }
        for ts, r in frame.iterrows()
    ]


def read_candles(engine, symbol: str, timeframe: str, limit: int | None) -> list[dict[str, Any]]:
    sid = _series_id(engine, symbol, timeframe)
    if sid is None:
        return []
    with engine.connect() as conn:
        frame = store.read_frame(conn, sid, limit=limit)
    return _rows_to_dicts(frame, legacy_source_label(SOURCE_SPOT))


def write_frame(
    engine,
    symbol: str,
    timeframe: str,
    source: str,
    df: pd.DataFrame,
) -> tuple[int, int]:
    """Grava o DataFrame do provedor. Devolve ``(novos, repetidos)``."""

    frame = df
    if frame.index.name == "timestamp_utc" and "timestamp_utc" not in frame.columns:
        frame = frame.reset_index()
    if "timestamp_utc" not in frame.columns:
        raise ValueError("Dataframe missing timestamp_utc")
    times = pd.to_datetime(frame["timestamp_utc"], utc=True, errors="coerce")
    clean = pd.DataFrame(
        {
            "open": pd.to_numeric(frame["open"], errors="coerce").to_numpy(),
            "high": pd.to_numeric(frame["high"], errors="coerce").to_numpy(),
            "low": pd.to_numeric(frame["low"], errors="coerce").to_numpy(),
            "close": pd.to_numeric(frame["close"], errors="coerce").to_numpy(),
            "volume": pd.to_numeric(frame.get("volume", 0.0), errors="coerce")
            .fillna(0.0)
            .to_numpy(),
        },
        index=pd.DatetimeIndex(times.to_numpy(), name="candle_time"),
    )
    clean = clean[clean.index.notna()].dropna(subset=["open", "high", "low", "close"])
    clean = clean[~clean.index.duplicated(keep="last")].sort_index()
    if clean.empty:
        return 0, 0
    spec = spec_for_legacy(symbol, timeframe, source)
    with engine.begin() as conn:
        series = store.get_or_create_series(conn, spec)
        table = store.ohlcv_table(conn)
        existing = int(
            conn.execute(
                text(
                    f"SELECT count(*) FROM {table} WHERE series_id = :s "
                    "AND candle_time >= :a AND candle_time <= :b"
                ),
                {
                    "s": series.series_id,
                    "a": clean.index.min().to_pydatetime(),
                    "b": clean.index.max().to_pydatetime(),
                },
            ).scalar()
            or 0
        )
    if spec.source == SOURCE_SPOT:
        from app.services.market_history.facade import get_history_service

        service = get_history_service()
        result = service.ingest_frame(series, clean)
        written = result
    else:
        with engine.begin() as conn:
            written = store.upsert_candles(
                conn, series, clean, legacy_source=legacy_source_label(spec.source)
            )
            store.extend_coverage_tail(conn, series, clean.index)
    duplicates = min(existing, len(clean))
    return len(clean) - duplicates, duplicates
