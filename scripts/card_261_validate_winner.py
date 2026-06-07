#!/usr/bin/env python3
"""Validate the best HARD MODE V3 winner candidate before saving."""

from __future__ import annotations

import json
import logging
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.combo_optimizer import _metrics_from_trades, extract_trades_with_mode
from app.strategies.combos import ComboStrategy
from src.data.incremental_loader import IncrementalLoader


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-261-hard-mode-v3-btc-pareto"
T0_PATH = ARTIFACT_DIR / "t0_snapshot_20260607T013730Z.json"
SEARCH_PATH = ARTIFACT_DIR / "candidate_search_20260607T014201+0000.json"
SYMBOL = "BTC/USDT"
TIMEFRAME = "1d"
FULL_START = "2017-08-17"
FULL_END = "2026-06-07"
INITIAL_CAPITAL = 100
FINAL_STRATEGY_NAME = "quant_btc_1d_ema_roc_rsi_guard_long_v2_20260607"
FINAL_PUBLIC_NAME = "Momentum BTC: Continuidade com Guard RSI"
FINAL_DESCRIPTION = (
    "Acompanha continuidade do BTC quando tendência, momentum e força relativa convergem, "
    "com proteção para reduzir entradas em contexto fraco. Use como apoio e sempre confira risco e histórico."
)


def final_template_data() -> dict[str, Any]:
    return {
        "indicators": [
            {"type": "ema", "alias": "trend", "params": {"length": 32}},
            {"type": "roc", "alias": "roc", "params": {"length": 9}},
            {"type": "rsi", "alias": "rsi", "params": {"length": 10}},
        ],
        "entry_logic": "(close > trend) & (roc > 0) & (rsi > 40)",
        "exit_logic": "(close < trend) | (rsi < 45)",
        "stop_loss": 0.028,
    }


def final_parameters() -> dict[str, Any]:
    return {
        "direction": "long",
        "data_source": "ccxt",
        "ema": 32,
        "roc": 9,
        "rsi": 10,
        "rsi_min": 40,
        "rsi_exit": 45,
        "stop": 0.028,
        "stop_loss": 0.028,
    }


def _metric(row: dict[str, Any], key: str) -> float | None:
    metrics = row.get("metrics") or {}
    try:
        return float(metrics.get(key))
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


def _candles(df) -> list[dict[str, Any]]:
    out = []
    for idx, row in df.iterrows():
        out.append(
            {
                "timestamp_utc": idx.isoformat() if hasattr(idx, "isoformat") else str(idx),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            }
        )
    return out


def _run(template_data: dict[str, Any], df_daily, df_15m, start: str, end: str) -> dict[str, Any]:
    window = df_daily.loc[start:end].copy()
    window_15m = df_15m.loc[start:end].copy()
    strategy = ComboStrategy(
        indicators=template_data["indicators"],
        entry_logic=template_data["entry_logic"],
        exit_logic=template_data["exit_logic"],
        stop_loss=template_data["stop_loss"],
    )
    signals = strategy.generate_signals(window.copy())
    trades, mode = extract_trades_with_mode(
        signals,
        template_data["stop_loss"],
        deep_backtest=True,
        symbol=SYMBOL,
        since_str=start,
        until_str=end,
        df_15m_cache=window_15m,
        direction="long",
        return_mode=True,
    )
    metrics = _metrics_from_trades(trades, INITIAL_CAPITAL, context_params=final_parameters())
    return {
        "start_date": start,
        "end_date": end,
        "execution_mode": mode,
        "metrics": metrics,
        "trades": trades,
        "candles": _candles(window),
    }


def _trade_concentration(trades: list[dict[str, Any]]) -> dict[str, Any]:
    profits = [float(t.get("profit") or 0) for t in trades]
    positives = sorted([p for p in profits if p > 0], reverse=True)
    if not profits:
        return {"available": False}
    total_positive = sum(positives)
    top1 = positives[0] if positives else 0
    top3 = sum(positives[:3])
    return {
        "available": True,
        "total_trades": len(profits),
        "positive_trades": len(positives),
        "largest_trade_return": top1,
        "top3_positive_return_sum": top3,
        "top1_share_of_positive_sum": top1 / total_positive if total_positive else None,
        "top3_share_of_positive_sum": top3 / total_positive if total_positive else None,
        "median_trade_return": statistics.median(profits),
    }


def _stress(df_daily, df_15m) -> list[dict[str, Any]]:
    variants = []
    for ema in [30, 32, 34]:
        for roc in [8, 9, 10]:
            for rsi_min in [38, 40, 42]:
                td = final_template_data()
                td["indicators"][0]["params"]["length"] = ema
                td["indicators"][1]["params"]["length"] = roc
                td["entry_logic"] = f"(close > trend) & (roc > 0) & (rsi > {rsi_min})"
                result = _run(td, df_daily, df_15m, FULL_START, FULL_END)
                variants.append(
                    {
                        "ema": ema,
                        "roc": roc,
                        "rsi_min": rsi_min,
                        "execution_mode": result["execution_mode"],
                        "metrics": result["metrics"],
                    }
                )
    return variants


