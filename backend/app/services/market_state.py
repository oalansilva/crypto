"""Estado do mercado, candle fechado e atraso real por série (card #1122, decisões 7 a 9).

- ``open``/``closed``: pregão regular de NY para ação/ETF; a cripto é 24/7 (sempre ``open``).
- ``stale`` (atraso real): falta o candle de um pregão ou bloco que o calendário diz que já fechou,
  passada uma tolerância por tempo gráfico. Fim de semana, feriado, fora do pregão e o candle em
  formação nunca contam. Falha de leitura sem nenhum candle conta.
- ``insufficient``: menos candles fechados do que a análise precisa (estado próprio, nunca atraso).

O episódio de atraso fica em ``monitor_data_health`` por (fonte, ativo): abre, mantém e fecha.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Iterable

import pandas as pd

from app.services.market_history import nyse_calendar as cal

logger = logging.getLogger(__name__)

# Tolerância para a publicação do candle (P3: calibrar com dado real do DEV).
STALE_TOLERANCE = {
    "15m": pd.Timedelta(minutes=10),
    "1h": pd.Timedelta(minutes=15),
    "4h": pd.Timedelta(minutes=30),
    "1d": pd.Timedelta(minutes=90),
}
DEFAULT_TOLERANCE = pd.Timedelta(minutes=90)
# Detalhe de um tempo gráfico que ninguém mais lê deixa de segurar o episódio.
DETAIL_TTL = timedelta(days=3)


def _utc(value: Any) -> pd.Timestamp | None:
    if value is None:
        return None
    try:
        ts = pd.Timestamp(value)
    except Exception:
        return None
    if pd.isna(ts):
        return None
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


def _iso(value: Any) -> str | None:
    ts = _utc(value)
    return ts.isoformat() if ts is not None else None


def is_equity_source(data_source: str | None) -> bool:
    return str(data_source or "").strip().lower() in {"binance_equity", "stooq"}


def tolerance_for(timeframe: str) -> pd.Timedelta:
    return STALE_TOLERANCE.get(str(timeframe or "").strip().lower(), DEFAULT_TOLERANCE)


def last_closed_start(equity: bool, timeframe: str, now: Any) -> pd.Timestamp:
    """Início do último candle fechado pelo calendário da classe."""

    if equity:
        return cal.last_closed_start(timeframe, now)
    return cal.crypto_last_closed_start(timeframe, now)


def _session_day(ts: pd.Timestamp) -> Any:
    """Data do pregão de um candle 1d (Binance: meia-noite de NY; Stooq: meia-noite UTC)."""

    return (ts + pd.Timedelta(hours=12)).tz_convert(cal.NY).date()


def candle_reached(
    equity: bool, timeframe: str, last: pd.Timestamp, expected: pd.Timestamp
) -> bool:
    if equity and str(timeframe).lower() == "1d":
        return _session_day(last) >= _session_day(expected)
    return last >= expected


def cut_to_closed(frame: pd.DataFrame, timeframe: str, now: Any) -> pd.DataFrame:
    """Série de ação/ETF só com candles fechados pelo calendário (sem candle em formação)."""

    if frame is None or frame.empty:
        return frame
    try:
        limit = cal.last_closed_start(timeframe, now)
    except Exception:
        return frame
    index = pd.DatetimeIndex(frame.index)
    index = index.tz_localize("UTC") if index.tz is None else index.tz_convert("UTC")
    if str(timeframe).lower() == "1d":
        limit_day = _session_day(limit)
        keep = [_session_day(ts) <= limit_day for ts in index]
    else:
        keep = list(index <= limit)
    return frame.loc[keep]


@dataclass
class SeriesCheck:
    data_source: str
    symbol: str
    timeframe: str
    stale: bool
    last_candle: pd.Timestamp | None
    expected_candle: pd.Timestamp | None
    error: str | None = None

    def detail(self, now: datetime) -> dict[str, Any]:
        return {
            "stale": self.stale,
            "last_candle": _iso(self.last_candle),
            "expected_candle": _iso(self.expected_candle),
            "error": self.error,
            "checked_at": now.isoformat(),
        }


def check_series(
    *,
    data_source: str,
    symbol: str,
    timeframe: str,
    last_candle: Any,
    now: Any,
    error: str | None = None,
) -> SeriesCheck:
    """Atraso real de uma série: último recebido < último fechado em ``now − tolerância``."""

    equity = is_equity_source(data_source)
    at = _utc(now) or pd.Timestamp.now(tz="UTC")
    tf = str(timeframe or "1d").strip().lower()
    try:
        expected = last_closed_start(equity, tf, at - tolerance_for(tf))
    except Exception as exc:  # calendário fora do ar: nunca inventa atraso
        logger.warning("market_state: calendário indisponível para %s %s: %s", symbol, tf, exc)
        return SeriesCheck(data_source, symbol, tf, False, _utc(last_candle), None, None)
    last = _utc(last_candle)
    if last is None:
        return SeriesCheck(data_source, symbol, tf, True, None, expected, error or "no_candles")
    stale = not candle_reached(equity, tf, last, expected)
    return SeriesCheck(data_source, symbol, tf, stale, last, expected, None)


def session_state(equity: bool, now: Any) -> dict[str, Any]:
    if not equity:
        return {
            "state": "open",
            "reason": "24x7",
            "closes_at": None,
            "next_open": None,
            "early_close": False,
            "timezone": None,
        }
    try:
        status = cal.market_status(now)
    except Exception:
        return {
            "state": "open",
            "reason": "unknown",
            "closes_at": None,
            "next_open": None,
            "early_close": False,
            "timezone": "America/New_York",
        }
    return {
        "state": status.state,
        "reason": status.reason,
        "closes_at": _iso(status.closes_at),
        "next_open": _iso(status.next_open),
        "early_close": bool(status.early_close),
        "timezone": "America/New_York",
    }


def build_market_state(
    *,
    equity: bool,
    now: Any,
    series: SeriesCheck | None,
    episode: dict[str, Any] | None = None,
    available: int | None = None,
    required: int | None = None,
) -> dict[str, Any]:
    """``market_state`` da linha do Monitor: ``open|closed|stale|insufficient`` e o contexto."""

    base = session_state(equity, now)
    session = base["state"]
    out = {
        **base,
        "session_state": session,
        "last_candle": _iso(series.last_candle) if series else None,
        "expected_candle": _iso(series.expected_candle) if series else None,
        "stale_since": None,
        "episode_id": None,
        "available": available,
        "required": required,
    }
    asset_stale = bool(episode and episode.get("state") == "stale")
    if asset_stale or (series is not None and series.stale):
        detail = series
        out["state"] = "stale"
        out["reason"] = "fetch_failed" if (detail and detail.error) else "delay"
        if episode:
            out["stale_since"] = episode.get("stale_since")
            out["episode_id"] = episode.get("episode_id")
            stale_detail = episode.get("stale_detail") or {}
            if not (detail and detail.stale) and stale_detail:
                out["last_candle"] = stale_detail.get("last_candle")
                out["expected_candle"] = stale_detail.get("expected_candle")
        return out
    if available is not None and required and available < required:
        out["state"] = "insufficient"
        out["reason"] = "insufficient"
    return out


# ---------------------------------------------------------------- episódio por (fonte, ativo)


@dataclass
class EpisodeUpdate:
    data_source: str
    symbol: str
    state: str
    episode_id: str | None
    stale_since: str | None
    opened: bool = False
    closed: bool = False
    stale_detail: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "data_source": self.data_source,
            "symbol": self.symbol,
            "state": self.state,
            "episode_id": self.episode_id,
            "stale_since": self.stale_since,
            "opened": self.opened,
            "closed": self.closed,
            "stale_detail": self.stale_detail,
        }


def update_data_health(
    db: Any, checks: Iterable[SeriesCheck], *, now: datetime | None = None
) -> dict[tuple[str, str], EpisodeUpdate]:
    """Abre, mantém ou fecha o episódio de cada (fonte, ativo) a partir das séries lidas agora.

    O ativo fica ``stale`` se qualquer série monitorada dele está; o episódio fecha quando todas
    normalizam. Recuperação nunca gera mensagem (só fecha o episódio).
    """

    from app.models import MonitorDataHealth

    now = now or datetime.utcnow()
    grouped: dict[tuple[str, str], list[SeriesCheck]] = {}
    for check in checks:
        grouped.setdefault((check.data_source, check.symbol), []).append(check)
    out: dict[tuple[str, str], EpisodeUpdate] = {}
    for (source, symbol), items in grouped.items():
        row = (
            db.query(MonitorDataHealth)
            .filter(MonitorDataHealth.data_source == source, MonitorDataHealth.symbol == symbol)
            .first()
        )
        detail = dict((row.detail_json or {}) if row is not None else {})
        for item in items:
            detail[item.timeframe] = item.detail(now)
        cutoff = now - DETAIL_TTL
        for tf in list(detail):
            checked = detail[tf].get("checked_at") if isinstance(detail[tf], dict) else None
            try:
                if checked and datetime.fromisoformat(str(checked)) < cutoff:
                    detail.pop(tf, None)
            except ValueError:
                detail.pop(tf, None)
        stale_tfs = [tf for tf, d in detail.items() if isinstance(d, dict) and d.get("stale")]
        stale = bool(stale_tfs)
        stale_detail = detail[stale_tfs[0]] if stale else {}
        if row is None:
            row = MonitorDataHealth(data_source=source, symbol=symbol, state="ok")
            db.add(row)
        opened = closed = False
        if stale and row.state != "stale":
            row.state = "stale"
            row.stale_since = now
            row.episode_id = uuid.uuid4().hex
            opened = True
        elif not stale and row.state == "stale":
            row.state = "ok"
            closed = True
        row.detail_json = detail
        row.updated_at = now
        out[(source, symbol)] = EpisodeUpdate(
            data_source=source,
            symbol=symbol,
            state=row.state,
            episode_id=row.episode_id if row.state == "stale" else None,
            stale_since=(
                row.stale_since.isoformat() if row.state == "stale" and row.stale_since else None
            ),
            opened=opened,
            closed=closed,
            stale_detail=stale_detail,
        )
    db.commit()
    return out
