#!/usr/bin/env python3
"""Search issue #277 BTC/USDT 1d Long candidates for a sequential Pareto chain."""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.data.incremental_loader import IncrementalLoader


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-277-hard-mode-v5-btc-long"
CARD_261_SCRIPT = ROOT / "scripts" / "card_261_candidate_search.py"
BENCHMARK_PATH = ARTIFACT_DIR / "benchmark-revalidation-latest.json"
FULL_START = "2017-08-17"
FULL_END = datetime.now(timezone.utc).date().isoformat()


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


def _candidate(
    module: Any,
    family: str,
    thesis: str,
    indicators: list[dict[str, Any]],
    entry: str,
    exit_: str,
    stop: float,
    parameters: dict[str, Any],
    route: str,
):
    return module.Candidate(
        family,
        thesis,
        module._td(indicators, entry, exit_, stop),
        {"direction": "long", **parameters},
        "BENCHMARK_PARETO_SET",
        route,
    )


def _sample_candidates(module: Any, limit: int, seed: int) -> list[Any]:
    rng = random.Random(seed)
    rows: list[Any] = []
    for _ in range(limit):
        kind = rng.choice(
            [
                "ma",
                "ma",
                "ma_breakout",
                "ema_roc_rsi",
                "macd_ema_roc",
                "adx_roc",
                "bb_roc",
                "rsi_reclaim",
                "dual_momentum",
            ]
        )
        if kind == "ma":
            ema = rng.randint(3, 24)
            sma_m = rng.randint(8, 55)
            sma_l = rng.randint(max(sma_m + 1, 24), 180)
            stop = rng.choice([0.008, 0.01, 0.012, 0.014, 0.018, 0.022, 0.026, 0.03, 0.034, 0.04, 0.05, 0.065])
            exit_ref = rng.choice(["medium", "long"])
            exit_logic = "crossunder(short, medium)" if exit_ref == "medium" else "crossunder(short, long)"
            rows.append(
                _candidate(
                    module,
                    "ma-chain-long",
                    "Long MA continuation tries to form sequential Pareto steps.",
                    [
                        {"type": "ema", "alias": "short", "params": {"length": ema}},
                        {"type": "sma", "alias": "medium", "params": {"length": sma_m}},
                        {"type": "sma", "alias": "long", "params": {"length": sma_l}},
                    ],
                    "(short > long) & (crossover(short, long) | crossover(short, medium))",
                    exit_logic,
                    stop,
                    {"ema": ema, "sma_m": sma_m, "sma_l": sma_l, "stop": stop, "exit_ref": exit_ref},
                    "return up with drawdown non-worse",
                )
            )
        elif kind == "ma_breakout":
            ema = rng.choice([5, 8, 13, 21, 34])
            sma_l = rng.choice([34, 55, 89, 144, 200])
            roc = rng.choice([4, 6, 8, 10, 14, 21])
            stop = rng.choice([0.008, 0.012, 0.016, 0.02, 0.026, 0.034])
            rows.append(
                _candidate(
                    module,
                    "ma-breakout-long",
                    "Fast MA plus ROC breakout targets lower drawdown entries.",
                    [
                        {"type": "ema", "alias": "fast", "params": {"length": ema}},
                        {"type": "sma", "alias": "trend", "params": {"length": sma_l}},
                        {"type": "roc", "alias": "roc", "params": {"length": roc}},
                    ],
                    "(close > trend) & crossover(fast, trend) & (roc > 0)",
                    "(close < fast) | (roc < 0)",
                    stop,
                    {"ema": ema, "sma_l": sma_l, "roc": roc, "stop": stop},
                    "defensive breakout",
                )
            )
        elif kind == "ema_roc_rsi":
            ema = rng.choice([8, 13, 21, 30, 34, 40, 55, 70, 89, 120, 144])
            roc = rng.choice([4, 6, 8, 10, 12, 14, 18, 21, 30, 34])
            rsi = rng.choice([7, 10, 14, 18, 21])
            rsi_min = rng.choice([30, 35, 38, 40, 42, 45, 48, 50, 55, 60])
            rsi_exit = rng.choice([35, 40, 42, 45, 50, 55, 60, 65, 70])
            stop = rng.choice([0.008, 0.012, 0.016, 0.02, 0.026, 0.032, 0.04, 0.05])
            rows.append(
                _candidate(
                    module,
                    "ema-roc-rsi-long",
                    "Long EMA/ROC/RSI continuation targets quality and segment stability.",
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": ema}},
                        {"type": "roc", "alias": "roc", "params": {"length": roc}},
                        {"type": "rsi", "alias": "rsi", "params": {"length": rsi}},
                    ],
                    f"(close > trend) & (roc > 0) & (rsi > {rsi_min})",
                    f"(close < trend) | (rsi < {rsi_exit})",
                    stop,
                    {"ema": ema, "roc": roc, "rsi": rsi, "rsi_min": rsi_min, "rsi_exit": rsi_exit, "stop": stop},
                    "quality improvement",
                )
            )
        elif kind == "macd_ema_roc":
            ema = rng.choice([8, 13, 20, 34, 55, 89, 144])
            fast = rng.choice([5, 6, 8, 10, 12, 14])
            slow = rng.choice([16, 18, 21, 26, 34, 40])
            signal = rng.choice([3, 4, 5, 7, 9, 12])
            roc = rng.choice([4, 6, 10, 14, 21, 34])
            stop = rng.choice([0.01, 0.014, 0.018, 0.026, 0.032, 0.04, 0.05])
            if fast >= slow:
                continue
            rows.append(
                _candidate(
                    module,
                    "macd-ema-roc-long",
                    "Long MACD/ROC filter targets non-duplicate quality improvement.",
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": ema}},
                        {"type": "macd", "alias": "macd", "params": {"fast": fast, "slow": slow, "signal": signal}},
                        {"type": "roc", "alias": "roc", "params": {"length": roc}},
                    ],
                    "(close > trend) & (macd.macd > macd.signal) & (roc > 0)",
                    "(macd.macd < macd.signal) | (close < trend)",
                    stop,
                    {"ema": ema, "fast": fast, "slow": slow, "signal": signal, "roc": roc, "stop": stop},
                    "quality improvement",
                )
            )
        elif kind == "adx_roc":
            ema = rng.choice([13, 21, 34, 55, 89, 144, 200])
            adx_len = rng.choice([7, 10, 14, 20, 28])
            adx = rng.choice([8, 10, 12, 15, 18, 20, 25, 30])
            roc = rng.choice([4, 6, 10, 14, 21, 34])
            stop = rng.choice([0.01, 0.014, 0.018, 0.026, 0.032, 0.04, 0.05])
            rows.append(
                _candidate(
                    module,
                    "adx-roc-long",
                    "Long ADX/ROC regime filter targets defensive continuation.",
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": ema}},
                        {"type": "adx", "alias": "adx", "params": {"length": adx_len}},
                        {"type": "roc", "alias": "roc", "params": {"length": roc}},
                    ],
                    f"(close > trend) & (adx > {adx}) & (roc > 0)",
                    "(close < trend) | (roc < 0)",
                    stop,
                    {"ema": ema, "adx_len": adx_len, "adx": adx, "roc": roc, "stop": stop},
                    "defensive continuation",
                )
            )
        elif kind == "bb_roc":
            bb_len = rng.choice([10, 14, 20, 30, 40, 55])
            bb_std = rng.choice([1.2, 1.3, 1.5, 1.8, 2.0, 2.3, 2.5, 3.0])
            roc = rng.choice([4, 6, 10, 14, 21, 34])
            roc_min = rng.choice([-4, -2, 0, 2, 4, 6])
            stop = rng.choice([0.01, 0.014, 0.018, 0.026, 0.032, 0.04, 0.05])
            rows.append(
                _candidate(
                    module,
                    "bb-roc-long",
                    "Long volatility breakout targets a different thesis.",
                    [
                        {"type": "bbands", "alias": "bb", "params": {"length": bb_len, "std": bb_std}},
                        {"type": "roc", "alias": "roc", "params": {"length": roc}},
                    ],
                    f"(close > bb.upper) & (roc > {roc_min})",
                    "(close < bb.middle) | (roc < 0)",
                    stop,
                    {"bb_len": bb_len, "bb_std": bb_std, "roc": roc, "roc_min": roc_min, "stop": stop},
                    "volatility breakout",
                )
            )
        elif kind == "rsi_reclaim":
            ema = rng.choice([21, 34, 55, 89, 144, 200])
            rsi = rng.choice([7, 10, 14, 21])
            reclaim = rng.choice([35, 40, 45, 50])
            exit_level = rng.choice([45, 50, 55, 60, 65])
            stop = rng.choice([0.01, 0.014, 0.018, 0.026, 0.032, 0.04])
            rows.append(
                _candidate(
                    module,
                    "rsi-reclaim-long",
                    "Long RSI reclaim after trend filter targets bullish reversal.",
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": ema}},
                        {"type": "rsi", "alias": "rsi", "params": {"length": rsi}},
                    ],
                    f"(close > trend) & (rsi > {reclaim})",
                    f"(close < trend) | (rsi < {exit_level})",
                    stop,
                    {"ema": ema, "rsi": rsi, "reclaim": reclaim, "exit_level": exit_level, "stop": stop},
                    "bullish reversal",
                )
            )
        else:
            ema_fast = rng.choice([5, 8, 13, 21, 34])
            ema_slow = rng.choice([34, 55, 89, 144, 200])
            roc_fast = rng.choice([4, 6, 8, 10])
            roc_slow = rng.choice([14, 21, 30, 34])
            stop = rng.choice([0.01, 0.014, 0.018, 0.026, 0.032, 0.04])
            rows.append(
                _candidate(
                    module,
                    "dual-momentum-long",
                    "Long dual momentum targets continuation without weak trend context.",
                    [
                        {"type": "ema", "alias": "fast", "params": {"length": ema_fast}},
                        {"type": "ema", "alias": "slow", "params": {"length": ema_slow}},
                        {"type": "roc", "alias": "roc_fast", "params": {"length": roc_fast}},
                        {"type": "roc", "alias": "roc_slow", "params": {"length": roc_slow}},
                    ],
                    "(fast > slow) & (roc_fast > roc_slow) & (roc_slow > 0)",
                    "(fast < slow) | (roc_fast < 0)",
                    stop,
                    {"ema_fast": ema_fast, "ema_slow": ema_slow, "roc_fast": roc_fast, "roc_slow": roc_slow, "stop": stop},
                    "dual momentum",
                )
            )
    return rows


