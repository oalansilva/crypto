#!/usr/bin/env python3
"""Capture T0 and deep benchmark evidence for issue #261."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
import pandas as pd
import requests
from sqlalchemy import create_engine, text

from app.middleware.authMiddleware import ADMIN_EMAILS, JWT_SECRET
from app.routes.combo_routes import execute_combo_backtest
from app.schemas.combo_params import ComboBacktestRequest
from app.services.strategy_descriptions import (
    PUBLIC_STRATEGY_DESCRIPTIONS,
    PUBLIC_STRATEGY_DISPLAY_NAMES,
    public_strategy_description,
    public_strategy_display_name,
)
from src.data.incremental_loader import IncrementalLoader


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-261-hard-mode-v3-btc-pareto"
SYMBOL = "BTC/USDT"
TIMEFRAME = "1d"
DIRECTION = "long"
INITIAL_CAPITAL = 100
FULL_START = "2017-08-17"
FULL_END = "2026-06-07"
API_BASE = os.getenv("CARD_261_API_BASE", "http://127.0.0.1:8003")


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return str(value)


def _decode(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _sanitize_metrics(metrics: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(metrics, dict):
        return {}
    public = {}
    allowed = {
        "total_trades",
        "win_rate",
        "total_return",
        "total_return_pct",
        "avg_profit",
        "max_drawdown",
        "max_drawdown_pct",
        "profit_factor",
        "sharpe_ratio",
        "analysis_execution_mode",
        "auto_refreshed_at",
        "trades_history_cached",
    }
    for key in allowed:
        if key in metrics:
            public[key] = metrics[key]
    return public


def _metric(result: dict[str, Any], key: str) -> float | None:
    metrics = result.get("metrics") or {}
    value = metrics.get(key)
    if value is None and key == "sharpe_ratio":
        value = metrics.get("sharpe")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    ar = _metric(a, "total_return_pct")
    br = _metric(b, "total_return_pct")
    add = _metric(a, "max_drawdown_pct")
    bdd = _metric(b, "max_drawdown_pct")
    asharpe = _metric(a, "sharpe_ratio")
    bsharpe = _metric(b, "sharpe_ratio")
    apf = _metric(a, "profit_factor")
    bpf = _metric(b, "profit_factor")
    if ar is None or br is None or add is None or bdd is None:
        return False
    quality_ge = False
    quality_strict = False
    if asharpe is not None and bsharpe is not None:
        quality_ge = quality_ge or asharpe >= bsharpe
        quality_strict = quality_strict or asharpe > bsharpe
    if apf is not None and bpf is not None:
        quality_ge = quality_ge or apf >= bpf
        quality_strict = quality_strict or apf > bpf
    if not quality_ge:
        return False
    return ar >= br and add <= bdd and (ar > br or add < bdd or quality_strict)


def _pareto(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in results:
        if not any(_dominates(other, row) for other in results if other is not row):
            out.append(row)
    return out


def _load_rows(engine) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    with engine.connect() as conn:
        favorite_rows = [
            dict(row)
            for row in conn.execute(
                text(
                    """
                    SELECT id, user_id, name, symbol, timeframe, strategy_name, parameters, metrics,
                           start_date, end_date, period_type, created_at, notes, tier,
                           notify_telegram, auto_refresh_status, auto_refresh_error,
                           auto_refresh_started_at, auto_refresh_completed_at,
                           auto_refresh_run_id
                    FROM favorite_strategies
                    WHERE symbol = :symbol AND timeframe = :timeframe
                    ORDER BY id
                    """
                ),
                {"symbol": SYMBOL, "timeframe": TIMEFRAME},
            ).mappings()
        ]
        template_rows = [
            dict(row)
            for row in conn.execute(
                text(
                    """
                    SELECT id, name, description, is_prebuilt, is_example, is_readonly,
                           template_data, optimization_schema, created_at, updated_at
                    FROM combo_templates
                    ORDER BY name
                    """
                )
            ).mappings()
        ]

    for row in favorite_rows:
        row["parameters"] = _decode(row.get("parameters"))
        row["metrics"] = _decode(row.get("metrics"))
        row["strategy_display_name"] = public_strategy_display_name(row.get("strategy_name"))
        row["strategy_description"] = public_strategy_description(row.get("strategy_name"))
    for row in template_rows:
        row["template_data"] = _decode(row.get("template_data"))
        row["optimization_schema"] = _decode(row.get("optimization_schema"))
    return favorite_rows, template_rows


def _admin_token(engine) -> tuple[str | None, str | None]:
    admin_emails = sorted(ADMIN_EMAILS)
    if not admin_emails:
        return None, None
    with engine.connect() as conn:
        user = conn.execute(
            text(
                """
                SELECT id, email
                FROM users
                WHERE lower(email) = ANY(:emails)
                ORDER BY email
                LIMIT 1
                """
            ),
            {"emails": admin_emails},
        ).mappings().first()
    if not user:
        return None, None
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user["id"]),
        "email": str(user["email"]).lower(),
        "type": "access",
        "exp": now + timedelta(minutes=15),
        "iat": now,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256"), str(user["id"])


def _api_favorites(engine) -> dict[str, Any]:
    token, user_id = _admin_token(engine)
    if not token:
        return {"available": False, "reason": "admin user/token unavailable"}
    response = requests.get(
        f"{API_BASE}/api/favorites/",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    data = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
    relevant = []
    if isinstance(data, list):
        for row in data:
            params = row.get("parameters") if isinstance(row, dict) else {}
            if (
                row.get("symbol") == SYMBOL
                and row.get("timeframe") == TIMEFRAME
                and str((params or {}).get("direction") or "long").lower() == DIRECTION
            ):
                relevant.append(
                    {
                        "id": row.get("id"),
                        "name": row.get("name"),
                        "strategy_name": row.get("strategy_name"),
                        "strategy_display_name": row.get("strategy_display_name"),
                        "strategy_description": row.get("strategy_description"),
                        "metrics": _sanitize_metrics(row.get("metrics")),
                        "auto_refresh_status": row.get("auto_refresh_status"),
                        "auto_refresh_completed_at": row.get("auto_refresh_completed_at"),
                    }
                )
    return {
        "available": response.ok,
        "status_code": response.status_code,
        "user_id": user_id,
        "relevant_favorites": relevant,
    }


async def _deep_backtest(row: dict[str, Any]) -> dict[str, Any]:
    params = row.get("parameters") if isinstance(row.get("parameters"), dict) else {}
    params = {**params, "direction": DIRECTION, "data_source": params.get("data_source") or "ccxt"}
    request = ComboBacktestRequest(
        template_name=row["strategy_name"],
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        start_date=FULL_START,
        end_date=FULL_END,
        parameters=params,
        deep_backtest=True,
        initial_capital=INITIAL_CAPITAL,
        direction=DIRECTION,
    )
    result = await execute_combo_backtest(request)
    return {
        "favorite_id": row["id"],
        "name": row["name"],
        "strategy_name": row["strategy_name"],
        "parameters": params,
        "payload": request.model_dump(),
        "execution_mode": result.get("execution_mode"),
        "metrics": result.get("metrics") or {},
        "trade_count": len(result.get("trades") or []),
        "first_candle": (result.get("candles") or [{}])[0].get("timestamp_utc"),
        "last_candle": (result.get("candles") or [{}])[-1].get("timestamp_utc"),
    }


def _buy_and_hold() -> dict[str, Any]:
    loader = IncrementalLoader()
    df = loader.fetch_data(SYMBOL, TIMEFRAME, FULL_START, FULL_END, read_only=True)
    if df.empty:
        return {"available": False}
    closes = df["close"].astype(float)
    equity = closes / closes.iloc[0]
    drawdown = (equity.cummax() - equity) / equity.cummax()
    returns = closes.pct_change().dropna()
    sharpe = None
    if len(returns) > 1 and float(returns.std()) > 0:
        sharpe = float((returns.mean() / returns.std()) * math.sqrt(365))
    return {
        "available": True,
        "first_candle": str(df.index.min()),
        "last_candle": str(df.index.max()),
        "metrics": {
            "total_return_pct": float((closes.iloc[-1] / closes.iloc[0] - 1) * 100),
            "max_drawdown_pct": float(drawdown.max() * 100),
            "sharpe_ratio": sharpe,
            "profit_factor": None,
            "total_trades": 1,
        },
    }


def _pine_files() -> list[dict[str, Any]]:
    out = []
    for path in sorted((ROOT / "docs" / "tradingview").glob("*.pine")):
        text_value = path.read_text(encoding="utf-8")
        if "btc" not in path.name.lower() and "BTC" not in text_value:
            continue
        out.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": hashlib.sha256(text_value.encode("utf-8")).hexdigest(),
                "size_bytes": len(text_value.encode("utf-8")),
            }
        )
    return out


async def main() -> None:
    logging.disable(logging.CRITICAL)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)

    favorite_rows, template_rows = _load_rows(engine)
    relevant_favorites = [
        row
        for row in favorite_rows
        if str((row.get("parameters") or {}).get("direction") or "long").lower() == DIRECTION
    ]
    revalidated = []
    for row in relevant_favorites:
        revalidated.append(await _deep_backtest(row))

    pareto = _pareto(revalidated)
    benchmark_return = max(revalidated, key=lambda r: _metric(r, "total_return_pct") or float("-inf"))
    benchmark_sharpe = max(revalidated, key=lambda r: _metric(r, "sharpe_ratio") or float("-inf"))
    benchmark_pf = max(revalidated, key=lambda r: _metric(r, "profit_factor") or float("-inf"))
    competitive = [
        row
        for row in revalidated
        if (_metric(row, "total_return_pct") or 0)
        >= 0.75 * (_metric(benchmark_return, "total_return_pct") or 0)
    ] or revalidated
    benchmark_dd = min(competitive, key=lambda r: _metric(r, "max_drawdown_pct") or float("inf"))

    snapshot = {
        "captured_at": timestamp,
        "card": 261,
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "direction": DIRECTION,
        "period": {"start_date": FULL_START, "end_date": FULL_END, "period_type": "all"},
        "invariants": {
            "deep_backtest": True,
            "initial_capital_usd": INITIAL_CAPITAL,
            "entry_size_pct": 100,
            "exit_size_pct": 100,
            "pyramiding": 0,
            "allow_partial_exits": False,
        },
        "favorites": relevant_favorites,
        "favorites_api": _api_favorites(engine),
        "templates": template_rows,
        "public_mappings": {
            "display_names": PUBLIC_STRATEGY_DISPLAY_NAMES,
            "descriptions": PUBLIC_STRATEGY_DESCRIPTIONS,
        },
        "pine_scripts": _pine_files(),
        "revalidated_favorites": revalidated,
        "baselines": {
            "multi_ma_crossover": next(
                (r for r in revalidated if r["strategy_name"] == "multi_ma_crossover"), None
            ),
            "multi_ma_crossoverV2": next(
                (r for r in revalidated if r["strategy_name"] == "multi_ma_crossoverV2"), None
            ),
            "buy_and_hold": _buy_and_hold(),
        },
        "benchmarks": {
            "BENCHMARK_RETURN": benchmark_return,
            "BENCHMARK_DD": benchmark_dd,
            "BENCHMARK_SHARPE": benchmark_sharpe,
            "BENCHMARK_PF": benchmark_pf,
            "BENCHMARK_PARETO_SET": pareto,
        },
    }
    filename_ts = timestamp.replace(":", "").replace("-", "").replace("+0000", "Z")
    output = ARTIFACT_DIR / f"t0_snapshot_{filename_ts}.json"
    output.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
    summary = {
        "output": str(output.relative_to(ROOT)),
        "captured_at": timestamp,
        "favorites": len(relevant_favorites),
        "templates": len(template_rows),
        "pine_scripts": len(snapshot["pine_scripts"]),
        "execution_modes": sorted({r["execution_mode"] for r in revalidated}),
        "benchmark_return": {
            "favorite_id": benchmark_return["favorite_id"],
            "strategy_name": benchmark_return["strategy_name"],
            "total_return_pct": _metric(benchmark_return, "total_return_pct"),
            "max_drawdown_pct": _metric(benchmark_return, "max_drawdown_pct"),
        },
        "pareto_ids": [row["favorite_id"] for row in pareto],
    }
    print(json.dumps(summary, ensure_ascii=False, default=_json_default))


if __name__ == "__main__":
    asyncio.run(main())
