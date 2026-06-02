#!/usr/bin/env python3
import json
import os
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
os.chdir(ROOT)

from app.database import SessionLocal
from app.models import ComboTemplate, FavoriteStrategy
from app.services.combo_optimizer import ComboOptimizer, _metrics_from_trades, extract_trades_with_mode
from app.services.combo_service import ComboService
from app.services.market_data_providers import CCXT_SOURCE, get_market_data_provider
from app.metrics.benchmark import calculate_buy_and_hold


OUT_DIR = ROOT / "qa_artifacts" / "strategy_search_20260601"
SNAPSHOT = OUT_DIR / "snapshot_t0.json"
SYMBOL = "BTC/USDT"
TIMEFRAME = "1d"
START_DATE = "2017-08-17"
END_DATE = "2026-06-01"
TRAIN_END = "2023-12-31"
OOS_START = "2024-01-01"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def schema(parameters, correlated=True):
    return {
        "parameters": parameters,
        "correlated_groups": [list(parameters.keys())] if correlated else [[k] for k in parameters],
    }


def candidate_templates():
    return [
        {
            "name": "tmp_quant_20260601_ema_roc_adx_guard_long_v1",
            "description": "T0+ candidate: EMA/ROC continuity with ADX regime guard; all-in/all-out long only.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 12}},
                    {"type": "roc", "alias": "roc", "params": {"length": 4}},
                    {"type": "adx", "alias": "adx", "params": {"length": 14}},
                ],
                "entry_logic": "(close > trend) and (roc > 0) and (adx > 18)",
                "exit_logic": "(close < trend) or (roc < -2) or (adx < 14)",
                "stop_loss": 0.03,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 8, "max": 20, "step": 4, "default": 12},
                    "roc_length": {"min": 2, "max": 6, "step": 2, "default": 4},
                    "adx_length": {"min": 10, "max": 18, "step": 4, "default": 14},
                    "stop_loss": {"min": 0.02, "max": 0.04, "step": 0.01, "default": 0.03},
                }
            ),
        },
        {
            "name": "tmp_quant_20260601_macd_ema_roc_trend_long_v1",
            "description": "T0+ candidate: MACD histogram confirmation over EMA trend with ROC momentum.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 16}},
                    {"type": "macd", "alias": "m", "params": {"fast": 10, "slow": 24, "signal": 8}},
                    {"type": "roc", "alias": "roc", "params": {"length": 4}},
                ],
                "entry_logic": "(close > trend) and (m_histogram > 0) and (m_macd > m_signal) and (roc > 0)",
                "exit_logic": "(close < trend) or (m_histogram < 0) or (roc < -2)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 8, "max": 20, "step": 4, "default": 16},
                    "m_fast": {"min": 8, "max": 12, "step": 2, "default": 10},
                    "m_slow": {"min": 22, "max": 30, "step": 4, "default": 24},
                    "m_signal": {"min": 6, "max": 10, "step": 2, "default": 8},
                    "roc_length": {"min": 2, "max": 6, "step": 2, "default": 4},
                    "stop_loss": {"min": 0.02, "max": 0.04, "step": 0.01, "default": 0.035},
                }
            ),
        },
        {
            "name": "tmp_quant_20260601_rsi_ema_pullback_continuation_long_v1",
            "description": "T0+ candidate: EMA trend continuation with RSI pullback window.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "fast", "params": {"length": 10}},
                    {"type": "ema", "alias": "slow", "params": {"length": 34}},
                    {"type": "rsi", "alias": "rsi", "params": {"length": 14}},
                ],
                "entry_logic": "(close > slow) and (close > fast) and (rsi > 42) and (rsi < 68)",
                "exit_logic": "(close < fast) or (rsi < 38) or (rsi > 82)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "fast_length": {"min": 8, "max": 16, "step": 4, "default": 10},
                    "slow_length": {"min": 24, "max": 48, "step": 12, "default": 34},
                    "rsi_length": {"min": 10, "max": 20, "step": 5, "default": 14},
                    "stop_loss": {"min": 0.02, "max": 0.05, "step": 0.01, "default": 0.035},
                }
            ),
        },
        {
            "name": "tmp_quant_20260601_adx_volume_momentum_long_v1",
            "description": "T0+ candidate: momentum continuation with ADX and volume participation guard.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 14}},
                    {"type": "roc", "alias": "roc", "params": {"length": 4}},
                    {"type": "adx", "alias": "adx", "params": {"length": 14}},
                    {"type": "volume_sma", "alias": "vol_avg", "params": {"length": 20}},
                ],
                "entry_logic": "(close > trend) and (roc > 0) and (adx > 20) and (volume > vol_avg)",
                "exit_logic": "(close < trend) or (roc < -1) or (adx < 15)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 8, "max": 20, "step": 4, "default": 14},
                    "roc_length": {"min": 2, "max": 6, "step": 2, "default": 4},
                    "adx_length": {"min": 10, "max": 18, "step": 4, "default": 14},
                    "vol_avg_length": {"min": 14, "max": 28, "step": 7, "default": 20},
                    "stop_loss": {"min": 0.02, "max": 0.04, "step": 0.01, "default": 0.035},
                }
            ),
        },
        {
            "name": "tmp_quant_20260601_bbands_ema_roc_compression_long_v1",
            "description": "T0+ candidate: EMA trend continuation through Bollinger middle-band pressure.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 14}},
                    {"type": "bbands", "alias": "bb", "params": {"length": 20, "std": 2.0}},
                    {"type": "roc", "alias": "roc", "params": {"length": 4}},
                ],
                "entry_logic": "(close > trend) and (close > bb_middle) and (close < bb_upper) and (roc > 0)",
                "exit_logic": "(close < bb_middle) or (roc < -1)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 8, "max": 20, "step": 4, "default": 14},
                    "bb_length": {"min": 14, "max": 28, "step": 7, "default": 20},
                    "bb_std": {"min": 1.8, "max": 2.4, "step": 0.3, "default": 2.0},
                    "roc_length": {"min": 2, "max": 6, "step": 2, "default": 4},
                    "stop_loss": {"min": 0.02, "max": 0.04, "step": 0.01, "default": 0.035},
                }
            ),
        },
        {
            "name": "tmp_quant_20260601_atr_trend_breakout_long_v1",
            "description": "T0+ candidate: EMA trend plus ATR-adjusted close breakout and defensive reversal exit.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 16}},
                    {"type": "atr", "alias": "atr", "params": {"length": 14}},
                ],
                "entry_logic": "(close > trend) and (close > close.shift(1) + atr * 0.5)",
                "exit_logic": "(close < trend) or (close < close.shift(1) - atr * 0.4)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 8, "max": 20, "step": 4, "default": 16},
                    "atr_length": {"min": 10, "max": 18, "step": 4, "default": 14},
                    "stop_loss": {"min": 0.02, "max": 0.05, "step": 0.01, "default": 0.035},
                }
            ),
        },
    ]


