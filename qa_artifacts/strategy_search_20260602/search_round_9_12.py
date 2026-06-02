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

from app.database import SessionLocal
from app.models import ComboTemplate
from app.services.combo_optimizer import _metrics_from_trades, extract_trades_with_mode
from app.services.combo_service import ComboService
from app.services.market_data_providers import CCXT_SOURCE, get_market_data_provider


OUT_DIR = ROOT / "qa_artifacts" / "strategy_search_20260602"
SYMBOL = "BTC/USDT"
TIMEFRAME = "1d"
DIRECTION = "long"
START = "2017-08-17"
END = "2026-06-02"
INITIAL_CAPITAL = 100
PREFIX = "tmp_quant_20260602c_"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(name: str, payload: Any) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def ensure_template(name: str, description: str, template_data: dict[str, Any]) -> int:
    with SessionLocal() as db:
        row = db.query(ComboTemplate).filter(ComboTemplate.name == name).first()
        if row is None:
            row = ComboTemplate(
                name=name,
                description=description,
                is_prebuilt=False,
                is_example=False,
                is_readonly=False,
                template_data=template_data,
                optimization_schema={"parameters": {}, "correlated_groups": []},
            )
            db.add(row)
        else:
            row.description = description
            row.template_data = template_data
        db.commit()
        db.refresh(row)
        return int(row.id)


def metric_subset(metrics: dict[str, Any]) -> dict[str, Any]:
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


def dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    am = a["metrics"]
    bm = b["metrics"]
    ret = (am.get("total_return_pct") or -10**18) >= (bm.get("total_return_pct") or -10**18)
    dd = (am.get("max_drawdown_pct") or 10**18) <= (bm.get("max_drawdown_pct") or 10**18)
    spf = ((am.get("sharpe_ratio") or -10**18) >= (bm.get("sharpe_ratio") or -10**18)) or (
        (am.get("profit_factor") or -10**18) >= (bm.get("profit_factor") or -10**18)
    )
    strict = (
        (am.get("total_return_pct") or -10**18) > (bm.get("total_return_pct") or -10**18)
        or (am.get("max_drawdown_pct") or 10**18) < (bm.get("max_drawdown_pct") or 10**18)
        or (am.get("sharpe_ratio") or -10**18) > (bm.get("sharpe_ratio") or -10**18)
        or (am.get("profit_factor") or -10**18) > (bm.get("profit_factor") or -10**18)
    )
    return ret and dd and spf and strict


def concentration(trades: list[dict[str, Any]], total_return_pct: float) -> dict[str, Any]:
    profits = []
    for trade in trades:
        value = trade.get("profit_pct")
        if value is None and trade.get("profit") is not None:
            value = float(trade["profit"]) * 100.0
        if value is not None:
            profits.append(float(value))
    positives = sorted((p for p in profits if p > 0), reverse=True)
    denom = abs(total_return_pct) or 1.0
    return {
        "largest_trade_return_pct": positives[0] if positives else 0.0,
        "top5_return_pct_sum": sum(positives[:5]),
        "largest_trade_share_of_total_return": (positives[0] if positives else 0.0) / denom,
        "top5_share_of_total_return": sum(positives[:5]) / denom,
        "positive_trade_count": len(positives),
    }


def load_benchmarks() -> list[dict[str, Any]]:
    deep = json.loads((OUT_DIR / "api_deep_revalidation_t0_20260602.json").read_text())
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "strategy_name": row["strategy_name"],
            "metrics": row["metrics"],
            "execution_mode": row.get("execution_mode") or row.get("metrics", {}).get("analysis_execution_mode"),
        }
        for row in deep["results"]
        if row.get("status") == 200 and (row.get("metrics", {}).get("total_trades") or 0) >= 8
    ]


