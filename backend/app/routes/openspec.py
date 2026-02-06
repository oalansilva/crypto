"""OpenSpec read-only viewer endpoints (single-tenant MVP).

Allows the frontend to list and fetch spec markdown files from
`crypto/openspec/specs/**/*.md`.

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


_SPEC_SEGMENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _normalize_spec_id(spec_id: str) -> List[str]:
    """Normalize and validate a spec id.

    We support nested specs like `backend/spec` which maps to
    `openspec/specs/backend/spec.md`.

    Security constraints:
    - Only allow safe path segments (no traversal, no empty segments)
    - Always resolve under the specs directory
    - Caller appends `.md` (ids should not include extension)
    """

    spec_id = (spec_id or "").strip().replace("\\", "/")
    if not spec_id:
        raise HTTPException(status_code=400, detail="Invalid spec id")

    # Disallow passing the extension explicitly.
    if spec_id.endswith(".md"):
        spec_id = spec_id[: -len(".md")]

    parts = [p for p in spec_id.split("/") if p]
    if not parts:
        raise HTTPException(status_code=400, detail="Invalid spec id")

    for p in parts:
        if p in (".", ".."):
            raise HTTPException(status_code=400, detail="Invalid spec id")
        if not _SPEC_SEGMENT_RE.match(p):
            raise HTTPException(status_code=400, detail="Invalid spec id")

    return parts


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

    for p in sorted(specs_dir.glob("**/*.md"), key=_mtime_key, reverse=True):
        # id is the relative path from specs dir without the .md suffix
        try:
            rel = p.relative_to(specs_dir)
        except Exception:
            continue
        spec_id = rel.as_posix()
        if spec_id.endswith(".md"):
            spec_id = spec_id[: -len(".md")]
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = _parse_frontmatter(txt)
        items.append(
            OpenSpecListItem(
                id=spec_id,
                path=str(Path("openspec") / "specs" / rel),
                title=fm.get("title"),
                status=fm.get("status"),
                updated_at=fm.get("updated_at") or fm.get("created_at"),
            )
        )

    return OpenSpecListResponse(items=items)


@router.get("/specs/{spec_id:path}", response_model=OpenSpecGetResponse)
async def get_spec(spec_id: str) -> OpenSpecGetResponse:
    parts = _normalize_spec_id(spec_id)

    # IMPORTANT: spec ids may contain dots (e.g. crypto.lab.langgraph.studio.v1).
    # `Path.with_suffix(".md")` would treat the last dot segment as an extension and
    # incorrectly drop it ("...v1" -> "...md"). So we append ".md" explicitly.
    p = Path(str(_specs_dir().joinpath(*parts)) + ".md")
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="Spec not found")

    # Extra safety: ensure the resolved path stays under specs dir.
    specs_dir = _specs_dir().resolve()
    resolved = p.resolve()
    if resolved == specs_dir or specs_dir not in resolved.parents:
        raise HTTPException(status_code=400, detail="Invalid path")

    try:
        md = p.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read spec: {e}")

    # Return the normalized id as posix path without extension
    norm_id = "/".join(parts)
    return OpenSpecGetResponse(id=norm_id, markdown=md)
