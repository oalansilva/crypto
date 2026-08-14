"""Lightweight log tail endpoint for cloud monitoring.

Security:
- Only allows tailing a small allowlist of server-side log files.
- Caps line count.

This is meant for development / single-tenant deployments.
"""

from __future__ import annotations

import stat
from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/logs", tags=["logs"])


LOG_MAP = {
    "full_execution_log": Path(__file__).resolve().parents[2] / "full_execution_log.txt",
    "backtest_debug": Path(__file__).resolve().parents[2] / "logs" / "backtest_debug.log",
}

# Maximum number of bytes returned per incremental request. Keeps bursts
# bounded while still streaming arbitrarily large files across polls.
MAX_INCREMENTAL_BYTES = 256 * 1024

# Tail cap for the legacy (no cursor) path.
MAX_TAIL_LINES = 2000


def _file_snapshot(path: Path) -> dict | None:
    """Return a consistent snapshot of the file or None when it cannot be read."""
    try:
        st = path.stat()
    except OSError:
        return None
    return {
        "file_size": st.st_size,
        "file_id": f"{st.st_dev}:{st.st_ino}",
        "mtime_ns": st.st_mtime_ns,
    }


def _is_regular_file(path: Path) -> bool:
    try:
        return stat.S_ISREG(path.stat().st_mode)
    except OSError:
        return False


def _tail_lines(path: Path, lines: int) -> str:
    """Return the last ``lines`` lines of a file efficiently.

    Reads from the end of the file (seek-from-end) instead of loading the whole
    file into memory, so large log files (e.g. 300MB+ full_execution_log.txt)
    stay fast on every poll.
    """
    size = path.stat().st_size if _is_regular_file(path) else 0
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


def _split_utf8_tail(data: bytes) -> tuple[bytes, bytes]:
    """Split ``data`` at the last complete UTF-8 sequence.

    Returns ``(deliverable, pending)`` where ``pending`` is an incomplete
    trailing multibyte sequence retained for the next request. Both bytes are
    concatenated back together on the next read from disk, so no character is
    corrupted or duplicated.
    """
    if not data:
        return data, b""
    cut = len(data)
    while cut > 0:
        b = data[cut - 1]
        if b & 0x80 == 0:
            return data[:cut], data[cut:]
        if b & 0xC0 == 0xC0:
            if b & 0xE0 == 0xC0:
                need = 2
            elif b & 0xF0 == 0xE0:
                need = 3
            elif b & 0xF8 == 0xF0:
                need = 4
            else:
                return data[:cut], data[cut:]
            start = cut - 1
            if len(data) - start < need:
                return data[:start], data[start:]
            return data, b""
        cut -= 1
    return data, b""


def _read_incremental(
    path: Path, after_offset: int, snapshot: dict, client_file_id: str | None
) -> dict:
    """Read new bytes after ``after_offset`` against a fresh snapshot.

    Returns ``content`` (new bytes, retained UTF-8 suffix pending), the next
    byte offset to continue from, and ``cursor_reset`` signalling truncation,
    rotation or identity change. On reset the client restarts the session with
    a fresh base request, so the response carries no content.
    """
    if client_file_id is not None and client_file_id != snapshot["file_id"]:
        return {
            "content": "",
            "next_offset": snapshot["file_size"],
            "cursor_reset": True,
        }

    if after_offset > snapshot["file_size"]:
        return {
            "content": "",
            "next_offset": snapshot["file_size"],
            "cursor_reset": True,
        }

    if snapshot["file_size"] > after_offset:
        try:
            with open(path, "rb") as fh:
                fh.seek(after_offset)
                raw = fh.read(min(MAX_INCREMENTAL_BYTES, snapshot["file_size"] - after_offset))
        except OSError:
            return {
                "content": "",
                "next_offset": after_offset,
                "cursor_reset": False,
            }
        deliverable, pending = _split_utf8_tail(raw)
        next_offset = after_offset + len(deliverable)
        return {
            "content": deliverable.decode("utf-8", errors="replace"),
            "next_offset": next_offset,
            "cursor_reset": False,
        }

    return {
        "content": "",
        "next_offset": after_offset,
        "cursor_reset": False,
    }


@router.get("/tail")
def tail_log(
    name: Annotated[
        Literal["full_execution_log", "backtest_debug"], Query()
    ] = "full_execution_log",
    lines: Annotated[int, Query(ge=10, le=MAX_TAIL_LINES)] = 200,
    after_offset: Annotated[int | None, Query(ge=0)] = None,
    file_id: Annotated[str | None, Query()] = None,
):
    path = LOG_MAP.get(name)
    if not path:
        raise HTTPException(status_code=404, detail="Unknown log name")

    snapshot = _file_snapshot(path)
    if snapshot is None:
        # Arquivo ainda não existe: sessão vazia que aguarda os primeiros bytes.
        return {
            "name": name,
            "path": str(path),
            "lines": lines,
            "content": "",
            "next_offset": 0,
            "file_size": 0,
            "file_id": "",
            "cursor_reset": False,
        }

    if after_offset is not None:
        increment = _read_incremental(path, after_offset, snapshot, file_id)
        return {
            "name": name,
            "path": str(path),
            "lines": lines,
            "content": increment["content"],
            "next_offset": increment["next_offset"],
            "file_size": snapshot["file_size"],
            "file_id": snapshot["file_id"],
            "cursor_reset": increment["cursor_reset"],
        }

    content = _tail_lines(path, lines)
    return {
        "name": name,
        "path": str(path),
        "lines": lines,
        "content": content,
        "next_offset": snapshot["file_size"],
        "file_size": snapshot["file_size"],
        "file_id": snapshot["file_id"],
        "cursor_reset": False,
    }