def template_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for rsi_min, rsi_max, rsi_exit in [(42, 86, 38), (45, 84, 39), (48, 82, 40), (50, 80, 42)]:
        specs.append(
            {
                "cycle": 9,
                "family": "ema_roc_rsi_quality",
                "name": f"{PREFIX}ema_roc_rsi_q_{rsi_min}_{rsi_max}_{rsi_exit}",
                "thesis": "EMA/ROC compounding with RSI quality gates tries to keep the high-return Pareto member while removing exhausted or weak entries.",
                "template_data": {
                    "indicators": [
                        {"type": "ema", "alias": "trend", "params": {"length": 12}},
                        {"type": "roc", "alias": "roc", "params": {"length": 2}},
                        {"type": "rsi", "alias": "rsi", "params": {"length": 14}},
                    ],
                    "entry_logic": f"(close > trend) & (roc > 0) & (rsi > {rsi_min}) & (rsi < {rsi_max})",
                    "exit_logic": f"(close < trend) | (roc < -1) | (rsi < {rsi_exit})",
                    "stop_loss": 0.025,
                },
                "grid": {
                    "trend_length": [9, 12, 15, 18],
                    "roc_length": [2, 4, 6],
                    "rsi_length": [10, 14, 18, 22],
                    "stop_loss": [0.02, 0.025, 0.03, 0.035],
                },
            }
        )
    for adx_min, adx_exit in [(12, 10), (15, 11), (18, 13), (20, 15)]:
        specs.append(
            {
                "cycle": 10,
                "family": "ema_roc_adx_regime",
                "name": f"{PREFIX}ema_roc_adx_{adx_min}_{adx_exit}",
                "thesis": "ADX regime filter targets the high-return EMA/ROC member but rejects low-strength continuation.",
                "template_data": {
                    "indicators": [
                        {"type": "ema", "alias": "trend", "params": {"length": 12}},
                        {"type": "roc", "alias": "roc", "params": {"length": 2}},
                        {"type": "adx", "alias": "adx", "params": {"length": 14}},
                    ],
                    "entry_logic": f"(close > trend) & (roc > 0) & (adx > {adx_min})",
                    "exit_logic": f"(close < trend) | (roc < -1) | (adx < {adx_exit})",
                    "stop_loss": 0.025,
                },
                "grid": {
                    "trend_length": [9, 12, 15, 18],
                    "roc_length": [2, 4, 6],
                    "adx_length": [10, 14, 18],
                    "stop_loss": [0.02, 0.025, 0.03, 0.035],
                },
            }
        )
    for fast, slow, signal in [(8, 21, 5), (10, 22, 6), (12, 26, 8)]:
        specs.append(
            {
                "cycle": 11,
                "family": "ema_roc_macd_quality",
                "name": f"{PREFIX}ema_roc_macd_{fast}_{slow}_{signal}",
                "thesis": "MACD confirmation aims for a materially different momentum quality gate versus raw ROC continuation.",
                "template_data": {
                    "indicators": [
                        {"type": "ema", "alias": "trend", "params": {"length": 12}},
                        {"type": "roc", "alias": "roc", "params": {"length": 2}},
                        {"type": "macd", "alias": "m", "params": {"fast": fast, "slow": slow, "signal": signal}},
                    ],
                    "entry_logic": "(close > trend) & (roc > 0) & (m_histogram > 0)",
                    "exit_logic": "(close < trend) | (roc < -1) | (m_histogram < 0)",
                    "stop_loss": 0.025,
                },
                "grid": {
                    "trend_length": [9, 12, 15, 18],
                    "roc_length": [2, 4, 6],
                    "m_fast": [fast],
                    "m_slow": [slow],
                    "m_signal": [signal],
                    "stop_loss": [0.02, 0.025, 0.03, 0.035],
                },
            }
        )
    for bb_std, rsi_min in [(1.8, 46), (2.0, 46), (2.2, 48), (2.4, 50)]:
        specs.append(
            {
                "cycle": 12,
                "family": "bbands_ema_roc_quality",
                "name": f"{PREFIX}bb_ema_roc_q_{str(bb_std).replace('.', '_')}_{rsi_min}",
                "thesis": "Bollinger volatility quality plus ROC attempts a defensive Pareto profile distinct from raw EMA/ROC.",
                "template_data": {
                    "indicators": [
                        {"type": "ema", "alias": "trend", "params": {"length": 12}},
                        {"type": "roc", "alias": "roc", "params": {"length": 2}},
                        {"type": "bbands", "alias": "bb", "params": {"length": 21, "std": bb_std}},
                        {"type": "rsi", "alias": "rsi", "params": {"length": 14}},
                    ],
                    "entry_logic": f"(close > trend) & (close > bb_middle) & (close < bb_upper) & (roc > 0) & (rsi > {rsi_min})",
                    "exit_logic": "(close < bb_middle) | (roc < -1) | (rsi < 40)",
                    "stop_loss": 0.025,
                },
                "grid": {
                    "trend_length": [9, 12, 15, 18],
                    "roc_length": [2, 4, 6],
                    "bb_length": [14, 21, 28],
                    "bb_std": [bb_std],
                    "rsi_length": [10, 14, 18],
                    "stop_loss": [0.02, 0.025, 0.03, 0.035],
                },
            }
        )
    return specs


