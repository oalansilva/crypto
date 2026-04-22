from __future__ import annotations

import logging
import os
import json
from collections import defaultdict, deque
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd
from sqlalchemy import bindparam, text

from app.database import DB_URL, engine
from app.services.market_data_providers import (
    CCXT_SOURCE,
    STOOQ_SOURCE,
    get_market_data_provider,
    resolve_data_source_for_symbol,
)

logger = logging.getLogger(__name__)

DEFAULT_INGESTION_TIMEFRAMES = ["1m", "5m", "1h", "4h", "1d"]
SUPPORTED_OHLCV_TIMEFRAMES = {"1m", "5m", "15m", "1h", "4h", "1d"}

_TIMEFRAME_TO_INTERVAL = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
}

_TIMEFRAME_LOOKBACK = {
    "1m": timedelta(hours=36),
    "5m": timedelta(days=3),
    "15m": timedelta(days=7),
    "1h": timedelta(days=45),
    "4h": timedelta(days=180),
    "1d": timedelta(days=540),
}

_INGESTION_POLL_SECONDS = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
    "1d": 21600,
}
_INDEX_ASSERTION_ENABLED = os.getenv("MARKET_OHLCV_ASSERT_INDEX_PLAN", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
_INGESTION_LAG_ALERT_SECONDS = {
    timeframe: int(seconds) * 6
    for timeframe, seconds in [
        ("1m", _INGESTION_POLL_SECONDS["1m"]),
        ("5m", _INGESTION_POLL_SECONDS["5m"]),
        ("15m", _INGESTION_POLL_SECONDS["15m"]),
        ("1h", _INGESTION_POLL_SECONDS["1h"]),
        ("4h", _INGESTION_POLL_SECONDS["4h"]),
        ("1d", _INGESTION_POLL_SECONDS["1d"]),
    ]
}


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    idx = int((len(sorted_values) - 1) * pct)
    return float(sorted_values[idx])


class OhlcvStorageMetrics:
    """Minimal in-memory metrics used for ingestion and query observability."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._query_latency_seconds = deque(maxlen=5000)
        self._insert_lag_seconds = deque(maxlen=5000)
        self._rows_written = 0
        self._rows_received = 0
        self._rows_duplicate = 0
        self._stale_seconds_by_timeframe: dict[str, deque[float]] = defaultdict(
            lambda: deque(maxlen=5000)
        )

    def record_write(self, symbol: str, timeframe: str, rows_received: int, rows_duplicate: int, lag_seconds: float | None) -> None:
        with self._lock:
            self._rows_written += int(rows_received)
            self._rows_received += int(rows_received)
            self._rows_duplicate += int(rows_duplicate)
            if lag_seconds is not None:
                self._insert_lag_seconds.append(float(lag_seconds))
                self._stale_seconds_by_timeframe[_normalize_timeframe(timeframe)].append(
                    float(lag_seconds)
                )

    def record_query_latency(self, seconds: float) -> None:
        with self._lock:
            self._query_latency_seconds.append(float(seconds))

    def duplicate_rows(self) -> int:
        with self._lock:
            return int(self._rows_duplicate)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "ingest": {
                    "rows_written": self._rows_written,
                    "rows_received": self._rows_received,
                    "duplicates_skipped": self._rows_duplicate,
                    "lag_seconds": {
                        "p50": _percentile(list(self._insert_lag_seconds), 0.50),
                        "p95": _percentile(list(self._insert_lag_seconds), 0.95),
                        "p99": _percentile(list(self._insert_lag_seconds), 0.99),
                    },
                },
                "query": {
                    "latency_seconds": {
                        "p50": _percentile(list(self._query_latency_seconds), 0.50),
                        "p95": _percentile(list(self._query_latency_seconds), 0.95),
                        "p99": _percentile(list(self._query_latency_seconds), 0.99),
                    }
                },
            }


_METRICS = OhlcvStorageMetrics()


def _normalize_symbol(value: str) -> str:
    return str(value or "").strip().upper()


def _normalize_timeframe(value: str) -> str:
    return str(value or "").strip().lower()


def _to_utc_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    parsed = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.to_pydatetime() if isinstance(parsed, pd.Timestamp) else None


def _to_float(value: Any) -> float | None:
    parsed = pd.to_numeric(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return float(parsed)


def _walk_plan_uses_index(node: Any, required_index: str) -> bool:
    if not isinstance(node, dict):
        return False

    node_type = str(node.get("Node Type", ""))
    index_name = str(node.get("Index Name", ""))
    if required_index in index_name and node_type in {"Index Scan", "Index Only Scan", "Bitmap Index Scan"}:
        return True

    plans = node.get("Plans")
    if isinstance(plans, list):
        for child in plans:
            if _walk_plan_uses_index(child, required_index):
                return True
    return False


class MarketOhlcvRepository:
    def __init__(self) -> None:
        self._enabled = bool(DB_URL) and not DB_URL.startswith("sqlite:")

    @property
    def enabled(self) -> bool:
        return self._enabled

    def get_latest_candle_time(self, symbol: str, timeframe: str) -> datetime | None:
        if not self.enabled:
            return None

        normalized_symbol = _normalize_symbol(symbol)
        normalized_timeframe = _normalize_timeframe(timeframe)
        with engine.begin() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT MAX(candle_time) AS candle_time
                    FROM market_ohlcv
                    WHERE symbol = :symbol
                      AND timeframe = :timeframe
                    """
                ),
                {"symbol": normalized_symbol, "timeframe": normalized_timeframe},
            ).fetchone()

        if not row or row[0] is None:
            return None

        value = row[0]
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)

        return _to_utc_datetime(value)

    @staticmethod
    def _read_plan_uses_timeframe_index(plan_text: Any, required_index: str = "idx_market_ohlcv_symbol_timeframe_time") -> bool:
        if not plan_text:
            return False

        if isinstance(plan_text, str):
            try:
                plan_text = json.loads(plan_text)
            except Exception:
                return required_index in plan_text

        if isinstance(plan_text, list):
            nodes = plan_text
        else:
            nodes = [plan_text]

        for node in nodes:
            if not isinstance(node, dict):
                continue

            plan = node.get("Plan", node)
            if isinstance(plan, dict):
                candidates = [plan]
            elif isinstance(plan, list):
                candidates = plan
            elif isinstance(plan, str):
                if required_index in plan:
                    return True
                continue
            else:
                continue

            for entry in candidates:
                if not isinstance(entry, dict):
                    continue
                if any(
                    field in str(entry.get("Index Name", ""))
                    for field in (required_index, "Index")
                ):
                    if str(entry.get("Node Type", "")) in {"Index Scan", "Index Only Scan", "Bitmap Index Scan"}:
                        return True
                if _walk_plan_uses_index(entry, required_index):
                    return True
        return False

    def read_recent_candles(
        self, symbol: str, timeframe: str, limit: int
    ) -> list[dict[str, Any]]:
        if not self.enabled:
            return []

        normalized_symbol = _normalize_symbol(symbol)
        normalized_timeframe = _normalize_timeframe(timeframe)
        start = time.perf_counter()
        with engine.begin() as conn:
            if _INDEX_ASSERTION_ENABLED:
                try:
                    explain_sql = """
                        EXPLAIN (FORMAT JSON)
                        SELECT candle_time, open, high, low, close, volume, source
                        FROM market_ohlcv
                        WHERE symbol = :symbol
                          AND timeframe = :timeframe
                        ORDER BY candle_time DESC
                        LIMIT :limit
                    """
                    plan_row = conn.execute(
                        text(explain_sql),
                        {
                            "symbol": normalized_symbol,
                            "timeframe": normalized_timeframe,
                            "limit": int(limit),
                        },
                    ).scalar()
                    if not self._read_plan_uses_timeframe_index(plan_row):
                        logger.warning(
                            "Index plan check failed for market_ohlcv read",
                            extra={
                                "event": "ohlcv_index_plan_check",
                                "symbol": normalized_symbol,
                                "timeframe": normalized_timeframe,
                                "sql": "SELECT ... ORDER BY candle_time DESC LIMIT :limit",
                                "plan": plan_row,
                            },
                        )
                except Exception as exc:
                    logger.warning(
                        "Could not run plan check for market_ohlcv query",
                        extra={"event": "ohlcv_plan_check_error", "error": str(exc)},
                    )

            rows = conn.execute(
                text(
                    """
                    SELECT candle_time, open, high, low, close, volume, source
                    FROM market_ohlcv
                    WHERE symbol = :symbol
                      AND timeframe = :timeframe
                    ORDER BY candle_time DESC
                    LIMIT :limit
                    """
                ),
                {
                    "symbol": normalized_symbol,
                    "timeframe": normalized_timeframe,
                    "limit": int(limit),
                },
            ).mappings().all()

        candles: list[dict[str, Any]] = []
        for row in rows:
            candle_time = row["candle_time"]
            if not isinstance(candle_time, datetime):
                parsed = _to_utc_datetime(candle_time)
                if parsed is None:
                    continue
                candle_time = parsed

            candles.append(
                {
                    "timestamp_utc": candle_time.isoformat(),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"] or 0.0),
                    "source": row["source"],
                }
            )

        elapsed = time.perf_counter() - start
        _METRICS.record_query_latency(elapsed)
        return list(reversed(candles))

    def write_candles(
        self,
        symbol: str,
        timeframe: str,
        source: str,
        df: pd.DataFrame,
    ) -> int:
        if not self.enabled:
            return 0

        if df is None or df.empty:
            return 0

        normalized_symbol = _normalize_symbol(symbol)
        normalized_timeframe = _normalize_timeframe(timeframe)
        normalized_source = str(source or "").strip().lower() or CCXT_SOURCE

        rows_to_write: list[dict[str, Any]] = []
        frame = df
        if frame.index.name == "timestamp_utc" and "timestamp_utc" not in frame.columns:
            frame = frame.reset_index()

        if "timestamp_utc" not in frame.columns:
            raise ValueError("Dataframe missing timestamp_utc")

        for _, row in frame.iterrows():
            timestamp = _to_utc_datetime(row.get("timestamp_utc"))
            if timestamp is None:
                continue

            open_value = _to_float(row.get("open"))
            high_value = _to_float(row.get("high"))
            low_value = _to_float(row.get("low"))
            close_value = _to_float(row.get("close"))
            volume_value = _to_float(row.get("volume")) or 0.0

            if any(v is None for v in (open_value, high_value, low_value, close_value)):
                continue

            rows_to_write.append(
                {
                    "symbol": normalized_symbol,
                    "timeframe": normalized_timeframe,
                    "candle_time": timestamp,
                    "open": open_value,
                    "high": high_value,
                    "low": low_value,
                    "close": close_value,
                    "volume": volume_value,
                    "source": normalized_source,
                }
            )

        deduped = []
        seen_timestamps: set[int] = set()
        for row in rows_to_write:
            ts_key = int(row["candle_time"].timestamp() * 1_000)
            if ts_key in seen_timestamps:
                continue
            seen_timestamps.add(ts_key)
            deduped.append(row)
        rows_to_write = deduped

        if not rows_to_write:
            return 0

        rows_duplicate = 0
        insert_lag_seconds: float | None = None
        if rows_to_write:
            max_ts = max(row["candle_time"] for row in rows_to_write)
            if isinstance(max_ts, datetime):
                now = datetime.now(timezone.utc)
                if max_ts.tzinfo is None:
                    max_ts = max_ts.replace(tzinfo=timezone.utc)
                insert_lag_seconds = (now - max_ts).total_seconds()

        with engine.begin() as conn:
            existing_query = text(
                """
                SELECT COUNT(*)
                FROM market_ohlcv
                WHERE symbol = :symbol
                  AND timeframe = :timeframe
                  AND candle_time IN :candle_times
                """
            ).bindparams(bindparam("candle_times", expanding=True))
            rows_duplicate = int(
                conn.execute(
                    existing_query,
                    {
                        "symbol": normalized_symbol,
                        "timeframe": normalized_timeframe,
                        "candle_times": [r["candle_time"] for r in rows_to_write],
                    },
                ).scalar()
                or 0
            )

            conn.execute(
                text(
                    """
                    INSERT INTO market_ohlcv
                        (symbol, timeframe, candle_time, open, high, low, close, volume, source, created_at)
                    VALUES
                        (:symbol, :timeframe, :candle_time, :open, :high, :low, :close, :volume, :source, NOW())
                    ON CONFLICT (symbol, timeframe, candle_time)
                    DO UPDATE SET
                        source = EXCLUDED.source,
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume,
                        created_at = NOW()
                    """
                ),
                rows_to_write,
            )

        _METRICS.record_write(
            normalized_symbol,
            normalized_timeframe,
            rows_received=len(rows_to_write),
            rows_duplicate=rows_duplicate,
            lag_seconds=insert_lag_seconds,
        )
        return len(rows_to_write)

    def get_metrics(self) -> dict[str, Any]:
        return _METRICS.snapshot()


