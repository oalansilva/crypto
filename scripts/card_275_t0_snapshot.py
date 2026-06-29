#!/usr/bin/env python3
"""Capture card #275 BTC/USDT 1D Short T0 evidence without mutating Favorites."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
import requests

from app.database import SessionLocal
from app.middleware.authMiddleware import ADMIN_EMAILS
from app.models import ComboTemplate, FavoriteStrategy, User
from app.services.combo_optimizer import ComboOptimizer
from app.services.favorite_backtest_refresh_service import (
    _fixed_optimization_ranges,
)
from app.services.strategy_descriptions import (
    PUBLIC_STRATEGY_DESCRIPTIONS,
    PUBLIC_STRATEGY_DISPLAY_NAMES,
    public_strategy_description,
    public_strategy_display_name,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-275-hard-mode-v5-btc-short"
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
        direction = str(parameters.get("direction") or "long").lower()
        return direction if direction in {"long", "short"} else "long"
    return "long"


def _metric(metrics: dict[str, Any], *names: str) -> float | None:
    for name in names:
        value = metrics.get(name)
        if value is None or isinstance(value, bool):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _metrics_summary(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "total_return": _metric(metrics, "total_return", "total_return_pct"),
        "total_return_pct": _metric(metrics, "total_return_pct", "total_return"),
        "max_drawdown": _metric(metrics, "max_drawdown", "max_drawdown_pct"),
        "max_drawdown_pct": _metric(metrics, "max_drawdown_pct", "max_drawdown"),
        "sharpe_ratio": _metric(metrics, "sharpe_ratio", "sharpe"),
        "profit_factor": _metric(metrics, "profit_factor"),
        "total_trades": _metric(metrics, "total_trades"),
        "win_rate": _metric(metrics, "win_rate"),
        "analysis_execution_mode": metrics.get("analysis_execution_mode"),
    }


def _dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    am = a["metrics_summary"]
    bm = b["metrics_summary"]
    ret_a = am.get("total_return_pct")
    ret_b = bm.get("total_return_pct")
    dd_a = am.get("max_drawdown_pct")
    dd_b = bm.get("max_drawdown_pct")
    if None in {ret_a, ret_b, dd_a, dd_b}:
        return False
    sharpe_a = am.get("sharpe_ratio")
    sharpe_b = bm.get("sharpe_ratio")
    pf_a = am.get("profit_factor")
    pf_b = bm.get("profit_factor")
    quality_ok = False
    if sharpe_a is not None and sharpe_b is not None and sharpe_a >= sharpe_b:
        quality_ok = True
    if pf_a is not None and pf_b is not None and pf_a >= pf_b:
        quality_ok = True
    if not quality_ok:
        return False
    return ret_a >= ret_b and dd_a <= dd_b and (
        ret_a > ret_b
        or dd_a < dd_b
        or (sharpe_a is not None and sharpe_b is not None and sharpe_a > sharpe_b)
        or (pf_a is not None and pf_b is not None and pf_a > pf_b)
    )


def _pareto(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    valid = [row for row in rows if row.get("status") == "ok"]
    return [
        row
        for row in valid
        if not any(
            other["favorite_id"] != row["favorite_id"] and _dominates(other, row)
            for other in valid
        )
    ]


def _benchmarks(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in rows if row.get("status") == "ok"]

    def best_max(key: str) -> dict[str, Any] | None:
        candidates = [row for row in valid if row["metrics_summary"].get(key) is not None]
        return max(candidates, key=lambda row: row["metrics_summary"][key], default=None)

    def best_min(key: str) -> dict[str, Any] | None:
        candidates = [row for row in valid if row["metrics_summary"].get(key) is not None]
        return min(candidates, key=lambda row: row["metrics_summary"][key], default=None)

    return {
        "BENCHMARK_RETURN": best_max("total_return_pct"),
        "BENCHMARK_DD": best_min("max_drawdown_pct"),
        "BENCHMARK_SHARPE": best_max("sharpe_ratio"),
        "BENCHMARK_PF": best_max("profit_factor"),
        "BENCHMARK_PARETO_SET": _pareto(rows),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _favorite_payload(row: FavoriteStrategy) -> dict[str, Any]:
    strategy_name = str(row.strategy_name)
    params = row.parameters if isinstance(row.parameters, dict) else {}
    return {
        "id": row.id,
        "name": row.name,
        "strategy_name": strategy_name,
        "strategy_display_name": public_strategy_display_name(strategy_name),
        "strategy_description": public_strategy_description(strategy_name),
        "direction": _direction(params),
        "parameters": _jsonable(params),
        "metrics": _jsonable(row.metrics),
        "start_date": row.start_date,
        "end_date": row.end_date,
        "period_type": row.period_type,
        "created_at": _jsonable(row.created_at),
        "auto_refresh_status": row.auto_refresh_status,
        "auto_refresh_completed_at": _jsonable(row.auto_refresh_completed_at),
    }


def _template_direction(row: ComboTemplate) -> str | None:
    for blob in (row.template_data, row.optimization_schema):
        if isinstance(blob, dict):
            explicit = str(blob.get("direction") or "").lower()
            if explicit in {"long", "short"}:
                return explicit
    name = str(row.name or "").lower()
    description = str(row.description or "").lower()
    text = f"{name}\n{description}"
    if name.startswith("short_") or "short-only" in text or "direction=short" in text:
        return "short"
    if name.startswith("long_") or "long-only" in text or "direction=long" in text:
        return "long"
    return None


def _template_payload(row: ComboTemplate) -> dict[str, Any]:
    direction = _template_direction(row)
    return {
        "name": row.name,
        "description": row.description,
        "public_description": public_strategy_description(row.name, row.description),
        "inferred_direction": direction,
        "compatible_with_short": direction in {None, "short"},
        "template_data": _jsonable(row.template_data),
        "optimization_schema": _jsonable(row.optimization_schema),
        "created_at": _jsonable(row.created_at),
        "updated_at": _jsonable(row.updated_at),
    }


def _pine_payload(direction: str) -> list[dict[str, Any]]:
    pine_dir = ROOT / "docs" / "tradingview"
    if not pine_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(pine_dir.rglob("*.pine")):
        content = path.read_text(encoding="utf-8", errors="replace")
        lower = f"{path.name}\n{content}".lower()
        if "btc" not in lower:
            continue
        rows.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
                "contains_strategy_short": "strategy.short" in content,
                "contains_strategy_long": "strategy.long" in content,
                "compatible_with_direction": (
                    "strategy.short" in content if direction == "short" else "strategy.long" in content
                ),
                "first_line": content.splitlines()[0] if content.splitlines() else "",
            }
        )
    return rows


def _admin_user() -> User | None:
    emails = sorted(ADMIN_EMAILS)
    if not emails:
        return None
    with SessionLocal() as session:
        user = session.query(User).filter(User.email.in_(emails)).order_by(User.email.asc()).first()
        if user:
            session.expunge(user)
        return user


def _access_token(user: User) -> str:
    secret = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "user_id": str(user.id),
        "email": user.email,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=15),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _api_favorites(api: str, symbol: str, timeframe: str, direction: str) -> dict[str, Any]:
    user = _admin_user()
    payload: dict[str, Any] = {
        "api": api,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "timeframe": timeframe,
        "direction": direction,
        "favorites": [],
    }
    if not user:
        payload["status"] = "skipped"
        payload["reason"] = "No admin user found for configured ADMIN_EMAILS"
        return payload
    try:
        response = requests.get(
            f"{api.rstrip('/')}/api/favorites/",
            headers={"Authorization": f"Bearer {_access_token(user)}"},
            timeout=30,
        )
        payload["status_code"] = response.status_code
        if not response.ok:
            payload["status"] = "error"
            payload["error"] = response.text[:1000]
            return payload
        rows = response.json()
        payload["status"] = "ok"
        payload["favorites"] = [
            row
            for row in rows
            if row.get("symbol") == symbol
            and row.get("timeframe") == timeframe
            and _direction(row.get("parameters")) == direction
        ]
    except Exception as exc:  # noqa: BLE001 - evidence artifact
        payload["status"] = "error"
        payload["error"] = f"{exc.__class__.__name__}: {str(exc)[:1000]}"
    return payload


def _revalidate_favorites(
    favorites: list[FavoriteStrategy],
    symbol: str,
    timeframe: str,
    direction: str,
) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    rows: list[dict[str, Any]] = []
    optimizer = ComboOptimizer()
    for favorite in favorites:
        params = favorite.parameters if isinstance(favorite.parameters, dict) else {}
        result_row: dict[str, Any] = {
            "favorite_id": favorite.id,
            "name": favorite.name,
            "strategy_name": favorite.strategy_name,
            "saved_parameters": _jsonable(params),
            "payload": {
                "template_name": favorite.strategy_name,
                "symbol": symbol,
                "timeframe": timeframe,
                "data_source": params.get("data_source") or "ccxt",
                "start_date": favorite.start_date,
                "end_date": datetime.now(timezone.utc).date().isoformat(),
                "custom_ranges": _fixed_optimization_ranges(params),
                "deep_backtest": True,
                "initial_capital": 100,
                "direction": direction,
            },
        }
        try:
            result = optimizer.run_optimization(
                template_name=favorite.strategy_name,
                symbol=symbol,
                timeframe=timeframe,
                data_source=result_row["payload"]["data_source"],
                start_date=favorite.start_date,
                end_date=result_row["payload"]["end_date"],
                custom_ranges=result_row["payload"]["custom_ranges"],
                deep_backtest=True,
                direction=direction,
            )
            metrics = result.get("best_metrics") or result.get("metrics") or {}
            result_row.update(
                {
                    "status": "ok",
                    "execution_mode": result.get("execution_mode")
                    or metrics.get("analysis_execution_mode"),
                    "best_parameters": _jsonable(result.get("best_parameters") or result.get("parameters")),
                    "metrics_summary": _metrics_summary(metrics),
                    "trades_count": len(result.get("trades") or metrics.get("trades") or []),
                }
            )
        except Exception as exc:  # noqa: BLE001 - evidence artifact
            result_row.update(
                {
                    "status": "error",
                    "error": f"{exc.__class__.__name__}: {str(exc)[:1000]}",
                }
            )
        rows.append(result_row)
    return {
        "started_at": started.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "results": rows,
        "benchmarks": _benchmarks(rows),
    }


def capture(symbol: str, timeframe: str, direction: str, api: str) -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc)
    with SessionLocal() as session:
        all_favorites = (
            session.query(FavoriteStrategy)
            .filter(FavoriteStrategy.symbol == symbol, FavoriteStrategy.timeframe == timeframe)
            .order_by(FavoriteStrategy.id.asc())
            .all()
        )
        directional_favorites = [
            row for row in all_favorites if _direction(row.parameters) == direction
        ]
        for row in directional_favorites:
            session.expunge(row)

        templates = session.query(ComboTemplate).order_by(ComboTemplate.name.asc()).all()
        template_payloads = [_template_payload(row) for row in templates]

        return {
            "snapshot": {
                "card": 275,
                "timestamp_utc": timestamp.isoformat(),
                "symbol": symbol,
                "timeframe": timeframe,
                "direction": direction,
                "invariants": {
                    "deep_backtest": True,
                    "initial_capital": 100,
                    "entry_size_pct": 100,
                    "exit_size_pct": 100,
                    "pyramiding": 0,
                    "allow_partial_exits": False,
                    "mixed_directions_allowed": False,
                },
            },
            "favorites": [_favorite_payload(row) for row in directional_favorites],
            "favorite_counts": {
                "all_symbol_timeframe": len(all_favorites),
                "directional": len(directional_favorites),
                "by_direction": {
                    side: sum(1 for row in all_favorites if _direction(row.parameters) == side)
                    for side in ["long", "short"]
                },
            },
            "favorites_api": _api_favorites(api, symbol, timeframe, direction),
            "templates": template_payloads,
            "compatible_templates": [
                row for row in template_payloads if row["compatible_with_short"]
            ],
            "public_mappings": {
                "strategy_display_name": PUBLIC_STRATEGY_DISPLAY_NAMES,
                "strategy_description": PUBLIC_STRATEGY_DESCRIPTIONS,
                "source": MAPPING_SOURCE,
                "resolver_functions": [
                    "public_strategy_display_name",
                    "public_strategy_description",
                ],
            },
            "pine_scripts": _pine_payload(direction),
            "revalidated_favorites": _revalidate_favorites(
                directional_favorites, symbol, timeframe, direction
            ),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--timeframe", default="1d")
    parser.add_argument("--direction", default="short")
    parser.add_argument("--api", default="http://127.0.0.1:8003")
    args = parser.parse_args()

    if args.direction not in {"long", "short"}:
        raise SystemExit("direction must be long or short")
    if not os.getenv("DATABASE_URL"):
        raise SystemExit("DATABASE_URL is required")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    payload = capture(args.symbol, args.timeframe, args.direction, args.api)
    stamp = payload["snapshot"]["timestamp_utc"].replace(":", "").replace("+", "Z")
    output = ARTIFACT_DIR / f"t0-snapshot-{stamp}.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    latest = ARTIFACT_DIR / "t0-snapshot-latest.json"
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    summary = {
        "output": str(output.relative_to(ROOT)),
        "favorites_directional": len(payload["favorites"]),
        "favorites_api_directional": len(payload["favorites_api"].get("favorites") or []),
        "templates_total": len(payload["templates"]),
        "compatible_templates": len(payload["compatible_templates"]),
        "pine_scripts": len(payload["pine_scripts"]),
        "revalidated_ok": sum(
            1 for row in payload["revalidated_favorites"]["results"] if row.get("status") == "ok"
        ),
        "benchmark_return_exists": payload["revalidated_favorites"]["benchmarks"]["BENCHMARK_RETURN"] is not None,
    }
    print(output)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
