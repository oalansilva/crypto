from __future__ import annotations

import logging
import os
import sys
import fcntl
import json
import time
from datetime import datetime, timezone
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
REPO_ROOT = BACKEND_ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.services.ohlcv_storage import run_ohlcv_ingestion_once
from app.services.runtime_status import candle_writer_lock_path, candle_writer_state_path


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_state(payload: dict) -> None:
    path = candle_writer_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(f"{path.suffix}.tmp")
    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    tmp_path.replace(path)


def _state_payload(
    *,
    status: str,
    started_at: str,
    finished_at: str | None = None,
    runs: int = 0,
    duration_seconds: float | None = None,
    error: str | None = None,
) -> dict:
    payload = {
        "status": status,
        "pid": os.getpid(),
        "started_at": started_at,
        "finished_at": finished_at,
        "runs": runs,
        "lock_path": str(candle_writer_lock_path()),
    }
    if duration_seconds is not None:
        payload["duration_seconds"] = round(duration_seconds, 3)
    if error:
        payload["error"] = error
    return payload


def main() -> int:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    started_at = _utc_now()
    started_monotonic = time.monotonic()
    lock_path = candle_writer_lock_path()
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    with lock_path.open("a+", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            finished_at = _utc_now()
            _write_state(
                _state_payload(
                    status="skipped_lock_held",
                    started_at=started_at,
                    finished_at=finished_at,
                    runs=0,
                    duration_seconds=time.monotonic() - started_monotonic,
                )
            )
            print("canonical_candle_writer_skipped=lock_held")
            return 0

        lock_file.seek(0)
        lock_file.truncate()
        lock_file.write(f"pid={os.getpid()} started_at={started_at}\n")
        lock_file.flush()
        _write_state(_state_payload(status="running", started_at=started_at))

        try:
            runs = run_ohlcv_ingestion_once()
        except Exception as exc:
            finished_at = _utc_now()
            _write_state(
                _state_payload(
                    status="failed",
                    started_at=started_at,
                    finished_at=finished_at,
                    runs=0,
                    duration_seconds=time.monotonic() - started_monotonic,
                    error=str(exc),
                )
            )
            raise

        finished_at = _utc_now()
        _write_state(
            _state_payload(
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                runs=runs,
                duration_seconds=time.monotonic() - started_monotonic,
            )
        )
        print(f"canonical_candle_writer_runs={runs}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
