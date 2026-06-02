#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import os
import sys
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
os.chdir(ROOT)

from app.database import SessionLocal
from app.middleware.authMiddleware import JWT_SECRET
from app.models import ComboTemplate, User
from app.services.combo_optimizer import _metrics_from_trades, extract_trades_with_mode
from app.services.combo_service import ComboService
from app.services.market_data_providers import CCXT_SOURCE, get_market_data_provider


OUT_DIR = ROOT / "qa_artifacts" / "strategy_search_20260602"
SYMBOL = "BTC/USDT"
TIMEFRAME = "1d"
DIRECTION = "long"
INITIAL_CAPITAL = 100
START = "2017-08-17"
END = "2026-06-02"
API_BASE = os.getenv("CRYPTO_BACKEND_URL", "http://127.0.0.1:8003").rstrip("/")
PREFIX = "tmp_quant_20260602b_"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(name: str, payload: Any) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / name).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def schema(parameters: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {"parameters": parameters, "correlated_groups": [list(parameters.keys())]}


def specs() -> list[dict[str, Any]]:
    return [
        {
            "cycle": 5,
            "thesis": "ROC/EMA base winner with tighter stop and faster trend to reduce drawdown without losing compounding.",
            "name": PREFIX + "roc_ema_fast_guard_long_v1",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 9}},
                    {"type": "roc", "alias": "roc", "params": {"length": 2}},
                ],
                "entry_logic": "(close > trend) & (roc > 0)",
                "exit_logic": "(close < trend) | (roc < -1)",
                "stop_loss": 0.02,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 6, "max": 18, "step": 3, "default": 9},
                    "roc_length": {"min": 2, "max": 8, "step": 2, "default": 2},
                    "stop_loss": {"min": 0.015, "max": 0.035, "step": 0.005, "default": 0.02},
                }
            ),
        },
        {
            "cycle": 5,
            "thesis": "EMA/ROC/RSI winner family with faster trend and controlled RSI ceiling for better Pareto balance.",
            "name": PREFIX + "ema_roc_rsi_fast_quality_long_v1",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 10}},
                    {"type": "roc", "alias": "roc", "params": {"length": 8}},
                    {"type": "rsi", "alias": "rsi", "params": {"length": 18}},
                ],
                "entry_logic": "(close > trend) & (roc > 0) & (rsi > 46) & (rsi < 80)",
                "exit_logic": "(close < trend) | (roc < -2) | (rsi < 40)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 6, "max": 18, "step": 3, "default": 10},
                    "roc_length": {"min": 4, "max": 12, "step": 2, "default": 8},
                    "rsi_length": {"min": 14, "max": 24, "step": 2, "default": 18},
                    "stop_loss": {"min": 0.025, "max": 0.045, "step": 0.005, "default": 0.035},
                }
            ),
        },
        {
            "cycle": 6,
            "thesis": "Dual EMA alignment keeps compounding trends but exits faster when short trend loses structure.",
            "name": PREFIX + "dual_ema_roc_rsi_alignment_long_v1",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "fast", "params": {"length": 8}},
                    {"type": "ema", "alias": "slow", "params": {"length": 24}},
                    {"type": "roc", "alias": "roc", "params": {"length": 4}},
                    {"type": "rsi", "alias": "rsi", "params": {"length": 18}},
                ],
                "entry_logic": "(close > fast) & (fast > slow) & (roc > 0) & (rsi > 46)",
                "exit_logic": "(close < fast) | (fast < slow) | (roc < -1) | (rsi < 40)",
                "stop_loss": 0.03,
            },
            "optimization_schema": schema(
                {
                    "fast_length": {"min": 6, "max": 14, "step": 2, "default": 8},
                    "slow_length": {"min": 18, "max": 36, "step": 6, "default": 24},
                    "roc_length": {"min": 2, "max": 8, "step": 2, "default": 4},
                    "rsi_length": {"min": 14, "max": 22, "step": 4, "default": 18},
                    "stop_loss": {"min": 0.02, "max": 0.04, "step": 0.005, "default": 0.03},
                }
            ),
        },
        {
            "cycle": 6,
            "thesis": "Bollinger middle continuation plus ROC requires volatility quality and momentum together.",
            "name": PREFIX + "bbands_roc_quality_long_v1",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 10}},
                    {"type": "bbands", "alias": "bb", "params": {"length": 21, "std": 2.2}},
                    {"type": "roc", "alias": "roc", "params": {"length": 4}},
                    {"type": "rsi", "alias": "rsi", "params": {"length": 18}},
                ],
                "entry_logic": "(close > trend) & (close > bb_middle) & (close < bb_upper) & (roc > 0) & (rsi > 46)",
                "exit_logic": "(close < bb_middle) | (roc < -1) | (rsi < 40)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 6, "max": 18, "step": 3, "default": 10},
                    "bb_length": {"min": 14, "max": 28, "step": 7, "default": 21},
                    "bb_std": {"min": 1.8, "max": 2.4, "step": 0.3, "default": 2.2},
                    "roc_length": {"min": 2, "max": 8, "step": 2, "default": 4},
                    "rsi_length": {"min": 14, "max": 22, "step": 4, "default": 18},
                    "stop_loss": {"min": 0.025, "max": 0.045, "step": 0.005, "default": 0.035},
                }
            ),
        },
        {
            "cycle": 7,
            "thesis": "MACD histogram confirms trend persistence while RSI avoids exhausted entries.",
            "name": PREFIX + "macd_ema_rsi_compound_long_v1",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 10}},
                    {"type": "macd", "alias": "m", "params": {"fast": 8, "slow": 22, "signal": 6}},
                    {"type": "rsi", "alias": "rsi", "params": {"length": 18}},
                ],
                "entry_logic": "(close > trend) & (m_histogram > 0) & (m_macd > m_signal) & (rsi > 46) & (rsi < 82)",
                "exit_logic": "(close < trend) | (m_histogram < 0) | (rsi < 40)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 6, "max": 18, "step": 3, "default": 10},
                    "m_fast": {"min": 6, "max": 12, "step": 2, "default": 8},
                    "m_slow": {"min": 18, "max": 30, "step": 4, "default": 22},
                    "m_signal": {"min": 4, "max": 10, "step": 2, "default": 6},
                    "rsi_length": {"min": 14, "max": 22, "step": 4, "default": 18},
                    "stop_loss": {"min": 0.025, "max": 0.045, "step": 0.005, "default": 0.035},
                }
            ),
        },
        {
            "cycle": 7,
            "thesis": "Volume sponsorship filter accepts only continuation with participation above its own baseline.",
            "name": PREFIX + "volume_ema_roc_rsi_sponsored_long_v1",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 10}},
                    {"type": "roc", "alias": "roc", "params": {"length": 4}},
                    {"type": "rsi", "alias": "rsi", "params": {"length": 18}},
                    {"type": "volume_sma", "alias": "vol_avg", "params": {"length": 20}},
                ],
                "entry_logic": "(close > trend) & (roc > 0) & (rsi > 46) & (volume > vol_avg)",
                "exit_logic": "(close < trend) | (roc < -1) | (rsi < 40)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 6, "max": 18, "step": 3, "default": 10},
                    "roc_length": {"min": 2, "max": 8, "step": 2, "default": 4},
                    "rsi_length": {"min": 14, "max": 22, "step": 4, "default": 18},
                    "vol_avg_length": {"min": 14, "max": 28, "step": 7, "default": 20},
                    "stop_loss": {"min": 0.025, "max": 0.045, "step": 0.005, "default": 0.035},
                }
            ),
        },
        {
            "cycle": 8,
            "thesis": "ADX regime allows the high-return ROC/EMA family only when trend strength is present.",
            "name": PREFIX + "adx_ema_roc_compound_long_v1",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 10}},
                    {"type": "roc", "alias": "roc", "params": {"length": 4}},
                    {"type": "adx", "alias": "adx", "params": {"length": 14}},
                ],
                "entry_logic": "(close > trend) & (roc > 0) & (adx > 18)",
                "exit_logic": "(close < trend) | (roc < -1) | (adx < 14)",
                "stop_loss": 0.03,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 6, "max": 18, "step": 3, "default": 10},
                    "roc_length": {"min": 2, "max": 8, "step": 2, "default": 4},
                    "adx_length": {"min": 10, "max": 18, "step": 4, "default": 14},
                    "stop_loss": {"min": 0.02, "max": 0.04, "step": 0.005, "default": 0.03},
                }
            ),
        },
        {
            "cycle": 8,
            "thesis": "Moving-average breakout keeps the crossover reference but exits with long trend loss.",
            "name": PREFIX + "ma_breakout_trend_exit_long_v1",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "short", "params": {"length": 8}},
                    {"type": "sma", "alias": "medium", "params": {"length": 18}},
                    {"type": "sma", "alias": "long", "params": {"length": 34}},
                ],
                "entry_logic": "(short > medium) & (medium > long) & (close > short)",
                "exit_logic": "(close < medium) | (short < medium)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "ema_short": {"min": 4, "max": 12, "step": 2, "default": 8},
                    "sma_medium": {"min": 12, "max": 28, "step": 4, "default": 18},
                    "sma_long": {"min": 24, "max": 48, "step": 6, "default": 34},
                    "stop_loss": {"min": 0.025, "max": 0.045, "step": 0.005, "default": 0.035},
                }
            ),
        },
    ]


