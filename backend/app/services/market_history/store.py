"""Acesso ao PostgreSQL: séries, candles, cobertura e estado da coleta (card #1118)."""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime, timezone
from typing import Any, Iterable, Sequence

import pandas as pd
from psycopg2 import extras as psycopg2_extras
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from app.services.market_history import nyse_calendar as cal
from app.services.market_history.model import (
    EQUITY_DERIVED,
    ORIGIN_DERIVED,
    ORIGIN_NATIVE,
    SESSION_24X7,
    HistoryNotReady,
    SeriesRef,
    SeriesSpec,
    timeframe_delta,
)
from app.services.market_history.schema import (
    LIVE_OHLCV_TABLE,
    STAGING_OHLCV_TABLE,
    resolve_ohlcv_table,
)

logger = logging.getLogger(__name__)

MAX_STORED_GAPS = 200
UPSERT_CHUNK = 5000
_table_cache: dict[int, str] = {}
_table_lock = threading.Lock()


def reset_table_cache() -> None:
    with _table_lock:
        _table_cache.clear()


def ohlcv_table(conn: Connection) -> str:
    """Tabela de candles da forma nova; levanta ``HistoryNotReady`` sem ela."""

    key = id(conn.engine)
    with _table_lock:
        cached = _table_cache.get(key)
    if cached:
        return cached
    name = resolve_ohlcv_table(conn)
    if name is None:
        raise HistoryNotReady(
            "A tabela de candles com identidade de série ainda não existe. "
            "Aplique a revisão Alembic e o script de migração antes de ligar MARKET_HISTORY_UNIFIED."
        )
    # Só guarda a tabela definitiva; a de preparo pode ser trocada de nome depois.
    if name == LIVE_OHLCV_TABLE:
        with _table_lock:
            _table_cache[key] = name
    return name


def _ts(value: Any) -> datetime | None:
    if value is None:
        return None
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").to_pydatetime()


# --- Séries ------------------------------------------------------------------


def _series_from_row(row: Any, *, timeframe: str | None = None, derived: bool = False) -> SeriesRef:
    tf = timeframe or row.timeframe
    return SeriesRef(
        series_id=int(row.series_id),
        asset_id=row.asset_id,
        symbol=row.symbol,
        asset_class=row.asset_class,
        source=row.source,
        session=row.session,
        adjustment=row.adjustment,
        timeframe=tf,
        origin=ORIGIN_DERIVED if derived else row.origin,
        data_version=int(row.data_version),
        physical_timeframe=row.timeframe,
    )


_SERIES_COLUMNS = (
    "series_id, asset_id, symbol, asset_class, source, session, adjustment, "
    "timeframe, origin, data_version"
)


def get_or_create_series(conn: Connection, spec: SeriesSpec) -> SeriesRef:
    """Série nativa pela identidade. 15m de ação/ETF devolve a série do 5m, marcada derivada."""

    derived_from = EQUITY_DERIVED.get(spec.timeframe) if spec.source == "binance_equity" else None
    physical_tf = derived_from or spec.timeframe
    conn.execute(
        text(
            "INSERT INTO market_series "
            "(asset_id, symbol, asset_class, source, session, adjustment, timeframe, origin) "
            "VALUES (:asset_id, :symbol, :asset_class, :source, :session, :adjustment, :tf, 'native') "
            "ON CONFLICT ON CONSTRAINT uq_market_series_identity DO NOTHING"
        ),
        {
            "asset_id": spec.asset_id,
            "symbol": spec.symbol,
            "asset_class": spec.asset_class,
            "source": spec.source,
            "session": spec.session,
            "adjustment": spec.adjustment,
            "tf": physical_tf,
        },
    )
    row = conn.execute(
        text(
            f"SELECT {_SERIES_COLUMNS} FROM market_series WHERE asset_id = :a AND source = :s "
            "AND session = :se AND adjustment = :adj AND timeframe = :tf"
        ),
        {
            "a": spec.asset_id,
            "s": spec.source,
            "se": spec.session,
            "adj": spec.adjustment,
            "tf": physical_tf,
        },
    ).one()
    return _series_from_row(row, timeframe=spec.timeframe, derived=derived_from is not None)


