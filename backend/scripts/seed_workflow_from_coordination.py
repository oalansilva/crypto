#!/usr/bin/env python3
"""Seed workflow DB from file-based coordination artifacts.

Phase-1 cutover policy (centralize-workflow-state-db):
- Workflow DB becomes the operational source of truth for active changes.
- `docs/coordination/*.md` stays as a mirrored/audit artifact (human-readable).
- Legacy comments stored under `data/coordination_comments/*.jsonl` are migrated
  into `wf_comments` so the Kanban thread stays intact.

This script is idempotent:
- Projects/changes are upserted by slug/change_id.
- Gate statuses are inserted only if no approval exists yet for that gate.
- Comments are upserted by preserving the legacy comment `id` as the workflow
  comment primary key.

Usage (dev / VPS):
  WORKFLOW_DB_ENABLED=1 WORKFLOW_DATABASE_URL=postgresql+psycopg2://... \
    .venv/bin/python backend/scripts/seed_workflow_from_coordination.py --project crypto

If WORKFLOW_DATABASE_URL is not set, it falls back to `backend/workflow.db`.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.workflow_database import WorkflowSessionLocal, init_workflow_schema
from app.workflow_models import (
    ApprovalScope,
    ApprovalState,
    Change,
    CommentScope,
    Project,
    WorkItem,
    WorkItemState,
    WorkItemType,
    WorkflowApproval,
    WorkflowComment,
)
from app.services.coordination_service import list_coordination_changes, project_root


def _parse_iso(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _approval_state_from_coord_status(raw: str) -> ApprovalState:
    s = (raw or "").strip().lower()
    if s in {"approved", "done", "skipped"}:
        return ApprovalState.approved
    if s in {"rejected"}:
        return ApprovalState.rejected
    # not started | in progress | blocked | not reviewed | reviewed | etc
    return ApprovalState.pending


def _ensure_project(db: Session, *, slug: str, name: str) -> Project:
    p = db.query(Project).filter(Project.slug == slug).first()
    if p:
        if name and (p.name or "") != name:
            p.name = name
            db.flush()
        return p
    p = Project(slug=slug, name=name or slug)
    db.add(p)
    db.flush()
    return p


def _ensure_change(db: Session, *, project_id: str, change_id: str, title: str, column: str) -> Change:
    c = db.query(Change).filter(Change.project_id == project_id, Change.change_id == change_id).first()
    if c:
        changed = False
        if title is not None and (c.title or "") != (title or ""):
            c.title = title or ""
            changed = True
        if column and (c.status or "") != column:
            c.status = column
            changed = True
        if changed:
            db.flush()
        return c

    c = Change(project_id=project_id, change_id=change_id, title=title or "", status=column or "DEV")
    db.add(c)
    db.flush()
    return c


def _seed_gate_approvals(db: Session, *, change_pk: str, status: dict[str, str]) -> int:
    inserted = 0
    for gate, raw in (status or {}).items():
        gate = (gate or "").strip()
        if not gate:
            continue

        existing = (
            db.query(WorkflowApproval)
            .filter(WorkflowApproval.scope == ApprovalScope.change)
            .filter(WorkflowApproval.change_pk == change_pk)
            .filter(WorkflowApproval.gate == gate)
            .order_by(WorkflowApproval.created_at.asc())
            .first()
        )
        if existing:
            continue

        item = WorkflowApproval(
            scope=ApprovalScope.change,
            gate=gate,
            state=_approval_state_from_coord_status(raw),
            change_pk=change_pk,
            work_item_id=None,
            actor="migration",
            note=f"Seeded from docs/coordination status: {raw}",
        )
        db.add(item)
        inserted += 1

    return inserted


def _comments_file(change_id: str) -> Path:
    return project_root() / "data" / "coordination_comments" / f"{change_id}.jsonl"


def _extract_next_actions(md: str) -> list[tuple[bool, str]]:
    """Return a list of (checked, text) from `## Next actions` markdown section."""

    lines = md.splitlines()
    in_section = False
    out: list[tuple[bool, str]] = []

    for line in lines:
        s = line.rstrip("\n")
        if s.strip() == "## Next actions":
            in_section = True
            continue
        if in_section and s.strip().startswith("## "):
            break
        if not in_section:
            continue

        m = re.match(r"^\s*-\s*\[(?P<mark>[xX ])\]\s*(?P<text>.+?)\s*$", s)
        if not m:
            continue
        text = (m.group("text") or "").strip()
        if not text:
            continue
        checked = (m.group("mark") or " ").lower() == "x"
        out.append((checked, text))

    return out


def _seed_work_items_from_coordination(db: Session, *, change_pk: str, change_id: str) -> int:
    """Seed wf_work_items from `docs/coordination/<change>.md` Next actions.

    Minimal mapping (Phase-1): each checkbox becomes a WorkItem of type=story.
    Idempotency: we treat (change_pk, type, title) as a natural key.
    """

    p = project_root() / "docs" / "coordination" / f"{change_id}.md"
    if not p.exists():
        return 0

    md = p.read_text(encoding="utf-8")
    tasks = _extract_next_actions(md)
    if not tasks:
        return 0

    inserted = 0
    for checked, text in tasks:
        state = WorkItemState.done if checked else WorkItemState.queued

        exists = (
            db.query(WorkItem)
            .filter(WorkItem.change_pk == change_pk)
            .filter(WorkItem.type == WorkItemType.story)
            .filter(WorkItem.title == text)
            .first()
            is not None
        )
        if exists:
            continue

        wi = WorkItem(
            change_pk=change_pk,
            type=WorkItemType.story,
            state=state,
            parent_id=None,
            title=text,
            description="Seeded from docs/coordination Next actions",
            priority=0,
            owner_run_id=None,
        )
        db.add(wi)
        inserted += 1

    return inserted


def _seed_comments(db: Session, *, change_pk: str, change_id: str) -> int:
    p = _comments_file(change_id)
    if not p.exists():
        return 0

    inserted = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue

        cid = str(obj.get("id") or "").strip()
        if not cid:
            continue
        if db.query(WorkflowComment).filter(WorkflowComment.id == cid).first():
            continue

        created_at = _parse_iso(str(obj.get("created_at") or ""))
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
        if created_at is not None:
            item.created_at = created_at

        db.add(item)
        inserted += 1

    return inserted


def seed_active_changes(*, project_slug: str, project_name: str | None = None) -> dict:
    init_workflow_schema()

    if WorkflowSessionLocal is None:
        raise RuntimeError("Workflow DB disabled. Set WORKFLOW_DB_ENABLED=1")

    coordination = list_coordination_changes()
    active = [it for it in coordination if not bool(it.get("archived"))]

    out = {
        "project": project_slug,
        "active_changes": len(active),
        "inserted_changes": 0,
        "inserted_gate_approvals": 0,
        "inserted_work_items": 0,
        "inserted_comments": 0,
    }

    with WorkflowSessionLocal() as db:
        p = _ensure_project(db, slug=project_slug, name=project_name or project_slug)

        for it in active:
            change_id = str(it.get("id") or "").strip()
            if not change_id:
                continue
            title = it.get("title") or ""
            column = it.get("column") or "DEV"
            status = it.get("status") or {}

            existed = db.query(Change).filter(Change.project_id == p.id, Change.change_id == change_id).first() is not None
            c = _ensure_change(db, project_id=p.id, change_id=change_id, title=title, column=column)
            if not existed:
                out["inserted_changes"] += 1

            out["inserted_gate_approvals"] += _seed_gate_approvals(db, change_pk=c.id, status=status)
            out["inserted_work_items"] += _seed_work_items_from_coordination(db, change_pk=c.id, change_id=change_id)
            out["inserted_comments"] += _seed_comments(db, change_pk=c.id, change_id=change_id)

        db.commit()

    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="crypto", help="Project slug to seed into (default: crypto)")
    ap.add_argument("--project-name", default=None, help="Optional human name for the project")
    args = ap.parse_args()

    report = seed_active_changes(project_slug=args.project, project_name=args.project_name)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
