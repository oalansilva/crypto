"""
Import combo_templates from backend/config/combo_templates_export.json into backend/backtest.db.
Use this on the new server after cloning the repo (ensure the table exists and the JSON is present).
Run from project root: python scripts/import_templates.py
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "backend" / "backtest.db"
JSON_PATH = PROJECT_ROOT / "backend" / "config" / "combo_templates_export.json"


def main():
    if not JSON_PATH.exists():
        print(f"Export file not found: {JSON_PATH}")
        print("Run export_templates.py on the server that has the templates, then commit and pull.")
        return 1

    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH}. Run migrations first (e.g. create_combo_templates).")
        return 1

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        templates = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    imported = 0
    skipped = 0
    for t in templates:
        cursor.execute("SELECT 1 FROM combo_templates WHERE name = ?", (t["name"],))
        if cursor.fetchone():
            print(f"  Skip (exists): {t['name']}")
            skipped += 1
            continue
        template_data = t.get("template_data") or {}
        opt_schema = t.get("optimization_schema")
        if isinstance(template_data, dict):
            template_data = json.dumps(template_data)
        if isinstance(opt_schema, dict):
            opt_schema = json.dumps(opt_schema)

        cursor.execute("""
            INSERT INTO combo_templates (
                name, description, is_example, is_prebuilt, is_readonly,
                template_data, optimization_schema, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            t["name"],
            t.get("description"),
            1 if t.get("is_example") else 0,
            1 if t.get("is_prebuilt") else 0,
            1 if t.get("is_readonly") else 0,
            template_data,
            opt_schema,
            t.get("created_at") or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        print(f"  Imported: {t['name']}")
        imported += 1

    conn.commit()
    conn.close()
    print(f"Done: {imported} imported, {skipped} skipped.")
    return 0


if __name__ == "__main__":
    exit(main())
