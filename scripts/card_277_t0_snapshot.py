#!/usr/bin/env python3
"""Capture issue #277 T0 baseline without mutating Favorites."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.database import SessionLocal
from app.models import ComboTemplate, FavoriteStrategy
from app.services.strategy_descriptions import (
    PUBLIC_STRATEGY_DESCRIPTIONS,
    PUBLIC_STRATEGY_DISPLAY_NAMES,
    public_strategy_description,
    public_strategy_display_name,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-277-hard-mode-v5-btc-long"
MAPPING_SOURCE = "backend/app/services/strategy_descriptions.py"


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def _direction(parameters: Any) -> str:
    if isinstance(parameters, dict):
        return str(parameters.get("direction") or "long").lower()
    return "long"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _favorite_payload(row: FavoriteStrategy) -> dict[str, Any]:
    strategy_name = str(row.strategy_name)
    return {
        "id": row.id,
        "name": row.name,
        "strategy_name": strategy_name,
        "strategy_display_name": public_strategy_display_name(strategy_name),
        "strategy_description": public_strategy_description(strategy_name),
        "direction": _direction(row.parameters),
        "parameters": _jsonable(row.parameters),
        "metrics": _jsonable(row.metrics),
        "start_date": row.start_date,
        "end_date": row.end_date,
        "period_type": row.period_type,
        "created_at": _jsonable(row.created_at),
        "auto_refresh_status": row.auto_refresh_status,
        "auto_refresh_completed_at": _jsonable(row.auto_refresh_completed_at),
    }


def _template_payload(row: ComboTemplate) -> dict[str, Any]:
    template_direction = _direction(row.template_data)
    return {
        "name": row.name,
        "description": row.description,
        "direction": template_direction,
        "public_description": public_strategy_description(row.name, row.description),
        "template_data": _jsonable(row.template_data),
        "optimization_schema": _jsonable(row.optimization_schema),
        "created_at": _jsonable(row.created_at),
        "updated_at": _jsonable(row.updated_at),
    }


def _pine_payload(symbol: str, timeframe: str, direction: str) -> list[dict[str, Any]]:
    pine_dir = ROOT / "docs" / "tradingview"
    if not pine_dir.exists():
        return []
    needle_symbol = symbol.split("/")[0].lower()
    rows = []
    for path in sorted(pine_dir.rglob("*.pine")):
        content = path.read_text(encoding="utf-8", errors="replace")
        haystack = f"{path.name}\n{content}".lower()
        if needle_symbol not in haystack or timeframe.lower() not in haystack:
            continue
        if direction.lower() not in haystack:
            continue
        rows.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
                "first_line": content.splitlines()[0] if content.splitlines() else "",
            }
        )
    return rows


def capture(symbol: str, timeframe: str, direction: str) -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc)
    with SessionLocal() as session:
        all_favorites = (
            session.query(FavoriteStrategy)
            .filter(FavoriteStrategy.symbol == symbol, FavoriteStrategy.timeframe == timeframe)
            .order_by(FavoriteStrategy.id.asc())
            .all()
        )
        direction_counts: dict[str, int] = {}
        for row in all_favorites:
            row_direction = _direction(row.parameters)
            direction_counts[row_direction] = direction_counts.get(row_direction, 0) + 1
        favorites = [row for row in all_favorites if _direction(row.parameters) == direction]
        templates = session.query(ComboTemplate).order_by(ComboTemplate.name.asc()).all()
        compatible_templates = [
            row for row in templates if _direction(row.template_data) == direction
        ]

        return {
            "snapshot": {
                "card": 277,
                "timestamp_utc": timestamp.isoformat(),
                "symbol": symbol,
                "timeframe": timeframe,
                "direction": direction,
                "valid_direction_favorites_exist": bool(favorites),
                "cold_start_mode": not bool(favorites),
                "deep_backtest_revalidation_status": "pending",
            },
            "direction_counts": direction_counts,
            "favorites": [_favorite_payload(row) for row in favorites],
            "templates": [_template_payload(row) for row in compatible_templates],
            "public_mappings": {
                "strategy_display_name": PUBLIC_STRATEGY_DISPLAY_NAMES,
                "strategy_description": PUBLIC_STRATEGY_DESCRIPTIONS,
                "source": MAPPING_SOURCE,
                "resolver_functions": [
                    "public_strategy_display_name",
                    "public_strategy_description",
                ],
            },
            "pine_scripts": _pine_payload(symbol, timeframe, direction),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--timeframe", default="1d")
    parser.add_argument("--direction", choices=["long", "short"], default="long")
    args = parser.parse_args()

    if not os.getenv("DATABASE_URL"):
        raise SystemExit("DATABASE_URL is required")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    payload = capture(args.symbol, args.timeframe, args.direction)
    timestamp = payload["snapshot"]["timestamp_utc"].replace(":", "").replace("+", "Z")
    output = ARTIFACT_DIR / f"t0-snapshot-{timestamp}.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    latest = ARTIFACT_DIR / "t0-snapshot-latest.json"
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(output)
    print(
        json.dumps(
            {
                "favorites": len(payload["favorites"]),
                "direction_counts": payload["direction_counts"],
                "templates": len(payload["templates"]),
                "pine_scripts": len(payload["pine_scripts"]),
                "cold_start_mode": payload["snapshot"]["cold_start_mode"],
                "output": str(output),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
