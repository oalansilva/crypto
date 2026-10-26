"""Calendário da NYSE para o pregão regular (card #1118, decisão 8 do design).

Usa ``exchange_calendars`` (XNYS): pregões, feriados, meio-pregões, fuso de Nova
York e horário de verão. Os candles são guardados em UTC; o filtro local é a
autoridade do que entra na série.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Iterable
from zoneinfo import ZoneInfo

import pandas as pd

NY = ZoneInfo("America/New_York")
UTC = timezone.utc

FIVE_MIN = pd.Timedelta(minutes=5)
FIFTEEN_MIN = pd.Timedelta(minutes=15)
# Versão da regra dos tempos derivados do 5m (15m, 1h, 4h): entra na versão deles (design, decisão 9;
# card #1119, decisão 5: a mesma regra de blocos ancorados às 09:30 vale para os três).
DERIVED_15M_RULE_VERSION = 1
DERIVED_RULE_VERSION = DERIVED_15M_RULE_VERSION
# Tempos de ação/ETF montados do 5m, em minutos.
DERIVED_BLOCK_MINUTES = {"15m": 15, "1h": 60, "4h": 240}

_lock = threading.Lock()
_cache: dict[str, object] = {}


class CalendarUnavailable(RuntimeError):
    pass


def _calendar():
    """Calendário XNYS cobrindo de 2000 até um ano à frente (recriado a cada dia)."""

    today = datetime.now(UTC).date()
    key = today.isoformat()
    with _lock:
        if _cache.get("key") == key:
            return _cache["cal"]
        try:
            import exchange_calendars as xc
        except ImportError as exc:  # pragma: no cover - dependência declarada em requirements
            raise CalendarUnavailable(
                "exchange_calendars não está instalado (backend/requirements.txt)"
            ) from exc
        cal = xc.get_calendar(
            "XNYS",
            start=pd.Timestamp("2000-01-01"),
            end=pd.Timestamp(today + timedelta(days=366)),
        )
        _cache["key"] = key
        _cache["cal"] = cal
        _cache.pop("table", None)
        return cal


@dataclass(frozen=True)
class SessionWindow:
    session: date
    open_utc: pd.Timestamp
    close_utc: pd.Timestamp

    @property
    def is_early_close(self) -> bool:
        return self.close_utc.tz_convert(NY).time() < pd.Timestamp("16:00").time()


def session_table() -> pd.DataFrame:
    """DataFrame indexado por data do pregão com ``open_utc`` e ``close_utc``."""

    cal = _calendar()
    with _lock:
        table = _cache.get("table")
        if table is not None:
            return table  # type: ignore[return-value]
    sessions = cal.sessions
    opens = cal.opens.loc[sessions]
    closes = cal.closes.loc[sessions]
    frame = pd.DataFrame(
        {
            "open_utc": (
                pd.DatetimeIndex(opens.values).tz_localize("UTC")
                if opens.dt.tz is None
                else opens.dt.tz_convert("UTC").values
            ),
            "close_utc": (
                pd.DatetimeIndex(closes.values).tz_localize("UTC")
                if closes.dt.tz is None
                else closes.dt.tz_convert("UTC").values
            ),
        },
        index=pd.Index([d.date() for d in sessions], name="session"),
    )
    frame["open_utc"] = pd.to_datetime(frame["open_utc"], utc=True)
    frame["close_utc"] = pd.to_datetime(frame["close_utc"], utc=True)
    with _lock:
        _cache["table"] = frame
    return frame


def ny_date(ts_utc: pd.Series | pd.DatetimeIndex) -> pd.Series:
    """Data local de Nova York de cada instante UTC."""

    index = pd.DatetimeIndex(pd.to_datetime(ts_utc, utc=True))
    return pd.Series([d.date() for d in index.tz_convert(NY)], index=getattr(ts_utc, "index", None))


def sessions_between(start: datetime | pd.Timestamp, end: datetime | pd.Timestamp) -> list[date]:
    table = session_table()
    first = (
        pd.Timestamp(start).tz_convert(NY).date()
        if pd.Timestamp(start).tzinfo
        else pd.Timestamp(start).date()
    )
    last = (
        pd.Timestamp(end).tz_convert(NY).date()
        if pd.Timestamp(end).tzinfo
        else pd.Timestamp(end).date()
    )
    return [d for d in table.index if first <= d <= last]


def session_window(day: date) -> SessionWindow | None:
    table = session_table()
    if day not in table.index:
        return None
    row = table.loc[day]
    return SessionWindow(day, row["open_utc"], row["close_utc"])


def ny_midnight_utc(day: date) -> pd.Timestamp:
    """Meia-noite de Nova York em UTC: o ``t`` do candle 1D da Binance."""

    return pd.Timestamp(datetime(day.year, day.month, day.day, tzinfo=NY)).tz_convert("UTC")


def regular_5m_mask(times_utc: pd.DatetimeIndex) -> pd.Series:
    """True para candles de 5m que começam dentro do pregão regular.

    Antes e depois do pregão (pré, pós, noturno) e dias sem pregão ficam de fora,
    sem virar lacuna.
    """

    idx = pd.DatetimeIndex(pd.to_datetime(times_utc, utc=True))
    if len(idx) == 0:
        return pd.Series([], dtype=bool)
    table = session_table()
    days = pd.Index([d.date() for d in idx.tz_convert(NY)])
    opens = pd.DatetimeIndex(table["open_utc"].reindex(days).values).tz_localize("UTC")
    closes = pd.DatetimeIndex(table["close_utc"].reindex(days).values).tz_localize("UTC")
    ok = (~pd.isna(opens)) & (idx >= opens) & (idx < closes)
    return pd.Series(ok, index=range(len(idx)))


def session_candles_5m(day: date) -> list[pd.Timestamp]:
    window = session_window(day)
    if window is None:
        return []
    out = []
    t = window.open_utc
    while t < window.close_utc:
        out.append(t)
        t = t + FIVE_MIN
    return out


def expected_5m(start: pd.Timestamp, end: pd.Timestamp) -> pd.DatetimeIndex:
    """Candles de 5m esperados com início em ``[start, end]``."""

    pieces: list[pd.Timestamp] = []
    for day in sessions_between(start, end):
        pieces.extend(session_candles_5m(day))
    idx = pd.DatetimeIndex(pieces)
    if len(idx) == 0:
        return idx
    return idx[(idx >= start) & (idx <= end)]


def expected_1d(start: pd.Timestamp, end: pd.Timestamp) -> pd.DatetimeIndex:
    """Candles 1D esperados: um por pregão, ``t`` na meia-noite de Nova York."""

    pieces = [ny_midnight_utc(d) for d in sessions_between(start, end)]
    idx = pd.DatetimeIndex(pieces)
    if len(idx) == 0:
        return idx
    return idx[(idx >= start) & (idx <= end)]


def expected_blocks(minutes: int, start: pd.Timestamp, end: pd.Timestamp) -> pd.DatetimeIndex:
    """Blocos de 15m, 1h ou 4h esperados com início em ``[start, end]``, ancorados às 09:30 de NY.

    Mesma regra de ``derive_blocks``: o bloco nunca atravessa o fechamento (o último bloco do dia,
    mais curto, conta como um bloco). Card #1121 (decisão 5): cobertura da Descoberta.
    """

    block_td = pd.Timedelta(minutes=int(minutes))
    pieces: list[pd.Timestamp] = []
    for day in sessions_between(start, end):
        window = session_window(day)
        if window is None:
            continue
        t = window.open_utc
        while t < window.close_utc:
            pieces.append(t)
            t = t + block_td
    idx = pd.DatetimeIndex(pieces)
    if len(idx) == 0:
        return idx
    return idx[(idx >= start) & (idx <= end)]


def expected_candles(timeframe: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DatetimeIndex:
    if timeframe == "5m":
        return expected_5m(start, end)
    if timeframe == "1d":
        return expected_1d(start, end)
    if timeframe in DERIVED_BLOCK_MINUTES:
        return expected_blocks(DERIVED_BLOCK_MINUTES[timeframe], start, end)
    raise ValueError(f"Calendário de ação/ETF não define candles esperados para {timeframe}.")


def missing_runs(
    expected: pd.DatetimeIndex, present: Iterable[pd.Timestamp], step: pd.Timedelta
) -> list[tuple[pd.Timestamp, pd.Timestamp, int]]:
    """Agrupa candles esperados e ausentes em faixas contíguas.

    Devolve ``(primeiro, último, quantidade)``. "Contíguo" é seguir na lista de
    esperados (um pregão a seguir ao outro não precisa ser adjacente no relógio).
    """

    have = set(pd.DatetimeIndex(list(present)).as_unit("ns").asi8) if present is not None else set()
    runs: list[tuple[pd.Timestamp, pd.Timestamp, int]] = []
    run_first = None
    run_last = None
    count = 0
    for ts in expected:
        if ts.value in have:
            if run_first is not None:
                runs.append((run_first, run_last, count))
                run_first = run_last = None
                count = 0
            continue
        if run_first is None:
            run_first = ts
            count = 0
        run_last = ts
        count += 1
    if run_first is not None:
        runs.append((run_first, run_last, count))
    return runs


@dataclass
class DerivedBlocks:
    candles: pd.DataFrame
    # Blocos incompletos: (início do bloco, fim do bloco, 5m que faltam).
    incomplete: list[tuple[pd.Timestamp, pd.Timestamp, int]]


Derived15m = DerivedBlocks


def derive_15m(df5: pd.DataFrame, *, up_to: pd.Timestamp | None = None) -> DerivedBlocks:
    return derive_blocks(df5, 15, up_to=up_to)


def derive_blocks(
    df5: pd.DataFrame, minutes: int, *, up_to: pd.Timestamp | None = None
) -> DerivedBlocks:
    """Monta 15m, 1h ou 4h do 5m: blocos de ``minutes`` ancorados às 09:30 de Nova York.

    ``df5`` tem índice UTC e colunas open/high/low/close/volume. Um bloco nunca
    atravessa o fechamento (o meio-pregão termina às 13:00): o último bloco do
    dia é mais curto e não é incompleto. Bloco com 5m faltando não vira candle:
    sai em ``incomplete`` como lacuna herdada do 5m. ``up_to`` limita os blocos
    aos que já terminaram (o bloco em andamento não é lacuna).
    """

    minutes = int(minutes)
    if minutes < 5 or minutes % 5:
        raise ValueError(f"Bloco de {minutes} min não é múltiplo de 5m.")
    block_td = pd.Timedelta(minutes=minutes)
    per_block = minutes // 5
    empty = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    if df5 is None or df5.empty:
        empty.index = pd.DatetimeIndex([], tz="UTC", name="candle_time")
        return DerivedBlocks(empty, [])
    df5 = df5.sort_index()
    idx = pd.DatetimeIndex(df5.index)
    if idx.tz is None:
        idx = idx.tz_localize("UTC")
    table = session_table()
    days = [d.date() for d in idx.tz_convert(NY)]
    day_series = pd.Series(days, index=idx)
    opens = table["open_utc"].reindex(day_series.values)
    offset = (idx - pd.DatetimeIndex(opens.values).tz_localize("UTC")) / block_td
    block_no = pd.Series(offset).apply(lambda v: int(v // 1) if pd.notna(v) else -1).values
    work = df5.copy()
    work.index = idx
    work["_day"] = day_series.values
    work["_block"] = block_no
    work = work[work["_block"] >= 0]

    rows = []
    incomplete: list[tuple[pd.Timestamp, pd.Timestamp, int]] = []
    seen_days: dict = {}
    for (day, block), grp in work.groupby(["_day", "_block"], sort=True):
        window = session_window(day)
        if window is None:
            continue
        start = window.open_utc + block_td * int(block)
        if start >= window.close_utc:
            continue
        expected = [
            start + FIVE_MIN * k
            for k in range(per_block)
            if start + FIVE_MIN * k < window.close_utc
        ]
        end = min(start + block_td, window.close_utc)
        got = set(pd.DatetimeIndex(grp.index).as_unit("ns").asi8)
        missing = [t for t in expected if t.value not in got]
        seen_days[day] = max(seen_days.get(day, -1), int(block))
        if missing:
            if up_to is None or end <= up_to:
                incomplete.append((start, end, len(missing)))
            continue
        ordered = grp.sort_index()
        rows.append(
            (
                start,
                float(ordered["open"].iloc[0]),
                float(ordered["high"].max()),
                float(ordered["low"].min()),
                float(ordered["close"].iloc[-1]),
                float(ordered["volume"].sum()),
            )
        )
    # Blocos sem nenhum 5m (buraco inteiro) também são lacuna herdada do 5m.
    for day, last_block in seen_days.items():
        window = session_window(day)
        present_blocks = set(work.loc[work["_day"] == day, "_block"].astype(int).tolist())
        total_blocks = int(((window.close_utc - window.open_utc) / block_td) // 1)
        if (window.close_utc - window.open_utc) % block_td:
            total_blocks += 1
        first_block = min(present_blocks)
        for block in range(first_block, min(last_block, total_blocks - 1) + 1):
            if block in present_blocks:
                continue
            start = window.open_utc + block_td * block
            end = min(start + block_td, window.close_utc)
            if up_to is None or end <= up_to:
                incomplete.append((start, end, per_block))
    incomplete.sort()
    if not rows:
        empty.index = pd.DatetimeIndex([], tz="UTC", name="candle_time")
        return DerivedBlocks(empty, incomplete)
    frame = pd.DataFrame(rows, columns=["candle_time", "open", "high", "low", "close", "volume"])
    frame = frame.set_index(pd.DatetimeIndex(frame.pop("candle_time"), name="candle_time"))
    return DerivedBlocks(frame, incomplete)
