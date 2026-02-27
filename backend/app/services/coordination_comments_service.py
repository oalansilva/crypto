"""Coordination comments persistence (append-only).

Storage:
- File-based JSONL per change at: <project_root>/data/coordination_comments/<change_id>.jsonl

Rationale:
- Single-tenant MVP; lightweight; no DB migrations required.

Comment policy (v1, locked in docs/coordination/kanban-visual-coordination.md):
- Append-only: no edit/delete.
- Retention: indefinite (including archived changes).
- Fields: id, change, author, created_at (UTC ISO-8601), body (plain text, max 2000 chars).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.coordination_service import coordination_dir, project_root


MAX_COMMENT_BODY_LEN = 2000


@dataclass(frozen=True)
class CoordinationComment:
    id: str
    change: str
    author: str
    created_at: str
    body: str


def _comments_dir() -> Path:
    return project_root() / "data" / "coordination_comments"


def _change_exists(change_id: str) -> bool:
    # A change is considered valid if its coordination markdown exists.
    p = coordination_dir() / f"{change_id}.md"
    return p.exists() and p.is_file()


def _normalize_change_id(change_id: str) -> str:
    cid = str(change_id or "").strip()
    if not cid:
        raise ValueError("change_id must not be empty")
    return cid


def _normalize_author(author: str) -> str:
    a = str(author or "").strip()
    if not a:
        raise ValueError("author must not be empty")
    return a


def _normalize_body(body: str) -> str:
    b = str(body or "")
    # Preserve whitespace/newlines; just enforce length.
    if len(b) > MAX_COMMENT_BODY_LEN:
        raise ValueError(f"body must be at most {MAX_COMMENT_BODY_LEN} chars")
    if not b.strip():
        raise ValueError("body must not be empty")
    return b


def _file_for_change(change_id: str) -> Path:
    return _comments_dir() / f"{change_id}.jsonl"


def list_comments(change_id: str) -> List[Dict[str, Any]]:
    cid = _normalize_change_id(change_id)
    if not _change_exists(cid):
        raise FileNotFoundError(f"Unknown change '{cid}'")

    # Seed a first comment so the thread is never empty (improves UX and
    # creates an auditable single place for handoffs).
    p = _file_for_change(cid)
    if (not p.exists()) or p.stat().st_size == 0:
        try:
            add_comment(
                cid,
                author="system",
                body="Thread created. Use comments for handoffs, blockers, and decisions.",
            )
        except Exception:
            # Never break the UI if seeding fails.
            pass

    # Reload after potential seed.
    out: List[Dict[str, Any]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        out.append(obj)

    # Stable ordering: created_at.
    def _key(it: Dict[str, Any]):
        return str(it.get("created_at") or "")

    return sorted(out, key=_key)


def add_comment(change_id: str, author: str, body: str) -> Dict[str, Any]:
    cid = _normalize_change_id(change_id)
    if not _change_exists(cid):
        raise FileNotFoundError(f"Unknown change '{cid}'")

    a = _normalize_author(author)
    b = _normalize_body(body)

    created_at = datetime.now(timezone.utc).isoformat()
    comment = CoordinationComment(
        id=str(uuid4()),
        change=cid,
        author=a,
        created_at=created_at,
        body=b,
    )

    d = _comments_dir()
    d.mkdir(parents=True, exist_ok=True)

    p = _file_for_change(cid)
    record = asdict(comment)

    # Append-only JSONL.
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record