def ensure_template(spec: dict[str, Any]) -> int:
    with SessionLocal() as db:
        row = db.query(ComboTemplate).filter(ComboTemplate.name == spec["name"]).first()
        if row is None:
            row = ComboTemplate(
                name=spec["name"],
                description="Temporary hard-mode continuation candidate.",
                is_prebuilt=False,
                is_example=False,
                is_readonly=False,
                template_data=spec["template_data"],
                optimization_schema=spec["optimization_schema"],
            )
            db.add(row)
        else:
            row.template_data = spec["template_data"]
            row.optimization_schema = spec["optimization_schema"]
        db.commit()
        db.refresh(row)
        return int(row.id)


def admin_token() -> str:
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == "o.alan.silva@gmail.com").first()
        user = user or db.query(User).order_by(User.created_at.asc()).first()
    stamp = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user.id),
            "email": user.email,
            "type": "access",
            "iat": int(stamp.timestamp()),
            "exp": int((stamp + timedelta(hours=8)).timestamp()),
        },
        JWT_SECRET,
        algorithm="HS256",
    )


def post(path: str, payload: dict[str, Any], token: str) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE}{path}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=900,
    )
    response.raise_for_status()
    return response.json()


def values(meta: dict[str, Any]) -> list[Any]:
    start = meta["min"]
    end = meta["max"]
    step = meta.get("step") or 1
    out = []
    v = start
    while v <= end + 1e-12:
        out.append(int(v) if isinstance(start, int) and isinstance(end, int) and float(step).is_integer() else round(float(v), 6))
        v += step
    return out


