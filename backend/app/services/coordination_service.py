"""Coordination/Kanban file parsing (read-only).

Source of truth:
- Change coordination markdown files: `docs/coordination/*.md`

We parse the `## Status` section to derive gate statuses and the Kanban column,
according to the rules locked in:
`docs/coordination/kanban-visual-coordination.md`.

This module is intentionally lightweight and file-based (single-tenant MVP).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


_STATUS_LINE_RE = re.compile(r"^\s*-\s*([^:]+):\s*(.*?)\s*$")


def project_root() -> Path:
    # backend/app/services/coordination_service.py -> services -> app -> backend -> crypto
    return Path(__file__).resolve().parents[3]


def coordination_dir() -> Path:
    return project_root() / "docs" / "coordination"


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _extract_h1_title(md: str) -> Optional[str]:
    for line in md.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip() or None
        if s:  # stop at first non-empty line if no h1
            break
    return None


def _extract_status_section_lines(md: str) -> List[str]:
    lines = md.splitlines()
    in_status = False
    out: List[str] = []

    for line in lines:
        s = line.rstrip("\n")
        if s.strip() == "## Status":
            in_status = True
            continue
        if in_status and s.strip().startswith("## "):
            break
        if in_status:
            out.append(s)

    return out


def parse_status(md: str) -> Dict[str, str]:
    """Parse the `## Status` bullet list into a normalized dict.

    Returns keys in the original label form (e.g. "PO", "DEV", "Alan approval").
    """

    out: Dict[str, str] = {}
    for line in _extract_status_section_lines(md):
        m = _STATUS_LINE_RE.match(line)
        if not m:
            continue
        k = (m.group(1) or "").strip()
        v = (m.group(2) or "").strip()
        if not k or not v:
            continue
        out[k] = v
    return out


def _get_gate(status: Dict[str, str], key: str) -> Optional[str]:
    v = status.get(key)
    if v is None:
        return None
    return str(v).strip().lower()


def _alan_field(status: Dict[str, str], key: str) -> Optional[str]:
    """Get an Alan field with backward-compatible fallback."""

    v = _get_gate(status, key)
    if v is not None:
        return v
    fallback = _get_gate(status, "Alan (Stakeholder)")
    return fallback


def is_archived(md: str, status: Dict[str, str]) -> bool:
    # Rule 1: a heading exactly `## Closed` anywhere.
    for line in md.splitlines():
        if line.strip() == "## Closed":
            return True

    # Rule 2: all gates complete.
    po = _get_gate(status, "PO")
    dev = _get_gate(status, "DEV")
    qa = _get_gate(status, "QA")
    alan_approval = _alan_field(status, "Alan approval")
    alan_homologation = _alan_field(status, "Alan homologation")

    return (
        po == "done"
        and dev == "done"
        and qa == "done"
        and alan_approval == "approved"
        and alan_homologation == "approved"
    )


def derive_column(status: Dict[str, str], archived: bool) -> str:
    """Derive the Kanban column from gate statuses.

    Column selection algorithm (first match wins):
    1) archived -> Archived
    2) PO != done -> PO
    3) Alan approval != approved -> Alan approval
    4) DEV != done -> DEV
    5) QA != done -> QA
    6) Alan homologation != approved -> Alan homologation
    7) else -> Archived
    """

    if archived:
        return "Archived"

    po = _get_gate(status, "PO")
    dev = _get_gate(status, "DEV")
    qa = _get_gate(status, "QA")
    alan_approval = _alan_field(status, "Alan approval")
    alan_homologation = _alan_field(status, "Alan homologation")

    if po != "done":
        return "PO"
    if alan_approval != "approved":
        return "Alan approval"
    if dev != "done":
        return "DEV"
    if qa != "done":
        return "QA"
    if alan_homologation != "approved":
        return "Alan homologation"
    return "Archived"


def _archived_change_ids_from_openspec() -> set[str]:
    """Return change ids that are archived per OpenSpec archive folder.

    OpenSpec archives are stored under `openspec/changes/archive/<archive-id>/`.
    In this project, archive folder names are typically prefixed with YYYY-MM-DD-,
    so we strip that prefix to recover the original change id.

    This makes the Kanban board consistent even if `docs/coordination/<change>.md`
    was not updated at archive time.
    """

    archive_root = project_root() / "openspec" / "changes" / "archive"
    if not archive_root.exists():
        return set()

    out: set[str] = set()
    for d in archive_root.iterdir():
        if not d.is_dir():
            continue
        if not (d / ".openspec.yaml").exists():
            continue
        name = d.name
        # Strip common date prefix.
        m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", name)
        if m:
            out.add(m.group(1))
        else:
            out.add(name)

    return out


def list_coordination_changes() -> List[Dict[str, Any]]:
    base = coordination_dir()
    if not base.exists():
        return []

    openspec_archived_ids = _archived_change_ids_from_openspec()

    out: List[Dict[str, Any]] = []
    for p in sorted(base.glob("*.md")):
        if p.name in {"README.md", "template.md"}:
            continue
        change_id = p.stem
        try:
            md = _read_text(p)
        except Exception:
            continue

        status = parse_status(md)

        # Determine archived. OpenSpec archive status wins to avoid inconsistencies
        # between file-based coordination and the actual OpenSpec archive state.
        archived = is_archived(md, status) or (change_id in openspec_archived_ids)
        column = "Archived" if archived else derive_column(status, archived=archived)

        out.append(
            {
                "id": change_id,
                "title": _extract_h1_title(md),
                "path": str(Path("docs") / "coordination" / p.name),
                "status": status,
                "archived": archived,
                "column": column,
            }
        )

    return out