class OhlcvIngestionService:
    _instance: "OhlcvIngestionService | None" = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._repo = MarketOhlcvRepository()
        self._timeframes = self._resolve_timeframes()
        self._symbols = self._resolve_symbols()

    def _resolve_symbols(self) -> list[str]:
        raw_symbols = os.getenv("MARKET_OHLCV_SYMBOLS", "")
        if raw_symbols:
            symbols = [token.strip() for token in raw_symbols.split(",") if token.strip()]
            symbols = [token.upper() for token in symbols]
            if symbols:
                return symbols

        return [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "BNB/USDT",
            "XRP/USDT",
        ]

    def _resolve_timeframes(self) -> list[str]:
        raw = os.getenv("MARKET_OHLCV_TIMEFRAMES", ",".join(DEFAULT_INGESTION_TIMEFRAMES))
        parts = [part.strip() for part in str(raw).split(",") if part.strip()]
        filtered = [
            part for part in parts if _normalize_timeframe(part) in SUPPORTED_OHLCV_TIMEFRAMES
        ]
        if not filtered:
            return [*DEFAULT_INGESTION_TIMEFRAMES]
        return sorted(dict.fromkeys(_normalize_timeframe(part) for part in filtered))

    @staticmethod
    def _is_enabled() -> bool:
        enabled = os.getenv("MARKET_OHLCV_INGESTION_ENABLED", "1").strip().lower()
        return enabled not in {"0", "false", "no", "off"}

    @staticmethod
    def _timeframe_interval_seconds(timeframe: str) -> float:
        normalized = _normalize_timeframe(timeframe)
        seconds = _INGESTION_POLL_SECONDS.get(normalized)
        if seconds is None:
            return 3600.0
        return float(seconds)

    @staticmethod
    def _timeframe_overlap(timeframe: str) -> timedelta:
        normalized = _normalize_timeframe(timeframe)
        return _TIMEFRAME_TO_INTERVAL.get(normalized, timedelta(hours=1))

    def _lookback_for_timeframe(self, timeframe: str) -> timedelta:
        normalized = _normalize_timeframe(timeframe)
        return _TIMEFRAME_LOOKBACK.get(normalized, timedelta(days=30))

    def _resolve_source(self, symbol: str, timeframe: str) -> str:
        source = resolve_data_source_for_symbol(symbol)
        if source == STOOQ_SOURCE and timeframe != "1d":
            return CCXT_SOURCE
        return source

    def _resolve_since(self, symbol: str, timeframe: str) -> datetime:
        latest = self._repo.get_latest_candle_time(symbol, timeframe)
        now = datetime.now(timezone.utc)
        if latest is None:
            return now - self._lookback_for_timeframe(timeframe)

        return latest - self._timeframe_overlap(timeframe)

    def _fetch_provider_df(self, symbol: str, timeframe: str, source: str, since: datetime) -> pd.DataFrame:
        provider = get_market_data_provider(source)

        try:
            return provider.fetch_ohlcv(
                symbol,
                timeframe,
                since_str=since.isoformat(),
                limit=1000,
                full_history_if_empty=False,
            )
        except TypeError:
            return provider.fetch_ohlcv(
                symbol,
                timeframe,
                since_str=since.isoformat(),
                limit=1000,
            )

    def _ingestion_lag_warning_threshold(self, timeframe: str) -> float:
        env_key = f"MARKET_OHLCV_MAX_LAG_SECONDS_{timeframe.upper()}"
        raw = os.getenv(env_key, "").strip().lower()
        if raw:
            try:
                return max(60, int(float(raw)))
            except ValueError:
                pass
        return float(_INGESTION_LAG_ALERT_SECONDS.get(_normalize_timeframe(timeframe), 3600))

    def _ingest_symbol(self, symbol: str, timeframe: str) -> None:
        normalized_symbol = _normalize_symbol(symbol)
        source = self._resolve_source(normalized_symbol, timeframe)

        if source == STOOQ_SOURCE and timeframe != "1d":
            return

        if timeframe == "1d" and source == STOOQ_SOURCE:
            try:
                logger.debug(
                    "Ingesting stooq stock candles for %s [%s]",
                    normalized_symbol,
                    timeframe,
                )
            except Exception:
                pass

        since = self._resolve_since(normalized_symbol, timeframe)
        try:
            df = self._fetch_provider_df(normalized_symbol, timeframe, source, since)
        except Exception as exc:
            logger.debug(
                "Skipping ingest for %s [%s] because fetch failed: %s",
                normalized_symbol,
                timeframe,
                exc,
            )
            return

        if df is None or df.empty:
            return

        try:
            written = self._repo.write_candles(normalized_symbol, timeframe, source, df)
            if written:
                latest = self._repo.get_latest_candle_time(normalized_symbol, timeframe)
                if latest:
                    lag = datetime.now(timezone.utc) - latest
                    threshold = self._ingestion_lag_warning_threshold(timeframe)
                    if lag.total_seconds() > threshold:
                        logger.warning(
                            "Market OHLCV ingestion lag exceeds threshold",
                            extra={
                                "event": "ohlcv_ingestion_lag_alert",
                                "symbol": normalized_symbol,
                                "timeframe": timeframe,
                                "lag_seconds": lag.total_seconds(),
                                "lag_threshold_seconds": threshold,
                            },
                        )
                logger.debug(
                    "Ingested %s candles for %s [%s] from source=%s",
                    written,
                    normalized_symbol,
                    timeframe,
                    source,
                )
        except Exception as exc:
            logger.warning(
                "Failed to write candles for %s [%s]: %s",
                normalized_symbol,
                timeframe,
                exc,
            )

    def _run_loop(self) -> None:
        next_runs = {
            tf: 0.0 for tf in self._timeframes if tf in SUPPORTED_OHLCV_TIMEFRAMES
        }

        while not self._stop_event.is_set():
            now = time.time()
            next_wait: float | None = None

            for timeframe in next_runs:
                if not next_runs[timeframe] or now >= next_runs[timeframe]:
                    try:
                        for symbol in self._symbols:
                            if self._stop_event.is_set():
                                break
                            self._ingest_symbol(symbol, timeframe)
                    except Exception as exc:
                        logger.warning("Ingestion loop error [%s]: %s", timeframe, exc)
                    next_runs[timeframe] = now + self._timeframe_interval_seconds(timeframe)

                remaining = max(0.5, next_runs[timeframe] - now)
                next_wait = remaining if next_wait is None else min(next_wait, remaining)

            if not next_runs:
                next_wait = 5.0

            self._stop_event.wait(timeout=next_wait)

    def start(self) -> None:
        if not self._is_enabled():
            logger.info("[ohlcv] ingestion disabled by MARKET_OHLCV_INGESTION_ENABLED")
            return

        if not self._repo.enabled:
            logger.info("[ohlcv] storage is disabled (sqlite/test); skipping ingestion thread")
            return

        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="ohlcv-ingestion", daemon=True)
        self._thread.start()
        logger.info("[ohlcv] background ingestion started")

    def stop(self) -> None:
        self._stop_event.set()
        thread = self._thread
        if thread is None:
            return

        thread.join(timeout=5.0)
        self._thread = None
        logger.info("[ohlcv] background ingestion stopped")


_INGESTION_SERVICE = OhlcvIngestionService()


def start_ohlcv_ingestion() -> None:
    _INGESTION_SERVICE.start()


def stop_ohlcv_ingestion() -> None:
    _INGESTION_SERVICE.stop()
