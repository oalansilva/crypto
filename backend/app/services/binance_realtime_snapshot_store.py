from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from app.config import get_settings


def _default_snapshot_path() -> Path:
    backend_dir = Path(__file__).resolve().parents[2]
    return backend_dir / "runtime" / "binance_realtime_snapshot.json"


def _setting(name: str, default: Any) -> Any:
    settings = get_settings()
    value = getattr(settings, name, default)
    return default if value is None else value


def get_snapshot_path() -> Path:
    configured = _setting("binance_realtime_snapshot_path", None) or os.getenv(
        "BINANCE_REALTIME_SNAPSHOT_PATH"
    )
    if configured:
        return Path(str(configured))
    return _default_snapshot_path()


def read_snapshot() -> dict[str, Any] | None:
    path = get_snapshot_path()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None

    if not isinstance(payload, dict):
        return None
    return payload


def write_snapshot(payload: dict[str, Any]) -> None:
    path = get_snapshot_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":")),
        encoding="utf-8",
    )
    temp_path.replace(path)


def snapshot_is_fresh(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False

    heartbeat = payload.get("heartbeat_ts")
    if not isinstance(heartbeat, (int, float)):
        return False

    max_age = max(2.0, float(_setting("binance_realtime_snapshot_max_age_seconds", 15.0)))
    now_ts = float(payload.get("now_ts") or 0.0)
    if now_ts <= 0:
        import time

        now_ts = time.time()
    return (now_ts - float(heartbeat)) <= max_age