def find_series(conn: Connection, spec: SeriesSpec) -> SeriesRef | None:
    derived_from = EQUITY_DERIVED.get(spec.timeframe) if spec.source == "binance_equity" else None
    physical_tf = derived_from or spec.timeframe
    row = conn.execute(
        text(
            f"SELECT {_SERIES_COLUMNS} FROM market_series WHERE asset_id = :a AND source = :s "
            "AND session = :se AND adjustment = :adj AND timeframe = :tf"
        ),
        {
            "a": spec.asset_id,
            "s": spec.source,
            "se": spec.session,
            "adj": spec.adjustment,
            "tf": physical_tf,
        },
    ).first()
    if row is None:
        return None
    return _series_from_row(row, timeframe=spec.timeframe, derived=derived_from is not None)


def refresh_series(conn: Connection, series: SeriesRef) -> SeriesRef:
    """Relê a versão atual (outra coleta pode ter trocado)."""

    row = conn.execute(
        text("SELECT data_version FROM market_series WHERE series_id = :i"),
        {"i": series.series_id},
    ).one()
    return series.with_version(int(row.data_version))


# --- Candles -----------------------------------------------------------------


def upsert_candles(
    conn: Connection,
    series: SeriesRef,
    frame: pd.DataFrame,
    *,
    legacy_source: str,
) -> int:
    """Grava candles (índice UTC; colunas open/high/low/close/volume). Idempotente.

    Devolve quantos candles entraram ou mudaram de fato; linha idêntica não é
    reescrita. Qualquer mudança avança ``content_seq`` (chave do cache Parquet).
    """

    if frame is None or frame.empty:
        return 0
    table = ohlcv_table(conn)
    index = pd.DatetimeIndex(frame.index)
    if index.tz is None:
        index = index.tz_localize("UTC")
    rows = [
        (
            series.series_id,
            ts.to_pydatetime(),
            o,
            h,
            l,
            c,
            v,
            series.symbol,
            series.physical_timeframe,
            legacy_source,
        )
        for ts, o, h, l, c, v in zip(
            index,
            frame["open"].tolist(),
            frame["high"].tolist(),
            frame["low"].tolist(),
            frame["close"].tolist(),
            frame["volume"].tolist(),
        )
    ]
    sql = (
        f"INSERT INTO {table} "
        "(series_id, candle_time, open, high, low, close, volume, symbol, timeframe, source) "
        "VALUES %s "
        "ON CONFLICT (series_id, candle_time) DO UPDATE SET "
        "open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low, "
        "close = EXCLUDED.close, volume = EXCLUDED.volume, created_at = now() "
        f"WHERE ({table}.open, {table}.high, {table}.low, {table}.close, {table}.volume) "
        "IS DISTINCT FROM (EXCLUDED.open, EXCLUDED.high, EXCLUDED.low, EXCLUDED.close, EXCLUDED.volume)"
    )
    affected = 0
    cursor = conn.connection.cursor()
    try:
        for start in range(0, len(rows), UPSERT_CHUNK):
            chunk = rows[start : start + UPSERT_CHUNK]
            psycopg2_extras.execute_values(cursor, sql, chunk, page_size=len(chunk))
            affected += max(0, cursor.rowcount)
    finally:
        cursor.close()
    if affected:
        bump_content_seq(conn, series.series_id, series.data_version)
    return affected


def bump_content_seq(conn: Connection, series_id: int, version: int = 1) -> None:
    conn.execute(
        text(
            "INSERT INTO market_series_coverage (series_id, data_version, content_seq) "
            "VALUES (:s, :v, 1) ON CONFLICT (series_id) DO UPDATE SET "
            "content_seq = market_series_coverage.content_seq + 1"
        ),
        {"s": series_id, "v": version},
    )


