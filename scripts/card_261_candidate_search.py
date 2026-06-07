#!/usr/bin/env python3
"""Run HARD MODE V3 candidate search for issue #261 without saving favorites."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import logging
import math
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from app.services.combo_optimizer import _metrics_from_trades, extract_trades_with_mode
from app.strategies.combos import ComboStrategy
from src.data.incremental_loader import IncrementalLoader


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-261-hard-mode-v3-btc-pareto"
T0_PATH = ARTIFACT_DIR / "t0_snapshot_20260607T013730Z.json"
SYMBOL = "BTC/USDT"
TIMEFRAME = "1d"
FULL_START = "2017-08-17"
FULL_END = "2026-06-07"
INITIAL_CAPITAL = 100
MIN_TRADES = 8


@dataclass(frozen=True)
class Candidate:
    family: str
    thesis: str
    template_data: dict[str, Any]
    parameters: dict[str, Any]
    target: str
    route: str


def _metric(row: dict[str, Any], key: str) -> float | None:
    metrics = row.get("metrics") or {}
    value = metrics.get(key)
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


def _fingerprint(candidate: Candidate) -> str:
    payload = {
        "family": candidate.family,
        "template_data": candidate.template_data,
        "parameters": candidate.parameters,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _ranges(values: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = list(values.keys())
    return [dict(zip(keys, combo)) for combo in itertools.product(*(values[k] for k in keys))]


def _sample(items: list[dict[str, Any]], limit: int, seed: int) -> list[dict[str, Any]]:
    if len(items) <= limit:
        return items
    rng = random.Random(seed)
    picked = rng.sample(items, limit)
    picked.sort(key=lambda item: json.dumps(item, sort_keys=True))
    return picked


def _td(indicators, entry, exit_, stop_loss):
    return {
        "indicators": indicators,
        "entry_logic": entry,
        "exit_logic": exit_,
        "stop_loss": stop_loss,
    }


def _families() -> list[tuple[str, str, str, Callable[[], list[Candidate]]]]:
    def ma_fast_medium():
        vals = _sample(
            _ranges(
                {
                    "ema": [4, 6, 8, 10, 12, 14, 16],
                    "sma_m": [14, 18, 22, 26, 30, 34],
                    "sma_l": [28, 35, 45, 55, 70, 90],
                    "stop": [0.018, 0.026, 0.034, 0.042, 0.055, 0.075],
                    "exit_ref": ["medium", "long"],
                }
            ),
            36,
            1,
        )
        out = []
        for p in vals:
            exit_logic = "crossunder(short, medium)" if p["exit_ref"] == "medium" else "crossunder(short, long)"
            out.append(
                Candidate(
                    "ma-fast-medium-cross",
                    "MA crossover variants try to beat Pareto return with controlled stop.",
                    _td(
                        [
                            {"type": "ema", "alias": "short", "params": {"length": p["ema"]}},
                            {"type": "sma", "alias": "medium", "params": {"length": p["sma_m"]}},
                            {"type": "sma", "alias": "long", "params": {"length": p["sma_l"]}},
                        ],
                        "(short > long) & (crossover(short, long) | crossover(short, medium))",
                        exit_logic,
                        p["stop"],
                    ),
                    {"direction": "long", **p},
                    "Pareto id 9",
                    "more return with drawdown not worse",
                )
            )
        return out

    def ema_roc_trend():
        vals = _sample(
            _ranges(
                {
                    "ema": [20, 30, 45, 60, 90, 120, 180],
                    "roc": [8, 12, 16, 20, 30, 45],
                    "entry": [-2, 0, 2, 4, 6],
                    "exit": [-10, -6, -3, 0, 2],
                    "stop": [0.018, 0.026, 0.034, 0.045, 0.065],
                }
            ),
            34,
            2,
        )
        return [
            Candidate(
                "ema-roc-trend-continuation",
                "Trend plus ROC continuation seeks higher return with fewer weak-context entries.",
                _td(
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": p["ema"]}},
                        {"type": "roc", "alias": "roc", "params": {"length": p["roc"]}},
                    ],
                    f"(close > trend) & (roc > {p['entry']})",
                    f"(close < trend) | (roc < {p['exit']})",
                    p["stop"],
                ),
                {"direction": "long", **p},
                "Pareto id 9",
                "regime/filter materially different",
            )
            for p in vals
        ]

    def ema_roc_rsi_guard():
        vals = _sample(
            _ranges(
                {
                    "ema": [20, 34, 55, 89, 144],
                    "roc": [10, 14, 21, 34],
                    "rsi": [10, 14, 21],
                    "rsi_min": [35, 40, 45, 50],
                    "rsi_exit": [45, 55, 65, 70],
                    "stop": [0.018, 0.028, 0.04, 0.06],
                }
            ),
            32,
            3,
        )
        return [
            Candidate(
                "ema-roc-rsi-guard",
                "Momentum continuation with RSI guard targets PF/Sharpe improvement.",
                _td(
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": p["ema"]}},
                        {"type": "roc", "alias": "roc", "params": {"length": p["roc"]}},
                        {"type": "rsi", "alias": "rsi", "params": {"length": p["rsi"]}},
                    ],
                    f"(close > trend) & (roc > 0) & (rsi > {p['rsi_min']})",
                    f"(close < trend) | (rsi < {p['rsi_exit']})",
                    p["stop"],
                ),
                {"direction": "long", **p},
                "Pareto id 122",
                "PF/Sharpe much superior with OOS stability",
            )
            for p in vals
        ]

    def macd_ema_roc():
        vals = _sample(
            _ranges(
                {
                    "ema": [20, 34, 55, 89, 144],
                    "fast": [8, 10, 12, 14],
                    "slow": [21, 26, 34, 40],
                    "signal": [5, 7, 9, 12],
                    "roc": [10, 20, 34],
                    "stop": [0.02, 0.032, 0.045, 0.065],
                }
            ),
            34,
            4,
        )
        return [
            Candidate(
                "macd-ema-roc-quality",
                "MACD plus trend and ROC quality filter targets non-dominated return/PF.",
                _td(
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": p["ema"]}},
                        {"type": "macd", "alias": "macd", "params": {"fast": p["fast"], "slow": p["slow"], "signal": p["signal"]}},
                        {"type": "roc", "alias": "roc", "params": {"length": p["roc"]}},
                    ],
                    "(close > trend) & (macd.macd > macd.signal) & (roc > 0)",
                    "(macd.macd < macd.signal) | (close < trend)",
                    p["stop"],
                ),
                {"direction": "long", **p},
                "Pareto id 9 and 122",
                "regime/filter materially different",
            )
            for p in vals
        ]

    def adx_roc_trend():
        vals = _sample(
            _ranges(
                {
                    "ema": [30, 55, 89, 144, 200],
                    "adx_len": [10, 14, 20, 28],
                    "adx": [15, 20, 25, 30],
                    "roc": [10, 20, 30],
                    "stop": [0.018, 0.03, 0.045, 0.065],
                }
            ),
            30,
            5,
        )
        return [
            Candidate(
                "adx-roc-trend-regime",
                "ADX regime filter tries to reduce drawdown while keeping enough return.",
                _td(
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": p["ema"]}},
                        {"type": "adx", "alias": "adx", "params": {"length": p["adx_len"]}},
                        {"type": "roc", "alias": "roc", "params": {"length": p["roc"]}},
                    ],
                    f"(close > trend) & (adx > {p['adx']}) & (roc > 0)",
                    "(close < trend) | (roc < 0)",
                    p["stop"],
                ),
                {"direction": "long", **p},
                "Pareto id 122",
                "drawdown much lower with return sufficient",
            )
            for p in vals
        ]

    def bb_roc_breakout():
        vals = _sample(
            _ranges(
                {
                    "bb_len": [14, 20, 30, 40, 55],
                    "bb_std": [1.5, 2.0, 2.5, 3.0],
                    "roc": [8, 13, 21, 34],
                    "roc_min": [-2, 0, 2, 4],
                    "stop": [0.018, 0.03, 0.045, 0.065],
                }
            ),
            26,
            6,
        )
        return [
            Candidate(
                "bb-roc-breakout",
                "Volatility breakout with momentum guard targets a different thesis.",
                _td(
                    [
                        {"type": "bbands", "alias": "bb", "params": {"length": p["bb_len"], "std": p["bb_std"]}},
                        {"type": "roc", "alias": "roc", "params": {"length": p["roc"]}},
                    ],
                    f"(close > bb.upper) & (roc > {p['roc_min']})",
                    "(close < bb.middle) | (roc < 0)",
                    p["stop"],
                ),
                {"direction": "long", **p},
                "Pareto id 9",
                "regime/filter materially different",
            )
            for p in vals
        ]

    def atr_trend_breakout():
        vals = _sample(
            _ranges(
                {
                    "ema": [30, 55, 89, 144],
                    "atr_len": [10, 14, 20],
                    "entry_mult": [0.2, 0.4, 0.6, 0.8],
                    "exit_mult": [0.1, 0.2, 0.35],
                    "stop": [0.018, 0.03, 0.045, 0.065],
                }
            ),
            24,
            7,
        )
        return [
            Candidate(
                "atr-trend-breakout",
                "ATR breakout seeks strong continuation without MA crossover duplication.",
                _td(
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": p["ema"]}},
                        {"type": "atr", "alias": "atr", "params": {"length": p["atr_len"]}},
                    ],
                    f"(close > trend) & (close > close.shift(1) + atr * {p['entry_mult']})",
                    f"(close < trend) | (close < close.shift(1) - atr * {p['exit_mult']})",
                    p["stop"],
                ),
                {"direction": "long", **p},
                "Pareto id 9",
                "more return with drawdown not worse",
            )
            for p in vals
        ]

    def ema_pullback_continuation():
        vals = _sample(
            _ranges(
                {
                    "fast": [10, 14, 21, 30],
                    "slow": [55, 89, 144, 200],
                    "rsi": [10, 14, 21],
                    "rsi_low": [35, 40, 45],
                    "rsi_high": [55, 60, 65],
                    "stop": [0.018, 0.03, 0.045, 0.065],
                }
            ),
            24,
            8,
        )
        return [
            Candidate(
                "ema-rsi-pullback-continuation",
                "Pullback inside uptrend targets defensive profile.",
                _td(
                    [
                        {"type": "ema", "alias": "fast", "params": {"length": p["fast"]}},
                        {"type": "ema", "alias": "slow", "params": {"length": p["slow"]}},
                        {"type": "rsi", "alias": "rsi", "params": {"length": p["rsi"]}},
                    ],
                    f"(close > slow) & (close < fast) & (rsi > {p['rsi_low']}) & (rsi < {p['rsi_high']})",
                    "(close < slow) | (rsi > 75)",
                    p["stop"],
                ),
                {"direction": "long", **p},
                "Pareto id 122",
                "drawdown much lower with return sufficient",
            )
            for p in vals
        ]

    def volume_roc_breakout():
        vals = _sample(
            _ranges(
                {
                    "vol_len": [10, 20, 30, 50],
                    "vol_mult": [1.1, 1.3, 1.5, 1.8],
                    "roc": [8, 13, 21, 34],
                    "roc_min": [-2, 0, 2, 4],
                    "stop": [0.018, 0.03, 0.045, 0.065],
                }
            ),
            24,
            9,
        )
        return [
            Candidate(
                "volume-roc-breakout",
                "Volume and ROC breakout tests participation-confirmed continuation.",
                _td(
                    [
                        {"type": "volume_sma", "alias": "vol_avg", "params": {"length": p["vol_len"]}},
                        {"type": "roc", "alias": "roc", "params": {"length": p["roc"]}},
                    ],
                    f"(volume > vol_avg * {p['vol_mult']}) & (roc > {p['roc_min']})",
                    "(roc < 0) | (close < close.shift(3))",
                    p["stop"],
                ),
                {"direction": "long", **p},
                "Pareto id 9",
                "regime/filter materially different",
            )
            for p in vals
        ]

    def rsi_regime_reentry():
        vals = _sample(
            _ranges(
                {
                    "ema": [55, 89, 144, 200],
                    "rsi": [10, 14, 21, 28],
                    "low": [30, 35, 40, 45],
                    "exit": [60, 65, 70, 75],
                    "stop": [0.018, 0.03, 0.045, 0.065],
                }
            ),
            22,
            10,
        )
        return [
            Candidate(
                "rsi-regime-reentry",
                "RSI reentry in BTC uptrend tests defensive exceptional profile.",
                _td(
                    [
                        {"type": "ema", "alias": "trend", "params": {"length": p["ema"]}},
                        {"type": "rsi", "alias": "rsi", "params": {"length": p["rsi"]}},
                    ],
                    f"(close > trend) & (rsi > {p['low']}) & (rsi < 55)",
                    f"(close < trend) | (rsi > {p['exit']})",
                    p["stop"],
                ),
                {"direction": "long", **p},
                "Pareto id 122",
                "PF/Sharpe much superior with OOS stability",
            )
            for p in vals
        ]

    def macd_adx_regime():
        vals = _sample(
            _ranges(
                {
                    "fast": [8, 10, 12, 14],
                    "slow": [21, 26, 34, 40],
                    "signal": [5, 7, 9],
                    "adx_len": [10, 14, 20],
                    "adx": [15, 20, 25],
                    "stop": [0.018, 0.03, 0.045, 0.065],
                }
            ),
            24,
            11,
        )
        return [
            Candidate(
                "macd-adx-regime",
                "MACD signal gated by ADX tries to improve PF without weak regimes.",
                _td(
                    [
                        {"type": "macd", "alias": "macd", "params": {"fast": p["fast"], "slow": p["slow"], "signal": p["signal"]}},
                        {"type": "adx", "alias": "adx", "params": {"length": p["adx_len"]}},
                    ],
                    f"(macd.macd > macd.signal) & (adx > {p['adx']})",
                    "(macd.macd < macd.signal)",
                    p["stop"],
                ),
                {"direction": "long", **p},
                "Pareto id 122",
                "PF/Sharpe much superior with OOS stability",
            )
            for p in vals
        ]

    def bb_rsi_defensive():
        vals = _sample(
            _ranges(
                {
                    "bb_len": [14, 20, 30, 40],
                    "bb_std": [1.5, 2.0, 2.5],
                    "rsi": [10, 14, 21],
                    "rsi_low": [25, 30, 35, 40],
                    "stop": [0.018, 0.03, 0.045, 0.065],
                }
            ),
            22,
            12,
        )
        return [
            Candidate(
                "bb-rsi-defensive-reversion",
                "Defensive volatility reversion explores a low drawdown Pareto profile.",
                _td(
                    [
                        {"type": "bbands", "alias": "bb", "params": {"length": p["bb_len"], "std": p["bb_std"]}},
                        {"type": "rsi", "alias": "rsi", "params": {"length": p["rsi"]}},
                    ],
                    f"(close < bb.lower) & (rsi < {p['rsi_low']})",
                    "(close > bb.middle) | (rsi > 65)",
                    p["stop"],
                ),
                {"direction": "long", **p},
                "Pareto id 122",
                "defensive exceptional profile",
            )
            for p in vals
        ]

    return [
        ("cycle-1", "more return with drawdown not worse", "MA crossover material variants", ma_fast_medium),
        ("cycle-2", "regime/filter materially different", "EMA ROC continuation", ema_roc_trend),
        ("cycle-3", "PF/Sharpe superior", "EMA ROC RSI guard", ema_roc_rsi_guard),
        ("cycle-4", "regime/filter materially different", "MACD EMA ROC quality", macd_ema_roc),
        ("cycle-5", "drawdown lower with return sufficient", "ADX ROC trend", adx_roc_trend),
        ("cycle-6", "regime/filter materially different", "BB ROC breakout", bb_roc_breakout),
        ("cycle-7", "more return with drawdown not worse", "ATR trend breakout", atr_trend_breakout),
        ("cycle-8", "defensive profile", "EMA RSI pullback continuation", ema_pullback_continuation),
        ("cycle-9", "regime/filter materially different", "Volume ROC breakout", volume_roc_breakout),
        ("cycle-10", "PF/Sharpe superior", "RSI regime reentry", rsi_regime_reentry),
        ("cycle-11", "PF/Sharpe superior", "MACD ADX regime", macd_adx_regime),
        ("cycle-12", "defensive exceptional profile", "BB RSI defensive reversion", bb_rsi_defensive),
    ]


def _evaluate(candidate: Candidate, df_daily, df_15m) -> dict[str, Any]:
    strategy = ComboStrategy(
        indicators=candidate.template_data["indicators"],
        entry_logic=candidate.template_data["entry_logic"],
        exit_logic=candidate.template_data["exit_logic"],
        stop_loss=candidate.template_data["stop_loss"],
    )
    df_signals = strategy.generate_signals(df_daily.copy())
    trades, mode = extract_trades_with_mode(
        df_signals,
        candidate.template_data["stop_loss"],
        deep_backtest=True,
        symbol=SYMBOL,
        since_str=FULL_START,
        until_str=FULL_END,
        df_15m_cache=df_15m,
        direction="long",
        return_mode=True,
    )
    metrics = _metrics_from_trades(trades, INITIAL_CAPITAL, context_params=candidate.parameters)
    return {
        "fingerprint": _fingerprint(candidate),
        "family": candidate.family,
        "thesis": candidate.thesis,
        "target": candidate.target,
        "route": candidate.route,
        "strategy_name": f"tmp_quant_20260607_{candidate.family}",
        "parameters": candidate.parameters,
        "template_data": candidate.template_data,
        "execution_mode": mode,
        "metrics": metrics,
        "trade_count": len(trades),
        "sample_trades": trades[:3],
        "last_trade": trades[-1] if trades else None,
    }


def _save_gate(row: dict[str, Any], t0: dict[str, Any]) -> tuple[bool, str]:
    metrics = row["metrics"]
    if row["execution_mode"] != "deep_15m":
        return False, "not_deep_15m"
    if metrics.get("total_trades", 0) < MIN_TRADES:
        return False, "too_few_trades"

    current = t0["revalidated_favorites"]
    if any(_dominates(fav, row) for fav in current):
        return False, "dominated_by_current_favorite"

    br = t0["benchmarks"]["BENCHMARK_RETURN"]["metrics"]
    b_return = br["total_return_pct"]
    b_dd = br["max_drawdown_pct"]
    b_pf = br["profit_factor"]
    ret = metrics["total_return_pct"]
    dd = metrics["max_drawdown_pct"]
    pf = metrics["profit_factor"]
    sharpe = metrics.get("sharpe_ratio", 0)
    current_sharpe = max((fav["metrics"].get("sharpe_ratio") or 0) for fav in current)

    if ret >= b_return and dd <= b_dd and pf >= b_pf * 0.98:
        return True, "dominancia_clara"
    if ret >= 0.90 * b_return and dd <= 0.85 * b_dd and (pf > b_pf or sharpe > current_sharpe):
        return True, "perfil_pareto_defensavel"
    if dd <= 0.75 * b_dd and ret >= 0.75 * b_return and pf > b_pf and sharpe > current_sharpe:
        return True, "defensiva_excepcional"
    return False, "fails_superation_gate"


def _stress(row: dict[str, Any], df_daily, df_15m) -> dict[str, Any]:
    params = row["parameters"]
    variants = []
    numeric_keys = [k for k, v in params.items() if isinstance(v, (int, float)) and k not in {"direction"}]
    for key in numeric_keys[:4]:
        for delta in (-1, 1):
            mutated = json.loads(json.dumps(row["template_data"]))
            value = params[key]
            if isinstance(value, int):
                new_value = max(1, int(value + delta))
            else:
                new_value = max(0.001, float(value) * (1 + 0.05 * delta))
            # Mutating exact template is intentionally best-effort for stress summary.
            text_blob = json.dumps(mutated)
            text_blob = text_blob.replace(json.dumps(value), json.dumps(new_value), 1)
            mutated = json.loads(text_blob)
            c = Candidate(
                row["family"],
                row["thesis"],
                mutated,
                {**params, key: new_value},
                row["target"],
                row["route"],
            )
            try:
                variants.append(_evaluate(c, df_daily, df_15m))
            except Exception as exc:
                variants.append({"error": str(exc), "parameters": c.parameters})
    valid = [v for v in variants if not v.get("error")]
    return {
        "variant_count": len(variants),
        "valid_count": len(valid),
        "min_return_pct": min((v["metrics"]["total_return_pct"] for v in valid), default=None),
        "max_drawdown_pct": max((v["metrics"]["max_drawdown_pct"] for v in valid), default=None),
        "all_deep_15m": all(v.get("execution_mode") == "deep_15m" for v in valid),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-candidates", type=int, default=300)
    args = parser.parse_args()

    logging.disable(logging.CRITICAL)
    start = time.monotonic()
    t0 = json.loads(T0_PATH.read_text(encoding="utf-8"))

    loader = IncrementalLoader()
    df_daily = loader.fetch_data(SYMBOL, TIMEFRAME, FULL_START, FULL_END, read_only=True)
    df_15m = loader.fetch_intraday_data(SYMBOL, "15m", FULL_START, FULL_END, read_only=True)
    if df_daily.empty or df_15m.empty:
        raise SystemExit("Missing daily or 15m data")

    results = []
    cycles = []
    seen = set()
    duplicate_count = 0
    for cycle, route, thesis, factory in _families():
        cycle_candidates = factory()
        cycle_rows = []
        for candidate in cycle_candidates:
            fp = _fingerprint(candidate)
            if fp in seen:
                duplicate_count += 1
                continue
            seen.add(fp)
            row = _evaluate(candidate, df_daily, df_15m)
            row["cycle"] = cycle
            eligible, reason = _save_gate(row, t0)
            row["eligible_for_save"] = eligible
            row["gate_reason"] = reason
            results.append(row)
            cycle_rows.append(row)
            if len(results) >= args.min_candidates:
                break
        best = sorted(
            cycle_rows,
            key=lambda r: (
                r["eligible_for_save"],
                r["metrics"].get("total_return_pct", 0),
                -r["metrics"].get("max_drawdown_pct", 999),
                r["metrics"].get("profit_factor", 0),
            ),
            reverse=True,
        )[:3]
        cycles.append(
            {
                "cycle": cycle,
                "route": route,
                "thesis": thesis,
                "target": cycle_rows[0]["target"] if cycle_rows else None,
                "executed": len(cycle_rows),
                "eligible": sum(1 for r in cycle_rows if r["eligible_for_save"]),
                "best": [
                    {
                        "family": r["family"],
                        "parameters": r["parameters"],
                        "metrics": r["metrics"],
                        "gate_reason": r["gate_reason"],
                    }
                    for r in best
                ],
            }
        )
        if len(results) >= args.min_candidates:
            break

    finalists = [
        r
        for r in results
        if r["execution_mode"] == "deep_15m"
        and r["metrics"].get("total_trades", 0) >= MIN_TRADES
        and r["gate_reason"] not in {"dominated_by_current_favorite", "too_few_trades"}
    ]
    finalists = sorted(
        finalists,
        key=lambda r: (
            r["eligible_for_save"],
            r["metrics"].get("total_return_pct", 0),
            -r["metrics"].get("max_drawdown_pct", 999),
            r["metrics"].get("profit_factor", 0),
        ),
        reverse=True,
    )
    stress_targets = finalists[:6]
    stress = [
        {
            "fingerprint": row["fingerprint"],
            "family": row["family"],
            "parameters": row["parameters"],
            "base_metrics": row["metrics"],
            "stress": _stress(row, df_daily, df_15m),
        }
        for row in stress_targets
    ]
    elapsed = time.monotonic() - start
    report = {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "direction": "long",
        "period": {"start_date": FULL_START, "end_date": FULL_END},
        "search_seconds": elapsed,
        "cycles": cycles,
        "distinct_theses": len(_families()),
        "unique_template_families": len({r["family"] for r in results}),
        "executed_material_deep_candidates": len(results),
        "duplicate_candidates": duplicate_count,
        "post_benchmark_adaptive_rounds": len(cycles),
        "all_execution_modes": sorted({r["execution_mode"] for r in results}),
        "eligible_winners": [
            r
            for r in results
            if r["eligible_for_save"]
        ],
        "finalists_for_stress": stress,
        "ranking_top_25": [
            {
                "rank": idx + 1,
                "family": r["family"],
                "cycle": r["cycle"],
                "parameters": r["parameters"],
                "metrics": r["metrics"],
                "eligible_for_save": r["eligible_for_save"],
                "gate_reason": r["gate_reason"],
                "target": r["target"],
                "route": r["route"],
            }
            for idx, r in enumerate(
                sorted(
                    results,
                    key=lambda r: (
                        r["eligible_for_save"],
                        r["metrics"].get("total_return_pct", 0),
                        -r["metrics"].get("max_drawdown_pct", 999),
                        r["metrics"].get("profit_factor", 0),
                    ),
                    reverse=True,
                )[:25]
            )
        ],
        "discard_summary": {
            reason: sum(1 for r in results if r["gate_reason"] == reason)
            for reason in sorted({r["gate_reason"] for r in results})
        },
    }
    filename = f"candidate_search_{report['created_at'].replace(':', '').replace('-', '').replace('+00:00', 'Z')}.json"
    output = ARTIFACT_DIR / filename
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    summary = {
        "output": str(output.relative_to(ROOT)),
        "executed": len(results),
        "families": report["unique_template_families"],
        "cycles": len(cycles),
        "eligible_winners": len(report["eligible_winners"]),
        "top": report["ranking_top_25"][:5],
        "discard_summary": report["discard_summary"],
        "seconds": round(elapsed, 2),
    }
    print(json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
