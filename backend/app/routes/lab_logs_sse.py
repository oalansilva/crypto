"""Helpers for Lab per-step logs and SSE streaming."""

from __future__ import annotations

import asyncio
import base64
import contextlib
import hashlib
import hmac
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, Optional

from fastapi import HTTPException

try:
    import aiofiles  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    aiofiles = None


_LOG_LINE_RE = re.compile(r"^\[(?P<timestamp>[^\]]+)\]\s+\[(?P<level>[A-Z]+)\]\s+(?P<message>.*)$")
_SAFE_SEGMENT_RE = re.compile(r"[^A-Za-z0-9._-]+")
_JWT_SEGMENT_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_LOG_DIR = Path("/tmp")
_VALID_LEVELS = {"INFO", "WARN", "ERROR", "DEBUG"}


def _sanitize_segment(raw: str) -> str:
    return _SAFE_SEGMENT_RE.sub("_", str(raw or "").strip()).strip("._") or "unknown"


def get_log_path(run_id: str, step: str) -> Path:
    run_safe = _sanitize_segment(run_id)
    step_safe = _sanitize_segment(step)
    return _LOG_DIR / f"lab_{run_safe}_{step_safe}.log"


def list_log_paths(run_id: str) -> list[Path]:
    run_safe = _sanitize_segment(run_id)
    return sorted(_LOG_DIR.glob(f"lab_{run_safe}_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)


def latest_step_with_logs(run_id: str) -> Optional[str]:
    run_safe = _sanitize_segment(run_id)
    prefix = f"lab_{run_safe}_"
    for path in list_log_paths(run_id):
        name = path.name
        if not name.startswith(prefix) or not name.endswith(".log"):
            continue
        step = name[len(prefix) : -len(".log")]
        if step:
            return step
    return None


def _normalize_level(level: str) -> str:
    value = str(level or "INFO").upper()
    if value == "WARNING":
        return "WARN"
    if value not in _VALID_LEVELS:
        return "INFO"
    return value


def _iso_utc_from_ms(timestamp_ms: Optional[int] = None) -> str:
    ts = int(timestamp_ms if isinstance(timestamp_ms, int) else int(time.time() * 1000))
    dt = datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def append_lab_log_line(
    *,
    run_id: str,
    step: str,
    level: str,
    message: str,
    timestamp_ms: Optional[int] = None,
) -> Path:
    path = get_log_path(run_id, step)
    line = f"[{_iso_utc_from_ms(timestamp_ms)}] [{_normalize_level(level)}] {str(message or '').rstrip()}\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
    return path


class _UtcLogFormatter(logging.Formatter):
    converter = time.gmtime


@contextlib.contextmanager
def capture_step_logs(run_id: str, step: str, *, level: int = logging.INFO):
    """Attach a temporary FileHandler that mirrors combo logs into the Lab step log."""

    log_path = get_log_path(run_id, step)
    root = logging.getLogger()

    for handler in root.handlers:
        if isinstance(handler, logging.FileHandler):
            filename = getattr(handler, "baseFilename", "") or ""
            if Path(filename) == log_path:
                yield log_path
                return

    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(_UtcLogFormatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ"))
    root.addHandler(file_handler)
    try:
        yield log_path
    finally:
        root.removeHandler(file_handler)
        file_handler.close()


def _urlsafe_b64decode(segment: str) -> bytes:
    if not _JWT_SEGMENT_RE.match(segment or ""):
        raise HTTPException(status_code=401, detail="Invalid JWT segment")
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _decode_json_segment(segment: str) -> Dict[str, Any]:
    try:
        return json.loads(_urlsafe_b64decode(segment).decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid JWT payload") from exc


def _extract_token(authorization_header: Optional[str], query_token: Optional[str]) -> str:
    header = str(authorization_header or "").strip()
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return str(query_token or "").strip()


def _validate_time_claims(payload: Dict[str, Any]) -> None:
    now = int(time.time())
    exp = payload.get("exp")
    if exp is not None:
        try:
            if now >= int(exp):
                raise HTTPException(status_code=401, detail="JWT expired")
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="Invalid JWT exp claim") from exc

    nbf = payload.get("nbf")
    if nbf is not None:
        try:
            if now < int(nbf):
                raise HTTPException(status_code=401, detail="JWT not active")
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="Invalid JWT nbf claim") from exc


def _decode_jwt_unverified(token: str) -> Dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Invalid JWT token")
    header = _decode_json_segment(parts[0])
    payload = _decode_json_segment(parts[1])
    if str(header.get("typ") or "JWT").upper() not in ("JWT", "JOSE"):
        raise HTTPException(status_code=401, detail="Invalid JWT header")
    _validate_time_claims(payload)
    return payload


def _decode_jwt_hs256(token: str, secret: str) -> Dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Invalid JWT token")
    header_b64, payload_b64, signature_b64 = parts
    header = _decode_json_segment(header_b64)
    payload = _decode_json_segment(payload_b64)

    alg = str(header.get("alg") or "").upper()
    if alg != "HS256":
        raise HTTPException(status_code=401, detail="Unsupported JWT algorithm")

    signed_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), signed_input, hashlib.sha256).digest()
    actual = _urlsafe_b64decode(signature_b64)
    if not hmac.compare_digest(expected, actual):
        raise HTTPException(status_code=401, detail="Invalid JWT signature")

    _validate_time_claims(payload)
    return payload