def sample_params(schema_params: dict[str, dict[str, Any]], limit: int = 18) -> list[dict[str, Any]]:
    keys = list(schema_params)
    grids = [values(schema_params[k]) for k in keys]
    combos = [dict(zip(keys, item)) for item in itertools.product(*grids)]
    defaults = {k: v.get("default") for k, v in schema_params.items()}
    combos.sort(key=lambda c: sum(abs(float(c[k]) - float(defaults[k])) for k in keys if defaults[k] is not None))
    selected = combos[: max(1, limit // 3)]
    if len(combos) > len(selected):
        stride = max(1, len(combos) // (limit - len(selected)))
        selected.extend(combos[::stride][: limit - len(selected)])
    dedup = []
    seen = set()
    for combo in selected:
        marker = tuple(sorted(combo.items()))
        if marker not in seen:
            seen.add(marker)
            dedup.append(combo)
    return dedup[:limit]


def backtest_direct(template_name: str, params: dict[str, Any]) -> dict[str, Any]:
    service = ComboService()
    provider = get_market_data_provider(CCXT_SOURCE)
    df = provider.fetch_ohlcv(SYMBOL, TIMEFRAME, since_str=START, until_str=END)
    full_params = {**params, "direction": DIRECTION, "data_source": "ccxt"}
    strategy = service.create_strategy(template_name, parameters=full_params)
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
    return {
        "template_name": template_name,
        "parameters": full_params,
        "execution_mode": mode,
        "metrics": metrics,
        "trade_count": len(trades),
        "trades": trades,
    }


def compact_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
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
    strict = ((am.get("total_return_pct") or -10**18) > (bm.get("total_return_pct") or -10**18)) or (
        (am.get("max_drawdown_pct") or 10**18) < (bm.get("max_drawdown_pct") or 10**18)
    ) or ((am.get("profit_factor") or -10**18) > (bm.get("profit_factor") or -10**18))
    return ret and dd and spf and strict


def concentration(trades: list[dict[str, Any]], total_return_pct: float) -> dict[str, Any]:
    profits = []
    for trade in trades:
        value = trade.get("profit_pct")
        if value is None and trade.get("profit") is not None:
            value = float(trade["profit"]) * 100
        if value is not None:
            profits.append(float(value))
    positives = sorted([p for p in profits if p > 0], reverse=True)
    top1 = positives[0] if positives else 0.0
    top5 = sum(positives[:5])
    denom = abs(total_return_pct) or 1.0
    return {
        "largest_trade_return_pct": top1,
        "top5_return_pct_sum": top5,
        "largest_trade_share_of_total_return": top1 / denom,
        "top5_share_of_total_return": top5 / denom,
        "positive_trade_count": len(positives),
    }


def main() -> None:
    token = admin_token()
    deep_report = json.loads((OUT_DIR / "api_deep_revalidation_t0_20260602.json").read_text())
    benchmarks = [
        {
            "id": row["id"],
            "name": row["name"],
            "strategy_name": row["strategy_name"],
            "execution_mode": row.get("execution_mode"),
            "metrics": row["metrics"],
        }
        for row in deep_report["results"]
        if row.get("status") == 200 and (row.get("metrics", {}).get("total_trades") or 0) >= 8
    ]
    benchmark_return = max(benchmarks, key=lambda x: x["metrics"].get("total_return_pct") or -10**18)

    created = []
    optimize_reports = []
    candidates = []
    failures = []
    for spec in specs():
        template_id = ensure_template(spec)
        created.append({"id": template_id, "name": spec["name"], "cycle": spec["cycle"], "thesis": spec["thesis"]})
        opt_payload = {
            "template_name": spec["name"],
            "symbol": SYMBOL,
            "timeframe": TIMEFRAME,
            "data_source": "ccxt",
            "start_date": START,
            "end_date": END,
            "deep_backtest": True,
            "initial_capital": INITIAL_CAPITAL,
            "direction": DIRECTION,
            "custom_ranges": spec["optimization_schema"]["parameters"],
        }
        print(f"{now()} optimize {spec['name']}", flush=True)
        try:
            opt = post("/api/combos/optimize", opt_payload, token)
            optimize_reports.append(
                {
                    "template_name": spec["name"],
                    "best_parameters": opt.get("best_parameters"),
                    "best_metrics": compact_metrics(opt.get("best_metrics") or {}),
                    "stages_count": len(opt.get("stages") or []),
                }
            )
        except Exception as exc:
            failures.append({"template": spec["name"], "stage": "optimize", "error": repr(exc)})

        sampled = sample_params(spec["optimization_schema"]["parameters"], limit=18)
        if optimize_reports and optimize_reports[-1]["template_name"] == spec["name"] and optimize_reports[-1].get("best_parameters"):
            sampled.insert(0, optimize_reports[-1]["best_parameters"])
        for params in sampled:
            print(f"{now()} backtest {spec['name']} {params}", flush=True)
            try:
                result = backtest_direct(spec["name"], params)
                metrics = result["metrics"]
                item = {
                    "template_name": spec["name"],
                    "cycle": spec["cycle"],
                    "thesis": spec["thesis"],
                    "parameters": result["parameters"],
                    "execution_mode": result["execution_mode"],
                    "metrics": compact_metrics(metrics),
                    "concentration": concentration(result["trades"], metrics.get("total_return_pct") or 0),
                }
                item["dominated_by"] = [
                    {"id": b["id"], "strategy_name": b["strategy_name"], "metrics": b["metrics"]}
                    for b in benchmarks
                    if dominates(b, item)
                    or (
                        (b["metrics"].get("total_return_pct") or 0) > (metrics.get("total_return_pct") or 0)
                        and (b["metrics"].get("max_drawdown_pct") or 999) <= (metrics.get("max_drawdown_pct") or 999)
                    )
                ]
                item["strong_gate"] = {
                    "dominance_clear": (metrics.get("total_return_pct") or 0) >= (benchmark_return["metrics"].get("total_return_pct") or 0)
                    and (metrics.get("max_drawdown_pct") or 999) <= (benchmark_return["metrics"].get("max_drawdown_pct") or 999)
                    and (metrics.get("profit_factor") or 0) >= (benchmark_return["metrics"].get("profit_factor") or 0) * 0.95,
                    "new_pareto_defensible": (metrics.get("total_return_pct") or 0) >= (benchmark_return["metrics"].get("total_return_pct") or 0) * 0.90
                    and (metrics.get("max_drawdown_pct") or 999) <= (benchmark_return["metrics"].get("max_drawdown_pct") or 999) * 0.85
                    and (metrics.get("profit_factor") or 0) > (benchmark_return["metrics"].get("profit_factor") or 0),
                    "defensive_exceptional": (metrics.get("total_return_pct") or 0) >= (benchmark_return["metrics"].get("total_return_pct") or 0) * 0.75
                    and (metrics.get("max_drawdown_pct") or 999) <= (benchmark_return["metrics"].get("max_drawdown_pct") or 999) * 0.75
                    and (metrics.get("profit_factor") or 0) > (benchmark_return["metrics"].get("profit_factor") or 0),
                }
                candidates.append(item)
            except Exception as exc:
                failures.append({"template": spec["name"], "stage": "backtest", "params": params, "error": repr(exc)})

    ranked = sorted(
        candidates,
        key=lambda x: (
            not x["dominated_by"],
            any(x["strong_gate"].values()),
            x["metrics"].get("total_return_pct") or -10**18,
            -(x["metrics"].get("max_drawdown_pct") or 999),
            x["metrics"].get("profit_factor") or 0,
        ),
        reverse=True,
    )
    report = {
        "generated_at": now(),
        "benchmarks": benchmarks,
        "benchmark_return": benchmark_return,
        "created_templates": created,
        "optimize_reports": optimize_reports,
        "candidate_count": len(candidates),
        "failure_count": len(failures),
        "failures": failures[:30],
        "ranking": ranked,
        "eligible": [
            item
            for item in ranked
            if not item["dominated_by"] and any(item["strong_gate"].values()) and (item["metrics"].get("total_trades") or 0) >= 8
        ],
    }
    write_json("continue_search_report.json", report)
    print(json.dumps({"candidate_count": len(candidates), "eligible_count": len(report["eligible"]), "top5": ranked[:5]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
