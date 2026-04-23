from __future__ import annotations

import logging
import os
import random
import threading
import time
from datetime import UTC, datetime, timedelta
from typing import Any

import pandas as pd
from requests.exceptions import RequestException

from app.config import get_settings
from app.services.ohlcv_storage import SUPPORTED_OHLCV_TIMEFRAMES, MarketOhlcvRepository
from app.services.market_data_providers import (
    CCXT_SOURCE,
    STOOQ_SOURCE,
    get_market_data_provider,
    resolve_data_source_for_symbol,
)
from app.services.ohlcv_backfill_store import (
    OhlcvBackfillStore,
    _default_job_state,
    get_backfill_store,
)

logger = logging.getLogger(__name__)

_WINDOW_YEAR_DAYS = 365
_MAX_RETRIES = 4
_LOOKBACK_TF_SECONDS = {
    "1m": 60,
    "5m": 60,
    "15m": 60,
    "1h": 120,
    "4h": 120,
    "1d": 60 * 60,
}
_TIMEFRAME_INTERVAL_SECONDS = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
}


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _to_iso(value: datetime | None = None) -> str:
    return (value or _utc_now()).isoformat()


def _normalize_symbol(value: str) -> str:
    return str(value or "").strip().upper()


def _normalize_timeframe(value: str) -> str:
    return str(value or "").strip().lower()


def _normalize_timeframes(values: list[str]) -> list[str]:
    normalized = [
        _normalize_timeframe(value) for value in (values or []) if _normalize_timeframe(value)
    ]
    output: list[str] = []
    seen: set[str] = set()
    for timeframe in normalized:
        if timeframe in seen:
            continue
        if timeframe not in SUPPORTED_OHLCV_TIMEFRAMES:
            continue
        seen.add(timeframe)
        output.append(timeframe)
    if not output:
        return ["1d"]
    return output


def _parse_iso(value: str | datetime | None) -> datetime:
    if value is None:
        return _utc_now()
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except Exception:
        return _utc_now()


