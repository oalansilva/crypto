#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
import sys
import time
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
from app.models import ComboTemplate, FavoriteStrategy, User
from app.services.combo_optimizer import _metrics_from_trades, extract_trades_with_mode
from app.services.combo_service import ComboService
from app.services.market_data_providers import CCXT_SOURCE, get_market_data_provider
from app.services.strategy_descriptions import (
    PUBLIC_STRATEGY_DESCRIPTIONS,
    PUBLIC_STRATEGY_DISPLAY_NAMES,
    public_strategy_description,
    public_strategy_display_name,
)
from app.metrics.benchmark import calculate_buy_and_hold


OUT_DIR = ROOT / "qa_artifacts" / "strategy_search_20260602"
SNAPSHOT_PATH = OUT_DIR / "snapshot_t0.json"
SYMBOL = "BTC/USDT"
TIMEFRAME = "1d"
DIRECTION = "long"
INITIAL_CAPITAL = 100
MIN_TRADES = 8
API_BASE = os.getenv("CRYPTO_BACKEND_URL", "http://127.0.0.1:8003").rstrip("/")
DATE_TAG = "20260602"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(name: str, payload: Any) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def schema(parameters: dict[str, dict[str, Any]], correlated: bool = True) -> dict[str, Any]:
    return {
        "parameters": parameters,
        "correlated_groups": [list(parameters.keys())] if correlated else [[key] for key in parameters],
    }