def authenticate_log_stream(
    *,
    authorization_header: Optional[str],
    query_token: Optional[str],
) -> Dict[str, Any]:
    """Authenticate log SSE requests.

    If LAB_LOGS_JWT_SECRET is configured, JWT signature is required (HS256).
    Without a secret, auth stays optional for single-tenant environments.
    """

    token = _extract_token(authorization_header, query_token)
    secret = str(os.getenv("LAB_LOGS_JWT_SECRET") or "").strip()

    if secret:
        if not token:
            raise HTTPException(status_code=401, detail="Missing bearer token")
        return _decode_jwt_hs256(token, secret)

    if token:
        # Best-effort parsing to keep the interface JWT-compatible in dev mode.
        return _decode_jwt_unverified(token)

    return {}


def _parse_line(line: str, step: str) -> Dict[str, Any]:
    raw = str(line or "").strip()
    if not raw:
        return {}

    match = _LOG_LINE_RE.match(raw)
    if not match:
        return {
            "timestamp": _iso_utc_from_ms(),
            "level": "INFO",
            "message": raw,
            "step": step,
        }

    return {
        "timestamp": str(match.group("timestamp")),
        "level": _normalize_level(match.group("level")),
        "message": str(match.group("message")),
        "step": step,
    }


def _to_sse(payload: Dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _done_event(status: str) -> str:
    return f"event: done\ndata: {json.dumps({'status': status})}\n\n"


def _is_step_running(run_state: Dict[str, Any], step: str) -> bool:
    status = str((run_state or {}).get("status") or "").strip().lower()
    current_step = str((run_state or {}).get("step") or "").strip()
    return status == "running" and current_step == step


def _read_from_offset_sync(path: Path, offset: int) -> tuple[str, int]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        handle.seek(offset)
        chunk = handle.read()
        new_offset = handle.tell()
    return chunk, new_offset


async def _read_from_offset(path: Path, offset: int) -> tuple[str, int]:
    if aiofiles is not None:
        async with aiofiles.open(path, "r", encoding="utf-8", errors="replace") as handle:
            await handle.seek(offset)
            chunk = await handle.read()
            new_offset = await handle.tell()
        return chunk, new_offset

    # Some constrained runtimes do not allow threadpool workers reliably.
    # Keep a deterministic synchronous fallback when aiofiles is unavailable.
    return _read_from_offset_sync(path, offset)


async def stream_lab_logs(
    run_id: str,
    step: str,
    *,
    run_state_reader: Optional[Callable[[], Dict[str, Any]]] = None,
    poll_interval: float = 0.4,
    idle_timeout: float = 20.0,
    history_lines: int = 300,
) -> AsyncIterator[str]:
    """Tail Lab step logs and emit SSE messages."""

    path = get_log_path(run_id, step)
    if not path.exists():
        raise FileNotFoundError(str(path))

    content, offset = await _read_from_offset(path, 0)
    initial = content.splitlines()
    for line in initial[-history_lines:]:
        payload = _parse_line(line, step)
        if payload:
            yield _to_sse(payload)

    last_activity = time.monotonic()
    while True:
        chunk, new_offset = await _read_from_offset(path, offset)
        offset = new_offset

        if chunk:
            for line in chunk.splitlines():
                payload = _parse_line(line, step)
                if payload:
                    yield _to_sse(payload)
            last_activity = time.monotonic()
            continue

        if run_state_reader is not None:
            try:
                run_state = run_state_reader() or {}
                if not _is_step_running(run_state, step):
                    yield _done_event("completed")
                    return
            except Exception:
                pass

        if time.monotonic() - last_activity > idle_timeout:
            yield _done_event("timeout")
            return

        await asyncio.sleep(poll_interval)
