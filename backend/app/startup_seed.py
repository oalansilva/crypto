"""Startup seed helpers.

Goal: ensure combo templates exist in SQLite for a fresh install.

Behavior:
- If combo_templates table exists but is empty, import templates from
  backend/config/combo_templates_export.json.
- Idempotent: upsert by name.

This avoids the frontend showing "No templates available" on new servers.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List


def _get_db_path() -> str:
    from app.database import DB_PATH  # single source of truth

    return str(DB_PATH)


def _get_export_path() -> str:
    # backend/app/startup_seed.py -> backend/config/...
    backend_dir = Path(__file__).resolve().parents[1]
    return str(backend_dir / "config" / "combo_templates_export.json")


def seed_combo_templates_if_empty(db_path: str | None = None, export_path: str | None = None) -> int:
    """Return number of templates imported/updated."""

    db_path = db_path or _get_db_path()
    export_path = export_path or _get_export_path()

    # Nothing to do if export file missing
    if not Path(export_path).exists():
        return 0

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Ensure table exists (some deployments create via SQLAlchemy models)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS combo_templates (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name VARCHAR NOT NULL,
            description VARCHAR,
            is_prebuilt BOOLEAN,
            is_example BOOLEAN,
            is_readonly BOOLEAN,
            template_data TEXT NOT NULL,
            optimization_schema TEXT,
            created_at DATETIME,
            updated_at DATETIME
        )
        """
    )

    cur.execute("SELECT COUNT(*) FROM combo_templates")
    count = int(cur.fetchone()[0] or 0)
    if count > 0:
        con.close()
        return 0

    data: List[Dict[str, Any]] = json.loads(Path(export_path).read_text(encoding="utf-8"))

    imported = 0
    for item in data:
        name = item.get("name")
        if not name:
            continue

        description = item.get("description") or ""
        is_prebuilt = 1 if item.get("is_prebuilt") else 0
        is_example = 1 if item.get("is_example") else 0
        is_readonly = 1 if item.get("is_readonly") else 0
        template_data = item.get("template_data") or {}
        optimization_schema = item.get("optimization_schema")
        created_at = item.get("created_at")

        # Upsert by name (safe even if table was pre-created with some entries)
        cur.execute("SELECT id FROM combo_templates WHERE name = ?", (name,))
        row = cur.fetchone()
        if row:
            cur.execute(
                """
                UPDATE combo_templates
                SET description = ?,
                    is_prebuilt = ?,
                    is_example = ?,
                    is_readonly = ?,
                    template_data = ?,
                    optimization_schema = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
                """,
                (
                    description,
                    is_prebuilt,
                    is_example,
                    is_readonly,
                    json.dumps(template_data, ensure_ascii=False),
                    json.dumps(optimization_schema, ensure_ascii=False) if optimization_schema is not None else None,
                    name,
                ),
            )
        else:
            if created_at is not None:
                cur.execute(
                    """
                    INSERT INTO combo_templates (
                        name, description, is_prebuilt, is_example, is_readonly,
                        template_data, optimization_schema, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (
                        name,
                        description,
                        is_prebuilt,
                        is_example,
                        is_readonly,
                        json.dumps(template_data, ensure_ascii=False),
                        json.dumps(optimization_schema, ensure_ascii=False) if optimization_schema is not None else None,
                        created_at,
                    ),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO combo_templates (
                        name, description, is_prebuilt, is_example, is_readonly,
                        template_data, optimization_schema
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        description,
                        is_prebuilt,
                        is_example,
                        is_readonly,
                        json.dumps(template_data, ensure_ascii=False),
                        json.dumps(optimization_schema, ensure_ascii=False) if optimization_schema is not None else None,
                    ),
                )
        imported += 1

    con.commit()
    con.close()

    return imported
