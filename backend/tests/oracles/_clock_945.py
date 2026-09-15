#!/usr/bin/env python3
"""Worktree clock of the representative combination. Not a systemd proof."""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

import pandas as pd

from app.services.combo_optimizer import ComboOptimizer
from app.strategies.combos import ComboStrategy
from tests.oracles._build_card_945 import apply_param_overrides, load_templates, metadata_from_export

logging.basicConfig(level=logging.WARNING)

STORE = Path(os.environ.get("CARD945_CANDLE_DIR", "")).expanduser()


def _load(tf: str) -> pd.DataFrame:
    df = pd.read_parquet(STORE / f"1INCH_USDT_{tf}.parquet")
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    df = df.set_index("timestamp_utc", drop=False).sort_index()
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
    return df


def main() -> int:
    if not STORE.is_dir():
        raise SystemExit("set CARD945_CANDLE_DIR to a directory of 1INCH_USDT_*.parquet")
    df_1d = _load("1d")
    df_15m = _load("15m")
    templates = load_templates()
    meta = metadata_from_export(templates["multi_ma_crossover"])

    class FakeService:
        def get_template_metadata(self, _name):
            return meta

        def create_strategy(self, template_name, parameters=None):
            inds, stop = apply_param_overrides(meta, parameters or {})
            return ComboStrategy(
                indicators=inds,
                entry_logic=meta["entry_logic"],
                exit_logic=meta["exit_logic"],
                stop_loss=stop,
                direction=(parameters or {}).get("direction", "long"),
            )

    class FakeProvider:
        def fetch_ohlcv(self, **_kwargs):
            return df_1d.copy()

    class FakeLoader:
        def fetch_intraday_data(self, **_kwargs):
            return df_15m

        def check_intraday_availability(self, *_a, **_k):
            return {"available": True, "coverage": {"end": str(df_15m.index.max())}}

        def _get_parquet_path(self, symbol, timeframe):
            return str(STORE / f"{symbol.replace('/', '_')}_{timeframe}.parquet")

    from app.services import combo_optimizer as co

    opt = ComboOptimizer(checkpoint_dir="/tmp/card-945-clock")
    opt.combo_service = FakeService()
    opt.loader = FakeLoader()
    co.get_market_data_provider = lambda *_a, **_k: FakeProvider()
    co.resolve_data_source_for_symbol = lambda *_a, **_k: "ccxt"
    co.validate_data_source_timeframe = lambda *_a, **_k: "ccxt"

    round_times: list[tuple] = []
    orig_exec = ComboOptimizer._execute_opt_stages
    orig_pool = ComboOptimizer._execute_r2r4_pooled

    def timed_exec(self, *a, **k):
        t0 = time.perf_counter()
        result = orig_exec(self, *a, **k)
        round_times.append(("stage", time.perf_counter() - t0, a[2] if len(a) > 2 else None))
        return result

    def timed_pool(self, *a, **k):
        t0 = time.perf_counter()
        result = orig_pool(self, *a, **k)
        round_times.append(("pooled", time.perf_counter() - t0, a[2] if len(a) > 2 else None))
        return result

    ComboOptimizer._execute_opt_stages = timed_exec
    ComboOptimizer._execute_r2r4_pooled = timed_pool

    t0 = time.perf_counter()
    result = opt.run_optimization(
        template_name="multi_ma_crossover",
        symbol="1INCH/USDT",
        timeframe="1d",
        data_source="ccxt",
        start_date="2017-01-01",
        end_date="2026-09-15",
        direction="long",
        deep_backtest=True,
        split_train_ratio=0.7,
    )
    elapsed = time.perf_counter() - t0
    r1r4 = sum(item[1] for item in round_times)
    payload = {
        "elapsed_s": round(elapsed, 3),
        "r1r4_s": round(r1r4, 3),
        "round_times": [(k, round(t, 3), n) for k, t, n in round_times],
        "best_parameters": result.get("best_parameters"),
        "oos_verdict": (result.get("oos_verdict") or {}).get("status"),
        "workers": max(1, (os.cpu_count() or 2) - 1),
        "n_1d": int(len(df_1d)),
        "n_15m": int(len(df_15m)),
        "note": "worktree ComboOptimizer.run_optimization; candles already on disk; not systemd unit",
    }
    print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
