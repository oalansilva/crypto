#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
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
from app.services.strategy_descriptions import public_strategy_description, public_strategy_display_name


OUT_DIR = ROOT / "qa_artifacts" / "strategy_search_20260602"
API_BASE = os.getenv("CRYPTO_BACKEND_URL", "http://127.0.0.1:8003").rstrip("/")
SYMBOL = "BTC/USDT"
TIMEFRAME = "1d"
DIRECTION = "long"
START = "2017-08-17"
END = "2026-06-02"
INITIAL_CAPITAL = 100
STRATEGY_NAME = "quant_btc_1d_ema_roc_rsi_quality_guard_long_v1_20260602"
DISPLAY_NAME = "Momentum BTC: Continuidade com Filtro de Qualidade"
DESCRIPTION = (
    "Acompanha continuidade do BTC com filtro adicional de qualidade para evitar entradas fracas ou esticadas. "
    "Serve como apoio de leitura e deve ser comparada com histórico, contexto do ativo e risco."
)
PARAMETERS = {
    "trend_length": 15,
    "roc_length": 2,
    "rsi_length": 10,
    "stop_loss": 0.025,
    "direction": DIRECTION,
    "data_source": "ccxt",
}
TEMPLATE_DATA = {
    "indicators": [
        {"type": "ema", "alias": "trend", "params": {"length": 15}},
        {"type": "roc", "alias": "roc", "params": {"length": 2}},
        {"type": "rsi", "alias": "rsi", "params": {"length": 10}},
    ],
    "entry_logic": "(close > trend) & (roc > 0) & (rsi > 48) & (rsi < 82)",
    "exit_logic": "(close < trend) | (roc < -1) | (rsi < 40)",
    "stop_loss": 0.025,
}
OPTIMIZATION_SCHEMA = {
    "parameters": {
        "trend_length": {"type": "int", "min": 12, "max": 18, "step": 3},
        "roc_length": {"type": "int", "min": 2, "max": 4, "step": 2},
        "rsi_length": {"type": "int", "min": 10, "max": 18, "step": 4},
        "stop_loss": {"type": "float", "min": 0.02, "max": 0.03, "step": 0.005},
    },
    "correlated_groups": [],
}


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
            "analysis_execution_mode",
            "initial_capital_usd",
            "entry_size_pct",
            "exit_size_pct",
            "pyramiding",
            "allow_partial_exits",
        )
    }


def ensure_template() -> dict[str, Any]:
    with SessionLocal() as db:
        row = db.query(ComboTemplate).filter(ComboTemplate.name == STRATEGY_NAME).first()
        if row is None:
            row = ComboTemplate(
                name=STRATEGY_NAME,
                description=DESCRIPTION,
                is_prebuilt=False,
                is_example=False,
                is_readonly=False,
                template_data=TEMPLATE_DATA,
                optimization_schema=OPTIMIZATION_SCHEMA,
            )
            db.add(row)
        else:
            row.description = DESCRIPTION
            row.template_data = TEMPLATE_DATA
            row.optimization_schema = OPTIMIZATION_SCHEMA
        db.commit()
        db.refresh(row)
        return {
            "id": row.id,
            "name": row.name,
            "description": row.description,
            "template_data": row.template_data,
            "optimization_schema": row.optimization_schema,
        }


