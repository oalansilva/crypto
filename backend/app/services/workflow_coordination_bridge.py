"""Bridges legacy coordination surfaces into the workflow-state DB.

Why this exists
---------------
The Kanban UI drawer reads comments from the workflow DB (wf_comments).
Historically, comments/evidence were stored in append-only JSONL files under
`data/coordination_comments/<change_id>.jsonl`.

We do **not** want to keep two sources of truth long-term. But we *do* want to
be resilient to agents/tools that still append to the JSONL surface.

This module provides *forward migration* helpers:
- import JSONL comments into wf_comments (idempotent)
- optionally dual-write from the legacy API into the DB (best-effort)

Design principles
-----------------
- Never render directly from JSONL in the Kanban UI. Always migrate into the DB.
- Idempotent: safe to call on every request.
- Best-effort: errors must not break the main workflow API.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from sqlalchemy.orm import Session

from app.services.coordination_service import project_root
from app.workflow_models import CommentScope, WorkflowComment


def _parse_iso(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _comments_file(change_id: str) -> Path:
    return project_root() / "data" / "coordination_comments" / f"{change_id}.jsonl"


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except Exception:
            continue
        if isinstance(obj, dict):
            yield obj


def migrate_coordination_comments_into_workflow_db(
    db: Session,
    *,
    change_pk: str,
    change_id: str,
) -> int:
    """Import legacy JSONL comments into wf_comments.

    Returns number of inserted rows.

    Idempotency: we keep the original JSONL `id` as the wf_comments PK and
    skip if already present.
    """

    p = _comments_file(change_id)
    if not p.exists():
        return 0

    inserted = 0
    for obj in _iter_jsonl(p):
        cid = str(obj.get("id") or "").strip()
        if not cid:
            continue
        if db.query(WorkflowComment).filter(WorkflowComment.id == cid).first() is not None:
            continue

        author = str(obj.get("author") or "").strip() or "unknown"
        body = str(obj.get("body") or "").rstrip("\n")
        if not body.strip():
            continue

        item = WorkflowComment(
            id=cid,
            scope=CommentScope.change,
            change_pk=change_pk,
            work_item_id=None,
            author=author,
            body=body,
        )

        created_at = _parse_iso(str(obj.get("created_at") or ""))
        if created_at is not None:
            item.created_at = created_at

        db.add(item)
        inserted += 1

    if inserted:
        db.commit()

    return inserted


def dual_write_coordination_comment_to_workflow_db(
    db: Session,
    *,
    change_pk: str,
    comment_id: str,
    author: str,
    body: str,
    created_at_iso: str,
) -> bool:
    """Best-effort write of a legacy coordination comment into wf_comments.

    Returns True if inserted, False if skipped/already-exists.

    IMPORTANT: caller controls transaction boundaries. We commit only when we
    insert (to keep behavior simple for legacy endpoints).
    """

    cid = str(comment_id or "").strip()
    if not cid:
        return False

    if db.query(WorkflowComment).filter(WorkflowComment.id == cid).first() is not None:
        return False

    item = WorkflowComment(
        id=cid,
        scope=CommentScope.change,
        change_pk=change_pk,
        work_item_id=None,
        author=(author or "unknown").strip() or "unknown",
        body=(body or "").rstrip("\n"),
    )

    created_at = _parse_iso(created_at_iso)
    if created_at is not None:
        item.created_at = created_at

    db.add(item)
    db.commit()
    return True
