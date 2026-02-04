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
    # Simple + safe tail (files are small in this project). If this grows, switch to seek-from-end.
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""
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