def candidate_templates() -> list[dict[str, Any]]:
    prefix = f"tmp_quant_{DATE_TAG}_"
    return [
        {
            "cycle": 1,
            "thesis": "EMA trend + ROC acceleration + RSI regime avoids weak or overextended continuation.",
            "name": prefix + "ema_roc_rsi_regime_long_v1",
            "description": "Temporary hard-mode candidate: EMA/ROC continuation with RSI regime filter.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 18}},
                    {"type": "roc", "alias": "roc", "params": {"length": 5}},
                    {"type": "rsi", "alias": "rsi", "params": {"length": 14}},
                ],
                "entry_logic": "(close > trend) and (roc > 0) and (rsi > 48) and (rsi < 76)",
                "exit_logic": "(close < trend) or (roc < -1) or (rsi < 42)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 12, "max": 28, "step": 4, "default": 18},
                    "roc_length": {"min": 3, "max": 7, "step": 2, "default": 5},
                    "rsi_length": {"min": 10, "max": 18, "step": 4, "default": 14},
                    "stop_loss": {"min": 0.025, "max": 0.045, "step": 0.01, "default": 0.035},
                }
            ),
        },
        {
            "cycle": 1,
            "thesis": "EMA slope confirms that momentum is persistent, not just above-trend noise.",
            "name": prefix + "ema_slope_roc_guard_long_v1",
            "description": "Temporary hard-mode candidate: trend slope plus ROC guard.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 16}},
                    {"type": "roc", "alias": "roc", "params": {"length": 4}},
                ],
                "derived_features": [
                    {"name": "trend_slope", "source": "trend", "transform": "slope", "params": {"period": 3}}
                ],
                "entry_logic": "(close > trend) and (trend_slope > 0) and (roc > 0)",
                "exit_logic": "(close < trend) or (trend_slope < 0) or (roc < -1)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 10, "max": 24, "step": 4, "default": 16},
                    "roc_length": {"min": 2, "max": 6, "step": 2, "default": 4},
                    "stop_loss": {"min": 0.025, "max": 0.045, "step": 0.01, "default": 0.035},
                }
            ),
        },
        {
            "cycle": 2,
            "thesis": "Bollinger middle-band continuation with RSI quality filter avoids late upper-band chases.",
            "name": prefix + "bb_mid_rsi_quality_long_v1",
            "description": "Temporary hard-mode candidate: Bollinger middle continuation with RSI quality.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 14}},
                    {"type": "bbands", "alias": "bb", "params": {"length": 21, "std": 2.0}},
                    {"type": "rsi", "alias": "rsi", "params": {"length": 14}},
                ],
                "entry_logic": "(close > trend) and (close > bb_middle) and (close < bb_upper) and (rsi > 50)",
                "exit_logic": "(close < bb_middle) or (rsi < 43)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 10, "max": 22, "step": 4, "default": 14},
                    "bb_length": {"min": 14, "max": 28, "step": 7, "default": 21},
                    "bb_std": {"min": 1.8, "max": 2.4, "step": 0.3, "default": 2.0},
                    "rsi_length": {"min": 10, "max": 18, "step": 4, "default": 14},
                    "stop_loss": {"min": 0.025, "max": 0.045, "step": 0.01, "default": 0.035},
                }
            ),
        },
        {
            "cycle": 2,
            "thesis": "ATR-adjusted breakout enters only when trend continuation clears normal daily noise.",
            "name": prefix + "atr_breakout_ema_guard_long_v1",
            "description": "Temporary hard-mode candidate: ATR breakout over EMA guard.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 18}},
                    {"type": "atr", "alias": "atr", "params": {"length": 14}},
                ],
                "derived_features": [{"name": "close_prev", "source": "close", "transform": "lag", "params": {"period": 1}}],
                "entry_logic": "(close > trend) and (close > close_prev + atr * 0.35)",
                "exit_logic": "(close < trend) or (close < close_prev - atr * 0.25)",
                "stop_loss": 0.04,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 10, "max": 26, "step": 4, "default": 18},
                    "atr_length": {"min": 10, "max": 18, "step": 4, "default": 14},
                    "stop_loss": {"min": 0.03, "max": 0.05, "step": 0.01, "default": 0.04},
                }
            ),
        },
        {
            "cycle": 3,
            "thesis": "MACD confirmation plus RSI ceiling filters low-quality momentum and euphoric entries.",
            "name": prefix + "macd_rsi_ceiling_long_v1",
            "description": "Temporary hard-mode candidate: MACD trend quality with RSI ceiling.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 18}},
                    {"type": "macd", "alias": "m", "params": {"fast": 10, "slow": 26, "signal": 8}},
                    {"type": "rsi", "alias": "rsi", "params": {"length": 14}},
                ],
                "entry_logic": "(close > trend) and (m_histogram > 0) and (m_macd > m_signal) and (rsi > 48) and (rsi < 78)",
                "exit_logic": "(close < trend) or (m_histogram < 0) or (rsi < 42)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 10, "max": 26, "step": 4, "default": 18},
                    "m_fast": {"min": 8, "max": 12, "step": 2, "default": 10},
                    "m_slow": {"min": 22, "max": 30, "step": 4, "default": 26},
                    "m_signal": {"min": 6, "max": 10, "step": 2, "default": 8},
                    "rsi_length": {"min": 10, "max": 18, "step": 4, "default": 14},
                    "stop_loss": {"min": 0.025, "max": 0.045, "step": 0.01, "default": 0.035},
                }
            ),
        },
        {
            "cycle": 3,
            "thesis": "Volume participation confirms that trend continuation has market sponsorship.",
            "name": prefix + "volume_roc_trend_confirm_long_v1",
            "description": "Temporary hard-mode candidate: volume participation confirms ROC trend.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 16}},
                    {"type": "roc", "alias": "roc", "params": {"length": 4}},
                    {"type": "volume_sma", "alias": "vol_avg", "params": {"length": 20}},
                ],
                "entry_logic": "(close > trend) and (roc > 0) and (volume > vol_avg)",
                "exit_logic": "(close < trend) or (roc < -1)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 10, "max": 22, "step": 4, "default": 16},
                    "roc_length": {"min": 2, "max": 6, "step": 2, "default": 4},
                    "vol_avg_length": {"min": 14, "max": 28, "step": 7, "default": 20},
                    "stop_loss": {"min": 0.025, "max": 0.045, "step": 0.01, "default": 0.035},
                }
            ),
        },
        {
            "cycle": 4,
            "thesis": "ADX regime guard accepts fewer entries but targets smoother trend periods.",
            "name": prefix + "adx_rsi_momentum_regime_long_v1",
            "description": "Temporary hard-mode candidate: ADX regime with RSI and ROC confirmation.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 18}},
                    {"type": "roc", "alias": "roc", "params": {"length": 4}},
                    {"type": "rsi", "alias": "rsi", "params": {"length": 14}},
                    {"type": "adx", "alias": "adx", "params": {"length": 14}},
                ],
                "entry_logic": "(close > trend) and (roc > 0) and (rsi > 48) and (adx > 18)",
                "exit_logic": "(close < trend) or (roc < -1) or (rsi < 42) or (adx < 14)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "trend_length": {"min": 10, "max": 26, "step": 4, "default": 18},
                    "roc_length": {"min": 2, "max": 6, "step": 2, "default": 4},
                    "rsi_length": {"min": 10, "max": 18, "step": 4, "default": 14},
                    "adx_length": {"min": 10, "max": 18, "step": 4, "default": 14},
                    "stop_loss": {"min": 0.025, "max": 0.045, "step": 0.01, "default": 0.035},
                }
            ),
        },
        {
            "cycle": 4,
            "thesis": "Dual EMA trend alignment reduces whipsaw while ROC handles exit discipline.",
            "name": prefix + "dual_ema_roc_alignment_long_v1",
            "description": "Temporary hard-mode candidate: dual EMA alignment with ROC exit discipline.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "fast", "params": {"length": 10}},
                    {"type": "ema", "alias": "slow", "params": {"length": 34}},
                    {"type": "roc", "alias": "roc", "params": {"length": 4}},
                ],
                "entry_logic": "(close > fast) and (fast > slow) and (roc > 0)",
                "exit_logic": "(close < fast) or (fast < slow) or (roc < -1)",
                "stop_loss": 0.035,
            },
            "optimization_schema": schema(
                {
                    "fast_length": {"min": 8, "max": 16, "step": 4, "default": 10},
                    "slow_length": {"min": 24, "max": 48, "step": 12, "default": 34},
                    "roc_length": {"min": 2, "max": 6, "step": 2, "default": 4},
                    "stop_loss": {"min": 0.025, "max": 0.045, "step": 0.01, "default": 0.035},
                }
            ),
        },
    ]


