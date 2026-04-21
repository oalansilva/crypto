#!/usr/bin/env python3
"""Legacy utility kept only for auditability.

This script previously synchronized `docs/coordination/<change>.md` on archive.
The solo workflow no longer writes coordination files, so this utility is now
effectively a no-op unless the legacy directory exists.

Goal:
- If a change is archived under openspec/changes/archive/<...>/.openspec.yaml,
  then ensure docs/coordination/<change>.md reflects closure:
  - Homologation: approved
  - add a '## Closed' section

This prevents Kanban showing archived changes in 'Homologation' due to stale coordination.

Safe:
- Only edits existing docs/coordination/<change>.md files.
- Does not touch code or OpenSpec archive artifacts.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = ROOT / "openspec" / "changes" / "archive"
COORD_DIR = ROOT / "docs" / "coordination"

DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-(.+)$")


def archived_change_ids() -> set[str]:
    out: set[str] = set()
    if not ARCHIVE_ROOT.exists():
        return out
    for d in ARCHIVE_ROOT.iterdir():
        if not d.is_dir():
            continue
        if not (d / ".openspec.yaml").exists():
            continue
        m = DATE_PREFIX.match(d.name)
        out.add(m.group(1) if m else d.name)
    return out


def ensure_closed(md: str) -> str:
    if "\n## Closed\n" not in md and not md.strip().endswith("## Closed"):
        # Insert Closed section right after Status block if possible.
        lines = md.splitlines()
        out = []
        inserted = False
        i = 0
        while i < len(lines):
            out.append(lines[i])
            if lines[i].strip() == "## Status":
                # copy until next header
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("## "):
                    out.append(lines[i])
                    i += 1
                out.append("")
                out.append("## Closed")
                out.append("")
                out.append("- Homologated by Alan and archived.")
                out.append("")
                inserted = True
                continue
            i += 1
        if not inserted:
            out.append("")
            out.append("## Closed")
            out.append("")
            out.append("- Homologated by Alan and archived.")
        md = "\n".join(out) + "\n"
    return md


def set_homologation_approved(md: str) -> str:
    # Replace within Status bullet lines.
    md = re.sub(
        r"(^\s*-\s*Homologation:\s*).*$",
        r"\1approved",
        md,
        flags=re.MULTILINE,
    )
    return md


def main() -> int:
    if not COORD_DIR.is_dir():
        print("INFO: docs/coordination not present; nothing to reconcile")
        return 0
    ids = archived_change_ids()
    changed = 0
    for cid in sorted(ids):
        p = COORD_DIR / f"{cid}.md"
        if not p.exists():
            continue
        md = p.read_text(encoding="utf-8")
        new = md
        new = set_homologation_approved(new)
        new = ensure_closed(new)
        if new != md:
            p.write_text(new, encoding="utf-8")
            changed += 1

    print(f"reconciled {changed} coordination file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
