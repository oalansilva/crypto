"""OpenSpec read-only viewer endpoints (single-tenant MVP).

Allows the frontend to list and fetch spec markdown files from
`crypto/openspec/specs/*.md`.

Security:
- No auth (explicit by user).
- Strict allowlist to the specs directory.
- Prevent path traversal by validating ids.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/openspec", tags=["openspec"])


_SPEC_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _project_root() -> Path:
    # backend/app/routes/openspec.py -> backend/app/routes -> backend/app -> backend -> crypto
    return Path(__file__).resolve().parents[3]


def _specs_dir() -> Path:
    return _project_root() / "openspec" / "specs"


def _parse_frontmatter(text: str) -> Dict[str, Any]:
    """Very small YAML-frontmatter parser.

    Only supports `---` fenced blocks with `key: value` lines.
    """

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out: Dict[str, Any] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if not k:
            continue
        out[k] = v
    return out


class OpenSpecListItem(BaseModel):
    id: str
    path: str
    title: Optional[str] = None
    status: Optional[str] = None
    updated_at: Optional[str] = None


class OpenSpecListResponse(BaseModel):
    items: List[OpenSpecListItem]


class OpenSpecGetResponse(BaseModel):
    id: str
    markdown: str


@router.get("/specs", response_model=OpenSpecListResponse)
async def list_specs() -> OpenSpecListResponse:
    specs_dir = _specs_dir()
    if not specs_dir.exists():
        return OpenSpecListResponse(items=[])

    items: List[OpenSpecListItem] = []

    # Newest first (by file mtime). Falls back to name sort if stat fails.
    def _mtime_key(p: Path) -> float:
        try:
            return p.stat().st_mtime
        except Exception:
            return 0.0

    for p in sorted(specs_dir.glob("*.md"), key=_mtime_key, reverse=True):
        spec_id = p.stem
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = _parse_frontmatter(txt)
        items.append(
            OpenSpecListItem(
                id=spec_id,
                path=str(Path("openspec") / "specs" / p.name),
                title=fm.get("title"),
                status=fm.get("status"),
                updated_at=fm.get("updated_at") or fm.get("created_at"),
            )
        )

    return OpenSpecListResponse(items=items)


@router.get("/specs/{spec_id}", response_model=OpenSpecGetResponse)
async def get_spec(spec_id: str) -> OpenSpecGetResponse:
    spec_id = (spec_id or "").strip()
    if not _SPEC_ID_RE.match(spec_id):
        raise HTTPException(status_code=400, detail="Invalid spec id")

    p = _specs_dir() / f"{spec_id}.md"
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="Spec not found")

    # Extra safety: ensure the resolved path stays under specs dir.
    specs_dir = _specs_dir().resolve()
    if specs_dir not in p.resolve().parents:
        raise HTTPException(status_code=400, detail="Invalid path")

    try:
        md = p.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read spec: {e}")

    return OpenSpecGetResponse(id=spec_id, markdown=md)