def read_frame(
    conn: Connection,
    series_id: int,
    start: Any = None,
    end: Any = None,
    *,
    limit: int | None = None,
) -> pd.DataFrame:
    """Candles da série, ordem crescente. ``limit`` pega os últimos N da janela."""

    table = ohlcv_table(conn)
    where = ["series_id = :sid"]
    params: dict[str, Any] = {"sid": series_id}
    if start is not None:
        where.append("candle_time >= :start")
        params["start"] = _ts(start)
    if end is not None:
        where.append("candle_time <= :end")
        params["end"] = _ts(end)
    clause = " AND ".join(where)
    if limit:
        sql = (
            f"SELECT candle_time, open, high, low, close, volume FROM ("
            f"SELECT candle_time, open, high, low, close, volume FROM {table} WHERE {clause} "
            f"ORDER BY candle_time DESC LIMIT :limit) q ORDER BY candle_time ASC"
        )
        params["limit"] = int(limit)
    else:
        sql = (
            f"SELECT candle_time, open, high, low, close, volume FROM {table} "
            f"WHERE {clause} ORDER BY candle_time ASC"
        )
    rows = conn.execute(text(sql), params).all()
    return rows_to_frame(rows)


def rows_to_frame(rows: Sequence[Any]) -> pd.DataFrame:
    if not rows:
        frame = pd.DataFrame(columns=["open", "high", "low", "close", "volume"], dtype="float64")
        frame.index = pd.DatetimeIndex([], tz="UTC", name="candle_time")
        return frame
    frame = pd.DataFrame(
        {
            "candle_time": pd.to_datetime([r[0] for r in rows], utc=True),
            "open": [float(r[1]) for r in rows],
            "high": [float(r[2]) for r in rows],
            "low": [float(r[3]) for r in rows],
            "close": [float(r[4]) for r in rows],
            "volume": [float(r[5]) for r in rows],
        }
    )
    return frame.set_index("candle_time")


def stored_extent(conn: Connection, series_id: int) -> tuple[datetime | None, datetime | None, int]:
    table = ohlcv_table(conn)
    row = conn.execute(
        text(
            f"SELECT min(candle_time), max(candle_time), count(*) FROM {table} WHERE series_id = :s"
        ),
        {"s": series_id},
    ).one()
    return row[0], row[1], int(row[2])


# --- Cobertura ---------------------------------------------------------------


def _gap_json(start: pd.Timestamp, end: pd.Timestamp, count: int, **extra: Any) -> dict[str, Any]:
    out = {
        "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": int(count),
    }
    out.update(extra)
    return out


def compute_gaps_24x7(conn: Connection, series: SeriesRef) -> list[dict[str, Any]]:
    """Lacunas internas de uma série contínua: salto maior que um candle."""

    table = ohlcv_table(conn)
    step = timeframe_delta(series.physical_timeframe)
    rows = conn.execute(
        text(
            "SELECT candle_time, next_t FROM ("
            f"SELECT candle_time, lead(candle_time) OVER (ORDER BY candle_time) AS next_t "
            f"FROM {table} WHERE series_id = :s) q "
            "WHERE next_t IS NOT NULL AND next_t - candle_time > make_interval(secs => :secs) "
            "ORDER BY candle_time"
        ),
        {"s": series.series_id, "secs": step.total_seconds()},
    ).all()
    gaps: list[dict[str, Any]] = []
    for before, after in rows:
        first = pd.Timestamp(before).tz_convert("UTC") + pd.Timedelta(step)
        last = pd.Timestamp(after).tz_convert("UTC") - pd.Timedelta(step)
        count = int((pd.Timestamp(after) - pd.Timestamp(before)) / pd.Timedelta(step)) - 1
        gaps.append(_gap_json(first, last, count))
    return gaps


def compute_gaps_rth(series: SeriesRef, times: pd.DatetimeIndex) -> list[dict[str, Any]]:
    """Lacunas só dentro do pregão regular: candle esperado pelo calendário que não veio."""

    if len(times) == 0:
        return []
    times = pd.DatetimeIndex(times).sort_values()
    tf = series.physical_timeframe
    expected = cal.expected_candles(tf, times[0], times[-1])
    step = pd.Timedelta(timeframe_delta(tf))
    gaps = []
    for first, last, count in cal.missing_runs(expected, times, step):
        gaps.append(_gap_json(first, last, count))
    return gaps


