"""OpenSpec change tasks parsing (read-only).

Source of truth:
- `openspec/changes/<change>/tasks.md`

We parse a markdown checklist into a simple tree structure that the Kanban UI can
render (sections + nested items).

This is intentionally lightweight and tolerant: non-checkbox bullet items are
kept as children with `checked=None`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from app.services.coordination_service import project_root


_H2_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$")
_BULLET_RE = re.compile(
    r"^(?P<indent>\s*)-\s+(?:(?P<box>\[(?P<mark>[ xX])\])\s+)?(?P<text>.*)$"
)
_TASK_CODE_RE = re.compile(r"^(?P<code>\d+(?:\.\d+)+)\s+(?P<title>.+)$")


@dataclass
class TaskItem:
    text: str
    checked: Optional[bool] = None
    code: Optional[str] = None
    title: Optional[str] = None
    children: List["TaskItem"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "checked": self.checked,
            "code": self.code,
            "title": self.title,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class TaskSection:
    title: str
    items: List[TaskItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"title": self.title, "items": [i.to_dict() for i in self.items]}


def _tasks_path(change_id: str) -> Path:
    # Active changes live here
    p = project_root() / "openspec" / "changes" / change_id / "tasks.md"
    if p.exists():
        return p

    # Archived changes live under openspec/changes/archive/<archive-id>/tasks.md
    # Archive folder is usually prefixed with YYYY-MM-DD-<change_id>.
    archive_root = project_root() / "openspec" / "changes" / "archive"
    if archive_root.exists():
        # 1) try common date prefix
        matches = list(archive_root.glob(f"????-??-??-{change_id}/tasks.md"))
        if matches:
            return matches[0]
        # 2) try exact folder match
        p2 = archive_root / change_id / "tasks.md"
        if p2.exists():
            return p2

    return p


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def parse_tasks_markdown(md: str) -> List[TaskSection]:
    sections: List[TaskSection] = []
    current: Optional[TaskSection] = None

    # Stack per section: (indent, item)
    stack: List[tuple[int, TaskItem]] = []

    for raw in md.splitlines():
        line = raw.rstrip("\n")

        m_h2 = _H2_RE.match(line.strip())
        if m_h2:
            current = TaskSection(title=m_h2.group("title").strip())
            sections.append(current)
            stack = []
            continue

        if current is None:
            # ignore preamble until first section
            continue

        m = _BULLET_RE.match(line)
        if not m:
            continue

        indent = len(m.group("indent") or "")
        text = (m.group("text") or "").strip()
        if not text:
            continue

        mark = m.group("mark")
        checked: Optional[bool]
        if mark is None:
            checked = None
        else:
            checked = mark.strip().lower() == "x"

        code = None
        title = None
        m_code = _TASK_CODE_RE.match(text)
        if m_code:
            code = m_code.group("code")
            title = m_code.group("title").strip() or None

        item = TaskItem(text=text, checked=checked, code=code, title=title)

        # attach to parent based on indentation
        while stack and indent <= stack[-1][0]:
            stack.pop()

        if stack:
            stack[-1][1].children.append(item)
        else:
            current.items.append(item)

        stack.append((indent, item))

    return sections


def get_change_tasks_checklist(change_id: str) -> Dict[str, Any]:
    p = _tasks_path(change_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"tasks.md not found for change '{change_id}'")

    try:
        md = _read_text(p)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to read tasks.md for change '{change_id}': {e}")

    sections = parse_tasks_markdown(md)
    return {
        "change_id": change_id,
        "path": str(p.relative_to(project_root())),
        "sections": [s.to_dict() for s in sections],
    }
