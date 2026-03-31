"""Startup seed helpers for combo templates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.database import SessionLocal
from app.models import ComboTemplate


def _get_export_path() -> str:
    # backend/app/startup_seed.py -> backend/config/...
    backend_dir = Path(__file__).resolve().parents[1]
    return str(backend_dir / "config" / "combo_templates_export.json")


def seed_combo_templates_if_empty(export_path: str | None = None) -> int:
    """Return number of templates imported/updated."""

    export_path = export_path or _get_export_path()

    # Nothing to do if export file missing
    if not Path(export_path).exists():
        return 0

    data: List[Dict[str, Any]] = json.loads(Path(export_path).read_text(encoding="utf-8"))

    with SessionLocal() as db:
        count = db.query(ComboTemplate).count()
        if count > 0:
            return 0

        imported = 0
        for item in data:
            name = item.get("name")
            if not name:
                continue

            row = ComboTemplate(
                name=name,
                description=item.get("description") or "",
                is_prebuilt=bool(item.get("is_prebuilt")),
                is_example=bool(item.get("is_example")),
                is_readonly=bool(item.get("is_readonly")),
                template_data=item.get("template_data") or {},
                optimization_schema=item.get("optimization_schema"),
                created_at=item.get("created_at"),
            )
            db.add(row)
            imported += 1

        db.commit()
        return imported