def _m(row: dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float((row.get("metrics") or {}).get(key, default) or default)
    except (TypeError, ValueError):
        return default


def _dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    ar, br = _m(a, "total_return_pct"), _m(b, "total_return_pct")
    add, bdd = _m(a, "max_drawdown_pct", 999), _m(b, "max_drawdown_pct", 999)
    asharpe, bsharpe = _m(a, "sharpe_ratio"), _m(b, "sharpe_ratio")
    apf, bpf = _m(a, "profit_factor"), _m(b, "profit_factor")
    return ar >= br and add <= bdd and (asharpe >= bsharpe or apf >= bpf) and (
        ar > br or add < bdd or asharpe > bsharpe or apf > bpf
    )


def _sequential_ok(prev: dict[str, Any], cur: dict[str, Any]) -> bool:
    pr, cr = _m(prev, "total_return_pct"), _m(cur, "total_return_pct")
    pdd, cdd = _m(prev, "max_drawdown_pct", 999), _m(cur, "max_drawdown_pct", 999)
    ps, cs = _m(prev, "sharpe_ratio"), _m(cur, "sharpe_ratio")
    ppf, cpf = _m(prev, "profit_factor"), _m(cur, "profit_factor")
    material = (
        cr >= pr * 1.02
        or cdd <= pdd * 0.95
        or (cs >= ps + 0.05 and cr >= pr and cdd <= pdd)
        or (cpf >= ppf + 0.10 and cr >= pr and cdd <= pdd)
    )
    return cr >= pr and cdd <= pdd and (cs >= ps or cpf >= ppf) and material


def _find_chain(rows: list[dict[str, Any]], length: int = 5, min_families: int = 3) -> list[dict[str, Any]]:
    ordered = sorted(
        rows,
        key=lambda r: (_m(r, "max_drawdown_pct", 999), _m(r, "total_return_pct"), _m(r, "profit_factor")),
    )
    best: list[dict[str, Any]] = []

    def dfs(path: list[dict[str, Any]], remaining: list[dict[str, Any]]) -> None:
        nonlocal best
        if len(path) > len(best):
            best = path[:]
        if len(path) >= length:
            return
        for idx, row in enumerate(remaining):
            if path and not all(_sequential_ok(prev, row) for prev in path):
                continue
            dfs(path + [row], remaining[idx + 1 :])

    dfs([], ordered)
    if len(best) >= length and len({row["family"] for row in best}) >= min_families:
        return best

    diverse_best: list[dict[str, Any]] = []

    def diverse_score(path: list[dict[str, Any]]) -> tuple[int, int, float]:
        return (
            len(path),
            len({row["family"] for row in path}),
            sum(_m(row, "total_return_pct") for row in path),
        )

    def dfs_diverse(path: list[dict[str, Any]], remaining: list[dict[str, Any]]) -> None:
        nonlocal diverse_best
        if diverse_score(path) > diverse_score(diverse_best):
            diverse_best = path[:]
        if len(path) >= length:
            return
        for idx, row in enumerate(remaining):
            if path and not all(_sequential_ok(prev, row) for prev in path):
                continue
            # Prefer material thesis changes: allow a repeated family only when
            # the chain cannot yet reach the requested length with available families.
            dfs_diverse(path + [row], remaining[idx + 1 :])

    # Put one representative of each family earlier, then allow repeats.
    diverse_order = sorted(
        rows,
        key=lambda r: (
            r["family"],
            _m(r, "max_drawdown_pct", 999),
            _m(r, "total_return_pct"),
        ),
    )
    dfs_diverse([], diverse_order)
    return diverse_best if diverse_score(diverse_best) > diverse_score(best) else best


def _benchmark_rows() -> list[dict[str, Any]]:
    payload = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    rows = []
    for row in payload["results"]:
        if row.get("status") != "ok" or row.get("execution_mode") != "deep_15m":
            continue
        rows.append(
            {
                "favorite_id": row["favorite_id"],
                "name": row["name"],
                "strategy_name": row["strategy_name"],
                "metrics": row["metrics_summary"],
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1800)
    parser.add_argument("--seed", type=int, default=277)
    args = parser.parse_args()

    module = _load_eval_module()
    started = time.monotonic()
    loader = IncrementalLoader()
    df_daily = loader.fetch_data("BTC/USDT", "1d", FULL_START, FULL_END, read_only=True)
    df_15m = loader.fetch_intraday_data("BTC/USDT", "15m", FULL_START, FULL_END, read_only=True)
    benchmark_rows = _benchmark_rows()
    candidates = _sample_candidates(module, args.limit, args.seed)
    seen: set[str] = set()
    results = []
    for candidate in candidates:
        fp = module._fingerprint(candidate)
        if fp in seen:
            continue
        seen.add(fp)
        try:
            row = module._evaluate(candidate, df_daily, df_15m)
        except Exception as exc:  # noqa: BLE001 - invalid family evidence
            row = {
                "family": candidate.family,
                "thesis": candidate.thesis,
                "target": candidate.target,
                "route": candidate.route,
                "template_data": candidate.template_data,
                "parameters": candidate.parameters,
                "execution_mode": None,
                "metrics": {},
                "direction": "long",
                "eligible_basic": False,
                "rejection_reasons": ["evaluation_error"],
                "error": f"{exc.__class__.__name__}: {str(exc)[:500]}",
            }
            results.append(row)
            continue
        metrics = row["metrics"]
        row["direction"] = "long"
        row["eligible_basic"] = (
            row["execution_mode"] == "deep_15m"
            and metrics.get("total_trades", 0) >= 8
            and not any(_dominates(benchmark, row) for benchmark in benchmark_rows)
        )
        row["rejection_reasons"] = []
        if row["execution_mode"] != "deep_15m":
            row["rejection_reasons"].append("not_deep_15m")
        if metrics.get("total_trades", 0) < 8:
            row["rejection_reasons"].append("too_few_trades")
        if any(_dominates(benchmark, row) for benchmark in benchmark_rows):
            row["rejection_reasons"].append("dominated_by_t0")
        results.append(row)
    eligible = [row for row in results if row["eligible_basic"]]
    chain = _find_chain(eligible, 5)
    report = {
        "card": 277,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "direction": "long",
        "symbol": "BTC/USDT",
        "timeframe": "1d",
        "full_start": FULL_START,
        "full_end": FULL_END,
        "seed": args.seed,
        "executed_material_deep_candidates": len(
            [r for r in results if r["execution_mode"] == "deep_15m"]
        ),
        "unique_candidates": len(results),
        "unique_template_families": len({r["family"] for r in results}),
        "eligible_basic": len(eligible),
        "best_chain_length": len(chain),
        "best_chain": chain,
        "eligible_rows": eligible,
        "rejection_counts": {
            reason: sum(1 for r in results if reason in r["rejection_reasons"])
            for reason in ["not_deep_15m", "too_few_trades", "dominated_by_t0", "evaluation_error"]
        },
        "benchmark_rows": benchmark_rows,
        "top_100": sorted(
            results,
            key=lambda r: (
                r["eligible_basic"],
                -_m(r, "max_drawdown_pct", 999),
                _m(r, "total_return_pct"),
                _m(r, "profit_factor"),
            ),
            reverse=True,
        )[:100],
        "seconds": round(time.monotonic() - started, 3),
    }
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = report["created_at"].replace(":", "").replace("+00:00", "Z")
    output = ARTIFACT_DIR / f"chain-search-{stamp}.json"
    latest = ARTIFACT_DIR / "chain-search-latest.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    latest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output),
                "executed_material_deep_candidates": report["executed_material_deep_candidates"],
                "unique_template_families": report["unique_template_families"],
                "eligible_basic": report["eligible_basic"],
                "best_chain_length": report["best_chain_length"],
                "seconds": report["seconds"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
