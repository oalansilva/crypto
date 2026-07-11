#!/usr/bin/env python3
"""Save and validate issue #277 sequential BTC/USDT 1d Long winners."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
import requests
from sqlalchemy import create_engine, text

from app.middleware.authMiddleware import ADMIN_EMAILS, JWT_SECRET
from app.services.combo_optimizer import _metrics_from_trades, extract_trades_with_mode
from app.services.strategy_descriptions import (
    public_strategy_description,
    public_strategy_display_name,
)
from app.strategies.combos import ComboStrategy
from src.data.incremental_loader import IncrementalLoader


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-277-hard-mode-v5-btc-long"
PINE_DIR = ROOT / "docs" / "tradingview" / "card-277-hard-mode-v5-btc-long"
def _latest_artifact(pattern: str) -> Path:
    latest = ARTIFACT_DIR / pattern.replace("*", "latest")
    if latest.exists():
        return latest
    matches = sorted(ARTIFACT_DIR.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No artifact matches {ARTIFACT_DIR / pattern}")
    return matches[-1]


CHAIN_PATH = _latest_artifact("chain-search-*.json")
T0_PATH = _latest_artifact("t0-snapshot-*.json")
BENCHMARK_PATH = _latest_artifact("benchmark-revalidation-*.json")
API_BASE = os.getenv("CARD_277_API_BASE", "http://127.0.0.1:8003")
SYMBOL = "BTC/USDT"
TIMEFRAME = "1d"
FULL_START = "2017-08-17"
FULL_END = datetime.now(timezone.utc).date().isoformat()
INITIAL_CAPITAL = 100
FORBIDDEN_COPY = {
    "",
    "Estratégia Cripto Farol",
    "estratégia cripto farol",
    "Strategy",
    "Nova estratégia",
}

WINNER_META = [
    {
        "strategy_name": "quant_btc_1d_long_bb_roc_chain_w1_20260629",
        "name": "BTC 1D LONG WINNER 1 - Bandas com Rompimento Defensivo",
        "thesis": "Bandas e momentum para inicializar a cadeia Long com drawdown menor que o Pareto T0.",
    },
    {
        "strategy_name": "quant_btc_1d_long_dual_momentum_chain_w2_20260629",
        "name": "BTC 1D LONG WINNER 2 - Momentum Duplo de Continuidade",
        "thesis": "Duas leituras de momentum e tendência para elevar retorno mantendo o drawdown do primeiro degrau.",
    },
    {
        "strategy_name": "quant_btc_1d_long_dual_momentum_chain_w3_20260629",
        "name": "BTC 1D LONG WINNER 3 - Momentum Duplo Acelerado",
        "thesis": "Variante material de momentum com janelas mais curtas para ampliar retorno sem piorar drawdown.",
    },
    {
        "strategy_name": "quant_btc_1d_long_ma_breakout_chain_w4_20260629",
        "name": "BTC 1D LONG WINNER 4 - Médias com Rompimento Confirmado",
        "thesis": "Médias e confirmação de força para superar os três primeiros degraus com retorno e qualidade maiores.",
    },
    {
        "strategy_name": "quant_btc_1d_long_ma_trend_chain_w5_20260629",
        "name": "BTC 1D LONG WINNER 5 - Médias com Continuidade Forte",
        "thesis": "Cadeia de médias com saída defensiva para fechar a sequência com maior retorno e menor drawdown.",
    },
]


def _json_default(value: Any) -> str:
    return str(value)


def _admin_token(engine) -> tuple[str, str]:
    emails = sorted(ADMIN_EMAILS)
    if not emails:
        raise RuntimeError("ADMIN_EMAILS is empty")
    with engine.connect() as conn:
        user = conn.execute(
            text(
                """
                SELECT id, email
                FROM users
                WHERE lower(email) = ANY(:emails)
                ORDER BY email
                LIMIT 1
                """
            ),
            {"emails": [email.lower() for email in emails]},
        ).mappings().first()
    if not user:
        raise RuntimeError("No admin user found for configured ADMIN_EMAILS")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user["id"]),
        "user_id": str(user["id"]),
        "email": str(user["email"]).lower(),
        "type": "access",
        "exp": now + timedelta(minutes=30),
        "iat": now,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256"), str(user["id"])


def _reject_copy(value: Any, field: str) -> str:
    text = str(value or "").strip()
    lowered = text.lower()
    if text in FORBIDDEN_COPY or "estratégia cripto farol" in lowered or "estrategia cripto farol" in lowered:
        raise RuntimeError(f"fallback public copy for {field}: {text!r}")
    return text


def _normalize_params(params: dict[str, Any]) -> dict[str, Any]:
    clean = dict(params)
    clean["direction"] = "long"
    clean["data_source"] = "ccxt"
    clean["deep_backtest"] = True
    clean["initial_capital"] = INITIAL_CAPITAL
    clean["entry_size_pct"] = 100
    clean["exit_size_pct"] = 100
    clean["pyramiding"] = 0
    clean["allow_partial_exits"] = False
    return clean


def _evaluate(row: dict[str, Any], df_daily, df_15m) -> dict[str, Any]:
    template_data = row["template_data"]
    strategy = ComboStrategy(
        indicators=template_data["indicators"],
        entry_logic=template_data["entry_logic"],
        exit_logic=template_data["exit_logic"],
        stop_loss=template_data["stop_loss"],
    )
    df_signals = strategy.generate_signals(df_daily.copy())
    trades, mode = extract_trades_with_mode(
        df_signals,
        template_data["stop_loss"],
        deep_backtest=True,
        symbol=SYMBOL,
        since_str=FULL_START,
        until_str=FULL_END,
        df_15m_cache=df_15m,
        direction="long",
        return_mode=True,
    )
    metrics = _metrics_from_trades(trades, INITIAL_CAPITAL, context_params=row["parameters"])
    return {"execution_mode": mode, "trades": trades, "metrics": metrics}


def _segment_metrics(trades: list[dict[str, Any]]) -> dict[str, Any]:
    buckets = {
        "train_2017_2020": [],
        "oos_2021_2023": [],
        "oos_2024_2026": [],
    }
    for trade in trades:
        raw_time = str(trade.get("exit_time") or trade.get("entry_time") or "")
        year = int(raw_time[:4]) if raw_time[:4].isdigit() else 0
        if year <= 2020:
            buckets["train_2017_2020"].append(trade)
        elif year <= 2023:
            buckets["oos_2021_2023"].append(trade)
        else:
            buckets["oos_2024_2026"].append(trade)
    return {name: _metrics_from_trades(rows, INITIAL_CAPITAL) for name, rows in buckets.items()}


def _apply_param(template_data: dict[str, Any], key: str, value: int | float) -> None:
    for indicator in template_data.get("indicators", []):
        params = indicator.get("params") or {}
        alias = indicator.get("alias")
        ind_type = indicator.get("type")
        if key in {"ema", "ema_fast"} and ind_type == "ema" and alias in {"fast", "short"}:
            params["length"] = value
        elif key in {"sma_l", "ema_slow"} and alias in {"trend", "slow", "long"}:
            params["length"] = value
        elif key == "sma_m" and alias == "medium":
            params["length"] = value
        elif key in {"roc", "roc_fast"} and alias in {"roc", "roc_fast"}:
            params["length"] = value
        elif key == "roc_slow" and alias == "roc_slow":
            params["length"] = value
        elif key == "bb_len" and ind_type == "bbands":
            params["length"] = value
        elif key == "bb_std" and ind_type == "bbands":
            params["std"] = value
    if key == "stop":
        template_data["stop_loss"] = value


def _stress_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, value in row["parameters"].items():
        if key in {"direction", "data_source", "exit_ref"} or not isinstance(value, (int, float)) or isinstance(value, bool):
            continue
        for sign in (-1, 1):
            variant = json.loads(json.dumps(row))
            if isinstance(value, int):
                next_value: int | float = max(1, value + sign)
            else:
                next_value = round(max(0.001, value * (1 + 0.10 * sign)), 6)
            variant["parameters"][key] = next_value
            _apply_param(variant["template_data"], key, next_value)
            rows.append(variant)
    return rows[:10]


def _stress(row: dict[str, Any], df_daily, df_15m) -> dict[str, Any]:
    results = []
    baseline = row["metrics"]
    for variant in _stress_rows(row):
        evaluation = _evaluate(variant, df_daily, df_15m)
        metrics = evaluation["metrics"]
        results.append(
            {
                "parameters": variant["parameters"],
                "execution_mode": evaluation["execution_mode"],
                "metrics": metrics,
                "passes": (
                    evaluation["execution_mode"] == "deep_15m"
                    and metrics.get("total_trades", 0) >= 8
                    and metrics.get("max_drawdown_pct", 999) <= max(8.5, baseline.get("max_drawdown_pct", 0) * 1.35)
                    and metrics.get("total_return_pct", 0) >= max(0, baseline.get("total_return_pct", 0) * 0.35)
                ),
            }
        )
    return {
        "variants_tested": len(results),
        "variants_passed": sum(1 for result in results if result["passes"]),
        "results": results,
    }


def _dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    am = a["metrics"]
    bm = b["metrics"]
    ar = float(am.get("total_return_pct", 0) or 0)
    br = float(bm.get("total_return_pct", 0) or 0)
    add = float(am.get("max_drawdown_pct", am.get("max_drawdown", 999) * 100) or 999)
    bdd = float(bm.get("max_drawdown_pct", bm.get("max_drawdown", 999) * 100) or 999)
    asharpe = float(am.get("sharpe_ratio", 0) or 0)
    bsharpe = float(bm.get("sharpe_ratio", 0) or 0)
    apf = float(am.get("profit_factor", 0) or 0)
    bpf = float(bm.get("profit_factor", 0) or 0)
    return ar >= br and add <= bdd and (asharpe >= bsharpe or apf >= bpf) and (
        ar > br or add < bdd or asharpe > bsharpe or apf > bpf
    )


def _sequential_ok(previous: list[dict[str, Any]], current: dict[str, Any]) -> bool:
    cm = current["metrics"]
    for prior in previous:
        pm = prior["metrics"]
        if cm["total_return_pct"] < pm["total_return_pct"]:
            return False
        if cm["max_drawdown_pct"] > pm["max_drawdown_pct"]:
            return False
        if not (
            cm.get("sharpe_ratio", 0) >= pm.get("sharpe_ratio", 0)
            or cm.get("profit_factor", 0) >= pm.get("profit_factor", 0)
        ):
            return False
        material = (
            cm["total_return_pct"] >= pm["total_return_pct"] * 1.02
            or cm["max_drawdown_pct"] <= pm["max_drawdown_pct"] * 0.95
            or (
                cm.get("sharpe_ratio", 0) >= pm.get("sharpe_ratio", 0) + 0.05
                and cm["total_return_pct"] >= pm["total_return_pct"]
                and cm["max_drawdown_pct"] <= pm["max_drawdown_pct"]
            )
            or (
                cm.get("profit_factor", 0) >= pm.get("profit_factor", 0) + 0.10
                and cm["total_return_pct"] >= pm["total_return_pct"]
                and cm["max_drawdown_pct"] <= pm["max_drawdown_pct"]
            )
        )
        if not material:
            return False
    return True


def _template_schema(parameters: dict[str, Any]) -> dict[str, Any]:
    ranges: dict[str, Any] = {}
    for key, value in parameters.items():
        if key in {"direction", "data_source", "exit_ref"} or isinstance(value, bool):
            continue
        if isinstance(value, int):
            ranges[key] = {"min": value, "max": value, "default": value, "step": 1}
        elif isinstance(value, float):
            ranges[key] = {"min": value, "max": value, "default": value, "step": 0.0001}
    return {"parameters": ranges, "correlated_groups": [list(ranges.keys())]}


def _ensure_template(engine, name: str, description: str, row: dict[str, Any]) -> str:
    with engine.begin() as conn:
        existing = conn.execute(text("SELECT id FROM combo_templates WHERE name = :name"), {"name": name}).mappings().first()
        payload = {
            "name": name,
            "description": description,
            "template_data": json.dumps(row["template_data"], ensure_ascii=False),
            "optimization_schema": json.dumps(_template_schema(row["parameters"]), ensure_ascii=False),
        }
        if existing:
            conn.execute(
                text(
                    """
                    UPDATE combo_templates
                    SET description = :description,
                        template_data = :template_data,
                        optimization_schema = :optimization_schema,
                        updated_at = now()
                    WHERE name = :name
                    """
                ),
                payload,
            )
            return "updated"
        conn.execute(
            text(
                """
                INSERT INTO combo_templates
                    (name, description, is_prebuilt, is_example, is_readonly, template_data, optimization_schema, created_at, updated_at)
                VALUES
                    (:name, :description, false, false, false, :template_data, :optimization_schema, now(), now())
                """
            ),
            payload,
        )
        return "created"


def _favorite_existing(engine, strategy_names: list[str]) -> list[dict[str, Any]]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id, name, strategy_name, created_at
                FROM favorite_strategies
                WHERE symbol = 'BTC/USDT'
                  AND timeframe = '1d'
                  AND strategy_name = ANY(:names)
                ORDER BY id
                """
            ),
            {"names": strategy_names},
        ).mappings().all()
    return [dict(row) for row in rows]