def grid_values(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = list(grid)
    return [dict(zip(keys, values)) for values in itertools.product(*(grid[key] for key in keys))]


def main() -> None:
    started_at = now()
    benchmarks = load_benchmarks()
    benchmark_return = max(benchmarks, key=lambda item: item["metrics"].get("total_return_pct") or -10**18)
    service = ComboService()
    provider = get_market_data_provider(CCXT_SOURCE)
    df = provider.fetch_ohlcv(SYMBOL, TIMEFRAME, since_str=START, until_str=END)
    created: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for spec in template_specs():
        template_id = ensure_template(spec["name"], "Temporary hard-mode round 9-12 candidate.", spec["template_data"])
        created.append({"id": template_id, "name": spec["name"], "cycle": spec["cycle"], "family": spec["family"], "thesis": spec["thesis"]})
        for params in grid_values(spec["grid"]):
            full_params = {**params, "direction": DIRECTION, "data_source": "ccxt"}
            try:
                strategy = service.create_strategy(spec["name"], parameters=full_params)
                signals = strategy.generate_signals(df.copy())
                trades, mode = extract_trades_with_mode(
                    signals,
                    full_params.get("stop_loss", getattr(strategy, "stop_loss", 0.0)),
                    deep_backtest=True,
                    symbol=SYMBOL,
                    since_str=START,
                    until_str=END,
                    direction=DIRECTION,
                    return_mode=True,
                )
                metrics = _metrics_from_trades(trades, initial_capital=INITIAL_CAPITAL, context_params=full_params)
                item = {
                    "template_name": spec["name"],
                    "cycle": spec["cycle"],
                    "family": spec["family"],
                    "thesis": spec["thesis"],
                    "parameters": full_params,
                    "execution_mode": mode,
                    "metrics": metric_subset(metrics),
                    "concentration": concentration(trades, metrics.get("total_return_pct") or 0.0),
                }
                item["dominated_by"] = [
                    {"id": b["id"], "name": b["name"], "strategy_name": b["strategy_name"], "metrics": metric_subset(b["metrics"])}
                    for b in benchmarks
                    if dominates(b, item)
                    or (
                        (b["metrics"].get("total_return_pct") or 0.0) > (metrics.get("total_return_pct") or 0.0)
                        and (b["metrics"].get("max_drawdown_pct") or 999.0) <= (metrics.get("max_drawdown_pct") or 999.0)
                    )
                ]
                item["strong_gate"] = {
                    "dominance_clear": (metrics.get("total_return_pct") or 0.0) >= (benchmark_return["metrics"].get("total_return_pct") or 0.0)
                    and (metrics.get("max_drawdown_pct") or 999.0) <= (benchmark_return["metrics"].get("max_drawdown_pct") or 999.0)
                    and (metrics.get("profit_factor") or 0.0) >= (benchmark_return["metrics"].get("profit_factor") or 0.0) * 0.95,
                    "new_pareto_defensible": (metrics.get("total_return_pct") or 0.0) >= (benchmark_return["metrics"].get("total_return_pct") or 0.0) * 0.90
                    and (metrics.get("max_drawdown_pct") or 999.0) <= (benchmark_return["metrics"].get("max_drawdown_pct") or 999.0) * 0.85
                    and (metrics.get("profit_factor") or 0.0) > (benchmark_return["metrics"].get("profit_factor") or 0.0),
                    "defensive_exceptional": (metrics.get("total_return_pct") or 0.0) >= (benchmark_return["metrics"].get("total_return_pct") or 0.0) * 0.75
                    and (metrics.get("max_drawdown_pct") or 999.0) <= (benchmark_return["metrics"].get("max_drawdown_pct") or 999.0) * 0.75
                    and (metrics.get("profit_factor") or 0.0) > (benchmark_return["metrics"].get("profit_factor") or 0.0),
                }
                candidates.append(item)
            except Exception as exc:
                failures.append({"template": spec["name"], "parameters": params, "error": repr(exc)})

    ranking = sorted(
        candidates,
        key=lambda item: (
            not item["dominated_by"],
            any(item["strong_gate"].values()),
            item["metrics"].get("total_return_pct") or -10**18,
            -(item["metrics"].get("max_drawdown_pct") or 999.0),
            item["metrics"].get("profit_factor") or 0.0,
        ),
        reverse=True,
    )
    eligible = [
        item
        for item in ranking
        if (item["metrics"].get("total_trades") or 0) >= 8
        and item["execution_mode"] == "deep_15m"
        and not item["dominated_by"]
        and any(item["strong_gate"].values())
    ]
    report = {
        "started_at": started_at,
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
        "benchmark_return": benchmark_return,
        "created_templates": created,
        "candidate_count": len(candidates),
        "families": sorted({item["family"] for item in created}),
        "cycles": sorted({item["cycle"] for item in created}),
        "failure_count": len(failures),
        "failures": failures[:20],
        "eligible_count": len(eligible),
        "eligible": eligible[:20],
        "top30": ranking[:30],
    }
    path = write_json("search_round_9_12_report.json", report)
    print(json.dumps({"path": str(path), "candidate_count": len(candidates), "eligible_count": len(eligible), "top5": ranking[:5]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
