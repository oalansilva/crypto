#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
os.chdir(ROOT)

from app.services.combo_optimizer import _metrics_from_trades, extract_trades_with_mode
from app.services.combo_service import ComboService
from app.services.market_data_providers import CCXT_SOURCE, get_market_data_provider


OUT_DIR = ROOT / "qa_artifacts" / "strategy_search_20260602"
SEARCH_REPORT = OUT_DIR / "search_round_9_12_report.json"
SYMBOL = "BTC/USDT"
TIMEFRAME = "1d"
DIRECTION = "long"
FULL_START = "2017-08-17"
FULL_END = "2026-06-02"
INITIAL_CAPITAL = 100


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(name: str, payload: Any) -> Path:
    path = OUT_DIR / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def subset(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        key: metrics.get(key)
        for key in (
            "total_trades",
            "win_rate",
            "total_return",
            "total_return_pct",
            "max_drawdown",
            "max_drawdown_pct",
            "sharpe_ratio",
            "profit_factor",
            "max_loss",
            "max_consecutive_losses",
            "expectancy_pct",
        )
    }


def run_backtest(service: ComboService, df, item: dict[str, Any], start: str, end: str) -> dict[str, Any]:
    params = dict(item["parameters"])
    strategy = service.create_strategy(item["template_name"], parameters=params)
    signals = strategy.generate_signals(df.copy())
    trades, mode = extract_trades_with_mode(
        signals,
        params.get("stop_loss", getattr(strategy, "stop_loss", 0.0)),
        deep_backtest=True,
        symbol=SYMBOL,
        since_str=start,
        until_str=end,
        direction=DIRECTION,
        return_mode=True,
    )
    metrics = _metrics_from_trades(trades, initial_capital=INITIAL_CAPITAL, context_params=params)
    return {
        "start": start,
        "end": end,
        "execution_mode": mode,
        "metrics": subset(metrics),
        "trade_count": len(trades),
        "conservative_cost_stress": cost_stress(trades, metrics),
    }


def cost_stress(trades: list[dict[str, Any]], metrics: dict[str, Any]) -> dict[str, Any]:
    trade_count = len(trades)
    # Approximate 20 bps round-trip drag per closed trade when the engine cannot
    # model fees/slippage directly for this validation path.
    drag_pct_points = trade_count * 0.20
    stressed_return_pct = float(metrics.get("total_return_pct") or 0.0) - drag_pct_points
    return {
        "method": "return_pct_minus_20bps_round_trip_per_trade",
        "trade_count": trade_count,
        "drag_pct_points": drag_pct_points,
        "stressed_total_return_pct": stressed_return_pct,
        "stressed_positive": stressed_return_pct > 0,
    }


def perturbations(item: dict[str, Any]) -> list[dict[str, Any]]:
    params = item["parameters"]
    trends = sorted({max(3, int(params.get("trend_length", 15)) + delta) for delta in (-3, 0, 3)})
    rocs = sorted({max(1, int(params.get("roc_length", 2)) + delta) for delta in (0, 2)})
    stops = sorted({round(max(0.005, float(params.get("stop_loss", 0.025)) + delta), 3) for delta in (-0.005, 0.0, 0.005)})
    rsis = [params.get("rsi_length")]
    if params.get("rsi_length") is not None:
        rsis = sorted({max(2, int(params["rsi_length"]) + delta) for delta in (-4, 0, 4)})
    adxs = [params.get("adx_length")]
    if params.get("adx_length") is not None:
        adxs = sorted({max(2, int(params["adx_length"]) + delta) for delta in (-4, 0, 4)})
    bbs = [params.get("bb_length")]
    if params.get("bb_length") is not None:
        bbs = sorted({max(5, int(params["bb_length"]) + delta) for delta in (-7, 0, 7)})

    rows: list[dict[str, Any]] = []
    for trend, roc, stop, rsi, adx, bb in itertools.product(trends, rocs, stops, rsis, adxs, bbs):
        candidate = dict(params)
        candidate["trend_length"] = trend
        candidate["roc_length"] = roc
        candidate["stop_loss"] = stop
        if rsi is not None:
            candidate["rsi_length"] = rsi
        if adx is not None:
            candidate["adx_length"] = adx
        if bb is not None:
            candidate["bb_length"] = bb
        rows.append(candidate)
    return rows[:54]


