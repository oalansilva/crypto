"""Export the complete PostgreSQL combo template catalog for drift-safe tests."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.database import SessionLocal
from app.models import ComboTemplate


def _json_value(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def export_combo_templates(destination: Path) -> int:
    with SessionLocal() as database:
        rows = database.query(ComboTemplate).order_by(ComboTemplate.name.asc()).all()

    payload = [
        {
            "name": row.name,
            "description": row.description,
            "is_example": bool(row.is_example),
            "is_prebuilt": bool(row.is_prebuilt),
            "is_readonly": bool(row.is_readonly),
            "template_data": _json_value(row.template_data),
            "optimization_schema": _json_value(row.optimization_schema),
            "created_at": _json_value(row.created_at),
        }
        for row in rows
    ]
    destination.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return len(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "config" / "combo_templates_export.json",
    )
    args = parser.parse_args()
    count = export_combo_templates(args.output)
    print(f"Exported {count} combo templates to {args.output}")


if __name__ == "__main__":
    main()
