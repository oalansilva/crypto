#!/usr/bin/env python3
"""Targeted issue #262 search for sequential BTC/USDT 1d winner chains."""

from __future__ import annotations

import importlib.util
import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.data.incremental_loader import IncrementalLoader


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-262-hard-mode-v5"
CARD_261_SCRIPT = ROOT / "scripts" / "card_261_candidate_search.py"
FULL_START = "2017-08-17"
FULL_END = "2026-06-07"


def _load_eval_module():
    spec = importlib.util.spec_from_file_location("card_261_candidate_search", CARD_261_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {CARD_261_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.FULL_START = FULL_START
    module.FULL_END = FULL_END
    module.ARTIFACT_DIR = ARTIFACT_DIR
    return module


def _candidate(module: Any, family: str, thesis: str, indicators, entry: str, exit_: str, stop: float, parameters: dict[str, Any], route: str):
    return module.Candidate(
        family,
        thesis,
        module._td(indicators, entry, exit_, stop),
        {"direction": "long", **parameters},
        "CHAIN_BENCHMARK_SET",
        route,
    )


def _sample_candidates(module: Any, limit: int) -> list[Any]:
    rng = random.Random(262)
    rows: list[Any] = []
    for _ in range(limit):
        kind = rng.choice(["ma", "ma", "ema_roc_rsi", "macd_ema_roc", "adx_roc", "bb_roc"])
        if kind == "ma":
            ema = rng.randint(3, 20)
            sma_m = rng.randint(10, 40)
            sma_l = rng.randint(max(sma_m + 1, 22), 110)
            stop = rng.choice([0.014, 0.018, 0.022, 0.026, 0.03, 0.034, 0.04, 0.05, 0.065, 0.08])
            exit_ref = rng.choice(["medium", "long"])
            exit_logic = "crossunder(short, medium)" if exit_ref == "medium" else "crossunder(short, long)"
            rows.append(
                _candidate(
                    module,
                    "targeted-ma-chain",
                    "MA chain search targets higher return with non-worse drawdown.",
                    [
                        {"type": "ema", "alias": "short", "params": {"length": ema}},
                        {"type": "sma", "alias": "medium", "params": {"length": sma_m}},
                        {"type": "sma", "alias": "long", "params": {"length": sma_l}},
                    ],
                    "(short > long) & (crossover(short, long) | crossover(short, medium))",
                    exit_logic,
                    stop,
                    {"ema": ema, "sma_m": sma_m, "sma_l": sma_l, "stop": stop, "exit_ref": exit_ref},
                    "return up and drawdown down versus chain",
                )
            )
        elif kind == "ema_roc_rsi":
            ema = rng.choice([13, 21, 30, 34, 40, 55, 70, 89, 120])
            roc = rng.choice([6, 8, 10, 12, 14, 18, 21, 30, 34])
            rsi = rng.choice([7, 10, 14, 18, 21])
            rsi_min = rng.choice([30, 35, 38, 40, 42, 45, 48, 50, 55])
            rsi_exit = rng.choice([42, 45, 50, 55, 60, 65, 70])
            stop = rng.choice([0.014, 0.018, 0.022, 0.026, 0.028, 0.032, 0.04, 0.05])
            rows.append(
                _candidate(
                    module,
                    "targeted-ema-roc-rsi",
                    "Momentum guard chain search targets return without extra drawdown.",
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": ema}},
                        {"type": "roc", "alias": "roc", "params": {"length": roc}},
                        {"type": "rsi", "alias": "rsi", "params": {"length": rsi}},
                    ],
                    f"(close > trend) & (roc > 0) & (rsi > {rsi_min})",
                    f"(close < trend) | (rsi < {rsi_exit})",
                    stop,
                    {"ema": ema, "roc": roc, "rsi": rsi, "rsi_min": rsi_min, "rsi_exit": rsi_exit, "stop": stop},
                    "return up and drawdown down versus chain",
                )
            )
        elif kind == "macd_ema_roc":
            ema = rng.choice([13, 20, 34, 55, 89])
            fast = rng.choice([6, 8, 10, 12, 14])
            slow = rng.choice([18, 21, 26, 34, 40])
            signal = rng.choice([4, 5, 7, 9, 12])
            roc = rng.choice([6, 10, 14, 21, 34])
            stop = rng.choice([0.018, 0.026, 0.032, 0.04, 0.05, 0.065])
            if fast >= slow:
                continue
            rows.append(
                _candidate(
                    module,
                    "targeted-macd-ema-roc",
                    "MACD/ROC chain search targets quality filter differentiation.",
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": ema}},
                        {"type": "macd", "alias": "macd", "params": {"fast": fast, "slow": slow, "signal": signal}},
                        {"type": "roc", "alias": "roc", "params": {"length": roc}},
                    ],
                    "(close > trend) & (macd.macd > macd.signal) & (roc > 0)",
                    "(macd.macd < macd.signal) | (close < trend)",
                    stop,
                    {"ema": ema, "fast": fast, "slow": slow, "signal": signal, "roc": roc, "stop": stop},
                    "quality improvement without worse return/dd",
                )
            )
        elif kind == "adx_roc":
            ema = rng.choice([21, 34, 55, 89, 144, 200])
            adx_len = rng.choice([7, 10, 14, 20, 28])
            adx = rng.choice([10, 15, 18, 20, 25, 30])
            roc = rng.choice([6, 10, 14, 21, 34])
            stop = rng.choice([0.018, 0.026, 0.032, 0.04, 0.05, 0.065])
            rows.append(
                _candidate(
                    module,
                    "targeted-adx-roc",
                    "ADX/ROC chain search targets regime-filtered continuation.",
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": ema}},
                        {"type": "adx", "alias": "adx", "params": {"length": adx_len}},
                        {"type": "roc", "alias": "roc", "params": {"length": roc}},
                    ],
                    f"(close > trend) & (adx > {adx}) & (roc > 0)",
                    "(close < trend) | (roc < 0)",
                    stop,
                    {"ema": ema, "adx_len": adx_len, "adx": adx, "roc": roc, "stop": stop},
                    "regime-filtered chain improvement",
                )
            )
        else:
            bb_len = rng.choice([10, 14, 20, 30, 40, 55])
            bb_std = rng.choice([1.3, 1.5, 1.8, 2.0, 2.3, 2.5, 3.0])
            roc = rng.choice([6, 10, 14, 21, 34])
            roc_min = rng.choice([-4, -2, 0, 2, 4, 6])
            stop = rng.choice([0.018, 0.026, 0.032, 0.04, 0.05, 0.065])
            rows.append(
                _candidate(
                    module,
                    "targeted-bb-roc",
                    "BB/ROC chain search targets breakout differentiation.",
                    [
                        {"type": "bbands", "alias": "bb", "params": {"length": bb_len, "std": bb_std}},
                        {"type": "roc", "alias": "roc", "params": {"length": roc}},
                    ],
                    f"(close > bb.upper) & (roc > {roc_min})",
                    "(close < bb.middle) | (roc < 0)",
                    stop,
                    {"bb_len": bb_len, "bb_std": bb_std, "roc": roc, "roc_min": roc_min, "stop": stop},
                    "breakout chain improvement",
                )
            )
    return rows


