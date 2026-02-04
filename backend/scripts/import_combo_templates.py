"""Import combo templates from JSON export into SQLite.

Usage:
  python3 backend/scripts/import_combo_templates.py \
    --db backend/backtest.db \
    --json backend/config/combo_templates_export.json

Idempotent behavior:
- Upserts by template name (UPDATE if exists, INSERT otherwise)
- Does not delete anything

Notes:
- Expects current schema with columns:
    name, description, is_prebuilt, is_example, is_readonly,
    template_data (TEXT/JSON), optimization_schema (TEXT/JSON), created_at, updated_at
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def _default_db_path() -> str:
    try:
        from app.database import DB_PATH  # type: ignore
        return str(DB_PATH)
    except Exception:
        return str(Path(__file__).resolve().parents[2] / "backend" / "backtest.db")


def _parse_dt(dt: Optional[str]) -> Optional[str]:
    """Return dt string if looks valid; otherwise None.

    We keep whatever format is already used in the export.
    """
    if not dt:
        return None
    s = str(dt).strip()
    return s or None


def import_templates(db_path: str, json_path: str) -> Dict[str, int]:
    db_path = str(Path(db_path))
    json_path = str(Path(json_path))

    data: List[Dict[str, Any]] = json.loads(Path(json_path).read_text(encoding="utf-8"))

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    inserted = 0
    updated = 0

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

        created_at = _parse_dt(item.get("created_at"))

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
            updated += 1
        else:
            # created_at: if present in export, keep it; else default DB value via NULL -> CURRENT_TIMESTAMP.
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
            inserted += 1

    conn.commit()
    conn.close()

    return {"inserted": inserted, "updated": updated, "total": len(data)}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--db", default=_default_db_path(), help="Path to SQLite DB (backtest.db)")
    p.add_argument(
        "--json",
        default=str(Path(__file__).resolve().parents[2] / "backend" / "config" / "combo_templates_export.json"),
        help="Path to combo_templates_export.json",
    )
    args = p.parse_args()

    res = import_templates(args.db, args.json)
    print(f"✅ Import concluído: inserted={res['inserted']} updated={res['updated']} total_in_file={res['total']}")


if __name__ == "__main__":
    main()