def recompute_coverage(conn: Connection, series: SeriesRef) -> dict[str, Any]:
    """Recalcula e grava a cobertura da série (início, fim, contagem, lacunas)."""

    first, last, count = stored_extent(conn, series.series_id)
    gaps: list[dict[str, Any]] = []
    if count > 1:
        if series.session == SESSION_24X7:
            gaps = compute_gaps_24x7(conn, series)
        else:
            table = ohlcv_table(conn)
            times = pd.to_datetime(
                [
                    r[0]
                    for r in conn.execute(
                        text(
                            f"SELECT candle_time FROM {table} WHERE series_id = :s "
                            "ORDER BY candle_time"
                        ),
                        {"s": series.series_id},
                    )
                ],
                utc=True,
            )
            gaps = compute_gaps_rth(series, pd.DatetimeIndex(times))
    return save_coverage(conn, series, first, last, count, gaps)


def save_coverage(
    conn: Connection,
    series: SeriesRef,
    first: Any,
    last: Any,
    count: int,
    gaps: list[dict[str, Any]],
    *,
    touch: bool = True,
) -> dict[str, Any]:
    version = int(
        conn.execute(
            text("SELECT data_version FROM market_series WHERE series_id = :i"),
            {"i": series.series_id},
        ).scalar()
        or 1
    )
    gap_count = len(gaps)
    stored = gaps[-MAX_STORED_GAPS:]
    conn.execute(
        text(
            "INSERT INTO market_series_coverage "
            "(series_id, first_candle, last_candle, candle_count, gap_count, gaps, updated_at, data_version) "
            "VALUES (:s, :f, :l, :n, :gc, CAST(:g AS jsonb), now(), :v) "
            "ON CONFLICT (series_id) DO UPDATE SET first_candle = EXCLUDED.first_candle, "
            "last_candle = EXCLUDED.last_candle, candle_count = EXCLUDED.candle_count, "
            "gap_count = EXCLUDED.gap_count, gaps = EXCLUDED.gaps, "
            + ("updated_at = now(), " if touch else "")
            + "data_version = EXCLUDED.data_version"
        ),
        {
            "s": series.series_id,
            "f": _ts(first),
            "l": _ts(last),
            "n": int(count),
            "gc": gap_count,
            "g": json.dumps(stored),
            "v": version,
        },
    )
    return {"gap_count": gap_count}


def extend_coverage_tail(
    conn: Connection, series: SeriesRef, batch_times: pd.DatetimeIndex
) -> None:
    """Cobertura barata para a escrita contínua de cripto.

    Quando o lote só acrescenta ao fim, as lacunas antigas não mudam: soma-se só o
    que o lote trouxe. Lote que toca o passado recalcula tudo.
    """

    current = get_coverage(conn, series.series_id)
    first, last, count = stored_extent(conn, series.series_id)
    batch = pd.DatetimeIndex(batch_times).sort_values()
    if (
        current is None
        or current["last_candle"] is None
        or series.session != SESSION_24X7
        or len(batch) == 0
        or batch[0] < pd.Timestamp(current["last_candle"])
        or current["first_candle"] is None
        or pd.Timestamp(current["first_candle"]) != pd.Timestamp(first)
    ):
        recompute_coverage(conn, series)
        return
    step = pd.Timedelta(timeframe_delta(series.physical_timeframe))
    prev_last = pd.Timestamp(current["last_candle"])
    gaps = list(current["gaps"])
    gap_count = int(current["gap_count"])
    anchor = prev_last
    for ts in batch:
        if ts == anchor:
            continue
        if ts - anchor > step:
            n = int((ts - anchor) / step) - 1
            gaps.append(_gap_json(anchor + step, ts - step, n))
            gap_count += 1
        anchor = ts
    stored = gaps[-MAX_STORED_GAPS:]
    conn.execute(
        text(
            "UPDATE market_series_coverage SET last_candle = :l, first_candle = :f, "
            "candle_count = :n, gap_count = :gc, gaps = CAST(:g AS jsonb), updated_at = now() "
            "WHERE series_id = :s"
        ),
        {
            "s": series.series_id,
            "l": _ts(last),
            "f": _ts(first),
            "n": int(count),
            "gc": gap_count,
            "g": json.dumps(stored),
        },
    )