def _parse_int(value: Any, *, default: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed


def _coerce_status(value: str) -> str:
    return str(value or "").strip().lower() or "pending"


def _invoke_provider_fetch(
    provider: Any,
    *,
    symbol: str,
    timeframe: str,
    since_str: str,
    until_str: str,
    limit: int,
) -> Any:
    fetcher = getattr(provider, "fetch_ohlcv")
    kwargs = {
        "symbol": symbol,
        "timeframe": timeframe,
        "since_str": since_str,
        "until_str": until_str,
        "limit": limit,
    }
    try:
        return fetcher(**kwargs)
    except TypeError as exc:
        fetcher_fn = getattr(fetcher, "__func__", None)
        if fetcher_fn is None:
            raise

        message = str(exc).lower()
        if "positional argument" not in message and "positional arguments" not in message:
            raise

        try:
            return fetcher_fn(**kwargs)
        except TypeError:
            raise exc


def _estimate_total_for_range(start: datetime, end: datetime, timeframe: str) -> int:
    interval = _TIMEFRAME_INTERVAL_SECONDS.get(_normalize_timeframe(timeframe))
    if not interval or interval <= 0:
        return 0
    total = int((end - start).total_seconds() / interval) + 1
    return max(0, total)


def _is_retriable_error(error: BaseException) -> bool:
    message = str(error).lower()
    if any(
        token in message
        for token in (
            "429",
            "temporarily",
            "too many requests",
            "timeout",
            "connection",
            "temporario",
        )
    ):
        return True

    status = getattr(error, "status", None)
    if isinstance(status, int) and 500 <= status < 600:
        return True
    status_code = getattr(error, "status_code", None)
    if isinstance(status_code, int) and (status_code == 429 or 500 <= status_code < 600):
        return True

    return isinstance(error, RequestException)


class OhlcvBackfillService:
    _instance: "OhlcvBackfillService | None" = None
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
        self._store: OhlcvBackfillStore = get_backfill_store()
        self._repo = MarketOhlcvRepository()
        self._jobs_lock = threading.Lock()
        self._scheduler_lock = threading.Lock()
        self._scheduler_stop = threading.Event()
        self._scheduler_thread: threading.Thread | None = None
        self._throttle_lock = threading.Lock()
        self._next_request_time: float | None = None

    @staticmethod
    def _default_symbols() -> list[str]:
        raw_symbols = os.getenv("MARKET_OHLCV_SYMBOLS", "")
        if not raw_symbols.strip():
            return ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]

        normalized: list[str] = []
        seen: set[str] = set()
        for raw in raw_symbols.split(","):
            symbol = _normalize_symbol(raw)
            if not symbol or symbol in seen:
                continue
            seen.add(symbol)
            normalized.append(symbol)
        return normalized or ["BTC/USDT"]

    @staticmethod
    def _default_timeframes() -> list[str]:
        raw = os.getenv("BACKFILL_DEFAULT_TIMEFRAMES", "1d")
        filtered = [
            tf for tf in _normalize_timeframes([part.strip() for part in str(raw).split(",")]) if tf
        ]
        return filtered or ["1d"]

    def _sleep_for_rate_limit(self, max_requests_per_minute: int) -> None:
        max_rpm = _parse_int(max_requests_per_minute, default=60)
        if max_rpm <= 0:
            return

        interval = 60.0 / max_rpm
        with self._throttle_lock:
            now = time.monotonic()
            if self._next_request_time is None:
                self._next_request_time = now
                return
            if now < self._next_request_time:
                time.sleep(self._next_request_time - now)
            self._next_request_time = time.monotonic() + interval

    def _record_event(
        self, job_id: str, message: str, *, level: str = "info", timeframe: str | None = None
    ) -> None:
        payload = {
            "ts": _to_iso(),
            "level": level,
            "timeframe": timeframe,
            "message": message,
        }
        self._store.record_event(job_id, payload)

    def _resolve_job_source(self, symbol: str, requested_source: str | None) -> str:
        if requested_source is not None and str(requested_source).strip():
            # let underlying provider validator enforce constraints
            return resolve_data_source_for_symbol(symbol, requested_source)
        return resolve_data_source_for_symbol(symbol)

    def _refresh_totals(self, job_id: str) -> None:
        job = self._store.get_job(job_id)
        if not job:
            return
        timeframe_states = job.get("timeframe_states") or {}

        processed = 0
        written = 0
        duplicates = 0
        estimated_total = 0
        for state in timeframe_states.values():
            processed += _parse_int(state.get("processed"), default=0)
            written += _parse_int(state.get("written"), default=0)
            duplicates += _parse_int(state.get("duplicates"), default=0)
            estimated_total += _parse_int(state.get("estimated_total"), default=0)

        percent = self._store.calculate_percent(processed, estimated_total or None)
        eta_seconds = self._store.estimate_eta_seconds(
            job.get("started_at"), processed, estimated_total or None
        )
        self._store.update_job(
            job_id,
            processed=processed,
            written=written,
            duplicates=duplicates,
            estimated_total=estimated_total or None,
            percent=percent,
            eta_seconds=eta_seconds,
        )

    def _needs_job(self, symbol: str, timeframes: list[str], history_years: int) -> bool:
        if not self._repo.enabled:
            return False
        now = _utc_now()
        window_start = now - timedelta(
            days=_WINDOW_YEAR_DAYS * _parse_int(history_years, default=2)
        )
        for timeframe in timeframes:
            earliest = self._repo.get_earliest_candle_time(symbol, timeframe)
            if earliest is None:
                return True
            if earliest > window_start:
                return True
        return False

    def _fetch_with_retries(
        self,
        provider,
        symbol: str,
        timeframe: str,
        since: datetime,
        until: datetime,
        limit: int,
        max_requests_per_minute: int,
        max_retries: int,
        job_id: str,
        timeframe_state: dict[str, Any],
    ) -> pd.DataFrame:
        attempt = 0
        max_attempts = max(1, max_retries)
        while True:
            attempt += 1
            self._sleep_for_rate_limit(max_requests_per_minute)

            try:
                return _invoke_provider_fetch(
                    provider,
                    symbol=symbol,
                    timeframe=timeframe,
                    since_str=since.isoformat(),
                    until_str=until.isoformat(),
                    limit=limit,
                )
            except Exception as exc:
                if attempt >= max_attempts or not _is_retriable_error(exc):
                    raise

                timeframe_state["retries"] = (
                    _parse_int(timeframe_state.get("retries"), default=0) + 1
                )
                self._record_event(
                    job_id,
                    f"Retry {attempt}/{max_attempts} em {symbol}/{timeframe}: {exc}",
                    level="warning",
                    timeframe=timeframe,
                )

                backoff = min(30.0, 1.0 * (2 ** (attempt - 1)))
                jitter = random.uniform(0.4, 1.2)
                time.sleep(backoff * jitter)

    def _run_timeframe_backfill(self, job_id: str, timeframe: str, source: str) -> bool:
        job = self._store.get_job(job_id)
        if not job:
            return False

        requested_window = job.get("requested_window") or {}
        window_start = _parse_iso(requested_window.get("start"))
        window_end = _parse_iso(requested_window.get("end"))
        page_size = _parse_int(job.get("page_size"), default=1000)
        max_requests_per_minute = _parse_int(job.get("max_requests_per_minute"), default=60)
        max_retries = _parse_int(job.get("max_retries"), default=_MAX_RETRIES)
        timeframe_states = job.get("timeframe_states") or {}
        state = timeframe_states.get(timeframe)
        if state is None:
            estimate_total = _estimate_total_for_range(window_start, window_end, timeframe)
            state = self._store.build_timeframe_state(
                timeframe, window_start.isoformat(), estimate_total
            )
            timeframe_states[timeframe] = state

        interval_seconds = _TIMEFRAME_INTERVAL_SECONDS.get(_normalize_timeframe(timeframe), 60)
        checkpoint_raw = (
            state.get("checkpoint") or requested_window.get("start") or window_start.isoformat()
        )
        checkpoint = _parse_iso(checkpoint_raw)
        if checkpoint < window_start:
            checkpoint = window_start

        if source == STOOQ_SOURCE and timeframe != "1d":
            state["status"] = "completed"
            state["checkpoint"] = _to_iso(window_end)
            timeframe_states[timeframe] = state
            job = self._store.get_job(job_id) or job
            self._store.update_job(job_id, timeframe_states=timeframe_states)
            return True

        provider = get_market_data_provider(source)
        state["status"] = _coerce_status(state.get("status"))
        state["errors"] = _parse_int(state.get("errors"), default=0)
        state["requests"] = _parse_int(state.get("requests"), default=0)
        state["processed"] = _parse_int(state.get("processed"), default=0)
        state["written"] = _parse_int(state.get("written"), default=0)
        state["duplicates"] = _parse_int(state.get("duplicates"), default=0)
        state["last_error"] = None

        while True:
            job = self._store.get_job(job_id) or job
            if not job:
                return False
            if _coerce_status(job.get("status")) in {"cancelled", "failed"}:
                state["status"] = _coerce_status(job.get("status"))
                timeframe_states[timeframe] = state
                self._store.update_job(job_id, timeframe_states=timeframe_states)
                return False
            if job.get("cancel_requested"):
                state["status"] = "cancelled"
                timeframe_states[timeframe] = state
                self._store.update_job(
                    job_id,
                    status="cancelled",
                    timeframe_states=timeframe_states,
                    last_error="Cancelado pelo operador.",
                )
                return False

            if checkpoint >= window_end:
                state["status"] = "completed"
                state["checkpoint"] = _to_iso(checkpoint)
                timeframe_states[timeframe] = state
                self._store.update_job(
                    job_id, timeframe_states=timeframe_states, current_timeframe=timeframe
                )
                return True

            try:
                frame = self._fetch_with_retries(
                    provider=provider,
                    symbol=job["symbol"],
                    timeframe=timeframe,
                    since=checkpoint,
                    until=window_end,
                    limit=page_size,
                    max_requests_per_minute=max_requests_per_minute,
                    max_retries=max_retries,
                    job_id=job_id,
                    timeframe_state=state,
                )
            except Exception as exc:
                state["status"] = "failed"
                state["errors"] += 1
                state["last_error"] = str(exc)
                state["retries"] = _parse_int(state.get("retries"), default=0) + 1
                timeframe_states[timeframe] = state
                self._store.update_job(
                    job_id,
                    status="failed",
                    timeframe_states=timeframe_states,
                    current_timeframe=timeframe,
                    last_error=str(exc),
                )
                self._record_event(
                    job_id,
                    f"Falha permanente em {job['symbol']}/{timeframe} (tentativa {state['errors']}/{max_retries}): {exc}",
                    level="error",
                    timeframe=timeframe,
                )
                self._refresh_totals(job_id)
                return False

            if frame is None or frame.empty:
                state["status"] = "partial_complete" if checkpoint < window_end else "completed"
                state["current_lookback_to"] = _to_iso(checkpoint)
                timeframe_states[timeframe] = state
                self._store.update_job(
                    job_id,
                    timeframe_states=timeframe_states,
                    current_timeframe=timeframe,
                    current_lookback_to=state.get("current_lookback_to"),
                )
                self._record_event(
                    job_id,
                    f"Sem novos candles para {job['symbol']}/{timeframe} a partir de {checkpoint.isoformat()}",
                    level="warning",
                    timeframe=timeframe,
                )
                self._refresh_totals(job_id)
                return state["status"] == "completed"

            if "timestamp_utc" not in frame.columns:
                if frame.index.name == "timestamp_utc":
                    frame = frame.reset_index()
                elif "time" in frame.columns:
                    frame["timestamp_utc"] = pd.to_datetime(
                        frame["time"], utc=True, errors="coerce"
                    )
                else:
                    raise ValueError(
                        "Provider returned invalid dataframe without timestamp_utc/time."
                    )

            normalized = frame.copy()
            normalized["timestamp_utc"] = pd.to_datetime(
                normalized["timestamp_utc"], utc=True, errors="coerce"
            )
            normalized = normalized.dropna(subset=["timestamp_utc"]).sort_values("timestamp_utc")

            windowed = normalized[
                (normalized["timestamp_utc"] >= pd.Timestamp(window_start))
                & (normalized["timestamp_utc"] <= pd.Timestamp(window_end))
            ]
            if windowed.empty:
                state["status"] = "partial_complete" if checkpoint < window_end else "completed"
                state["current_lookback_to"] = _to_iso(checkpoint)
                timeframe_states[timeframe] = state
                self._store.update_job(
                    job_id,
                    timeframe_states=timeframe_states,
                    current_timeframe=timeframe,
                    current_lookback_to=state.get("current_lookback_to"),
                )
                self._record_event(
                    job_id,
                    f"Janela vazia após filtro para {job['symbol']}/{timeframe}",
                    level="warning",
                    timeframe=timeframe,
                )
                self._refresh_totals(job_id)
                return state["status"] == "completed"

            latest_ts = pd.to_datetime(windowed["timestamp_utc"].iloc[-1]).to_pydatetime()
            if latest_ts.tzinfo is None:
                latest_ts = latest_ts.replace(tzinfo=UTC)
            else:
                latest_ts = latest_ts.astimezone(UTC)

            written, duplicates = self._repo.write_candles(
                job["symbol"],
                timeframe,
                job.get("provider") or provider.source,
                windowed,
                return_metrics=True,
            )
            written = int(written)
            duplicates = int(duplicates)
            received = len(windowed)

            state["status"] = "running"
            state["requests"] += 1
            state["processed"] += received
            state["written"] += written
            state["duplicates"] += duplicates
            state["latest_ingested"] = _to_iso(latest_ts)
            state["checkpoint"] = _to_iso(latest_ts + timedelta(seconds=interval_seconds))
            timeframe_states[timeframe] = state
            checkpoint = _parse_iso(state["checkpoint"])

            self._store.update_job(
                job_id,
                timeframe_states=timeframe_states,
                current_timeframe=timeframe,
                current_lookback_to=state["checkpoint"],
                last_error=None,
            )
            self._record_event(
                job_id,
                f"{job['symbol']}/{timeframe}: lote={received} recebidos, {written} gravados, {duplicates} duplicados",
                timeframe=timeframe,
            )
            self._refresh_totals(job_id)

            if state["checkpoint"] and _parse_iso(state["checkpoint"]) >= window_end:
                state["status"] = "completed"
                timeframe_states[timeframe] = state
                self._store.update_job(
                    job_id, timeframe_states=timeframe_states, current_timeframe=timeframe
                )
                return True

            if received < page_size:
                # Provider returned fewer rows than requested before reaching the requested window end:
                # usually means no more historical window available.
                state["status"] = (
                    "partial_complete"
                    if _parse_iso(state["checkpoint"]) < window_end
                    else "completed"
                )
                timeframe_states[timeframe] = state
                self._store.update_job(
                    job_id,
                    timeframe_states=timeframe_states,
                    current_timeframe=timeframe,
                    current_lookback_to=state["checkpoint"],
                )
                self._refresh_totals(job_id)
                return state["status"] == "completed"

    def _run_job(self, job_id: str) -> None:
        job = self._store.get_job(job_id)
        if not job:
            return

        status = _coerce_status(job.get("status"))
        if status not in {"pending", "retrying"}:
            return

        source = self._resolve_job_source(job["symbol"], job.get("requested_source"))
        self._store.update_job(
            job_id,
            status="running",
            provider=source,
            started_at=_to_iso(),
            cancel_requested=False,
            last_error=None,
            current_timeframe=None,
            attempts=_parse_int(job.get("attempts"), default=0) + 1,
        )
        self._record_event(
            job_id, f"Iniciando backfill de {job['symbol']} via {source}", level="info"
        )
        self._store.update_job(job_id, total_estimate=0)

        job = self._store.get_job(job_id)
        if not job:
            return

        timeframe_states = job.get("timeframe_states") or {}
        all_complete = True
        partial_found = False
        failed = False

        for timeframe in job.get("timeframes", []):
            if self._store.get_job(job_id) is None:
                return
            if _coerce_status(job.get("status")) != "running":
                break

            state = timeframe_states.get(timeframe) or {}
            state_status = _coerce_status(state.get("status"))
            state["status"] = state_status

            checkpoint = _parse_iso(state.get("checkpoint"))
            if checkpoint > datetime.fromtimestamp(0, tz=UTC):
                self._record_event(
                    job_id,
                    f"Retomando {job['symbol']}/{timeframe} em {checkpoint.isoformat()}",
                    timeframe=timeframe,
                    level="info",
                )
            if state_status == "completed":
                continue
            self._store.update_job(job_id, current_timeframe=timeframe)

            result = self._run_timeframe_backfill(job_id=job_id, timeframe=timeframe, source=source)
            job = self._store.get_job(job_id) or job
            if not job:
                return

            state = (job.get("timeframe_states") or {}).get(timeframe) or {}
            new_status = _coerce_status(state.get("status"))
            if new_status == "failed":
                failed = True
                break
            if new_status == "partial_complete":
                partial_found = True
                all_complete = False
            elif new_status in {"pending", "running"}:
                partial_found = True
                all_complete = False

            if new_status == "completed":
                continue

        if failed or _coerce_status(job.get("status")) == "cancelled":
            final_status = (
                "cancelled" if _coerce_status(job.get("status")) == "cancelled" else "failed"
            )
        elif partial_found or not all_complete:
            final_status = "partial_complete"
        else:
            final_status = "completed"

        self._store.update_job(
            job_id,
            status=final_status,
            current_timeframe=None,
            finished_at=_to_iso(),
        )
        self._refresh_totals(job_id)
        self._record_event(job_id, f"Backfill finalizado com status {final_status}", level="info")

    def start_job(
        self,
        symbol: str,
        timeframes: list[str],
        *,
        data_source: str | None = None,
        history_window_years: int = 2,
        page_size: int = 1000,
        max_requests_per_minute: int = 60,
        max_retries: int = _MAX_RETRIES,
    ) -> str:
        normalized_symbol = _normalize_symbol(symbol)
        if not normalized_symbol:
            raise ValueError("symbol is required.")

        normalized_timeframes = _normalize_timeframes(timeframes)
        if not normalized_timeframes:
            raise ValueError("At least one valid timeframe is required.")

        source = self._resolve_job_source(normalized_symbol, data_source)
        now = _utc_now()
        years = max(1, min(10, _parse_int(history_window_years, default=2)))
        requested_window = {
            "start": (now - timedelta(days=_WINDOW_YEAR_DAYS * years)).isoformat(),
            "end": now.isoformat(),
            "history_window_years": years,
        }

        timeframe_states: dict[str, dict[str, Any]] = {}
        for timeframe in normalized_timeframes:
            estimate = _estimate_total_for_range(
                _parse_iso(requested_window["start"]),
                _parse_iso(requested_window["end"]),
                timeframe,
            )
            timeframe_states[timeframe] = self._store.build_timeframe_state(
                timeframe=timeframe,
                checkpoint=requested_window["start"],
                estimated_total=estimate,
            )

        from uuid import uuid4

        job_id = f"backfill-{uuid4().hex}"
        initial = _default_job_state(
            job_id=job_id,
            symbol=normalized_symbol,
            timeframes_state=timeframe_states,
            requested_window=requested_window,
            provider=source,
        )
        initial["requested_source"] = data_source
        initial["page_size"] = _parse_int(page_size, default=1000)
        initial["max_requests_per_minute"] = _parse_int(max_requests_per_minute, default=60)
        initial["max_retries"] = _parse_int(max_retries, default=_MAX_RETRIES)

        self._store.init_job(initial)
        self._record_event(
            job_id,
            f"Job criado para {normalized_symbol} ({', '.join(normalized_timeframes)})",
            level="info",
        )

        with self._jobs_lock:
            threading.Thread(
                target=self._run_job,
                kwargs={"job_id": job_id},
                name=f"ohlcv-backfill-{job_id}",
                daemon=True,
            ).start()

        return job_id

    def request_cancel_job(self, job_id: str) -> bool:
        job = self._store.get_job(job_id)
        if not job:
            return False
        if _coerce_status(job.get("status")) in {"completed", "cancelled", "failed"}:
            return False
        self._store.update_job(
            job_id,
            cancel_requested=True,
            status=(
                "cancelled" if job.get("status") == "pending" else _coerce_status(job.get("status"))
            ),
            finished_at=_to_iso() if job.get("status") == "pending" else None,
            last_error="Cancelamento solicitado.",
        )
        self._record_event(job_id, "Cancelamento solicitado pelo operador.", level="warning")
        return True

    def request_retry_job(self, job_id: str) -> bool:
        job = self._store.get_job(job_id)
        if not job:
            return False

        status = _coerce_status(job.get("status"))
        if status not in {"failed", "partial_complete", "cancelled"}:
            return False

        self._store.update_job(
            job_id,
            status="retrying",
            cancel_requested=False,
            started_at=None,
            finished_at=None,
            attempts=_parse_int(job.get("attempts"), default=0) + 1,
        )
        self._record_event(job_id, "Tentativa de retry solicitada.", level="info")

        with self._jobs_lock:
            threading.Thread(
                target=self._run_job,
                kwargs={"job_id": job_id},
                name=f"ohlcv-backfill-{job_id}",
                daemon=True,
            ).start()
        return True

    def list_jobs(
        self,
        page: int = 1,
        page_size: int = 50,
        status: str | None = None,
        symbol: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        return self._store.list_jobs(
            page=page,
            page_size=page_size,
            status_filter=status,
            symbol_filter=symbol,
        )

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        return self._store.get_job(job_id)

    def run_scheduler_once(self) -> int:
        with self._scheduler_lock:
            if self._store is None:
                return 0

            enabled = os.getenv("BACKFILL_SCHEDULER_ENABLED", "1").strip().lower() not in {
                "0",
                "false",
                "no",
                "off",
            }
            if not enabled:
                return 0

            symbols = [
                value.strip().upper()
                for value in str(os.getenv("BACKFILL_SCHEDULER_SYMBOLS", "")).split(",")
                if value.strip()
            ]
            if not symbols:
                symbols = self._default_symbols()

            timeframes = _normalize_timeframes(
                [
                    part.strip()
                    for part in str(
                        os.getenv(
                            "BACKFILL_SCHEDULER_TIMEFRAMES",
                            ",",
                        )
                    ).split(",")
                    if part.strip()
                ]
            )
            if not timeframes:
                timeframes = self._default_timeframes()

            years = _parse_int(os.getenv("BACKFILL_WINDOW_YEARS", "2"), default=2)
            data_source = os.getenv("BACKFILL_SCHEDULER_DATA_SOURCE") or None
            start_count = 0

            for symbol in symbols:
                if self._store.exists_active_for_symbol(symbol):
                    continue
                if not self._needs_job(symbol, timeframes, years):
                    continue

                try:
                    self.start_job(
                        symbol=symbol,
                        timeframes=timeframes,
                        data_source=data_source,
                        history_window_years=years,
                    )
                    start_count += 1
                except Exception as exc:
                    logger.warning("Could not schedule backfill for %s: %s", symbol, exc)
                    self._record_event(
                        "",
                        f"Falha ao disparar scheduler para {symbol}: {exc}",
                        level="error",
                    )
            return start_count

    def _scheduler_loop(self) -> None:
        interval_seconds = max(
            300,
            _parse_int(os.getenv("BACKFILL_SCHEDULER_INTERVAL_SECONDS"), default=24 * 60 * 60),
        )
        while not self._scheduler_stop.wait(interval_seconds):
            try:
                self.run_scheduler_once()
            except Exception as exc:
                logger.exception("Backfill scheduler loop failed: %s", exc)

    def start_scheduler(self) -> None:
        enabled = os.getenv("BACKFILL_SCHEDULER_ENABLED", "1").strip().lower() not in {
            "0",
            "false",
            "no",
            "off",
        }
        if not enabled:
            return

        if self._scheduler_thread is not None and self._scheduler_thread.is_alive():
            return

        self._scheduler_stop.clear()
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            name="ohlcv-backfill-scheduler",
            daemon=True,
        )
        self._scheduler_thread.start()

    def stop_scheduler(self) -> None:
        self._scheduler_stop.set()
        thread = self._scheduler_thread
        if thread is not None:
            thread.join(timeout=5.0)
            self._scheduler_thread = None


def get_backfill_service() -> OhlcvBackfillService:
    return OhlcvBackfillService()
