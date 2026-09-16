#!/usr/bin/env python3
"""Build the card #945 frozen oracle, parquet fixtures, and sha256 goldens.

Test-only. Does not modify product optimizer code.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import struct
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BACKEND))

CATALOG = [
    "Bollinger_Breakout",
    "MACD_Cross",
    "RSI_EMA_Scalping",
    "bollinger_rsi_adx",
    "ema_macd_volume",
    "ema_rsi",
    "ema_rsi_fibonacci",
    "multi_ma_crossover",
    "multi_ma_crossoverV2",
    "short_ema200_pullback",
    "volume_atr_breakout",
    "Example: Breakout with Volume",
    "Example: Scalping EMA 5/13",
    "Example: Swing RSI Divergence",
]
SYMBOLS = ("1INCH/USDT", "AAVE/USDT")
FIXTURE_START = "2023-01-01"
FIXTURE_END = "2025-01-01"
SRC_STORAGE = Path("/srv/apps/dev/criptofarol/source/data/storage/binance")
OUT_DIR = BACKEND / "tests" / "fixtures" / "card_945"
OHLCV_DIR = OUT_DIR / "ohlcv"
ORACLE_PATH = BACKEND / "tests" / "oracles" / "card_945_legacy.py"
N_PARAMS = 50
BURNIN = 250
OHLCV_COLS = ["open", "high", "low", "close", "volume"]


def _slice_src(symbol: str, timeframe: str) -> pd.DataFrame:
    safe = symbol.replace("/", "_")
    src = SRC_STORAGE / f"{safe}_{timeframe}.parquet"
    df = pd.read_parquet(src)
    ts = pd.to_datetime(df["timestamp_utc"], utc=True)
    start = pd.Timestamp(FIXTURE_START, tz="UTC")
    end = pd.Timestamp(FIXTURE_END, tz="UTC")
    if timeframe == "1d":
        end = end + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
    else:
        end = end + pd.Timedelta(days=1) - pd.Timedelta(minutes=15)
    mask = (ts >= start) & (ts <= end)
    out = df.loc[mask].copy()
    out["timestamp_utc"] = ts.loc[mask]
    if "timestamp" not in out.columns:
        out["timestamp"] = (out["timestamp_utc"].astype("int64") // 1_000_000).astype("int64")
    keep = ["timestamp", "timestamp_utc", "open", "high", "low", "close", "volume"]
    return out[keep].reset_index(drop=True)


def write_parquet() -> None:
    OHLCV_DIR.mkdir(parents=True, exist_ok=True)
    for symbol in SYMBOLS:
        for tf in ("1d", "15m"):
            df = _slice_src(symbol, tf)
            if len(df) < 80:
                raise RuntimeError(f"fixture too short: {symbol} {tf} rows={len(df)}")
            path = OHLCV_DIR / f"{symbol.replace('/', '_')}_{tf}.parquet"
            df.to_parquet(path, index=False)
            print(f"wrote {path} rows={len(df)}")


def write_oracle() -> None:
    cs = (BACKEND / "app" / "strategies" / "combos" / "combo_strategy.py").read_text()
    db = (BACKEND / "app" / "services" / "deep_backtest.py").read_text()
    opt = (BACKEND / "app" / "services" / "combo_optimizer.py").read_text()

    cs_start = cs.index("class ComboStrategy:")
    cs_body = cs[cs_start:]
    cs_body = cs_body.replace("class ComboStrategy:", "class LegacyComboStrategy:", 1)
    cs_body = cs_body.replace(
        "from .helpers import HELPER_FUNCTIONS",
        "from app.strategies.combos.helpers import HELPER_FUNCTIONS",
    )

    sim_start = db.index("TRADING_FEE = 0.00075")
    sim_end = db.index("    return trades", sim_start)
    sim_end = db.index("\n", sim_end) + 1
    sim_body = db[sim_start:sim_end]

    ext_start = opt.index("def extract_trades_from_signals(")
    ext_end = opt.index("\n\ndef extract_trades_with_mode(")
    ext_body = opt[ext_start:ext_end]

    mode_start = opt.index("def extract_trades_with_mode(")
    mode_end = opt.index(
        "\n\n# -----------------------------------------------------------------------------"
    )
    # first banner after extract_trades_with_mode
    mode_end = opt.index(
        "\n# -----------------------------------------------------------------------------\n# WORKER FUNCTION",
        mode_start,
    )
    mode_body = opt[mode_start:mode_end]
    mode_body = mode_body.replace(
        "from src.data.incremental_loader import IncrementalLoader\n",
        "",
    )

    run_start = opt.index("def _run_backtest_logic(")
    run_end = opt.index("\n\ndef _worker_run_backtest(")
    run_body = opt[run_start:run_end]
    run_body = run_body.replace(
        "from app.strategies.combos import ComboStrategy",
        "ComboStrategy = LegacyComboStrategy",
    )

    met_start = opt.index("def _metrics_from_trades(")
    met_end = opt.index("\n\ndef _calculate_heavy_metrics(")
    met_body = opt[met_start:met_end]

    header = '''"""Frozen combo-optimizer path at baseline-945=e43b93e5e0569a9c4a82d4cce2ef24dfa0ef5e4c.

