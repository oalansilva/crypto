"""Lightweight log tail endpoint for cloud monitoring.

Security:
- Only allows tailing a small allowlist of server-side log files.
- Caps line count.

This is meant for development / single-tenant deployments.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/logs", tags=["logs"])


LOG_MAP = {
    "full_execution_log": Path(__file__).resolve().parents[2] / "full_execution_log.txt",
    "backtest_debug": Path(__file__).resolve().parents[2] / "logs" / "backtest_debug.log",
}


def _tail_lines(path: Path, lines: int) -> str:
    """Return the last ``lines`` lines of a file efficiently.

    Reads from the end of the file (seek-from-end) instead of loading the whole
    file into memory, so large log files (e.g. 300MB+ full_execution_log.txt)
    stay fast on every poll.
    """
    try:
        size = path.stat().st_size
    except FileNotFoundError:
        return ""
    if size <= 0:
        return ""

    # Read backward in chunks until we have enough newlines to cover `lines`
    # (or reach the start of the file). Cap the scanned tail to avoid unbounded
    # reads on files with very long lines.
    chunk = 64 * 1024
    max_scan = max(chunk * 32, lines * 4096)
    offset = size
    data = b""
    try:
        with open(path, "rb") as fh:
            while offset > 0 and len(data) < max_scan:
                read_size = min(chunk, offset)
                offset -= read_size
                fh.seek(offset)
                data = fh.read(read_size) + data
                if data.count(b"\n") >= lines + 1:
                    break
    except OSError:
        return ""

    text = data.decode("utf-8", errors="replace")
    parts = text.splitlines()
    return "\n".join(parts[-lines:])


@router.get("/tail")
def tail_log(
    name: Literal["full_execution_log", "backtest_debug"] = Query("full_execution_log"),
    lines: int = Query(200, ge=10, le=2000),
):
    path = LOG_MAP.get(name)
    if not path:
        raise HTTPException(status_code=404, detail="Unknown log name")

    content = _tail_lines(path, lines)
    return {
        "name": name,
        "path": str(path),
        "lines": lines,
        "content": content,
    }