def _parse_dt(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _pine(meta: dict[str, Any], row: dict[str, Any]) -> str:
    p = row["parameters"]
    title = meta["name"].replace('"', "'")
    if row["family"] == "bb-roc-long":
        return f"""//@version=5
strategy("{title}", overlay=true, initial_capital=100, default_qty_type=strategy.percent_of_equity, default_qty_value=100, pyramiding=0)
[middle, upper, lower] = ta.bb(close, {p["bb_len"]}, {p["bb_std"]})
roc = ta.roc(close, {p["roc"]})
entry = close > upper and roc > {p["roc_min"]}
exitSignal = close < middle or roc < 0
if entry and strategy.position_size == 0
    strategy.entry("Long", strategy.long)
if strategy.position_size > 0
    strategy.exit("Stop", "Long", stop=strategy.position_avg_price * (1 - {p["stop"]}))
if exitSignal and strategy.position_size > 0
    strategy.close("Long")
plot(middle, color=color.gray)
plot(upper, color=color.teal)
plot(lower, color=color.teal)
"""
    if row["family"] == "dual-momentum-long":
        return f"""//@version=5
strategy("{title}", overlay=true, initial_capital=100, default_qty_type=strategy.percent_of_equity, default_qty_value=100, pyramiding=0)
fast = ta.ema(close, {p["ema_fast"]})
slow = ta.ema(close, {p["ema_slow"]})
rocFast = ta.roc(close, {p["roc_fast"]})
rocSlow = ta.roc(close, {p["roc_slow"]})
entry = fast > slow and rocFast > rocSlow and rocSlow > 0
exitSignal = fast < slow or rocFast < 0
if entry and strategy.position_size == 0
    strategy.entry("Long", strategy.long)
if strategy.position_size > 0
    strategy.exit("Stop", "Long", stop=strategy.position_avg_price * (1 - {p["stop"]}))
if exitSignal and strategy.position_size > 0
    strategy.close("Long")
plot(fast, color=color.teal)
plot(slow, color=color.orange)
"""
    if row["family"] == "ma-breakout-long":
        return f"""//@version=5
strategy("{title}", overlay=true, initial_capital=100, default_qty_type=strategy.percent_of_equity, default_qty_value=100, pyramiding=0)
fast = ta.ema(close, {p["ema"]})
trend = ta.sma(close, {p["sma_l"]})
roc = ta.roc(close, {p["roc"]})
entry = close > trend and ta.crossover(fast, trend) and roc > 0
exitSignal = close < fast or roc < 0
if entry and strategy.position_size == 0
    strategy.entry("Long", strategy.long)
if strategy.position_size > 0
    strategy.exit("Stop", "Long", stop=strategy.position_avg_price * (1 - {p["stop"]}))
if exitSignal and strategy.position_size > 0
    strategy.close("Long")
plot(fast, color=color.teal)
plot(trend, color=color.orange)
"""
    exit_line = "medium" if p.get("exit_ref") == "medium" else "longMa"
    return f"""//@version=5
strategy("{title}", overlay=true, initial_capital=100, default_qty_type=strategy.percent_of_equity, default_qty_value=100, pyramiding=0)
short = ta.ema(close, {p["ema"]})
medium = ta.sma(close, {p["sma_m"]})
longMa = ta.sma(close, {p["sma_l"]})
entry = short > longMa and (ta.crossover(short, longMa) or ta.crossover(short, medium))
exitSignal = ta.crossunder(short, {exit_line})
if entry and strategy.position_size == 0
    strategy.entry("Long", strategy.long)
if strategy.position_size > 0
    strategy.exit("Stop", "Long", stop=strategy.position_avg_price * (1 - {p["stop"]}))
if exitSignal and strategy.position_size > 0
    strategy.close("Long")
plot(short, color=color.teal)
plot(medium, color=color.blue)
plot(longMa, color=color.orange)
"""


def _save_payload(row: dict[str, Any], meta: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    strategy_name = meta["strategy_name"]
    _reject_copy(public_strategy_display_name(strategy_name), "strategy_display_name")
    _reject_copy(public_strategy_description(strategy_name), "strategy_description")
    full_metrics = dict(metrics)
    full_metrics["analysis_execution_mode"] = row["execution_mode"]
    full_metrics["trades"] = row["trades"]
    full_metrics["trades_history_cached"] = True
    full_metrics["trades_metrics_match"] = True
    full_metrics["card_277_full_period"] = {"start": FULL_START, "end": FULL_END}
    full_metrics["card_277_thesis"] = meta["thesis"]
    return {
        "name": meta["name"],
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "strategy_name": strategy_name,
        "parameters": _normalize_params(row["parameters"]),
        "metrics": full_metrics,
        "notes": f"Card #277 HARD MODE V5 LONG sequential Pareto winner. {meta['thesis']}",
        "tier": 2,
        "notify_telegram": True,
        "start_date": FULL_START,
        "end_date": FULL_END,
        "period_type": "all",
    }


def _post_favorite(token: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE}/api/favorites/",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=90,
    )
    if not response.ok:
        raise RuntimeError(f"Favorite save failed: status={response.status_code} body={response.text[:800]}")
    return response.json()


def _read_favorite(token: str, favorite_id: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    headers = {"Authorization": f"Bearer {token}"}
    all_response = requests.get(f"{API_BASE}/api/favorites/", headers=headers, timeout=60)
    all_response.raise_for_status()
    favorite = next((row for row in all_response.json() if int(row.get("id")) == int(favorite_id)), None)
    if not favorite:
        raise RuntimeError(f"favorite {favorite_id} not returned by list API")
    trades_response = requests.get(f"{API_BASE}/api/favorites/{favorite_id}/trades", headers=headers, timeout=90)
    trades_response.raise_for_status()
    meta_response = requests.get(
        f"{API_BASE}/api/combos/meta/{favorite['strategy_name']}",
        headers=headers,
        timeout=60,
    )
    meta_response.raise_for_status()
    return favorite, trades_response.json(), meta_response.json()


def _validate_api_copy(favorite: dict[str, Any], expected: dict[str, Any]) -> None:
    _reject_copy(favorite.get("name"), "api.name")
    _reject_copy(favorite.get("strategy_display_name"), "api.strategy_display_name")
    _reject_copy(favorite.get("strategy_description"), "api.strategy_description")
    if favorite.get("strategy_name") != expected["strategy_name"]:
        raise RuntimeError(f"strategy_name mismatch for favorite {favorite.get('id')}")
    params = favorite.get("parameters") or {}
    if str(params.get("direction")).lower() != "long":
        raise RuntimeError(f"direction mismatch for favorite {favorite.get('id')}: {params.get('direction')}")


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    PINE_DIR.mkdir(parents=True, exist_ok=True)
    chain_report = json.loads(CHAIN_PATH.read_text(encoding="utf-8"))
    t0 = json.loads(T0_PATH.read_text(encoding="utf-8"))
    benchmark_report = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    chain = chain_report["best_chain"]
    if len(chain) != 5:
        raise RuntimeError(f"expected 5 chain winners, got {len(chain)}")

    engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
    names = [meta["strategy_name"] for meta in WINNER_META]
    existing = _favorite_existing(engine, names)
    if existing:
        raise RuntimeError(f"Refusing duplicate strategy_names already saved: {existing}")

    token, admin_user_id = _admin_token(engine)
    loader = IncrementalLoader()
    df_daily = loader.fetch_data(SYMBOL, TIMEFRAME, FULL_START, FULL_END, read_only=True)
    df_15m = loader.fetch_intraday_data(SYMBOL, "15m", FULL_START, FULL_END, read_only=True)

    benchmark_rows = [
        {
            "id": fav.get("favorite_id"),
            "name": fav.get("name"),
            "strategy_name": fav.get("strategy_name"),
            "metrics": fav["metrics_summary"],
        }
        for fav in benchmark_report["results"]
        if fav.get("status") == "ok" and fav.get("execution_mode") == "deep_15m"
    ]
    saved_rows: list[dict[str, Any]] = []
    t0_time = _parse_dt(t0["snapshot"]["timestamp_utc"])
    report: dict[str, Any] = {
        "card": 277,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "api_base": API_BASE,
        "admin_user_id": admin_user_id,
        "source_chain": str(CHAIN_PATH.relative_to(ROOT)),
        "source_t0": str(T0_PATH.relative_to(ROOT)),
        "source_benchmark": str(BENCHMARK_PATH.relative_to(ROOT)),
        "executed_material_deep_candidates": chain_report["executed_material_deep_candidates"],
        "unique_template_families": chain_report["unique_template_families"],
        "eligible_basic": chain_report["eligible_basic"],
        "existing_before_run": existing,
        "winners": [],
    }

    for index, (meta, source_row) in enumerate(zip(WINNER_META, chain), start=1):
        row = json.loads(json.dumps(source_row))
        row["strategy_name"] = meta["strategy_name"]
        row["parameters"] = _normalize_params(row["parameters"])
        evaluation = _evaluate(row, df_daily, df_15m)
        row["execution_mode"] = evaluation["execution_mode"]
        row["trades"] = evaluation["trades"]
        row["metrics"] = evaluation["metrics"]
        if row["execution_mode"] != "deep_15m":
            raise RuntimeError(f"WINNER_{index} is not deep_15m: {row['execution_mode']}")
        if row["metrics"].get("total_trades", 0) < 8:
            raise RuntimeError(f"WINNER_{index} has too few trades")
        if any(_dominates(fav, row) for fav in benchmark_rows + saved_rows):
            raise RuntimeError(f"WINNER_{index} dominated by benchmark/previous winner")
        if not _sequential_ok(saved_rows, row):
            raise RuntimeError(f"WINNER_{index} fails sequential gate")

        display = _reject_copy(public_strategy_display_name(meta["strategy_name"]), "pre_save_display")
        description = _reject_copy(public_strategy_description(meta["strategy_name"]), "pre_save_description")
        template_status = _ensure_template(engine, meta["strategy_name"], description, row)
        pine_path = PINE_DIR / f"{index:02d}_{meta['strategy_name']}.pine"
        pine_path.write_text(_pine(meta, row), encoding="utf-8")

        segment_metrics = _segment_metrics(row["trades"])
        stress = _stress(row, df_daily, df_15m)
        if stress["variants_tested"] < 6 or stress["variants_passed"] < 3:
            raise RuntimeError(
                f"WINNER_{index} failed stress minimum: {stress['variants_passed']}/{stress['variants_tested']}"
            )

        payload = _save_payload(row, meta, row["metrics"])
        created = _post_favorite(token, payload)
        favorite, trades_response, template_api = _read_favorite(token, int(created["id"]))
        _validate_api_copy(favorite, meta)
        if trades_response.get("execution_mode") != "deep_15m":
            raise RuntimeError(f"WINNER_{index} trades endpoint not deep_15m")
        if _parse_dt(favorite["created_at"]) <= t0_time:
            raise RuntimeError(f"WINNER_{index} created_at is not after T0")

        winner_report = {
            "slot": f"WINNER_{index}",
            "favorite_id": favorite["id"],
            "created_at": favorite["created_at"],
            "direction": "long",
            "name": favorite["name"],
            "strategy_name": favorite["strategy_name"],
            "strategy_display_name": favorite.get("strategy_display_name"),
            "strategy_description": favorite.get("strategy_description"),
            "thesis": meta["thesis"],
            "parameters": payload["parameters"],
            "metrics_full_period": row["metrics"],
            "metrics_train_oos": segment_metrics,
            "stress": stress,
            "payload_deep_backtest": {
                "symbol": SYMBOL,
                "timeframe": TIMEFRAME,
                "direction": "long",
                "deep_backtest": True,
                "initial_capital": INITIAL_CAPITAL,
                "start_date": FULL_START,
                "end_date": FULL_END,
            },
            "payload_save": payload,
            "public_mapping_source": "backend/app/services/strategy_descriptions.py plus combo_templates.description",
            "template_status": template_status,
            "template_api": template_api,
            "trades_endpoint": {
                "favorite_id": trades_response.get("favorite_id"),
                "execution_mode": trades_response.get("execution_mode"),
                "regenerated": trades_response.get("regenerated"),
                "metrics_match": trades_response.get("metrics_match"),
                "trade_count": len(trades_response.get("trades") or []),
            },
            "pine_path": str(pine_path.relative_to(ROOT)),
            "long_execution_proof": {
                "pine_entry": "strategy.entry(..., strategy.long)",
                "entry_size_pct": 100,
                "exit_size_pct": 100,
                "pyramiding": 0,
                "allow_partial_exits": False,
            },
        }
        report["winners"].append(winner_report)
        saved_rows.append(
            {
                "id": favorite["id"],
                "name": favorite["name"],
                "strategy_name": favorite["strategy_name"],
                "metrics": row["metrics"],
            }
        )
        benchmark_rows.append(saved_rows[-1])

    report["final_status"] = "saved_5_of_5"
    report["favorite_ids"] = [winner["favorite_id"] for winner in report["winners"]]
    output = ARTIFACT_DIR / f"winner-save-validation-{report['created_at'].replace(':', '').replace('+00:00', 'Z')}.json"
    latest = ARTIFACT_DIR / "winner-save-validation-latest.json"
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
    latest.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output.relative_to(ROOT)),
                "latest": str(latest.relative_to(ROOT)),
                "status": report["final_status"],
                "favorite_ids": report["favorite_ids"],
                "pine_dir": str(PINE_DIR.relative_to(ROOT)),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
