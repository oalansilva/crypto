from __future__ import annotations

import fcntl
import json
import os
import re
from pathlib import Path
from typing import Any


def env_flag_enabled(name: str, default: str = "0") -> bool:
    value = os.getenv(name, default).strip().lower()
    return value not in {"", "0", "false", "no", "off"}


def should_start_ohlcv_ingestion() -> bool:
    return env_flag_enabled("MARKET_OHLCV_INGESTION_ENABLED", "0")


def should_start_backfill_scheduler() -> bool:
    return env_flag_enabled("BACKFILL_SCHEDULER_ENABLED", "0")


def should_start_binance_realtime_connector() -> bool:
    return env_flag_enabled("BINANCE_REALTIME_ENABLED", "0")


def candle_writer_lock_path() -> Path:
    return Path(os.getenv("CRYPTO_CANDLES_WRITER_LOCK_FILE", "/tmp/crypto-candle-writer.lock"))


def candle_writer_state_path() -> Path:
    return Path(
        os.getenv("CRYPTO_CANDLES_WRITER_STATE_FILE", "/tmp/crypto-candle-writer-state.json")
    )


def favorite_refresh_state_path() -> Path:
    return Path(
        os.getenv(
            "FAVORITE_BACKTEST_REFRESH_STATE_FILE",
            "/tmp/crypto-favorite-refresh-state.json",
        )
    )


def _safe_text(value: Any, *, limit: int = 200) -> str:
    text = str(value)
    text = re.sub(r"(?i)(password|passwd|secret|token|key)=([^\s]+)", r"\1=<redacted>", text)
    if len(text) > limit:
        return f"{text[:limit]}..."
    return text


def _sanitize_candle_writer_state(data: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "status",
        "pid",
        "started_at",
        "finished_at",
        "runs",
        "duration_seconds",
        "lag_alerts",
    }
    sanitized = {key: data[key] for key in allowed if key in data}
    if "error" in data:
        sanitized["error"] = _safe_text(data["error"])
    return sanitized


def read_candle_writer_state() -> dict[str, Any] | None:
    path = candle_writer_state_path()
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except FileNotFoundError:
        return None
    except Exception as exc:
        return {
            "status": "unreadable",
            "error": _safe_text(exc),
        }
    return _sanitize_candle_writer_state(data) if isinstance(data, dict) else {"status": "invalid"}


def _sanitize_favorite_refresh_state(data: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "status",
        "due",
        "selected",
        "success",
        "failed",
        "skipped_cpu",
        "skipped_limit",
        "cpu_limit_percent",
        "last_cpu_percent",
        "pause_seconds",
        "started_at",
        "completed_at",
        "updated_at",
    }
    sanitized = {key: data[key] for key in allowed if key in data}
    if "reason" in data and data["reason"]:
        sanitized["reason"] = _safe_text(data["reason"])
    return sanitized


def read_favorite_refresh_state() -> dict[str, Any] | None:
    path = favorite_refresh_state_path()
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except FileNotFoundError:
        return None
    except Exception as exc:
        return {
            "status": "unreadable",
            "error": _safe_text(exc),
        }
    return (
        _sanitize_favorite_refresh_state(data) if isinstance(data, dict) else {"status": "invalid"}
    )


def inspect_candle_writer_lock() -> dict[str, Any]:
    path = candle_writer_lock_path()
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "lock_held": False,
        }

    lock_held = False

    try:
        with path.open("r", encoding="utf-8") as handle:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
            except BlockingIOError:
                lock_held = True
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except Exception as exc:
        return {
            "path": str(path),
            "exists": True,
            "lock_held": None,
            "status": "unavailable",
            "error": _safe_text(exc),
        }

    return {
        "path": str(path),
        "exists": True,
        "lock_held": lock_held,
    }


def build_runtime_status_payload(
    *,
    market_ohlcv_enabled: bool,
    market_ohlcv_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    runtime_worker_routines = {
        "signal_monitor": env_flag_enabled("RUN_SIGNAL_MONITOR", "0"),
        "signal_feed_snapshot": env_flag_enabled("RUN_SIGNAL_FEED_SNAPSHOT_WORKER", "0"),
        "favorite_backtest_refresh": env_flag_enabled("RUN_FAVORITE_BACKTEST_REFRESH", "0"),
    }
    runtime_worker_enabled = env_flag_enabled("CRYPTO_RUNTIME_WORKER_ENABLED", "0") and any(
        runtime_worker_routines.values()
    )

    return {
        "status": "ok",
        "service": "crypto-runtime",
        "runtime": {
            "canonical_candles_mode": env_flag_enabled("CRYPTO_CANDLES_CANONICAL_MODE", "1"),
            "direct_fetch_fallback": env_flag_enabled("CRYPTO_CANDLES_DIRECT_FETCH_FALLBACK", "0"),
            "backend_ohlcv_ingestion_enabled": should_start_ohlcv_ingestion(),
            "backfill_scheduler_enabled": should_start_backfill_scheduler(),
            "binance_realtime_connector_enabled": should_start_binance_realtime_connector(),
        },
        "workers": {
            "runtime_worker": {
                "enabled": runtime_worker_enabled,
                "routines": runtime_worker_routines,
            },
            "celery_batch": {
                "enabled": env_flag_enabled("CRYPTO_CELERY_WORKER_ENABLED", "0"),
            },
            "binance_realtime_worker": {
                "enabled": env_flag_enabled("BINANCE_REALTIME_WORKER_ENABLED", "0"),
            },
        },
        "candle_writer": {
            "enabled": env_flag_enabled("CRYPTO_CANDLES_WRITER_ENABLED", "0"),
            "process_role": (
                "writer" if env_flag_enabled("CRYPTO_CANDLES_WRITER_ENABLED", "0") else "observer"
            ),
            "lock": inspect_candle_writer_lock(),
            "latest_run": read_candle_writer_state(),
        },
        "favorite_backtest_refresh": {
            "enabled": runtime_worker_routines["favorite_backtest_refresh"],
            "latest_run": read_favorite_refresh_state(),
            "interval_seconds": int(
                os.getenv("FAVORITE_BACKTEST_REFRESH_INTERVAL_SECONDS", "86400")
            ),
            "loop_seconds": int(os.getenv("FAVORITE_BACKTEST_REFRESH_LOOP_SECONDS", "3600")),
            "max_favorites": int(os.getenv("FAVORITE_BACKTEST_REFRESH_MAX_FAVORITES", "12")),
            "cpu_limit_percent": float(
                os.getenv("FAVORITE_BACKTEST_REFRESH_CPU_LIMIT_PERCENT", "60")
            ),
        },
        "market_ohlcv": {
            "enabled": market_ohlcv_enabled,
            "metrics": market_ohlcv_metrics or {},
        },
    }
