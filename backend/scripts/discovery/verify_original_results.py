"""Exact independent winning signals/trades, final metrics and cleanup checks."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import talib

from app.metrics.benchmark import calculate_buy_and_hold
from app.metrics.criteria import evaluate_discovery_go_nogo
from app.metrics.performance import calculate_cagr
from app.metrics.risk_adjusted import calculate_calmar_ratio
from app.services import combo_optimizer as opt
from app.services.combo_service import ComboService
from tests.fixtures.discovery_memory import semantic_oracle

ROOT = Path("/srv/apps/dev/criptofarol/crypto-worktrees/card-1093-discovery-memory")
FIXTURE = ROOT / "backend/tests/fixtures/discovery_memory"
EVIDENCE = ROOT / "openspec/changes/card-1093-discovery-memory"


def verify_historical_diversity():
    path = "backend/app/services/combo_optimizer.py"
    record = json.loads((FIXTURE / "historical_diversity.json").read_text())
    baseline = record["source"]

    def method(source):
        return next(
            node
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.FunctionDef) and node.name == "_select_top_candidates"
        )

    historical = method(baseline)
    assert hashlib.sha256(ast.dump(historical).encode()).hexdigest() == record["ast_sha256"]
    assert ast.dump(historical) == ast.dump(method((ROOT / path).read_text()))
    namespace = {"List": List, "Dict": Dict}
    exec(
        compile(ast.Module(body=[historical], type_ignores=[]), "historical-diversity", "exec"),
        namespace,
    )
    candidates = [
        {
            "params": {"length": trial % 21 / 2, "stop_loss": trial / 1000, "direction": "long"},
            "score": float(400 - trial // 3),
            "trial": trial,
        }
        for trial in range(401)
    ]
    legacy = namespace["_select_top_candidates"](None, candidates, top_k=20, min_dist=0.5)
    current = opt.ComboOptimizer._select_top_candidates(None, candidates, top_k=20, min_dist=0.5)
    assert current == legacy
    return {
        "baseline": "99a3070cd9d117539fe6de734361f07d5e1c4611",
        "method_ast_identical": True,
        "selected_trials": [candidate["trial"] for candidate in current],
    }


def digest(value):
    return hashlib.sha256(json.dumps(value, default=str, sort_keys=True).encode()).hexdigest()


def enrich(train):
    frame = train.copy()
    high, low, close = (frame[column].astype(float) for column in ("high", "low", "close"))
    frame["ATR_14"] = talib.ATR(high, low, close, timeperiod=14)
    frame["SMA_50"] = talib.SMA(close, timeperiod=50)
    frame["SMA_200"] = talib.SMA(close, timeperiod=200)
    frame["regime"] = "Unknown"
    frame.loc[close > frame.SMA_50, "regime"] = "Bull"
    frame.loc[close < frame.SMA_50, "regime"] = "Bear"
    return frame


def final_reference(report, frame, metadata):
    parameters = report["result"]["parameters"]
    train, holdout = opt.split_train_holdout(frame, 0.7)
    train = enrich(train)
    expected, trades, signals = semantic_oracle.evaluate(train, parameters, True, frame)
    service = object.__new__(ComboService)
    service.get_template_metadata = lambda _: metadata
    strategy = service.create_strategy(metadata["name"], parameters)
    actual = strategy.generate_signals(train.copy())
    np.testing.assert_array_equal(actual.signal, signals.signal)
    actual_trades = opt.extract_trades_with_mode(
        actual,
        parameters["stop_loss"],
        True,
        "BTC/USDT",
        "2025-10-06",
        "2026-10-06",
        frame,
        direction=parameters["direction"],
        slippage=opt.slippage_for_timeframe("15m"),
    )
    assert actual_trades == trades
    for regime in ("Bull", "Bear"):
        segment = [
            trade
            for trade in trades
            if signals.loc[signals.index.asof(pd.Timestamp(trade["entry_time"]))]["regime"]
            == regime
        ]
        expected["win_rate_" + regime.lower()] = (
            sum(trade["profit"] > 0 for trade in segment) / len(segment) if segment else 0
        )
    # Unchanged metric/cost functions are covered by historical exact goldens;
    # indicator series and position signals above come from the independent oracle.
    opt._enrich_ranking_metrics(trades, train.close, expected, legacy_zero_trade_ranking=True)
    evaluation = pd.concat([train.iloc[-250:][frame.columns], holdout])
    _, raw_trades, oos_signals = semantic_oracle.evaluate(evaluation, parameters, True, frame)
    actual_oos = strategy.generate_signals(evaluation.copy())
    np.testing.assert_array_equal(actual_oos.signal, oos_signals.signal)
    actual_oos_trades = opt.extract_trades_with_mode(
        actual_oos,
        parameters["stop_loss"],
        True,
        "BTC/USDT",
        str(evaluation.index.min().date()),
        str(evaluation.index.max().date()),
        frame,
        direction=parameters["direction"],
        slippage=opt.slippage_for_timeframe("15m"),
    )
    assert actual_oos_trades == raw_trades
    oos_trades = [
        trade for trade in raw_trades if pd.Timestamp(trade["entry_time"]) >= holdout.index.min()
    ]
    oos = opt._metrics_from_trades(oos_trades, 100)
    cap, equity_values = 100.0, [100.0]
    for trade in sorted(oos_trades, key=lambda value: pd.Timestamp(value["entry_time"])):
        cap *= 1.0 + float(trade.get("profit") or 0.0)
        equity_values.append(cap)
    years = opt._calendar_years_from_evidence(holdout.close, oos_trades)
    cagr = calculate_cagr(pd.Series(equity_values), years=years) if oos_trades and years else 0.0
    oos.update(
        cagr=cagr,
        calmar_ratio=calculate_calmar_ratio(cagr, float(oos["max_drawdown"] or 0.0)),
        benchmark=calculate_buy_and_hold(holdout.close, 100.0),
    )
    verdict = evaluate_discovery_go_nogo(expected, oos)
    expected.update(
        split_train_ratio=0.7,
        split_applied=True,
        oos_metrics=oos,
        oos_verdict={
            "status": verdict.status,
            "reasons": verdict.reasons,
            "warnings": verdict.warnings,
            "holdout_trades": len(oos_trades),
            "execution_mode": "deep_15m",
            "split_train_ratio": 0.7,
        },
    )
    # Persistence contract (JSONB rejects Infinity/NaN; verdict only for eligible
    # results): non-finite ranking values become omitted keys and low-sample
    # results (fewer than DISCOVERY_MIN_TRADES=30 train trades) carry no verdict.
    # The independently computed verdict is still hashed below.
    persisted = {
        key: value
        for key, value in expected.items()
        if not (isinstance(value, float) and not np.isfinite(value))
    }
    eligible = len(trades) >= 30
    if not eligible:
        persisted.pop("oos_verdict")
    assert report["result"]["eligibility"] == ("eligible" if eligible else "low_sample")
    assert report["result"]["metrics"] == persisted, (report["result"]["metrics"], persisted)
    return {
        "eligibility": report["result"]["eligibility"],
        "train_trades": len(trades),
        "holdout_trades": len(oos_trades),
        "parameters": parameters,
        "metrics_sha256": digest(expected),
        "train_trades_sha256": digest(trades),
        "holdout_trades_sha256": digest(oos_trades),
        "verdict": verdict.status,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    kind, count = ("pilot", 1) if args.pilot else ("original", 3)
    frame = pd.read_parquet(FIXTURE / "original_candles.parquet").set_index("timestamp_utc")
    fixture = json.loads((FIXTURE / "original_template.json").read_text())
    metadata = {"name": fixture["name"], **fixture["template_data"]}
    reports = [
        json.loads((EVIDENCE / f"{kind}_run_{run}.json").read_text()) for run in range(1, count + 1)
    ]
    references = [final_reference(report, frame, metadata) for report in reports]
    assert all(reference == references[0] for reference in references)
    assert all(
        report["cache_bytes"] == 0 and report["telemetry"]["cache_bytes"] == 0 for report in reports
    )
    growth = {}
    if count == 3:
        for key in ("rss_bytes", "pss_bytes", "memory.current"):
            values = [int(report["telemetry"][key]) for report in reports]
            increments = [values[index + 1] - values[index] for index in range(2)]
            assert values[2] - values[0] <= 128 * 1024**2, (key, values)
            assert not all(increment > 64 * 1024**2 for increment in increments), (key, values)
            growth[key] = {"bytes": values, "increments": increments}
    result = {
        "kind": kind,
        "complete_runs": count,
        "historical_diversity": verify_historical_diversity(),
        "exact_final_reference": references,
        "post_cleanup_growth": growth,
    }
    (EVIDENCE / f"{kind}_final_verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
