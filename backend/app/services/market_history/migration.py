"""Migração da cripto já guardada para a autoridade única (card #1118, plano de migração).

Passos (cada um idempotente, sem tocar no legado até a troca de nomes):

1. tira a política de retenção de 2 anos, se existir (Timescale);
2. copia ``market_ohlcv`` (legado) para ``market_ohlcv_v2`` (série ``binance_spot``,
   ``24x7``, ajuste "não se aplica");
3. importa do cache Parquet só os candles que faltam; divergências entre as duas
   cópias são registradas e vale o valor da tabela;
4. confere por série: contagem, primeiro e último candle e soma de fechamento;
5. troca os nomes numa transação (``market_ohlcv`` -> ``market_ohlcv_legacy``) só se
   a conferência passar e a divergência ficar abaixo do limite (0,01% por série).

``rollback`` desfaz a troca de nomes. Nada aqui reinicia serviço nem apaga o legado.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from psycopg2 import extras as psycopg2_extras
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.services.market_history import store
from app.services.market_history.model import (
    SOURCE_SPOT,
    legacy_source_label,
)
from app.services.market_history.compat import spec_for_legacy
from app.services.market_history.schema import (
    LEGACY_OHLCV_TABLE,
    LIVE_OHLCV_TABLE,
    STAGING_OHLCV_TABLE,
    configure_timescale,
    has_table,
    ohlcv_table_is_new_shape,
    remove_retention_policy,
)

logger = logging.getLogger(__name__)

DIVERGENCE_LIMIT = 0.0001  # 0,01% dos candles comparados de uma série
TOLERANCE = 1e-9
PARQUET_TIMEFRAMES = ("1m", "5m", "15m", "1h", "4h", "1d")
_FILE_RE = re.compile(
    r"^(?P<base>[A-Z0-9]+)_(?P<quote>[A-Z0-9]+)_(?P<tf>1m|5m|15m|1h|4h|1d)\.parquet$"
)
INSERT_PAGE = 5000


@dataclass
class SeriesOutcome:
    symbol: str
    timeframe: str
    series_id: int | None = None
    legacy_rows: int = 0
    copied: int = 0
    parquet_rows: int = 0
    parquet_imported: int = 0
    compared: int = 0
    divergences: int = 0
    first_candle: str | None = None
    last_candle: str | None = None
    close_sum_expected: float | None = None
    close_sum_actual: float | None = None
    ok: bool = True
    problems: list[str] = field(default_factory=list)

    @property
    def divergence_rate(self) -> float:
        return self.divergences / self.compared if self.compared else 0.0


@dataclass
class MigrationReport:
    started_at: str
    execute: bool
    timescale: dict[str, bool] = field(default_factory=dict)
    retention_removed: bool = False
    series: list[SeriesOutcome] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)
    swapped: bool = False
    divergence_limit: float = DIVERGENCE_LIMIT
    divergences_sample: list[dict[str, Any]] = field(default_factory=list)

    @property
    def totals(self) -> dict[str, int]:
        return {
            "series": len(self.series),
            "legacy_rows": sum(s.legacy_rows for s in self.series),
            "copied": sum(s.copied for s in self.series),
            "parquet_imported": sum(s.parquet_imported for s in self.series),
            "divergences": sum(s.divergences for s in self.series),
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at,
            "execute": self.execute,
            "timescale": self.timescale,
            "retention_removed": self.retention_removed,
            "swapped": self.swapped,
            "blocked": self.blocked,
            "divergence_limit": self.divergence_limit,
            "totals": self.totals,
            "series": [asdict(s) | {"divergence_rate": s.divergence_rate} for s in self.series],
            "divergences_sample": self.divergences_sample,
        }


def parse_parquet_name(name: str) -> tuple[str, str] | None:
    match = _FILE_RE.match(name)
    if not match:
        return None
    return f"{match['base']}/{match['quote']}", match["tf"]


def _legacy_series(conn) -> list[tuple[str, str, str, int]]:
    rows = conn.execute(
        text(
            f"SELECT symbol, timeframe, source, count(*) FROM {LIVE_OHLCV_TABLE} "
            "GROUP BY symbol, timeframe, source ORDER BY symbol, timeframe, source"
        )
    ).all()
    return [(r[0], r[1], r[2], int(r[3])) for r in rows]


def _read_parquet(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    if "timestamp" in frame.columns:
        times = pd.to_datetime(frame["timestamp"], unit="ms", utc=True)
    else:
        times = pd.to_datetime(frame["timestamp_utc"], utc=True)
    out = pd.DataFrame(
        {
            c: pd.to_numeric(frame[c], errors="coerce").to_numpy()
            for c in ("open", "high", "low", "close", "volume")
        },
        index=pd.DatetimeIndex(times.to_numpy(), name="candle_time"),
    )
    out = out.dropna(subset=["open", "high", "low", "close"])
    out["volume"] = out["volume"].fillna(0.0)
    out = out[~out.index.duplicated(keep="last")].sort_index()
    return out


def _insert_frame(conn, series, frame: pd.DataFrame, source: str) -> int:
    if frame.empty:
        return 0
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
            source,
        )
        for ts, o, h, l, c, v in zip(
            frame.index,
            frame["open"].tolist(),
            frame["high"].tolist(),
            frame["low"].tolist(),
            frame["close"].tolist(),
            frame["volume"].tolist(),
        )
    ]
    sql = (
        f"INSERT INTO {STAGING_OHLCV_TABLE} "
        "(series_id, candle_time, open, high, low, close, volume, symbol, timeframe, source) "
        "VALUES %s ON CONFLICT (series_id, candle_time) DO NOTHING"
    )
    cur = conn.connection.cursor()
    inserted = 0
    try:
        for start in range(0, len(rows), INSERT_PAGE):
            chunk = rows[start : start + INSERT_PAGE]
            psycopg2_extras.execute_values(cur, sql, chunk, page_size=len(chunk))
            inserted += max(0, cur.rowcount)
    finally:
        cur.close()
    return inserted


def _table_frame(conn, series_id: int, start=None, end=None) -> pd.DataFrame:
    where = "series_id = :s"
    params: dict[str, Any] = {"s": series_id}
    if start is not None:
        where += " AND candle_time >= :a"
        params["a"] = start.to_pydatetime()
    if end is not None:
        where += " AND candle_time <= :b"
        params["b"] = end.to_pydatetime()
    rows = conn.execute(
        text(
            f"SELECT candle_time, open, high, low, close, volume FROM {STAGING_OHLCV_TABLE} "
            f"WHERE {where} ORDER BY candle_time"
        ),
        params,
    ).all()
    return store.rows_to_frame(rows)


def _compare(existing: pd.DataFrame, parquet: pd.DataFrame) -> tuple[int, list[dict[str, Any]]]:
    common = existing.index.intersection(parquet.index)
    if len(common) == 0:
        return 0, []
    a = existing.loc[common]
    b = parquet.loc[common]
    bad = np.zeros(len(common), dtype=bool)
    for column in ("open", "high", "low", "close", "volume"):
        bad |= ~np.isclose(a[column].to_numpy(), b[column].to_numpy(), rtol=TOLERANCE, atol=0.0)
    samples = []
    for ts in common[bad][:5]:
        samples.append(
            {
                "candle_time": ts.isoformat(),
                "table": {c: float(a.at[ts, c]) for c in a.columns},
                "parquet": {c: float(b.at[ts, c]) for c in b.columns},
            }
        )
    return int(bad.sum()), samples


def migrate_series(
    engine: Engine,
    symbol: str,
    timeframe: str,
    sources: list[str],
    legacy_rows: int,
    parquet_path: Path | None,
    report: MigrationReport,
    *,
    execute: bool,
) -> SeriesOutcome:
    outcome = SeriesOutcome(symbol=symbol, timeframe=timeframe, legacy_rows=legacy_rows)
    parquet = _read_parquet(parquet_path) if parquet_path and parquet_path.exists() else None
    outcome.parquet_rows = 0 if parquet is None else len(parquet)
    spec = spec_for_legacy(symbol, timeframe, sources[0] if sources else "ccxt")
    if not execute:
        outcome.first_candle = None
        return outcome
    legacy_source = legacy_source_label(spec.source)
    with engine.begin() as conn:
        series = store.get_or_create_series(conn, spec)
        outcome.series_id = series.series_id
        # 1) cópia do legado (idempotente)
        copied = conn.execute(
            text(
                f"INSERT INTO {STAGING_OHLCV_TABLE} "
                "(series_id, candle_time, open, high, low, close, volume, symbol, timeframe, source) "
                "SELECT :sid, candle_time, open, high, low, close, volume, symbol, timeframe, source "
                f"FROM {LIVE_OHLCV_TABLE} WHERE symbol = :sym AND timeframe = :tf "
                "ON CONFLICT (series_id, candle_time) DO NOTHING"
            ),
            {"sid": series.series_id, "sym": symbol, "tf": timeframe},
        ).rowcount
        outcome.copied = int(copied)
        # Esperado = legado + o que só o Parquet tem. Calculado das duas fontes (não do que esta
        # execução importou), para a conferência valer também na repetição idempotente.
        legacy_count, legacy_sum = conn.execute(
            text(
                f"SELECT count(*), COALESCE(sum(close), 0) FROM {LIVE_OHLCV_TABLE} "
                "WHERE symbol = :sym AND timeframe = :tf"
            ),
            {"sym": symbol, "tf": timeframe},
        ).one()
        expected_sum = float(legacy_sum or 0)
        expected_rows = int(legacy_count)
        # 2) Parquet: só o que falta; divergência registrada, vale a tabela
        if parquet is not None and not parquet.empty:
            existing = _table_frame(
                conn, series.series_id, parquet.index.min(), parquet.index.max()
            )
            compared, samples = _compare(existing, parquet)
            outcome.compared = len(existing.index.intersection(parquet.index))
            outcome.divergences = compared
            for sample in samples:
                if len(report.divergences_sample) < 200:
                    report.divergences_sample.append(
                        {"symbol": symbol, "timeframe": timeframe, **sample}
                    )
            missing = parquet[~parquet.index.isin(existing.index)]
            outcome.parquet_imported = _insert_frame(conn, series, missing, legacy_source)
            legacy_times = pd.DatetimeIndex(
                pd.to_datetime(
                    [
                        r[0]
                        for r in conn.execute(
                            text(
                                f"SELECT candle_time FROM {LIVE_OHLCV_TABLE} "
                                "WHERE symbol = :sym AND timeframe = :tf"
                            ),
                            {"sym": symbol, "tf": timeframe},
                        )
                    ],
                    utc=True,
                )
            )
            only_in_parquet = parquet[~parquet.index.isin(legacy_times)]
            expected_rows += len(only_in_parquet)
            expected_sum += float(only_in_parquet["close"].sum())
        # 3) conferência por série
        first, last, count = store.stored_extent(conn, series.series_id)
        actual_sum = float(
            conn.execute(
                text(
                    f"SELECT COALESCE(sum(close), 0) FROM {STAGING_OHLCV_TABLE} WHERE series_id = :s"
                ),
                {"s": series.series_id},
            ).scalar()
            or 0
        )
        outcome.first_candle = first.isoformat() if first else None
        outcome.last_candle = last.isoformat() if last else None
        outcome.close_sum_expected = expected_sum
        outcome.close_sum_actual = actual_sum
        if count != expected_rows:
            outcome.ok = False
            outcome.problems.append(f"contagem {count} difere do esperado {expected_rows}")
        if not np.isclose(actual_sum, expected_sum, rtol=1e-9, atol=1e-6):
            outcome.ok = False
            outcome.problems.append("soma de fechamento difere")
        if outcome.divergence_rate > report.divergence_limit:
            outcome.ok = False
            outcome.problems.append(
                f"divergência {outcome.divergence_rate:.4%} acima do limite {report.divergence_limit:.2%}"
            )
        store.recompute_coverage(conn, series)
    return outcome


def swap_tables(engine: Engine) -> None:
    """Troca de nomes reversível, numa transação com a tabela legada travada."""

    with engine.begin() as conn:
        if ohlcv_table_is_new_shape(conn, LIVE_OHLCV_TABLE):
            raise RuntimeError("market_ohlcv já é a tabela nova.")
        if not has_table(conn, STAGING_OHLCV_TABLE):
            raise RuntimeError("market_ohlcv_v2 não existe.")
        conn.execute(text(f"LOCK TABLE {LIVE_OHLCV_TABLE} IN ACCESS EXCLUSIVE MODE"))
        for old, new in (
            ("market_ohlcv_pkey", "market_ohlcv_legacy_pkey"),
            (
                "uq_market_ohlcv_symbol_timeframe_candle_time",
                "uq_market_ohlcv_legacy_symbol_timeframe_candle_time",
            ),
            (
                "idx_market_ohlcv_symbol_timeframe_time",
                "idx_market_ohlcv_legacy_symbol_timeframe_time",
            ),
            (
                "idx_market_ohlcv_symbol_timeframe_source",
                "idx_market_ohlcv_legacy_symbol_timeframe_source",
            ),
        ):
            conn.execute(text(f"ALTER INDEX IF EXISTS {old} RENAME TO {new}"))
        conn.execute(text(f"ALTER TABLE {LIVE_OHLCV_TABLE} RENAME TO {LEGACY_OHLCV_TABLE}"))
        conn.execute(text(f"ALTER TABLE {STAGING_OHLCV_TABLE} RENAME TO {LIVE_OHLCV_TABLE}"))
        conn.execute(
            text(
                f"ALTER INDEX IF EXISTS {STAGING_OHLCV_TABLE}_pkey RENAME TO {LIVE_OHLCV_TABLE}_pkey"
            )
        )
        conn.execute(
            text(
                f"ALTER INDEX IF EXISTS idx_{STAGING_OHLCV_TABLE}_symbol_timeframe_time "
                f"RENAME TO idx_{LIVE_OHLCV_TABLE}_symbol_timeframe_time"
            )
        )
    store.reset_table_cache()


def rollback_swap(engine: Engine) -> None:
    """Volta os nomes: ``market_ohlcv`` (nova) -> ``market_ohlcv_v2``; legado reassume o nome."""

    with engine.begin() as conn:
        if not ohlcv_table_is_new_shape(conn, LIVE_OHLCV_TABLE) or not has_table(
            conn, LEGACY_OHLCV_TABLE
        ):
            raise RuntimeError("Nada a reverter: não há troca feita (ou o legado já foi removido).")
        conn.execute(text(f"LOCK TABLE {LIVE_OHLCV_TABLE} IN ACCESS EXCLUSIVE MODE"))
        conn.execute(
            text(
                f"ALTER INDEX IF EXISTS {LIVE_OHLCV_TABLE}_pkey RENAME TO {STAGING_OHLCV_TABLE}_pkey"
            )
        )
        conn.execute(
            text(
                f"ALTER INDEX IF EXISTS idx_{LIVE_OHLCV_TABLE}_symbol_timeframe_time "
                f"RENAME TO idx_{STAGING_OHLCV_TABLE}_symbol_timeframe_time"
            )
        )
        conn.execute(text(f"ALTER TABLE {LIVE_OHLCV_TABLE} RENAME TO {STAGING_OHLCV_TABLE}"))
        conn.execute(text(f"ALTER TABLE {LEGACY_OHLCV_TABLE} RENAME TO {LIVE_OHLCV_TABLE}"))
        for new, old in (
            ("market_ohlcv_pkey", "market_ohlcv_legacy_pkey"),
            (
                "uq_market_ohlcv_symbol_timeframe_candle_time",
                "uq_market_ohlcv_legacy_symbol_timeframe_candle_time",
            ),
            (
                "idx_market_ohlcv_symbol_timeframe_time",
                "idx_market_ohlcv_legacy_symbol_timeframe_time",
            ),
            (
                "idx_market_ohlcv_symbol_timeframe_source",
                "idx_market_ohlcv_legacy_symbol_timeframe_source",
            ),
        ):
            conn.execute(text(f"ALTER INDEX IF EXISTS {old} RENAME TO {new}"))
    store.reset_table_cache()


def run_migration(
    engine: Engine,
    *,
    parquet_dir: Path | None,
    execute: bool = False,
    swap: bool = False,
    only: set[tuple[str, str]] | None = None,
    divergence_limit: float = DIVERGENCE_LIMIT,
    progress: Callable[[str], None] | None = None,
) -> MigrationReport:
    report = MigrationReport(
        started_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        execute=execute,
        divergence_limit=divergence_limit,
    )
    say = progress or (lambda msg: None)
    with engine.begin() as conn:
        if ohlcv_table_is_new_shape(conn, LIVE_OHLCV_TABLE):
            report.blocked.append("market_ohlcv já tem identidade de série: nada a migrar.")
            return report
        if not has_table(conn, LIVE_OHLCV_TABLE):
            report.blocked.append("market_ohlcv (legado) não existe.")
            return report
        if not has_table(conn, STAGING_OHLCV_TABLE) or not has_table(conn, "market_series"):
            report.blocked.append(
                "Faltam market_ohlcv_v2/market_series: aplique a revisão Alembic 20261023_0001."
            )
            return report
        legacy = _legacy_series(conn)
        if execute:
            # Retenção sai antes de qualquer cópia (passo 3 do plano de migração).
            report.retention_removed = remove_retention_policy(conn, LIVE_OHLCV_TABLE)
    pairs: dict[tuple[str, str], list[str]] = {}
    rows: dict[tuple[str, str], int] = {}
    for symbol, timeframe, source, count in legacy:
        pairs.setdefault((symbol, timeframe), []).append(source)
        rows[(symbol, timeframe)] = rows.get((symbol, timeframe), 0) + count
    parquet_files: dict[tuple[str, str], Path] = {}
    if parquet_dir and parquet_dir.exists():
        for path in sorted(parquet_dir.glob("*.parquet")):
            parsed = parse_parquet_name(path.name)
            if parsed and parsed[1] in PARQUET_TIMEFRAMES:
                parquet_files[parsed] = path
    keys = sorted(set(pairs) | set(parquet_files))
    if only:
        keys = [k for k in keys if k in only]
    for index, (symbol, timeframe) in enumerate(keys, 1):
        outcome = migrate_series(
            engine,
            symbol,
            timeframe,
            pairs.get((symbol, timeframe), ["ccxt"]),
            rows.get((symbol, timeframe), 0),
            parquet_files.get((symbol, timeframe)),
            report,
            execute=execute,
        )
        report.series.append(outcome)
        if index % 100 == 0:
            say(f"{index}/{len(keys)} séries")
    if execute:
        # Hypertable/compressão da tabela nova, caso a revisão tenha rodado sem a extensão.
        with engine.begin() as conn:
            report.timescale = configure_timescale(conn, STAGING_OHLCV_TABLE)
        failing = [s for s in report.series if not s.ok]
        if failing:
            report.blocked.append(
                f"{len(failing)} série(s) não passaram na conferência; a chave não vira."
            )
        if swap and not failing:
            swap_tables(engine)
            report.swapped = True
        elif swap:
            report.blocked.append("Troca de nomes não feita.")
    return report
