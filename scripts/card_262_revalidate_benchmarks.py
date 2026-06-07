#!/usr/bin/env python3
"""Revalidate issue #262 BTC/USDT 1d Long T0 Favorites with Deep Backtest."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.database import SessionLocal
from app.models import FavoriteStrategy
from app.services.combo_optimizer import ComboOptimizer
from app.services.favorite_backtest_refresh_service import (
    _fixed_optimization_ranges,
    _favorite_direction,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-262-hard-mode-v5"


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def _metric(metrics: dict[str, Any], *names: str) -> float | None:
    for name in names:
        value = metrics.get(name)
        if value is None:
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
    sharpe_a = am.get("sharpe_ratio")
    sharpe_b = bm.get("sharpe_ratio")
    pf_a = am.get("profit_factor")
    pf_b = bm.get("profit_factor")
    if None in {ret_a, ret_b, dd_a, dd_b}:
        return False
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
    out = []
    for row in valid:
        if not any(other["favorite_id"] != row["favorite_id"] and _dominates(other, row) for other in valid):
            out.append(row)
    return out


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


def _favorite_rows(symbol: str, timeframe: str, direction: str) -> list[FavoriteStrategy]:
    with SessionLocal() as session:
        rows = (
            session.query(FavoriteStrategy)
            .filter(FavoriteStrategy.symbol == symbol, FavoriteStrategy.timeframe == timeframe)
            .order_by(FavoriteStrategy.id.asc())
            .all()
        )
        selected = []
        for row in rows:
            params = row.parameters if isinstance(row.parameters, dict) else {}
            if _favorite_direction(params) == direction:
                session.expunge(row)
                selected.append(row)
        return selected


def revalidate(symbol: str, timeframe: str, direction: str) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    rows = []
    optimizer = ComboOptimizer()
    for favorite in _favorite_rows(symbol, timeframe, direction):
        params = favorite.parameters if isinstance(favorite.parameters, dict) else {}
        data_source = params.get("data_source") or "ccxt"
        result_row: dict[str, Any] = {
            "favorite_id": favorite.id,
            "name": favorite.name,
            "strategy_name": favorite.strategy_name,
            "saved_parameters": _jsonable(params),
            "payload": {
                "template_name": favorite.strategy_name,
                "symbol": favorite.symbol,
                "timeframe": favorite.timeframe,
                "data_source": data_source,
                "start_date": favorite.start_date,
                "end_date": datetime.now(timezone.utc).date().isoformat(),
                "custom_ranges": _fixed_optimization_ranges(params),
                "deep_backtest": True,
                "initial_capital": 100,
                "direction": direction,
            },
        }
        t0 = time.time()
        try:
            result = optimizer.run_optimization(
                template_name=favorite.strategy_name,
                symbol=favorite.symbol,
                timeframe=favorite.timeframe,
                data_source=data_source,
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
                    "duration_seconds": round(time.time() - t0, 3),
                    "execution_mode": result.get("execution_mode")
                    or metrics.get("analysis_execution_mode"),
                    "best_parameters": _jsonable(result.get("best_parameters") or result.get("parameters")),
                    "metrics_summary": _metrics_summary(metrics),
                    "trades_count": len(result.get("trades") or metrics.get("trades") or []),
                    "candles_count": len(result.get("candles") or []),
                }
            )
        except Exception as exc:  # noqa: BLE001 - evidence artifact should capture exact blocker
            result_row.update(
                {
                    "status": "error",
                    "duration_seconds": round(time.time() - t0, 3),
                    "error": f"{exc.__class__.__name__}: {str(exc)[:1000]}",
                }
            )
        rows.append(result_row)

    payload = {
        "card": 262,
        "started_at": started.isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
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
        },
        "results": rows,
        "benchmarks": _benchmarks(rows),
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--timeframe", default="1d")
    parser.add_argument("--direction", default="long")
    args = parser.parse_args()
    if not os.getenv("DATABASE_URL"):
        raise SystemExit("DATABASE_URL is required")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    payload = revalidate(args.symbol, args.timeframe, args.direction)
    stamp = payload["completed_at"].replace(":", "").replace("+", "Z")
    output = ARTIFACT_DIR / f"benchmark-revalidation-{stamp}.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    latest = ARTIFACT_DIR / "benchmark-revalidation-latest.json"
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(output)
    print(
        json.dumps(
            {
                "ok": sum(1 for row in payload["results"] if row.get("status") == "ok"),
                "errors": sum(1 for row in payload["results"] if row.get("status") != "ok"),
                "output": str(output),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