def upsert_template(spec):
    with SessionLocal() as db:
        row = db.query(ComboTemplate).filter(ComboTemplate.name == spec["name"]).first()
        if row:
            return row.id, False
        row = ComboTemplate(
            name=spec["name"],
            description=spec["description"],
            is_prebuilt=False,
            is_example=False,
            is_readonly=False,
            template_data=spec["template_data"],
            optimization_schema=spec["optimization_schema"],
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id, True


def load_favorites():
    with SessionLocal() as db:
        rows = (
            db.query(FavoriteStrategy)
            .filter(FavoriteStrategy.symbol == SYMBOL, FavoriteStrategy.timeframe == TIMEFRAME)
            .order_by(FavoriteStrategy.id.asc())
            .all()
        )
        return [
            {
                "id": r.id,
                "name": r.name,
                "strategy_name": r.strategy_name,
                "parameters": deepcopy(r.parameters or {}),
                "metrics": deepcopy(r.metrics or {}),
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "start_date": r.start_date,
                "end_date": r.end_date,
                "period_type": r.period_type,
            }
            for r in rows
        ]


def backtest(template_name, parameters, start_date, end_date):
    service = ComboService()
    provider = get_market_data_provider(CCXT_SOURCE)
    df = provider.fetch_ohlcv(SYMBOL, TIMEFRAME, since_str=start_date, until_str=end_date)
    strategy = service.create_strategy(template_name, parameters=parameters)
    df_sig = strategy.generate_signals(df.copy())
    stop = parameters.get("stop_loss", getattr(strategy, "stop_loss", 0.0))
    trades, mode = extract_trades_with_mode(
        df_sig,
        stop,
        deep_backtest=True,
        symbol=SYMBOL,
        since_str=start_date,
        until_str=end_date,
        direction="long",
        return_mode=True,
    )
    metrics = _metrics_from_trades(trades, initial_capital=100, context_params=parameters)
    return {
        "template_name": template_name,
        "parameters": parameters,
        "start_date": start_date,
        "end_date": end_date,
        "execution_mode": mode,
        "metrics": metrics,
        "trades": trades,
        "candles_count": len(df),
    }


def metric_summary(result):
    m = result.get("best_metrics") or result.get("metrics") or {}
    return {
        "total_return_pct": m.get("total_return_pct"),
        "max_drawdown_pct": m.get("max_drawdown_pct"),
        "sharpe_ratio": m.get("sharpe_ratio"),
        "profit_factor": m.get("profit_factor"),
        "total_trades": m.get("total_trades"),
        "win_rate": m.get("win_rate"),
        "expectancy_pct": m.get("expectancy_pct"),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    created_templates = []
    for spec in candidate_templates():
        template_id, created = upsert_template(spec)
        created_templates.append({"name": spec["name"], "id": template_id, "created": created})

    optimizer = ComboOptimizer()
    payloads = []
    candidates = []
    for spec in candidate_templates():
        payload = {
            "template_name": spec["name"],
            "symbol": SYMBOL,
            "timeframe": TIMEFRAME,
            "data_source": "ccxt",
            "start_date": START_DATE,
            "end_date": END_DATE,
            "deep_backtest": True,
            "initial_capital": 100,
            "direction": "long",
            "custom_ranges": spec["optimization_schema"]["parameters"],
        }
        payloads.append(payload)
        print(f"[{utc_now()}] optimize {spec['name']}", flush=True)
        result = optimizer.run_optimization(
            template_name=spec["name"],
            symbol=SYMBOL,
            timeframe=TIMEFRAME,
            data_source="ccxt",
            start_date=START_DATE,
            end_date=END_DATE,
            custom_ranges=payload["custom_ranges"],
            deep_backtest=True,
            direction="long",
        )
        full = backtest(spec["name"], {**result["best_parameters"], "direction": "long", "data_source": "ccxt"}, START_DATE, END_DATE)
        train = backtest(spec["name"], {**result["best_parameters"], "direction": "long", "data_source": "ccxt"}, START_DATE, TRAIN_END)
        oos = backtest(spec["name"], {**result["best_parameters"], "direction": "long", "data_source": "ccxt"}, OOS_START, END_DATE)
        candidates.append(
            {
                "template_name": spec["name"],
                "payload": payload,
                "best_parameters": result["best_parameters"],
                "best_metrics": result["best_metrics"],
                "execution_mode": result.get("execution_mode"),
                "full_revalidation": {k: v for k, v in full.items() if k != "trades"},
                "train": {k: v for k, v in train.items() if k != "trades"},
                "oos": {k: v for k, v in oos.items() if k != "trades"},
                "trades_count_full": len(full["trades"]),
                "first_trade": full["trades"][0] if full["trades"] else None,
                "last_trade": full["trades"][-1] if full["trades"] else None,
            }
        )
        print(f"[{utc_now()}] done {spec['name']} {metric_summary(full)}", flush=True)

    favorites = load_favorites()
    benchmarks = []
    for fav in favorites:
        params = {**(fav["parameters"] or {}), "direction": "long", "data_source": "ccxt"}
        try:
            bt = backtest(fav["strategy_name"], params, START_DATE, END_DATE)
            benchmarks.append({"favorite": fav, "full_revalidation": {k: v for k, v in bt.items() if k != "trades"}})
        except Exception as exc:
            benchmarks.append({"favorite": fav, "error": str(exc)})

    provider = get_market_data_provider(CCXT_SOURCE)
    df = provider.fetch_ohlcv(SYMBOL, TIMEFRAME, since_str=START_DATE, until_str=END_DATE)
    buy_hold = calculate_buy_and_hold(df["close"], 100)

    def rank_key(item):
        m = item["full_revalidation"]["metrics"]
        return (
            m.get("total_trades", 0) >= 8,
            m.get("total_return_pct", -999),
            -(m.get("max_drawdown_pct") or 999),
            m.get("sharpe_ratio", -999),
        )

    candidates_sorted = sorted(candidates, key=rank_key, reverse=True)
    report = {
        "generated_at": utc_now(),
        "snapshot_t0": str(SNAPSHOT),
        "t0_timestamp_utc": t0["t0_timestamp_utc"],
        "period": {"start_date": START_DATE, "end_date": END_DATE, "train": [START_DATE, TRAIN_END], "oos": [OOS_START, END_DATE]},
        "created_templates": created_templates,
        "payloads_optimize": payloads,
        "benchmarks": benchmarks,
        "buy_and_hold": buy_hold,
        "candidates_ranked": candidates_sorted,
    }
    out = OUT_DIR / "cycle1_results.json"
    out.write_text(json.dumps(report, default=str, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    print(json.dumps([{"template": c["template_name"], **metric_summary(c["full_revalidation"])} for c in candidates_sorted], indent=2, default=str))


if __name__ == "__main__":
    main()
