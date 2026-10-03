"""Startup seed helpers for combo templates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.database import SessionLocal
from app.models import ComboTemplate

# Card #1074 — templates novos devem existir mesmo quando a tabela já foi seedada.
CARD_1074_TEMPLATE_NAMES: tuple[str, ...] = (
    "donchian_volume_breakout",
    "bollinger_squeeze",
    "long_ma_pullback_rsi_adx",
)


def _get_export_path() -> str:
    # backend/app/startup_seed.py -> backend/config/...
    backend_dir = Path(__file__).resolve().parents[1]
    return str(backend_dir / "config" / "combo_templates_export.json")


def seed_combo_templates_if_empty(export_path: str | None = None) -> int:
    """Return number of templates imported on first seed (0 if table already had rows)."""

    export_path = export_path or _get_export_path()

    # Nothing to do if export file missing
    if not Path(export_path).exists():
        return 0

    data: List[Dict[str, Any]] = json.loads(Path(export_path).read_text(encoding="utf-8"))

    with SessionLocal() as db:
        count = db.query(ComboTemplate).count()
        if count > 0:
            upsert_combo_templates_from_export(CARD_1074_TEMPLATE_NAMES, export_path=export_path)
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


def upsert_combo_templates_from_export(
    names: tuple[str, ...] | list[str],
    export_path: str | None = None,
) -> int:
    """Insert or refresh named templates from the export file (non-destructive for others)."""

    export_path = export_path or _get_export_path()
    if not Path(export_path).exists():
        return 0

    wanted = {str(n).strip() for n in names if str(n).strip()}
    if not wanted:
        return 0

    data: List[Dict[str, Any]] = json.loads(Path(export_path).read_text(encoding="utf-8"))
    by_name = {item.get("name"): item for item in data if item.get("name")}

    touched = 0
    with SessionLocal() as db:
        for name in sorted(wanted):
            item = by_name.get(name)
            if not item:
                continue
            row = db.query(ComboTemplate).filter(ComboTemplate.name == name).first()
            display_name = item.get("display_name") or None
            if row:
                row.description = item.get("description") or ""
                row.display_name = display_name
                row.is_prebuilt = bool(item.get("is_prebuilt"))
                row.is_example = bool(item.get("is_example"))
                row.is_readonly = bool(item.get("is_readonly"))
                row.template_data = item.get("template_data") or {}
                row.optimization_schema = item.get("optimization_schema")
            else:
                db.add(
                    ComboTemplate(
                        name=name,
                        description=item.get("description") or "",
                        display_name=display_name,
                        is_prebuilt=bool(item.get("is_prebuilt")),
                        is_example=bool(item.get("is_example")),
                        is_readonly=bool(item.get("is_readonly")),
                        template_data=item.get("template_data") or {},
                        optimization_schema=item.get("optimization_schema"),
                        created_at=item.get("created_at"),
                    )
                )
            touched += 1
        db.commit()
    return touched
