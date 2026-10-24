"""Tipos e regras de identidade de série (card #1118, decisão 3)."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import timedelta
from typing import Any

import pandas as pd

SOURCE_SPOT = "binance_spot"
SOURCE_EQUITY = "binance_equity"
SESSION_24X7 = "24x7"
SESSION_RTH = "rth"
ADJ_NA = "na"
ADJ_ADJUSTED = "adjusted"
ADJ_RAW = "raw"
ORIGIN_NATIVE = "native"
ORIGIN_DERIVED = "derived"

CLASS_CRYPTO = "crypto"
CLASS_STOCK = "stock"
CLASS_ETF = "etf"

TIMEFRAME_DELTA = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
}
CRYPTO_TIMEFRAMES = ("1m", "5m", "15m", "1h", "4h", "1d")
# Ação e ETF: 5m e 1d nativos; 15m, 1h e 4h montados do 5m (1h e 4h entram no #1119, decisão 5).
EQUITY_NATIVE_TIMEFRAMES = ("5m", "1d")
EQUITY_DERIVED = {"15m": "5m", "1h": "5m", "4h": "5m"}
# Minutos de cada tempo derivado do 5m.
DERIVED_MINUTES = {"15m": 15, "1h": 60, "4h": 240}

SOURCE_LABELS = {SOURCE_SPOT: "Binance Spot", SOURCE_EQUITY: "Binance Ações"}
NOTE_CRYPTO = "Binance Spot · 24/7 · ajuste não se aplica"
# Rótulo do ajuste verificado em 23/10/2026 (tarefa 2.3): ``ADJUSTED`` ajusta splits (NVDA 10:1 sem
# salto) e não ajusta dividendos (SPY e AAPL: ``ADJUSTED`` == ``UNADJUSTED`` em todos os ex-dividendos).
NOTE_EQUITY = {
    ADJ_ADJUSTED: "Binance Ações · pregão regular de Nova York · ajustado por split",
    ADJ_RAW: "Binance Ações · pregão regular de Nova York · sem ajuste",
}


class HistoryError(Exception):
    code = "history_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code


class SeriesNotSupported(HistoryError):
    code = "series_not_supported"


class HistoryNotReady(HistoryError):
    """``MARKET_HISTORY_UNIFIED`` ligado sem a tabela nova (migração pendente)."""

    code = "history_not_migrated"


@dataclass(frozen=True)
class SeriesSpec:
    asset_id: str
    symbol: str
    asset_class: str
    source: str
    session: str
    adjustment: str
    timeframe: str


@dataclass(frozen=True)
class SeriesRef:
    """Série lógica. Para o 15m derivado, ``series_id`` é o do 5m físico."""

    series_id: int
    asset_id: str
    symbol: str
    asset_class: str
    source: str
    session: str
    adjustment: str
    timeframe: str
    origin: str
    data_version: int
    physical_timeframe: str

    @property
    def is_derived(self) -> bool:
        return self.origin == ORIGIN_DERIVED

    @property
    def is_equity(self) -> bool:
        return self.source == SOURCE_EQUITY

    @property
    def label(self) -> str:
        return series_note(self)

    def as_dict(self) -> dict[str, Any]:
        return {
            "series_id": self.series_id,
            "asset_id": self.asset_id,
            "symbol": self.symbol,
            "asset_class": self.asset_class,
            "source": self.source,
            "source_label": SOURCE_LABELS.get(self.source, self.source),
            "session": self.session,
            "adjustment": self.adjustment,
            "timeframe": self.timeframe,
            "origin": self.origin,
            "derived_from": self.physical_timeframe if self.is_derived else None,
            "data_version": self.data_version,
        }

    def with_version(self, version: int) -> "SeriesRef":
        return replace(self, data_version=version)


def series_note(series: SeriesRef | SeriesSpec) -> str:
    if series.source == SOURCE_EQUITY:
        return NOTE_EQUITY.get(series.adjustment, NOTE_EQUITY[ADJ_ADJUSTED])
    if series.source == SOURCE_SPOT:
        return NOTE_CRYPTO
    return f"{series.source} · {series.session}"


def crypto_asset_id(symbol: str) -> str:
    return f"binance:spot:{str(symbol).strip().upper()}"


def crypto_spec(symbol: str, timeframe: str) -> SeriesSpec:
    sym = str(symbol).strip().upper()
    return SeriesSpec(
        asset_id=crypto_asset_id(sym),
        symbol=sym,
        asset_class=CLASS_CRYPTO,
        source=SOURCE_SPOT,
        session=SESSION_24X7,
        adjustment=ADJ_NA,
        timeframe=str(timeframe).strip().lower(),
    )


def equity_spec(
    asset_id: str,
    symbol: str,
    asset_class: str,
    timeframe: str,
    adjustment: str = ADJ_ADJUSTED,
) -> SeriesSpec:
    return SeriesSpec(
        asset_id=asset_id,
        symbol=str(symbol).strip().upper(),
        asset_class=asset_class,
        source=SOURCE_EQUITY,
        session=SESSION_RTH,
        adjustment=adjustment,
        timeframe=str(timeframe).strip().lower(),
    )


def legacy_spec(symbol: str, timeframe: str, source: str) -> SeriesSpec:
    """Série de provedor legado (Stooq, Yahoo...): nunca se mistura com a Binance."""

    src = str(source or "").strip().lower()
    sym = str(symbol).strip().upper()
    return SeriesSpec(
        asset_id=f"legacy:{src}:{sym}",
        symbol=sym,
        asset_class=CLASS_STOCK,
        source=src,
        session=SESSION_RTH,
        adjustment=ADJ_RAW,
        timeframe=str(timeframe).strip().lower(),
    )


def legacy_source_label(source: str) -> str:
    """Valor gravado em ``market_ohlcv.source`` (compatibilidade com leituras antigas)."""

    return "ccxt" if source == SOURCE_SPOT else source


def timeframe_delta(timeframe: str) -> timedelta:
    try:
        return TIMEFRAME_DELTA[timeframe]
    except KeyError:
        raise SeriesNotSupported(f"Timeframe {timeframe} não suportado.") from None


def to_utc(value: Any) -> pd.Timestamp | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return ts


def iso(value: Any) -> str | None:
    ts = to_utc(value)
    if ts is None:
        return None
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")
