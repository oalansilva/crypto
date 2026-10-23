"""Cobertura do histórico por ativo para o seletor (card #1118, decisão 16).

Lê só ``market_series_coverage`` e ``market_series_fetch``: o catálogo nunca
varre a tabela de candles nem dispara coleta. Cripto e ação/ETF usam a mesma
estrutura; o 15m derivado do 5m aparece como linha própria "montado do 5m".
"""

from __future__ import annotations

import json
import logging
from types import SimpleNamespace
from typing import Any, Iterable

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.services.market_history import nyse_calendar as cal
from app.services.market_history.model import (
    ADJ_ADJUSTED,
    ADJ_NA,
    SOURCE_EQUITY,
    SOURCE_SPOT,
    iso,
    series_note,
    to_utc,
)
from app.services.market_history.service import RUNNING_FRESH_SECONDS, inherit_gaps_15m

logger = logging.getLogger(__name__)

TIMEFRAME_ORDER = {"1d": 0, "4h": 1, "1h": 2, "15m": 3, "5m": 4, "1m": 5}
_QUERY = text("""
    SELECT s.asset_id, s.series_id, s.timeframe, s.source, s.adjustment, s.session,
           s.data_version, c.first_candle, c.last_candle, c.candle_count, c.gap_count,
           c.gaps, c.updated_at, c.last_request_since, c.last_request_until,
           f.state, f.pages_done, f.reached_start, f.binance_earliest, f.requested_since,
           f.requested_until, f.requested_at, f.last_error_code, f.last_error,
           f.updated_at AS fetch_updated_at, f.cursor_end_ms
    FROM market_series s
    LEFT JOIN market_series_coverage c ON c.series_id = s.series_id
    LEFT JOIN market_series_fetch f ON f.series_id = s.series_id
    WHERE s.asset_id = ANY(:ids)
      AND s.source IN ('binance_spot', 'binance_equity')
      AND s.adjustment IN ('na', 'adjusted')
    """)

_FAILURE_TEXT = {
    "binance_rate_limited": "limite de requisições da Binance",
    "binance_unavailable": "Binance indisponível",
    "binance_business_error": "a Binance recusou o pedido",
    "binance_format_changed": "formato da Binance mudou",
    "binance_circuit_open": "coleta em pausa por falhas seguidas da Binance",
    "internal_error": "erro interno na coleta",
}


def failure_text(code: str | None) -> str:
    return _FAILURE_TEXT.get(code or "", "falha na coleta")


