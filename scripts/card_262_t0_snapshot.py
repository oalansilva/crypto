#!/usr/bin/env python3
"""Capture the issue #262 T0 baseline without mutating Favorites."""

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
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-262-hard-mode-v5"
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
    return {
        "name": row.name,
        "description": row.description,
        "public_description": public_strategy_description(row.name, row.description),
        "template_data": _jsonable(row.template_data),
        "optimization_schema": _jsonable(row.optimization_schema),
        "created_at": _jsonable(row.created_at),
        "updated_at": _jsonable(row.updated_at),
    }


def _pine_payload() -> list[dict[str, Any]]:
    pine_dir = ROOT / "docs" / "tradingview"
    if not pine_dir.exists():
        return []
    rows = []
    for path in sorted(pine_dir.glob("*.pine")):
        content = path.read_text(encoding="utf-8", errors="replace")
        related = "btc" in path.name.lower() or "BTC" in content
        if not related:
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
        favorites = (
            session.query(FavoriteStrategy)
            .filter(FavoriteStrategy.symbol == symbol, FavoriteStrategy.timeframe == timeframe)
            .order_by(FavoriteStrategy.id.asc())
            .all()
        )
        favorites = [row for row in favorites if _direction(row.parameters) == direction]
        templates = session.query(ComboTemplate).order_by(ComboTemplate.name.asc()).all()

        return {
            "snapshot": {
                "card": 262,
                "timestamp_utc": timestamp.isoformat(),
                "symbol": symbol,
                "timeframe": timeframe,
                "direction": direction,
                "deep_backtest_revalidation_status": "pending",
            },
            "favorites": [_favorite_payload(row) for row in favorites],
            "templates": [_template_payload(row) for row in templates],
            "public_mappings": {
                "strategy_display_name": PUBLIC_STRATEGY_DISPLAY_NAMES,
                "strategy_description": PUBLIC_STRATEGY_DESCRIPTIONS,
                "source": MAPPING_SOURCE,
                "resolver_functions": [
                    "public_strategy_display_name",
                    "public_strategy_description",
                ],
            },
            "pine_scripts": _pine_payload(),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--timeframe", default="1d")
    parser.add_argument("--direction", default="long")
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
                "templates": len(payload["templates"]),
                "pine_scripts": len(payload["pine_scripts"]),
                "output": str(output),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