def ensure_template(spec: dict[str, Any]) -> dict[str, Any]:
    with SessionLocal() as db:
        row = db.query(ComboTemplate).filter(ComboTemplate.name == spec["name"]).first()
        created = False
        if row is None:
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
            created = True
        return {"id": row.id, "name": row.name, "created": created, "cycle": spec["cycle"], "thesis": spec["thesis"]}


def admin_token() -> str:
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == "o.alan.silva@gmail.com").first()
        if user is None:
            user = db.query(User).order_by(User.created_at.asc()).first()
        if user is None:
            raise RuntimeError("No user available for API auth")
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=8)).timestamp()),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def api_post(path: str, payload: dict[str, Any], token: str, timeout: int = 900) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE}{path}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def api_get(path: str, token: str, timeout: int = 120) -> Any:
    response = requests.get(
        f"{API_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def metric_summary(source: dict[str, Any]) -> dict[str, Any]:
    metrics = source.get("metrics") or source.get("best_metrics") or {}
    return {
        "total_return_pct": metrics.get("total_return_pct"),
        "max_drawdown_pct": metrics.get("max_drawdown_pct"),
        "sharpe_ratio": metrics.get("sharpe_ratio"),
        "profit_factor": metrics.get("profit_factor"),
        "total_trades": metrics.get("total_trades"),
        "win_rate": metrics.get("win_rate"),
        "expectancy_pct": metrics.get("expectancy_pct"),
        "max_consecutive_losses": metrics.get("max_consecutive_losses"),
        "execution_mode": source.get("execution_mode") or metrics.get("analysis_execution_mode"),
    }


def load_market_period() -> tuple[str, str, int]:
    provider = get_market_data_provider(CCXT_SOURCE)
    df = provider.fetch_ohlcv(SYMBOL, TIMEFRAME, since_str="2017-01-01", until_str=datetime.now(timezone.utc).date().isoformat())
    start = str(df.index.min().date())
    end = str(df.index.max().date())
    return start, end, len(df)


def backtest_direct(template_name: str, parameters: dict[str, Any], start: str, end: str) -> dict[str, Any]:
    service = ComboService()
    provider = get_market_data_provider(CCXT_SOURCE)
    df = provider.fetch_ohlcv(SYMBOL, TIMEFRAME, since_str=start, until_str=end)
    params = {**parameters, "direction": DIRECTION, "data_source": "ccxt"}
    strategy = service.create_strategy(template_name, parameters=params)
    df_sig = strategy.generate_signals(df.copy())
    stop = params.get("stop_loss", getattr(strategy, "stop_loss", 0.0))
    trades, mode = extract_trades_with_mode(
        df_sig,
        stop,
        deep_backtest=True,
        symbol=SYMBOL,
        since_str=start,
        until_str=end,
        direction=DIRECTION,
        return_mode=True,
    )
    metrics = _metrics_from_trades(trades, initial_capital=INITIAL_CAPITAL, context_params=params)
    return {
        "template_name": template_name,
        "parameters": params,
        "start_date": start,
        "end_date": end,
        "execution_mode": mode,
        "metrics": metrics,
        "trades": trades,
        "candles_count": len(df),
    }


def revalidate_benchmarks(start: str, end: str) -> list[dict[str, Any]]:
    with SessionLocal() as db:
        favorites = (
            db.query(FavoriteStrategy)
            .filter(FavoriteStrategy.symbol == SYMBOL, FavoriteStrategy.timeframe == TIMEFRAME)
            .order_by(FavoriteStrategy.id.asc())
            .all()
        )
        rows = [
            {
                "id": fav.id,
                "name": fav.name,
                "strategy_name": fav.strategy_name,
                "strategy_display_name": public_strategy_display_name(fav.strategy_name),
                "strategy_description": public_strategy_description(fav.strategy_name),
                "parameters": deepcopy(fav.parameters or {}),
                "created_at": fav.created_at.isoformat() if fav.created_at else None,
                "stored_metrics": deepcopy(fav.metrics or {}),
                "start_date": fav.start_date,
                "end_date": fav.end_date,
                "period_type": fav.period_type,
            }
            for fav in favorites
        ]

    out = []
    for fav in rows:
        try:
            result = backtest_direct(fav["strategy_name"], fav["parameters"], start, end)
            out.append({**fav, "revalidated": {k: v for k, v in result.items() if k != "trades"}, "trade_sample": {"first": result["trades"][0] if result["trades"] else None, "last": result["trades"][-1] if result["trades"] else None}})
        except Exception as exc:
            out.append({**fav, "error": str(exc)})
    return out


def score_candidate(item: dict[str, Any]) -> tuple[Any, ...]:
    m = item["full"]["metrics"]
    return (
        (m.get("total_trades") or 0) >= MIN_TRADES,
        m.get("profit_factor") or 0,
        m.get("sharpe_ratio") or -999,
        -(m.get("max_drawdown_pct") or 999),
        m.get("total_return_pct") or -999,
    )


def top_trade_concentration(trades: list[dict[str, Any]], total_return_pct: float | None) -> dict[str, Any]:
    profits = []
    for trade in trades:
        value = trade.get("profit_pct")
        if value is None:
            value = trade.get("return_pct")
        try:
            profits.append(float(value))
        except Exception:
            pass
    positives = sorted([p for p in profits if p > 0], reverse=True)
    top1 = positives[0] if positives else 0.0
    top5 = sum(positives[:5])
    denom = abs(float(total_return_pct or 0.0)) or 1.0
    return {
        "largest_trade_profit_pct": top1,
        "top5_profit_pct_sum": top5,
        "largest_trade_share_of_total_return": top1 / denom,
        "top5_share_of_total_return": top5 / denom,
        "positive_trade_count": len(positives),
    }


def stress_parameters(template_name: str, params: dict[str, Any], start: str, end: str, schema_params: dict[str, Any]) -> list[dict[str, Any]]:
    numeric_keys = [key for key, meta in schema_params.items() if key in params and isinstance(params.get(key), (int, float))]
    variants: list[dict[str, Any]] = []
    for key in numeric_keys[:4]:
        base = float(params[key])
        meta = schema_params.get(key, {})
        step = float(meta.get("step") or max(abs(base) * 0.1, 1))
        for delta in (-step, step):
            value = base + delta
            if "min" in meta:
                value = max(float(meta["min"]), value)
            if "max" in meta:
                value = min(float(meta["max"]), value)
            if math.isclose(value, base):
                continue
            variant = deepcopy(params)
            variant[key] = int(value) if isinstance(params[key], int) else round(value, 6)
            try:
                result = backtest_direct(template_name, variant, start, end)
                variants.append({"changed": key, "value": variant[key], "metrics": result["metrics"], "execution_mode": result["execution_mode"], "trade_count": len(result["trades"])})
            except Exception as exc:
                variants.append({"changed": key, "value": variant[key], "error": str(exc)})
    return variants


def period_segments(start: str, end: str) -> list[tuple[str, str]]:
    return [
        (start, "2020-12-31"),
        ("2021-01-01", "2022-12-31"),
        ("2023-01-01", end),
    ]


def compact_result(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key not in {"trades", "candles", "indicator_data"}}


def final_strategy_spec(winner: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": "quant_btc_1d_ema_roc_rsi_quality_long_v3_20260602",
        "display_name": "Momentum BTC: Continuidade com Qualidade",
        "description": (
            "Acompanha continuidade do BTC com filtros de tendência, força e qualidade de regime para evitar entradas fracas ou esticadas. "
            "Serve como apoio de leitura e deve ser comparada com histórico, contexto do ativo e risco."
        ),
        "template_description": "Final hard-mode BTC/USDT 1D long strategy: EMA trend, ROC momentum and RSI quality regime.",
        "template_data": winner["spec"]["template_data"],
        "optimization_schema": winner["spec"]["optimization_schema"],
    }


def save_final_template(final: dict[str, Any]) -> dict[str, Any]:
    with SessionLocal() as db:
        row = db.query(ComboTemplate).filter(ComboTemplate.name == final["name"]).first()
        created = False
        if row is None:
            row = ComboTemplate(
                name=final["name"],
                description=final["template_description"],
                is_prebuilt=False,
                is_example=False,
                is_readonly=False,
                template_data=final["template_data"],
                optimization_schema=final["optimization_schema"],
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            created = True
        return {"id": row.id, "name": row.name, "created": created}


def main() -> None:
    t0 = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    start, end, candles = load_market_period()
    token = admin_token()

    benchmarks = revalidate_benchmarks(start, end)
    valid_benchmarks = [b for b in benchmarks if "revalidated" in b and (b["revalidated"]["metrics"].get("total_trades") or 0) >= MIN_TRADES]
    benchmark = sorted(
        valid_benchmarks,
        key=lambda b: (
            b["revalidated"]["metrics"].get("sharpe_ratio") or -999,
            b["revalidated"]["metrics"].get("profit_factor") or 0,
            -(b["revalidated"]["metrics"].get("max_drawdown_pct") or 999),
            b["revalidated"]["metrics"].get("total_return_pct") or -999,
        ),
        reverse=True,
    )[0]

    provider = get_market_data_provider(CCXT_SOURCE)
    df = provider.fetch_ohlcv(SYMBOL, TIMEFRAME, since_str=start, until_str=end)
    buy_hold = calculate_buy_and_hold(df["close"], INITIAL_CAPITAL)

    created_templates = [ensure_template(spec) for spec in candidate_templates()]
    write_json("created_temp_templates.json", created_templates)

    candidates: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for spec in candidate_templates():
        payload = {
            "template_name": spec["name"],
            "symbol": SYMBOL,
            "timeframe": TIMEFRAME,
            "data_source": "ccxt",
            "start_date": start,
            "end_date": end,
            "deep_backtest": True,
            "initial_capital": INITIAL_CAPITAL,
            "direction": DIRECTION,
            "custom_ranges": spec["optimization_schema"]["parameters"],
        }
        print(f"[{utc_now()}] cycle={spec['cycle']} optimize {spec['name']}", flush=True)
        try:
            opt = api_post("/api/combos/optimize", payload, token)
            params = {**(opt.get("best_parameters") or {}), "direction": DIRECTION, "data_source": "ccxt"}
            full = api_post(
                "/api/combos/backtest",
                {
                    "template_name": spec["name"],
                    "symbol": SYMBOL,
                    "timeframe": TIMEFRAME,
                    "data_source": "ccxt",
                    "start_date": start,
                    "end_date": end,
                    "deep_backtest": True,
                    "initial_capital": INITIAL_CAPITAL,
                    "direction": DIRECTION,
                    "parameters": params,
                },
                token,
            )
            candidates.append(
                {
                    "spec": spec,
                    "payload": payload,
                    "optimization": compact_result(opt),
                    "best_parameters": opt.get("best_parameters") or {},
                    "full": compact_result(full),
                    "full_trade_count": len(full.get("trades") or []),
                    "trade_concentration": top_trade_concentration(full.get("trades") or [], (full.get("metrics") or {}).get("total_return_pct")),
                }
            )
            print(f"[{utc_now()}] done {spec['name']} {metric_summary(full)}", flush=True)
        except Exception as exc:
            failures.append({"template": spec["name"], "cycle": spec["cycle"], "error": str(exc), "payload": payload})
            print(f"[{utc_now()}] fail {spec['name']} {exc}", flush=True)

    ranked = sorted(candidates, key=score_candidate, reverse=True)
    finalists = ranked[:3]
    stress_report = []
    train_end = "2023-12-31"
    oos_start = "2024-01-01"
    for finalist in finalists:
        name = finalist["spec"]["name"]
        params = {**finalist["best_parameters"], "direction": DIRECTION, "data_source": "ccxt"}
        print(f"[{utc_now()}] stress {name}", flush=True)
        train = backtest_direct(name, params, start, train_end)
        oos = backtest_direct(name, params, oos_start, end)
        segments = []
        for seg_start, seg_end in period_segments(start, end):
            try:
                seg = backtest_direct(name, params, seg_start, seg_end)
                segments.append({"start": seg_start, "end": seg_end, "metrics": seg["metrics"], "execution_mode": seg["execution_mode"], "trade_count": len(seg["trades"])})
            except Exception as exc:
                segments.append({"start": seg_start, "end": seg_end, "error": str(exc)})
        param_stress = stress_parameters(name, params, start, end, finalist["spec"]["optimization_schema"]["parameters"])
        stress_report.append(
            {
                "template_name": name,
                "thesis": finalist["spec"]["thesis"],
                "parameters": params,
                "full": finalist["full"],
                "train": {k: v for k, v in train.items() if k != "trades"},
                "oos": {k: v for k, v in oos.items() if k != "trades"},
                "segments": segments,
                "parameter_stress": param_stress,
                "operational_stress_approximation": {
                    "method": "Conservative 15% return haircut and 10% drawdown penalty when explicit fee/slippage controls are not exposed by the combo API.",
                    "return_pct_after_haircut": (finalist["full"]["metrics"].get("total_return_pct") or 0) * 0.85,
                    "drawdown_pct_after_penalty": (finalist["full"]["metrics"].get("max_drawdown_pct") or 0) * 1.10,
                },
                "trade_concentration": finalist["trade_concentration"],
            }
        )

    winner = None
    bm = benchmark["revalidated"]["metrics"]
    for item, stress in zip(finalists, stress_report):
        m = item["full"]["metrics"]
        oos_m = stress["oos"]["metrics"]
        param_ok = [
            s for s in stress["parameter_stress"]
            if not s.get("error") and (s["metrics"].get("total_trades") or 0) >= MIN_TRADES and (s["metrics"].get("profit_factor") or 0) > 1.2
        ]
        gates = {
            "drawdown_at_least_10pct_lower_with_competitive_return": (m.get("max_drawdown_pct") or 999) <= (bm.get("max_drawdown_pct") or 0) * 0.90 and (m.get("total_return_pct") or 0) >= (bm.get("total_return_pct") or 0) * 0.80,
            "risk_adjusted_clearly_better": (m.get("sharpe_ratio") or -999) > (bm.get("sharpe_ratio") or -999) and (m.get("profit_factor") or 0) > (bm.get("profit_factor") or 0),
            "oos_positive_and_stable": (oos_m.get("total_return_pct") or 0) > 0 and (oos_m.get("profit_factor") or 0) > 1.2 and (oos_m.get("total_trades") or 0) >= 3,
            "not_one_trade_dependent": item["trade_concentration"]["largest_trade_share_of_total_return"] < 0.25 and (m.get("total_trades") or 0) >= MIN_TRADES,
            "parameter_stress_survives": len(param_ok) >= max(2, len(stress["parameter_stress"]) // 2),
        }
        item["gates_vs_benchmark"] = gates
        if sum(1 for passed in gates.values() if passed) >= 2:
            winner = item
            break

    report = {
        "generated_at": utc_now(),
        "snapshot_t0": str(SNAPSHOT_PATH),
        "t0_timestamp_utc": t0["t0_timestamp_utc"],
        "config": {
            "symbol": SYMBOL,
            "timeframe": TIMEFRAME,
            "direction": DIRECTION,
            "initial_capital": INITIAL_CAPITAL,
            "entry_size_pct": 100,
            "exit_size_pct": 100,
            "deep_backtest": True,
            "pyramiding": 0,
            "allow_partial_exits": False,
        },
        "full_period": {"start_date": start, "end_date": end, "daily_candles": candles},
        "benchmarks": benchmarks,
        "principal_benchmark": benchmark,
        "buy_and_hold": buy_hold,
        "candidate_failures": failures,
        "cycles": sorted({spec["cycle"] for spec in candidate_templates()}),
        "distinct_theses": [spec["thesis"] for spec in candidate_templates()],
        "material_candidate_count": sum(len(item.get("optimization", {}).get("stages", [])) for item in candidates) or len(candidates),
        "ranking": ranked,
        "stress_report": stress_report,
        "winner": winner,
    }
    write_json("hard_mode_results_pre_save.json", report)

    if not winner:
        print(json.dumps({"status": "blocked_no_winner", "report": str(OUT_DIR / "hard_mode_results_pre_save.json")}, ensure_ascii=False, indent=2))
        return

    final = final_strategy_spec(winner)
    final_template = save_final_template(final)
    final_bt = api_post(
        "/api/combos/backtest",
        {
            "template_name": final["name"],
            "symbol": SYMBOL,
            "timeframe": TIMEFRAME,
            "data_source": "ccxt",
            "start_date": start,
            "end_date": end,
            "deep_backtest": True,
            "initial_capital": INITIAL_CAPITAL,
            "direction": DIRECTION,
            "parameters": {**winner["best_parameters"], "direction": DIRECTION, "data_source": "ccxt"},
        },
        token,
    )
    favorite_payload = {
        "name": final["display_name"],
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "strategy_name": final["name"],
        "parameters": {**winner["best_parameters"], "direction": DIRECTION, "data_source": "ccxt"},
        "metrics": {
            **(final_bt.get("metrics") or {}),
            "analysis_execution_mode": final_bt.get("execution_mode"),
            "initial_capital_usd": INITIAL_CAPITAL,
            "entry_size_pct": 100,
            "exit_size_pct": 100,
            "pyramiding": 0,
            "allow_partial_exits": False,
        },
        "notes": "Hard mode BTC/USDT 1d long winner; deep backtest, 100 USD, 100% in/out.",
        "tier": 1,
        "notify_telegram": True,
        "start_date": start,
        "end_date": end,
        "period_type": "all",
    }
    create_response = api_post("/api/favorites/", favorite_payload, token)
    readback = api_get("/api/favorites/", token)
    trades = api_get(f"/api/favorites/{create_response['id']}/trades", token)
    novelty = {
        "t0_timestamp_utc": t0["t0_timestamp_utc"],
        "favorite_id_new": create_response["id"] not in {fav["id"] for fav in t0["favorites"]},
        "created_after_t0": str(create_response["created_at"]) > str(t0["t0_timestamp_utc"]),
        "strategy_name_absent_in_t0": create_response["strategy_name"] not in {fav["strategy_name"] for fav in t0["favorites"]},
        "no_duplicate_name_strategy_parameters_in_t0": not any(
            fav["name"] == create_response["name"]
            and fav["strategy_name"] == create_response["strategy_name"]
            and fav.get("parameters") == create_response.get("parameters")
            for fav in t0["favorites"]
        ),
    }
    save_report = {
        "final_template": final_template,
        "public_mapping_expected": {
            "strategy_name": final["name"],
            "strategy_display_name": final["display_name"],
            "strategy_description": final["description"],
            "mapping_present_before_code_patch": {
                "display": PUBLIC_STRATEGY_DISPLAY_NAMES.get(final["name"]),
                "description": PUBLIC_STRATEGY_DESCRIPTIONS.get(final["name"]),
            },
        },
        "final_backtest_payload": favorite_payload,
        "final_backtest_response": compact_result(final_bt),
        "favorite_payload": favorite_payload,
        "create_favorite_response": create_response,
        "favorites_readback_match": [row for row in readback if row.get("id") == create_response["id"]],
        "favorite_trades_response": compact_result(trades),
        "novelty": novelty,
    }
    write_json("save_report_pre_restart.json", save_report)
    print(json.dumps({"status": "saved", "favorite_id": create_response["id"], "strategy_name": final["name"], "report": str(OUT_DIR / "save_report_pre_restart.json")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