def admin_token() -> str:
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == "o.alan.silva@gmail.com").first()
        if user is None:
            user = db.query(User).order_by(User.created_at.asc()).first()
        if user is None:
            raise RuntimeError("No user available for API auth")
        issued = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "access",
            "iat": int(issued.timestamp()),
            "exp": int((issued + timedelta(hours=8)).timestamp()),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def api(method: str, path: str, token: str, payload: dict[str, Any] | None = None, timeout: int = 900) -> Any:
    response = requests.request(
        method,
        f"{API_BASE}{path}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json() if response.content else None


def final_backtest() -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    provider = get_market_data_provider(CCXT_SOURCE)
    df = provider.fetch_ohlcv(SYMBOL, TIMEFRAME, since_str=START, until_str=END)
    strategy = ComboService().create_strategy(STRATEGY_NAME, parameters=PARAMETERS)
    signals = strategy.generate_signals(df.copy())
    trades, mode = extract_trades_with_mode(
        signals,
        PARAMETERS["stop_loss"],
        deep_backtest=True,
        symbol=SYMBOL,
        since_str=START,
        until_str=END,
        direction=DIRECTION,
        return_mode=True,
    )
    metrics = _metrics_from_trades(trades, initial_capital=INITIAL_CAPITAL, context_params=PARAMETERS)
    metrics.update(
        {
            "analysis_execution_mode": mode,
            "initial_capital_usd": INITIAL_CAPITAL,
            "entry_size_pct": 100,
            "exit_size_pct": 100,
            "pyramiding": 0,
            "allow_partial_exits": False,
        }
    )
    return metrics, trades, mode


def dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    ret = (a.get("total_return_pct") or -10**18) >= (b.get("total_return_pct") or -10**18)
    dd = (a.get("max_drawdown_pct") or 10**18) <= (b.get("max_drawdown_pct") or 10**18)
    spf = ((a.get("sharpe_ratio") or -10**18) >= (b.get("sharpe_ratio") or -10**18)) or (
        (a.get("profit_factor") or -10**18) >= (b.get("profit_factor") or -10**18)
    )
    strict = (
        (a.get("total_return_pct") or -10**18) > (b.get("total_return_pct") or -10**18)
        or (a.get("max_drawdown_pct") or 10**18) < (b.get("max_drawdown_pct") or 10**18)
        or (a.get("sharpe_ratio") or -10**18) > (b.get("sharpe_ratio") or -10**18)
        or (a.get("profit_factor") or -10**18) > (b.get("profit_factor") or -10**18)
    )
    return ret and dd and spf and strict


def load_benchmarks() -> list[dict[str, Any]]:
    deep = json.loads((OUT_DIR / "api_deep_revalidation_t0_20260602.json").read_text(encoding="utf-8"))
    return [row for row in deep["results"] if row.get("status") == 200]


def delete_invalid(favorite_id: int, token: str) -> None:
    api("DELETE", f"/api/favorites/{favorite_id}", token, timeout=120)


def main() -> None:
    started = now()
    t0 = json.loads((OUT_DIR / "snapshot_t0.json").read_text(encoding="utf-8"))
    mapping = {
        "display": public_strategy_display_name(STRATEGY_NAME),
        "description": public_strategy_description(STRATEGY_NAME),
    }
    template = ensure_template()
    metrics, trades, mode = final_backtest()
    benchmarks = load_benchmarks()
    dominated_by = [
        {
            "id": row["id"],
            "name": row["name"],
            "strategy_name": row["strategy_name"],
            "metrics": subset(row["metrics"]),
        }
        for row in benchmarks
        if dominates(row["metrics"], metrics)
    ]
    if mode != "deep_15m" or dominated_by or mapping["display"] != DISPLAY_NAME or mapping["description"] != DESCRIPTION:
        raise RuntimeError(
            json.dumps(
                {
                    "mode": mode,
                    "dominated_by": dominated_by,
                    "mapping": mapping,
                },
                ensure_ascii=False,
            )
        )
    token = admin_token()
    payload = {
        "name": DISPLAY_NAME,
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "strategy_name": STRATEGY_NAME,
        "parameters": PARAMETERS,
        "metrics": metrics,
        "notes": "Hard mode BTC/USDT 1d long winner; deep backtest, 100 USD, 100% in/out, no partial exits.",
        "tier": 1,
        "notify_telegram": True,
        "start_date": START,
        "end_date": END,
        "period_type": "all",
        "auto_refresh_status": "completed",
        "auto_refresh_completed_at": datetime.now(timezone.utc).isoformat(),
    }
    created = api("POST", "/api/favorites/", token, payload)
    readback = api("GET", "/api/favorites/", token, timeout=120)
    trades_readback = api("GET", f"/api/favorites/{created['id']}/trades", token, timeout=900)
    match = [row for row in readback if row.get("id") == created["id"]]
    final_metrics = (match[0].get("metrics") if match else {}) or {}
    final_gate = {
        "favorite_id_new": created["id"] not in {fav["id"] for fav in t0["favorites"]},
        "created_after_t0": str(created["created_at"]) > str(t0["t0_timestamp_utc"]),
        "strategy_name_absent_in_t0": created["strategy_name"] not in {fav["strategy_name"] for fav in t0["favorites"]},
        "no_duplicate_name_strategy_parameters_in_t0": not any(
            fav["name"] == created["name"]
            and fav["strategy_name"] == created["strategy_name"]
            and fav.get("parameters") == created.get("parameters")
            for fav in t0["favorites"]
        ),
        "api_visible": bool(match),
        "display_name_ok": bool(match) and match[0].get("strategy_display_name") == DISPLAY_NAME,
        "description_ok": bool(match) and match[0].get("strategy_description") == DESCRIPTION,
        "fallback_absent": bool(match)
        and match[0].get("strategy_display_name") != "Estratégia Cripto Farol"
        and bool(match[0].get("strategy_description")),
        "backtest_updated": (final_metrics.get("analysis_execution_mode") == "deep_15m")
        and (final_metrics.get("total_trades") or 0) >= 8,
        "trades_visible": isinstance(trades_readback, dict)
        and (len(trades_readback.get("trades") or []) >= 8 or (trades_readback.get("metrics") or {}).get("total_trades", 0) >= 8),
        "not_dominated_by_t0": not dominated_by,
    }
    invalid_reasons = [key for key, value in final_gate.items() if not value]
    report = {
        "started_at": started,
        "generated_at": now(),
        "template": template,
        "mapping": mapping,
        "payload": payload,
        "create_response": created,
        "favorites_readback_match": match,
        "trades_readback_summary": {
            "keys": sorted(trades_readback.keys()) if isinstance(trades_readback, dict) else None,
            "trade_count": len(trades_readback.get("trades") or []) if isinstance(trades_readback, dict) else None,
            "metrics": subset((trades_readback.get("metrics") or {}) if isinstance(trades_readback, dict) else {}),
        },
        "final_metrics": subset(metrics),
        "local_trade_count": len(trades),
        "execution_mode": mode,
        "benchmarks": [
            {"id": row["id"], "name": row["name"], "strategy_name": row["strategy_name"], "metrics": subset(row["metrics"])}
            for row in benchmarks
        ],
        "dominated_by": dominated_by,
        "final_gate": final_gate,
        "invalid_reasons": invalid_reasons,
    }
    path = write_json("promotion_quality_guard_report.json", report)
    if invalid_reasons:
        delete_invalid(created["id"], token)
        report["removed_invalid_favorite_id"] = created["id"]
        write_json("promotion_quality_guard_report.json", report)
        raise RuntimeError(f"Final gate failed; favorite removed: {invalid_reasons}")
    print(json.dumps({"status": "saved", "favorite_id": created["id"], "report": str(path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