def _find_chain(rows: list[dict[str, Any]], length: int = 5) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda r: (r["metrics"]["total_return_pct"], -r["metrics"]["max_drawdown_pct"]))
    best: list[dict[str, Any]] = []

    def can_follow(prev: dict[str, Any], cur: dict[str, Any]) -> bool:
        pm = prev["metrics"]
        cm = cur["metrics"]
        return (
            cm["total_return_pct"] >= pm["total_return_pct"]
            and cm["max_drawdown_pct"] <= pm["max_drawdown_pct"]
            and (
                cm.get("sharpe_ratio", 0) >= pm.get("sharpe_ratio", 0)
                or cm.get("profit_factor", 0) >= pm.get("profit_factor", 0)
            )
            and (
                cm["total_return_pct"] >= pm["total_return_pct"] * 1.02
                or cm["max_drawdown_pct"] <= pm["max_drawdown_pct"] * 0.95
                or cm.get("sharpe_ratio", 0) >= pm.get("sharpe_ratio", 0) + 0.05
                or cm.get("profit_factor", 0) >= pm.get("profit_factor", 0) + 0.10
            )
        )

    def dfs(path: list[dict[str, Any]], remaining: list[dict[str, Any]]) -> None:
        nonlocal best
        if len(path) > len(best):
            best = path[:]
        if len(path) >= length:
            return
        for idx, row in enumerate(remaining):
            if path and not can_follow(path[-1], row):
                continue
            dfs(path + [row], remaining[idx + 1 :])

    dfs([], ordered)
    return best


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1800)
    args = parser.parse_args()
    module = _load_eval_module()
    started = time.monotonic()
    loader = IncrementalLoader()
    df_daily = loader.fetch_data("BTC/USDT", "1d", FULL_START, FULL_END, read_only=True)
    df_15m = loader.fetch_intraday_data("BTC/USDT", "15m", FULL_START, FULL_END, read_only=True)
    candidates = _sample_candidates(module, args.limit)
    seen: set[str] = set()
    results = []
    for candidate in candidates:
        fp = module._fingerprint(candidate)
        if fp in seen:
            continue
        seen.add(fp)
        row = module._evaluate(candidate, df_daily, df_15m)
        metrics = row["metrics"]
        row["eligible_basic"] = (
            row["execution_mode"] == "deep_15m"
            and metrics.get("total_trades", 0) >= 8
            and metrics.get("total_return_pct", 0) >= 19926.91312418972
            and metrics.get("max_drawdown_pct", 999) <= 12.214660412400955
            and (
                metrics.get("profit_factor", 0) >= 3.723343317608936 * 0.98
                or metrics.get("sharpe_ratio", 0) >= 0.5027793834983001 - 0.05
            )
        )
        results.append(row)
    eligible = [r for r in results if r["eligible_basic"]]
    chain = _find_chain(eligible, 5)
    report = {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "executed_material_deep_candidates": len(results),
        "unique_template_families": len({r["family"] for r in results}),
        "eligible_basic": len(eligible),
        "best_chain_length": len(chain),
        "best_chain": chain,
        "top_50": sorted(
            results,
            key=lambda r: (r["eligible_basic"], r["metrics"].get("total_return_pct", 0), -r["metrics"].get("max_drawdown_pct", 999)),
            reverse=True,
        )[:50],
        "seconds": round(time.monotonic() - started, 3),
    }
    output = ARTIFACT_DIR / f"targeted-chain-search-{report['created_at'].replace(':', '').replace('+00:00', 'Z')}.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output.relative_to(ROOT)),
                "executed": report["executed_material_deep_candidates"],
                "families": report["unique_template_families"],
                "eligible_basic": report["eligible_basic"],
                "best_chain_length": report["best_chain_length"],
                "best_chain": [
                    {
                        "family": row["family"],
                        "parameters": row["parameters"],
                        "ret": row["metrics"]["total_return_pct"],
                        "dd": row["metrics"]["max_drawdown_pct"],
                        "sharpe": row["metrics"].get("sharpe_ratio"),
                        "pf": row["metrics"].get("profit_factor"),
                        "trades": row["metrics"].get("total_trades"),
                    }
                    for row in chain
                ],
                "seconds": report["seconds"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