Literal copies of:
- ComboStrategy.calculate_indicators
- ComboStrategy._evaluate_logic_vectorized
- ComboStrategy.generate_signals (position loop)
- simulate_execution_with_15m
- extract_trades_from_signals
- _metrics_from_trades

Test-only. Not product. Speed commits MUST NOT edit this module.
"""

from __future__ import annotations

import ast
import copy
import logging
import re
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import talib

from app.strategies.combos.helpers import HELPER_FUNCTIONS
from src.data.incremental_loader import IncrementalLoader

_deep_coverage_warned: set = set()

'''
    text = (
        header
        + cs_body.rstrip()
        + "\n\n\n"
        + sim_body.rstrip()
        + "\n\n\n"
        + ext_body.rstrip()
        + "\n\n\n"
        + mode_body.rstrip()
        + "\n\n\n"
        + run_body.rstrip()
        + "\n\n\n"
        + met_body.rstrip()
        + "\n"
    )
    ORACLE_PATH.write_text(text)
    print(f"wrote {ORACLE_PATH} bytes={len(text)}")


def load_templates() -> dict:
    data = json.loads((BACKEND / "config" / "combo_templates_export.json").read_text())
    out = {}
    for row in data:
        if row["name"] in CATALOG:
            out[row["name"]] = row
    if len(out) != 14:
        raise RuntimeError(f"expected 14 catalog templates, got {sorted(out)}")
    return out


def metadata_from_export(row: dict) -> dict:
    td = dict(row.get("template_data") or {})
    stop_loss = td.get("stop_loss", 0.015)
    if not isinstance(stop_loss, dict):
        td["stop_loss"] = {"default": stop_loss}
    return {
        "name": row["name"],
        "optimization_schema": row.get("optimization_schema") or {},
        **td,
    }


def _ma_ok(params: dict) -> bool:
    p_short = p_inter = p_long = None
    for k, v in params.items():
        k_lower = str(k).lower()
        if (
            k_lower.endswith("media_curta")
            or k_lower.endswith("ema_short")
            or k_lower.endswith("sma_short")
        ):
            p_short = v
        elif k_lower.endswith("media_inter") or k_lower.endswith("sma_medium"):
            p_inter = v
        elif k_lower.endswith("media_longa") or k_lower.endswith("sma_long"):
            p_long = v
    if p_short is not None and p_inter is not None and p_long is not None:
        try:
            return float(p_short) < float(p_inter) < float(p_long)
        except (TypeError, ValueError):
            return True
    return True


def sample_r1_params(opt, template_name: str, metadata: dict) -> list[dict]:
    from app.services import combo_optimizer as co

    original = opt.combo_service.get_template_metadata
    opt.combo_service.get_template_metadata = lambda _n: metadata
    try:
        stages = opt.generate_stages(
            template_name=template_name,
            symbol="1INCH/USDT",
            fixed_timeframe="1d",
        )
    finally:
        opt.combo_service.get_template_metadata = original

    combos: list[dict] = []
    for stage in stages:
        names = stage["parameter"]
        value_lists = stage["values"]
        if not stage.get("grid_mode"):
            names = [names] if isinstance(names, str) else names
            value_lists = [value_lists]
        for combo in itertools.product(*value_lists):
            params = dict(zip(names, combo))
            if _ma_ok(params):
                combos.append(params)

    if not combos:
        combos = [{}]

    pad_stops = [0.0, 0.005, 0.01, 0.015, 0.02, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2, 0.3, 0.5]
    if len(combos) < N_PARAMS:
        padded = []
        for combo in combos:
            for stop in pad_stops:
                extra = dict(combo)
                extra["stop_loss"] = stop
                padded.append(extra)
        combos = padded or combos

    def pick(items: list[dict], n: int) -> list[dict]:
        if len(items) <= n:
            return list(items)
        idxs = [round(i * (len(items) - 1) / (n - 1)) for i in range(n)]
        seen = set()
        out = []
        for i in idxs:
            if i not in seen:
                seen.add(i)
                out.append(items[i])
        return out

    sampled = pick(combos, N_PARAMS)
    base = dict(sampled[0])
    extremes = []
    for stop in (0.0, 0.5):
        extra = dict(base)
        extra["stop_loss"] = stop
        extremes.append(extra)
    merged = []
    seen_keys = set()
    for item in extremes + sampled:
        key = tuple(sorted((str(k), repr(v)) for k, v in item.items()))
        if key in seen_keys:
            continue
        seen_keys.add(key)
        merged.append(item)
    if len(merged) > N_PARAMS + 2:
        head = merged[:2]
        rest = pick(merged[2:], N_PARAMS)
        merged = head + rest
    pad_i = 0
    while len(merged) < N_PARAMS:
        pad_i += 1
        extra = dict(merged[0] if merged else {})
        extra["stop_loss"] = round(0.001 * pad_i, 4)
        key = tuple(sorted((str(k), repr(v)) for k, v in extra.items()))
        if key in seen_keys:
            continue
        seen_keys.add(key)
        merged.append(extra)
        if pad_i > 400:
            break
    if len(merged) < N_PARAMS:
        raise RuntimeError(f"{template_name}: only {len(merged)} R1 params")
    return merged


def load_ohlcv(symbol: str, timeframe: str) -> pd.DataFrame:
    path = OHLCV_DIR / f"{symbol.replace('/', '_')}_{timeframe}.parquet"
    df = pd.read_parquet(path)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    df = df.set_index("timestamp_utc", drop=False).sort_index()
    for col in OHLCV_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
    return df


def split_windows(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    from app.services.combo_optimizer import split_train_holdout

    train, holdout = split_train_holdout(df, 0.7)
    burn = max(50, BURNIN)
    holdout_burnin = pd.concat([train.iloc[-burn:], holdout])
    return {
        "train_70": train,
        "holdout_burnin": holdout_burnin,
        "final": df,
    }


_CANONICAL_QNAN = struct.unpack("<d", struct.pack("<Q", 0x7FF8000000000000))[0]


def sha256_col(series: pd.Series) -> str:
    arr = np.ascontiguousarray(series.to_numpy(dtype=np.float64, copy=True))
    nonfinite = ~np.isfinite(arr)
    if np.any(nonfinite):
        arr[nonfinite] = _CANONICAL_QNAN
    return hashlib.sha256(arr.tobytes()).hexdigest()


def sha256_mask(series: pd.Series) -> str:
    arr = np.ascontiguousarray(series.fillna(False).astype(bool).to_numpy())
    return hashlib.sha256(arr.tobytes()).hexdigest()


def sha256_trades(trades: list) -> str:
    h = hashlib.sha256()
    for trade in trades:
        h.update(str(trade.get("entry_time") or "").encode())
        h.update(b"\0")
        h.update(str(trade.get("exit_time") or "").encode())
        h.update(b"\0")
        h.update(str(trade.get("exit_reason") or "").encode())
        h.update(b"\0")
        for key in ("entry_price", "exit_price", "profit"):
            val = trade.get(key)
            if val is None:
                h.update(b"none")
            else:
                h.update(struct.pack("<d", float(val)))
            h.update(b"\0")
    h.update(struct.pack("<I", len(trades)))
    return h.hexdigest()


def sha256_metrics(metrics: dict) -> str:
    skip = {"avg_atr", "avg_adx", "error"}
    h = hashlib.sha256()
    for key in sorted(metrics):
        if key in skip:
            continue
        val = metrics[key]
        h.update(key.encode())
        h.update(b"=")
        if val is None:
            h.update(b"none")
        elif isinstance(val, (bool, np.bool_)):
            h.update(b"1" if val else b"0")
        elif isinstance(val, (int, np.integer)) and not isinstance(val, bool):
            h.update(struct.pack("<q", int(val)))
        elif isinstance(val, (float, np.floating)):
            h.update(struct.pack("<d", float(val)))
        else:
            h.update(repr(val).encode())
        h.update(b"\n")
    return h.hexdigest()


def apply_param_overrides(template_data: dict, params: dict) -> tuple[list, Any]:
    """Same four override rules as combo_optimizer._run_backtest_logic."""
    import copy as _copy

    indicators = _copy.deepcopy(template_data["indicators"])
    stop_loss = template_data.get("stop_loss", 0.015)
    if isinstance(stop_loss, dict):
        stop_loss = stop_loss.get("default", 0.015)
    if not params:
        return indicators, stop_loss
    for param_key, param_value in params.items():
        if param_key == "stop_loss":
            stop_loss = param_value
            continue
        if param_key in ("timeframe", "direction"):
            continue
        for indicator in indicators:
            alias = indicator.get("alias", "")
            type_ = indicator.get("type", "")
            if alias and param_key.startswith(f"{alias}_"):
                indicator.setdefault("params", {})[param_key[len(alias) + 1 :]] = param_value
                break
            if alias and type_ and param_key == f"{type_}_{alias}":
                indicator.setdefault("params", {})
                if "length" in indicator["params"]:
                    indicator["params"]["length"] = param_value
                elif "period" in indicator["params"]:
                    indicator["params"]["period"] = param_value
                else:
                    indicator["params"]["length"] = param_value
                break
            if alias and param_key == alias:
                indicator.setdefault("params", {})
                if "length" in indicator["params"]:
                    indicator["params"]["length"] = param_value
                elif "period" in indicator["params"]:
                    indicator["params"]["period"] = param_value
                else:
                    indicator["params"]["length"] = param_value
                break
            if (not alias) and type_ and param_key.startswith(f"{type_}_"):
                indicator.setdefault("params", {})[param_key[len(type_) + 1 :]] = param_value
                break
    return indicators, stop_loss


def indicator_columns(df: pd.DataFrame) -> list[str]:
    skip = {
        "open",
        "high",
        "low",
        "close",
        "volume",
        "timestamp",
        "timestamp_utc",
        "time",
        "date",
        "signal",
        "signal_reason",
        "regime",
    }
    cols = []
    for col in df.columns:
        if col in skip:
            continue
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            cols.append(col)
    return cols


def write_goldens() -> None:
    from app.services.combo_optimizer import (
        ComboOptimizer,
        _metrics_from_trades,
        extract_trades_with_mode,
    )
    from app.strategies.combos.combo_strategy import ComboStrategy

    templates = load_templates()
    opt = ComboOptimizer(checkpoint_dir=str(OUT_DIR / "_checkpoints"))
    df_1d = {sym: load_ohlcv(sym, "1d") for sym in SYMBOLS}
    df_15m = {sym: load_ohlcv(sym, "15m") for sym in SYMBOLS}
    windows_1inch = split_windows(df_1d["1INCH/USDT"])

    r1: dict[str, list] = {}
    indicator_hashes: dict = {}
    mask_hashes: dict = {}
    trial_hashes: dict = {}

    def hash_trial(name, symbol, direction, mode_name, i, template_data, params, deep):
        trial_params = dict(params)
        trial_params["direction"] = direction
        inds, stop_loss = apply_param_overrides(template_data, trial_params)
        strat = ComboStrategy(
            indicators=inds,
            entry_logic=template_data["entry_logic"],
            exit_logic=template_data["exit_logic"],
            stop_loss=stop_loss,
            derived_features=template_data.get("derived_features") or [],
            direction=direction,
        )
        df_sig = strat.generate_signals(df_1d[symbol].copy())
        trades = extract_trades_with_mode(
            df_sig,
            stop_loss,
            deep_backtest=deep,
            symbol=symbol,
            since_str=str(df_1d[symbol].index.min().date()),
            until_str=str(df_1d[symbol].index.max().date()),
            df_15m_cache=df_15m[symbol] if deep else None,
            direction=direction,
        )
        metrics = _metrics_from_trades(trades, 100)
        tkey = f"{name}|{symbol}|{direction}|{mode_name}|{i}"
        trial_hashes[tkey] = {
            "trades": sha256_trades(trades),
            "metrics": sha256_metrics(metrics),
            "n_trades": int(metrics.get("total_trades") or 0),
        }

    primary = "1INCH/USDT"
    for name in CATALOG:
        meta = metadata_from_export(templates[name])
        params_list = sample_r1_params(opt, name, meta)
        r1[name] = params_list
        print(f"sampled {name}: {len(params_list)} params", flush=True)

        template_data = {
            "indicators": meta["indicators"],
            "entry_logic": meta["entry_logic"],
            "exit_logic": meta["exit_logic"],
            "stop_loss": meta.get("stop_loss", 0.015),
            "derived_features": meta.get("derived_features") or [],
        }

        for window_name, window_df in windows_1inch.items():
            ohlcv = window_df[OHLCV_COLS]
            for i, params in enumerate(params_list):
                inds, stop_loss = apply_param_overrides(template_data, params)
                strategy = ComboStrategy(
                    indicators=inds,
                    entry_logic=template_data["entry_logic"],
                    exit_logic=template_data["exit_logic"],
                    stop_loss=stop_loss,
                    derived_features=template_data["derived_features"],
                    direction="long",
                )
                calc = strategy.calculate_indicators(ohlcv.copy())
                cols = indicator_columns(calc)
                col_hashes = {col: sha256_col(calc[col]) for col in cols}

                def _mask(logic: str) -> pd.Series:
                    try:
                        return strategy._evaluate_logic_vectorized(calc, logic)
                    except Exception:
                        return pd.Series(False, index=calc.index)

                entry_mask = _mask(template_data["entry_logic"])
                exit_mask = _mask(template_data["exit_logic"])
                key = f"{name}|{window_name}|{i}"
                indicator_hashes[key] = {"columns": cols, "sha256": col_hashes}
                mask_hashes[key] = {
                    "entry": sha256_mask(entry_mask),
                    "exit": sha256_mask(exit_mask),
                }

        for direction in ("long", "short"):
            for i, params in enumerate(params_list):
                for mode_name, deep in (("deep_15m", True), ("fast_1d", False)):
                    hash_trial(name, primary, direction, mode_name, i, template_data, params, deep)
        print(f"hashed {name}", flush=True)

    secondary = "AAVE/USDT"
    for name in CATALOG:
        meta = metadata_from_export(templates[name])
        template_data = {
            "indicators": meta["indicators"],
            "entry_logic": meta["entry_logic"],
            "exit_logic": meta["exit_logic"],
            "stop_loss": meta.get("stop_loss", 0.015),
            "derived_features": meta.get("derived_features") or [],
        }
        for direction in ("long", "short"):
            for i, params in enumerate(r1[name]):
                for mode_name, deep in (("deep_15m", True), ("fast_1d", False)):
                    hash_trial(
                        name,
                        secondary,
                        direction,
                        mode_name,
                        i,
                        template_data,
                        params,
                        deep,
                    )
        print(f"hashed secondary {name}", flush=True)

    payload = {
        "indicator": indicator_hashes,
        "mask": mask_hashes,
        "trial": trial_hashes,
    }
    (OUT_DIR / "r1_params.json").write_text(json.dumps(r1, indent=2, sort_keys=True))
    (OUT_DIR / "sha256.json").write_text(json.dumps(payload, indent=2, sort_keys=True))
    print("wrote r1_params.json and sha256.json")


def write_versions() -> None:
    import talib

    versions = {
        "TA-Lib": getattr(talib, "__version__", None),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "baseline-945": "e43b93e5e0569a9c4a82d4cce2ef24dfa0ef5e4c",
    }
    (OUT_DIR / "versions.json").write_text(json.dumps(versions, indent=2, sort_keys=True) + "\n")
    print("versions", versions)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_oracle()
    write_parquet()
    write_versions()
    write_goldens()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
