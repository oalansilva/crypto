"""
Export combo_templates from backend/backtest.db to JSON.
Use this on the server that has the templates, then commit the JSON to the repo.
Run from project root: python scripts/export_templates.py
"""
import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "backend" / "backtest.db"
OUT_PATH = PROJECT_ROOT / "backend" / "config" / "combo_templates_export.json"


def main():
    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, description, is_example, is_prebuilt, is_readonly,
               template_data, optimization_schema, created_at
        FROM combo_templates
        ORDER BY name
    """)
    rows = cursor.fetchall()
    conn.close()

    out_data = []
    for row in rows:
        out_data.append({
            "name": row["name"],
            "description": row["description"],
            "is_example": bool(row["is_example"]),
            "is_prebuilt": bool(row["is_prebuilt"]),
            "is_readonly": bool(row["is_readonly"]),
            "template_data": row["template_data"] if isinstance(row["template_data"], dict) else json.loads(row["template_data"] or "{}"),
            "optimization_schema": row["optimization_schema"] if row["optimization_schema"] is None or isinstance(row["optimization_schema"], dict) else json.loads(row["optimization_schema"]),
            "created_at": row["created_at"],
        })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(out_data)} templates to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    exit(main())