def _gaps(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return value
    try:
        return json.loads(value or "[]")
    except (TypeError, ValueError):
        return []


def _timeframe_entry(row: Any, now: pd.Timestamp) -> dict[str, Any] | None:
    first = to_utc(row.first_candle)
    last = to_utc(row.last_candle)
    state = row.state or "idle"
    fetch_updated = to_utc(row.fetch_updated_at)
    running = (
        state == "running"
        and fetch_updated is not None
        and (now - fetch_updated).total_seconds() < RUNNING_FRESH_SECONDS
    )
    if first is None and not running and state != "failed":
        return None
    requested_since = to_utc(row.requested_since)
    reached = bool(row.reached_start)
    tolerance = pd.Timedelta(days=5) if row.session != "24x7" else pd.Timedelta(days=1)
    insufficient = bool(
        requested_since is not None
        and first is not None
        and reached
        and first > requested_since + tolerance
    )
    incomplete = (
        bool(
            requested_since is not None
            and first is not None
            and not reached
            and first > requested_since + tolerance
        )
        or state == "paused"
    )
    return {
        "timeframe": row.timeframe,
        "series_id": int(row.series_id),
        "from": iso(first),
        "to": iso(last),
        "candles": int(row.candle_count or 0),
        "gap_count": int(row.gap_count or 0),
        "gaps": _gaps(row.gaps),
        "updated_at": iso(row.updated_at),
        "origin": "native",
        "derived_from": None,
        "data_version": int(row.data_version),
        "state": "collecting" if running else ("failed" if state == "failed" else "idle"),
        "insufficient": insufficient,
        "incomplete": incomplete,
        "pages_done": int(row.pages_done or 0),
        "requested_since": iso(requested_since),
        "requested_until": iso(row.requested_until),
        "requested_at": iso(row.requested_at),
        "starts_at": iso(row.binance_earliest) if reached else None,
        "error_code": row.last_error_code if state == "failed" else None,
        "error": failure_text(row.last_error_code) if state == "failed" else None,
        "error_at": iso(row.fetch_updated_at) if state == "failed" else None,
        "source": row.source,
        "adjustment": row.adjustment,
        "session": row.session,
    }


def _derived_entry(five: dict[str, Any]) -> dict[str, Any]:
    entry = dict(five)
    entry.update(
        {
            "timeframe": "15m",
            "origin": "derived",
            "derived_from": "5m",
            "gap_count": 0,  # herdada do 5m: não soma de novo no resumo (decisão 9)
            "gaps": inherit_gaps_15m(five["gaps"]),
            "rule_version": cal.DERIVED_15M_RULE_VERSION,
        }
    )
    return entry


def summarize(
    asset: Any,
    entries: list[dict[str, Any]],
    *,
    tradable: bool,
) -> dict[str, Any]:
    """Estado e lista por timeframe de um ativo (``history`` do item do catálogo)."""

    equity = asset.asset_class != "crypto"
    ordered = sorted(entries, key=lambda e: TIMEFRAME_ORDER.get(e["timeframe"], 9))
    if equity:
        by_tf = {e["timeframe"]: e for e in ordered}
        if "5m" in by_tf and "15m" not in by_tf:
            ordered.append(_derived_entry(by_tf["5m"]))
            ordered.sort(key=lambda e: TIMEFRAME_ORDER.get(e["timeframe"], 9))
    with_data = [e for e in ordered if e["from"]]
    collecting = next((e for e in ordered if e["state"] == "collecting"), None)
    failed = next((e for e in ordered if e["state"] == "failed"), None)
    native = [e for e in ordered if e["origin"] == "native"]
    note_series = SimpleNamespace(
        source=SOURCE_EQUITY if equity else SOURCE_SPOT,
        adjustment=ADJ_ADJUSTED if equity else ADJ_NA,
        session="rth" if equity else "24x7",
    )
    if collecting is not None:
        status = "collecting"
    elif failed is not None:
        status = "failed"
    elif any(e["insufficient"] or e["incomplete"] for e in with_data):
        status = "partial"
    elif with_data and not tradable:
        status = "frozen"
    elif with_data:
        status = "covered"
    else:
        status = "on_demand" if tradable else "none"
    starts = [e["from"] for e in with_data]
    ends = [e["to"] for e in with_data]
    updates = [e["updated_at"] for e in with_data if e["updated_at"]]
    partial_entry = next((e for e in with_data if e["insufficient"] or e["incomplete"]), None)
    return {
        "status": status,
        "from": min(starts) if starts else None,
        "to": max(ends) if ends else None,
        "updated_at": max(updates) if updates else None,
        "gap_count": sum(e["gap_count"] for e in native if e["from"]),
        "timeframes": ordered,
        "note": series_note(note_series),
        "calendar_timezone": cal.NY.key if equity else None,
        "collecting": (
            {
                "timeframe": collecting["timeframe"],
                "page": collecting["pages_done"] + 1,
                "requested_at": collecting["requested_at"],
            }
            if collecting
            else None
        ),
        "error": (
            {
                "timeframe": failed["timeframe"],
                "code": failed["error_code"],
                "message": failed["error"],
                "at": failed["error_at"],
            }
            if failed
            else None
        ),
        "partial": (
            {
                "timeframe": partial_entry["timeframe"],
                "requested_since": partial_entry["requested_since"],
                "starts_at": partial_entry["starts_at"] or partial_entry["from"],
                "insufficient": partial_entry["insufficient"],
            }
            if partial_entry
            else None
        ),
    }


def coverage_for_assets(
    db: Any, assets: Iterable[Any], *, now: pd.Timestamp | None = None
) -> dict[str, dict[str, Any]]:
    """``asset_id`` -> ``history`` para os ativos pedidos; vazio se as tabelas não existem."""

    rows = list(assets)
    if not rows:
        return {}
    ids = [a.asset_id for a in rows]
    now = now or pd.Timestamp.now(tz="UTC")
    try:
        with db.begin_nested():
            fetched = db.execute(_QUERY, {"ids": ids}).all()
    except SQLAlchemyError:
        logger.info("Cobertura indisponível: tabelas do histórico ainda não existem")
        return {}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in fetched:
        entry = _timeframe_entry(row, now)
        if entry is not None:
            grouped.setdefault(row.asset_id, []).append(entry)
    out: dict[str, dict[str, Any]] = {}
    for asset in rows:
        entries = grouped.get(asset.asset_id)
        if not entries:
            continue
        out[asset.asset_id] = summarize(asset, entries, tradable=asset.state == "tradable")
    return out