def get_coverage(conn: Connection, series_id: int) -> dict[str, Any] | None:
    row = conn.execute(
        text(
            "SELECT first_candle, last_candle, candle_count, gap_count, gaps, updated_at, "
            "data_version, last_request_since, last_request_until, insufficient, content_seq "
            "FROM market_series_coverage WHERE series_id = :s"
        ),
        {"s": series_id},
    ).first()
    if row is None:
        return None
    gaps = row.gaps if isinstance(row.gaps, list) else json.loads(row.gaps or "[]")
    return {
        "first_candle": row.first_candle,
        "last_candle": row.last_candle,
        "candle_count": int(row.candle_count),
        "gap_count": int(row.gap_count),
        "gaps": gaps,
        "updated_at": row.updated_at,
        "data_version": int(row.data_version),
        "last_request_since": row.last_request_since,
        "last_request_until": row.last_request_until,
        "insufficient": bool(row.insufficient),
        "content_seq": int(row.content_seq),
    }


def record_request(conn: Connection, series: SeriesRef, since: Any, until: Any) -> None:
    conn.execute(
        text(
            "INSERT INTO market_series_coverage (series_id, last_request_since, last_request_until, data_version) "
            "VALUES (:s, :a, :b, :v) ON CONFLICT (series_id) DO UPDATE SET "
            "last_request_since = EXCLUDED.last_request_since, "
            "last_request_until = EXCLUDED.last_request_until"
        ),
        {"s": series.series_id, "a": _ts(since), "b": _ts(until), "v": series.data_version},
    )


# --- Estado da coleta --------------------------------------------------------

FETCH_FIELDS = (
    "direction",
    "cursor_end_ms",
    "pages_done",
    "state",
    "last_error_code",
    "last_error",
    "attempts",
    "reached_start",
    "binance_earliest",
    "requested_since",
    "requested_until",
    "requested_at",
    "checked_at",
    "started_at",
)


def get_fetch(conn: Connection, series_id: int) -> dict[str, Any] | None:
    row = conn.execute(
        text(
            f"SELECT {', '.join(FETCH_FIELDS)}, updated_at FROM market_series_fetch WHERE series_id = :s"
        ),
        {"s": series_id},
    ).first()
    if row is None:
        return None
    return dict(row._mapping)


def set_fetch(conn: Connection, series_id: int, **fields: Any) -> None:
    unknown = set(fields) - set(FETCH_FIELDS)
    if unknown:
        raise ValueError(f"campos desconhecidos em market_series_fetch: {sorted(unknown)}")
    conn.execute(
        text(
            "INSERT INTO market_series_fetch (series_id) VALUES (:s) ON CONFLICT (series_id) DO NOTHING"
        ),
        {"s": series_id},
    )
    if not fields:
        return
    assignments = ", ".join(f"{name} = :{name}" for name in fields)
    values = {
        k: (
            _ts(v)
            if k
            in {
                "binance_earliest",
                "requested_since",
                "requested_until",
                "requested_at",
                "checked_at",
                "started_at",
            }
            else v
        )
        for k, v in fields.items()
    }
    conn.execute(
        text(
            f"UPDATE market_series_fetch SET {assignments}, updated_at = now() WHERE series_id = :s"
        ),
        {**values, "s": series_id},
    )


def bump_version(conn: Connection, series: SeriesRef) -> SeriesRef:
    version = int(
        conn.execute(
            text(
                "UPDATE market_series SET data_version = data_version + 1 "
                "WHERE series_id = :s RETURNING data_version"
            ),
            {"s": series.series_id},
        ).scalar()
    )
    return series.with_version(version)


def delete_series_candles(conn: Connection, series_id: int) -> int:
    table = ohlcv_table(conn)
    return conn.execute(
        text(f"DELETE FROM {table} WHERE series_id = :s"), {"s": series_id}
    ).rowcount