def stress_params(service: ComboService, df, item: dict[str, Any]) -> dict[str, Any]:
    outcomes = []
    for params in perturbations(item):
        variant = {**item, "parameters": params}
        try:
            result = run_backtest(service, df, variant, FULL_START, FULL_END)
            outcomes.append({"parameters": params, **result})
        except Exception as exc:
            outcomes.append({"parameters": params, "error": repr(exc)})
    ok = [
        row
        for row in outcomes
        if not row.get("error")
        and row.get("execution_mode") == "deep_15m"
        and (row["metrics"].get("total_trades") or 0) >= 8
        and (row["metrics"].get("total_return_pct") or 0.0) > 0.0
    ]
    returns = [row["metrics"].get("total_return_pct") or 0.0 for row in ok]
    drawdowns = [row["metrics"].get("max_drawdown_pct") or 999.0 for row in ok]
    return {
        "tested": len(outcomes),
        "valid_positive": len(ok),
        "positive_rate": len(ok) / len(outcomes) if outcomes else 0.0,
        "median_return_pct": sorted(returns)[len(returns) // 2] if returns else None,
        "worst_return_pct": min(returns) if returns else None,
        "worst_drawdown_pct": max(drawdowns) if drawdowns else None,
        "sample": outcomes[:12],
    }


def main() -> None:
    search = json.loads(SEARCH_REPORT.read_text(encoding="utf-8"))
    top = [
        row
        for row in search["top30"]
        if not row.get("dominated_by")
        and row.get("execution_mode") == "deep_15m"
        and (row["metrics"].get("total_trades") or 0) >= 8
    ][:6]
    service = ComboService()
    provider = get_market_data_provider(CCXT_SOURCE)
    full_df = provider.fetch_ohlcv(SYMBOL, TIMEFRAME, since_str=FULL_START, until_str=FULL_END)
    segments = [
        ("early", "2017-08-17", "2020-12-31"),
        ("middle", "2021-01-01", "2023-12-31"),
        ("oos_recent", "2024-01-01", "2026-06-02"),
        ("bear_2022", "2022-01-01", "2022-12-31"),
        ("recent_2025_2026", "2025-01-01", "2026-06-02"),
    ]
    finalists = []
    for row in top:
        segment_results = []
        for label, start, end in segments:
            df = provider.fetch_ohlcv(SYMBOL, TIMEFRAME, since_str=start, until_str=end)
            segment_results.append({"label": label, **run_backtest(service, df, row, start, end)})
        finalists.append(
            {
                "template_name": row["template_name"],
                "family": row["family"],
                "thesis": row["thesis"],
                "parameters": row["parameters"],
                "full_period": run_backtest(service, full_df, row, FULL_START, FULL_END),
                "segments": segment_results,
                "parameter_stress": stress_params(service, full_df, row),
                "source_metrics": row["metrics"],
                "source_strong_gate": row["strong_gate"],
            }
        )
    report = {
        "generated_at": now(),
        "config": {
            "symbol": SYMBOL,
            "timeframe": TIMEFRAME,
            "direction": DIRECTION,
            "deep_backtest": True,
            "initial_capital": INITIAL_CAPITAL,
            "entry_size_pct": 100,
            "exit_size_pct": 100,
            "pyramiding": 0,
            "allow_partial_exits": False,
        },
        "finalist_count": len(finalists),
        "finalists": finalists,
    }
    path = write_json("stress_round_9_12_report.json", report)
    print(json.dumps({"path": str(path), "finalist_count": len(finalists)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