def _save_criteria(candidate: dict[str, Any], t0: dict[str, Any]) -> dict[str, Any]:
    current = t0["revalidated_favorites"]
    dominated_by = [fav["favorite_id"] for fav in current if _dominates(fav, candidate)]
    br = t0["benchmarks"]["BENCHMARK_RETURN"]["metrics"]
    ret = candidate["metrics"]["total_return_pct"]
    dd = candidate["metrics"]["max_drawdown_pct"]
    pf = candidate["metrics"]["profit_factor"]
    return {
        "dominated_by_current_favorites": dominated_by,
        "dominance_clear": (
            ret >= br["total_return_pct"]
            and dd <= br["max_drawdown_pct"]
            and pf >= br["profit_factor"] * 0.98
        ),
        "new_profile_pareto_defensible": (
            ret >= 0.90 * br["total_return_pct"]
            and dd <= 0.85 * br["max_drawdown_pct"]
            and pf > t0["benchmarks"]["BENCHMARK_PF"]["metrics"]["profit_factor"]
        ),
        "defensive_exceptional": (
            dd <= 0.75 * br["max_drawdown_pct"]
            and ret >= 0.75 * br["total_return_pct"]
            and pf > t0["benchmarks"]["BENCHMARK_PF"]["metrics"]["profit_factor"]
        ),
    }


def main() -> None:
    logging.disable(logging.CRITICAL)
    t0 = json.loads(T0_PATH.read_text(encoding="utf-8"))
    search = json.loads(SEARCH_PATH.read_text(encoding="utf-8"))
    loader = IncrementalLoader()
    df_daily = loader.fetch_data(SYMBOL, TIMEFRAME, FULL_START, FULL_END, read_only=True)
    df_15m = loader.fetch_intraday_data(SYMBOL, "15m", FULL_START, FULL_END, read_only=True)
    template_data = final_template_data()
    full = _run(template_data, df_daily, df_15m, FULL_START, FULL_END)
    candidate_row = {
        "strategy_name": FINAL_STRATEGY_NAME,
        "strategy_display_name": FINAL_PUBLIC_NAME,
        "strategy_description": FINAL_DESCRIPTION,
        "template_data": template_data,
        "parameters": final_parameters(),
        "execution_mode": full["execution_mode"],
        "metrics": full["metrics"],
    }
    train = _run(template_data, df_daily, df_15m, FULL_START, "2023-12-31")
    oos = _run(template_data, df_daily, df_15m, "2024-01-01", FULL_END)
    segments = [
        _run(template_data, df_daily, df_15m, "2017-08-17", "2020-12-31"),
        _run(template_data, df_daily, df_15m, "2021-01-01", "2023-12-31"),
        _run(template_data, df_daily, df_15m, "2024-01-01", FULL_END),
    ]
    stress = _stress(df_daily, df_15m)
    validation = {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_search": str(SEARCH_PATH.relative_to(ROOT)),
        "candidate_from_search_rank": next(
            (row for row in search["ranking_top_25"] if row["family"] == "ema-roc-rsi-guard"),
            None,
        ),
        "final_candidate": candidate_row,
        "full_period": full,
        "train": {
            "start_date": train["start_date"],
            "end_date": train["end_date"],
            "execution_mode": train["execution_mode"],
            "metrics": train["metrics"],
        },
        "oos": {
            "start_date": oos["start_date"],
            "end_date": oos["end_date"],
            "execution_mode": oos["execution_mode"],
            "metrics": oos["metrics"],
        },
        "segments": [
            {
                "start_date": row["start_date"],
                "end_date": row["end_date"],
                "execution_mode": row["execution_mode"],
                "metrics": row["metrics"],
            }
            for row in segments
        ],
        "stress": stress,
        "trade_concentration": _trade_concentration(full["trades"]),
        "save_criteria": _save_criteria(candidate_row, t0),
        "comparison_current_favorites": [
            {
                "favorite_id": fav["favorite_id"],
                "strategy_name": fav["strategy_name"],
                "candidate_dominates": _dominates(candidate_row, fav),
                "favorite_dominates_candidate": _dominates(fav, candidate_row),
                "favorite_metrics": fav["metrics"],
            }
            for fav in t0["revalidated_favorites"]
        ],
        "favorite_payload": {
            "name": FINAL_PUBLIC_NAME,
            "symbol": SYMBOL,
            "timeframe": TIMEFRAME,
            "strategy_name": FINAL_STRATEGY_NAME,
            "parameters": final_parameters(),
            "metrics": {
                **full["metrics"],
                "trades": full["trades"],
                "trades_history_cached": True,
                "trades_metrics_match": True,
                "analysis_candles": full["candles"],
                "analysis_indicator_data": {},
                "analysis_execution_mode": full["execution_mode"],
                "auto_refreshed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            },
            "notes": "card #261 HARD MODE V3 BTC/USDT 1d long Pareto winner",
            "tier": 1,
            "notify_telegram": True,
            "start_date": FULL_START,
            "end_date": FULL_END,
            "period_type": "all",
            "auto_refresh_status": "SUCCESS",
            "auto_refresh_completed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        },
    }
    output = ARTIFACT_DIR / "winner_validation_20260607T014201Z.json"
    output.write_text(json.dumps(validation, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output.relative_to(ROOT)),
                "execution_mode": full["execution_mode"],
                "full_metrics": full["metrics"],
                "oos_metrics": oos["metrics"],
                "segments": [row["metrics"] for row in validation["segments"]],
                "save_criteria": validation["save_criteria"],
                "stress_min_return_pct": min(row["metrics"]["total_return_pct"] for row in stress),
                "stress_max_drawdown_pct": max(row["metrics"]["max_drawdown_pct"] for row in stress),
                "trade_concentration": validation["trade_concentration"],
            },
            ensure_ascii=False,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
