"""Exact goldens for card #945. Equality only — never wall-clock, never allclose."""

from __future__ import annotations

import hashlib
import json
import os
import platform
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.services.combo_optimizer import (
    _metrics_from_trades,
    extract_trades_from_signals,
    extract_trades_with_mode,
    split_train_holdout,
)
from app.strategies.combos.combo_strategy import ComboStrategy
from oracles._build_card_945 import (
    CATALOG,
    N_PARAMS,
    OHLCV_COLS,
    OUT_DIR,
    apply_param_overrides,
    indicator_columns,
    load_ohlcv,
    load_templates,
    metadata_from_export,
    sha256_col,
    sha256_mask,
    sha256_metrics,
    sha256_trades,
    split_windows,
)
from oracles.card_945_legacy import (
    LegacyComboStrategy,
    _metrics_from_trades as oracle_metrics_from_trades,
    extract_trades_from_signals as oracle_extract_trades,
    extract_trades_with_mode as oracle_extract_with_mode,
    simulate_execution_with_15m as oracle_simulate_15m,
)

pytestmark = pytest.mark.timeout(300)


def _load_json(name: str):
    return json.loads((OUT_DIR / name).read_text())


@pytest.fixture(scope="module")
def r1_params():
    return _load_json("r1_params.json")


@pytest.fixture(scope="module")
def sha_payload():
    return _load_json("sha256.json")


_R1 = None
_SHA = None
# Indicator sha256 in sha256.json was frozen on this architecture.
FREEZE_MACHINE = "aarch64"
_VERSIONS = _load_json("versions.json")
_TEMPLATES = load_templates()


def _r1():
    global _R1
    if _R1 is None:
        _R1 = _load_json("r1_params.json")
    return _R1


def _sha():
    global _SHA
    if _SHA is None:
        _SHA = _load_json("sha256.json")
    return _SHA


def test_scientific_lib_versions_recorded():
    import talib

    assert _VERSIONS["TA-Lib"] == getattr(talib, "__version__", None)
    assert _VERSIONS["numpy"] == np.__version__
    assert _VERSIONS["pandas"] == pd.__version__
    assert _VERSIONS["baseline-945"] == "e43b93e5e0569a9c4a82d4cce2ef24dfa0ef5e4c"


def test_r1_params_cover_catalog_and_extreme_stops():
    payload = _r1()
    assert set(payload) == set(CATALOG)
    for name, rows in payload.items():
        assert len(rows) >= N_PARAMS, name
        stops = {row.get("stop_loss") for row in rows if "stop_loss" in row}
        assert 0.0 in stops or any(float(s) == 0.0 for s in stops if s is not None), name


def window_identity(df: pd.DataFrame) -> tuple:
    frame = df[list(OHLCV_COLS)]
    arr = np.ascontiguousarray(frame.to_numpy(dtype=np.float64, copy=True))
    return (
        int(pd.Timestamp(df.index[0]).value),
        int(pd.Timestamp(df.index[-1]).value),
        int(len(df)),
        hashlib.sha256(arr.tobytes()).hexdigest(),
    )


def _strategy(cls, template_data: dict, params: dict, direction: str = "long"):
    inds, stop_loss = apply_param_overrides(template_data, params)
    return cls(
        indicators=inds,
        entry_logic=template_data["entry_logic"],
        exit_logic=template_data["exit_logic"],
        stop_loss=stop_loss,
        derived_features=template_data.get("derived_features") or [],
        direction=direction,
    )


def _template_data(name: str) -> dict:
    meta = metadata_from_export(_TEMPLATES[name])
    return {
        "indicators": meta["indicators"],
        "entry_logic": meta["entry_logic"],
        "exit_logic": meta["exit_logic"],
        "stop_loss": meta.get("stop_loss", 0.015),
        "derived_features": meta.get("derived_features") or [],
    }


def _safe_mask(strategy, df, logic: str) -> pd.Series:
    try:
        return strategy._evaluate_logic_vectorized(df, logic)
    except Exception:
        return pd.Series(False, index=df.index)


@pytest.fixture(scope="module")
def inch_1d():
    return load_ohlcv("1INCH/USDT", "1d")


@pytest.fixture(scope="module")
def inch_15m():
    return load_ohlcv("1INCH/USDT", "15m")


@pytest.fixture(scope="module")
def aave_1d():
    return load_ohlcv("AAVE/USDT", "1d")


@pytest.fixture(scope="module")
def aave_15m():
    return load_ohlcv("AAVE/USDT", "15m")


@pytest.fixture(scope="module")
def inch_windows(inch_1d):
    return split_windows(inch_1d)


def test_indicator_columns_match_oracle_and_sha256(inch_windows):
    for name in CATALOG:
        td = _template_data(name)
        params_list = _r1()[name]
        for window_name, window_df in inch_windows.items():
            ohlcv = window_df[OHLCV_COLS]
            for i, params in enumerate(params_list):
                product = _strategy(ComboStrategy, td, params)
                oracle = _strategy(LegacyComboStrategy, td, params)
                prod_df = product.calculate_indicators(ohlcv.copy())
                ora_df = oracle.calculate_indicators(ohlcv.copy())
                prod_cols = indicator_columns(prod_df)
                ora_cols = indicator_columns(ora_df)
                assert prod_cols == ora_cols
                key = f"{name}|{window_name}|{i}"
                expected = _sha()["indicator"][key]
                assert prod_cols == expected["columns"]
                for col in prod_cols:
                    np.testing.assert_array_equal(prod_df[col].to_numpy(), ora_df[col].to_numpy())
                    assert prod_df[col].dtype == np.dtype("float64")
                    assert ora_df[col].dtype == np.dtype("float64")
                    digest = sha256_col(prod_df[col])
                    assert digest == sha256_col(ora_df[col])
                    if platform.machine() == FREEZE_MACHINE:
                        assert digest == expected["sha256"][col]


def test_entry_exit_masks_match_oracle_and_sha256(inch_windows):
    for name in CATALOG:
        td = _template_data(name)
        params_list = _r1()[name]
        for window_name, window_df in inch_windows.items():
            ohlcv = window_df[OHLCV_COLS]
            for i, params in enumerate(params_list):
                product = _strategy(ComboStrategy, td, params)
                oracle = _strategy(LegacyComboStrategy, td, params)
                prod_df = product.calculate_indicators(ohlcv.copy())
                ora_df = oracle.calculate_indicators(ohlcv.copy())
                p_entry = _safe_mask(product, prod_df, td["entry_logic"])
                o_entry = _safe_mask(oracle, ora_df, td["entry_logic"])
                p_exit = _safe_mask(product, prod_df, td["exit_logic"])
                o_exit = _safe_mask(oracle, ora_df, td["exit_logic"])
                np.testing.assert_array_equal(p_entry.to_numpy(), o_entry.to_numpy())
                np.testing.assert_array_equal(p_exit.to_numpy(), o_exit.to_numpy())
                key = f"{name}|{window_name}|{i}"
                expected = _sha()["mask"][key]
                assert sha256_mask(p_entry) == expected["entry"]
                assert sha256_mask(p_exit) == expected["exit"]


def test_window_keys_differ_across_train_holdout_final(inch_windows):
    keys = {name: window_identity(df) for name, df in inch_windows.items()}
    assert keys["train_70"] != keys["holdout_burnin"]
    assert keys["train_70"] != keys["final"]
    assert keys["holdout_burnin"] != keys["final"]


def test_cache_cold_hot_and_aba_bytes(inch_1d):
    td = _template_data("multi_ma_crossover")
    params_a = dict(_r1()["multi_ma_crossover"][2])
    params_b = dict(_r1()["multi_ma_crossover"][7])
    ohlcv = inch_1d[OHLCV_COLS]

    def run(params):
        strat = _strategy(ComboStrategy, td, params)
        calc = strat.calculate_indicators(ohlcv.copy())
        entry = _safe_mask(strat, calc, td["entry_logic"])
        exit_ = _safe_mask(strat, calc, td["exit_logic"])
        sig = strat.generate_signals(ohlcv.copy())
        trades = extract_trades_from_signals(sig, strat.stop_loss, direction="long")
        metrics = _metrics_from_trades(trades, 100)
        cols = indicator_columns(calc)
        return (
            tuple(sha256_col(calc[c]) for c in cols),
            sha256_mask(entry),
            sha256_mask(exit_),
            sha256_trades(trades),
            sha256_metrics(metrics),
        )

    cold = run(params_a)
    hot = run(params_a)
    other = run(params_b)
    again = run(params_a)
    assert cold == hot == again
    assert cold[0] != other[0] or params_a == params_b


def test_stop_loss_outside_indicator_key(inch_1d):
    td = _template_data("multi_ma_crossover")
    base = dict(_r1()["multi_ma_crossover"][3])
    a = dict(base)
    b = dict(base)
    a["stop_loss"] = 0.01
    b["stop_loss"] = 0.2
    ohlcv = inch_1d[OHLCV_COLS]
    sa = _strategy(ComboStrategy, td, a)
    sb = _strategy(ComboStrategy, td, b)
    ca = sa.calculate_indicators(ohlcv.copy())
    cb = sb.calculate_indicators(ohlcv.copy())
    for col in indicator_columns(ca):
        np.testing.assert_array_equal(ca[col].to_numpy(), cb[col].to_numpy())
        assert sha256_col(ca[col]) == sha256_col(cb[col])
    trades_a = extract_trades_from_signals(sa.generate_signals(ohlcv.copy()), sa.stop_loss)
    trades_b = extract_trades_from_signals(sb.generate_signals(ohlcv.copy()), sb.stop_loss)
    # Reusing the finished signal series across stops is not equivalent.
    assert sha256_trades(trades_a) != sha256_trades(trades_b) or sa.stop_loss == sb.stop_loss


def _run_trial(cls, extract_fn, metrics_fn, td, params, direction, df_1d, df_15m, deep):
    trial_params = dict(params)
    trial_params["direction"] = direction
    strat = _strategy(cls, td, trial_params, direction=direction)
    df_sig = strat.generate_signals(df_1d[OHLCV_COLS].copy())
    trades = extract_fn(
        df_sig,
        strat.stop_loss,
        deep_backtest=deep,
        symbol="1INCH/USDT",
        since_str=str(df_1d.index.min().date()),
        until_str=str(df_1d.index.max().date()),
        df_15m_cache=df_15m if deep else None,
        direction=direction,
    )
    metrics = metrics_fn(trades, 100)
    return trades, metrics


@pytest.mark.parametrize("name", CATALOG)
@pytest.mark.parametrize("direction", ("long", "short"))
@pytest.mark.parametrize("mode_name,deep", (("deep_15m", True), ("fast_1d", False)))
def test_trial_trades_and_metrics_match_oracle(name, direction, mode_name, deep, inch_1d, inch_15m):
    td = _template_data(name)
    for i, params in enumerate(_r1()[name]):
        prod_trades, prod_metrics = _run_trial(
            ComboStrategy,
            extract_trades_with_mode,
            _metrics_from_trades,
            td,
            params,
            direction,
            inch_1d,
            inch_15m,
            deep,
        )
        ora_trades, ora_metrics = _run_trial(
            LegacyComboStrategy,
            oracle_extract_with_mode,
            oracle_metrics_from_trades,
            td,
            params,
            direction,
            inch_1d,
            inch_15m,
            deep,
        )
        assert prod_trades == ora_trades
        for key in sorted(set(prod_metrics) | set(ora_metrics)):
            if key in {"avg_atr", "avg_adx", "error"}:
                continue
            assert prod_metrics.get(key) == ora_metrics.get(key), key
        tkey = f"{name}|1INCH/USDT|{direction}|{mode_name}|{i}"
        expected = _sha()["trial"][tkey]
        assert sha256_trades(prod_trades) == expected["trades"]
        assert sha256_metrics(prod_metrics) == expected["metrics"]


@pytest.mark.parametrize("name", CATALOG)
@pytest.mark.parametrize("direction", ("long", "short"))
@pytest.mark.parametrize("mode_name,deep", (("deep_15m", True), ("fast_1d", False)))
def test_trial_second_symbol_matches_oracle(name, direction, mode_name, deep, aave_1d, aave_15m):
    td = _template_data(name)
    for i, params in enumerate(_r1()[name]):
        trial_params = dict(params)
        trial_params["direction"] = direction
        prod = _strategy(ComboStrategy, td, trial_params, direction=direction)
        ora = _strategy(LegacyComboStrategy, td, trial_params, direction=direction)
        p_sig = prod.generate_signals(aave_1d[OHLCV_COLS].copy())
        o_sig = ora.generate_signals(aave_1d[OHLCV_COLS].copy())
        kwargs = dict(
            deep_backtest=deep,
            symbol="AAVE/USDT",
            since_str=str(aave_1d.index.min().date()),
            until_str=str(aave_1d.index.max().date()),
            df_15m_cache=aave_15m if deep else None,
            direction=direction,
        )
        p_trades = extract_trades_with_mode(p_sig, prod.stop_loss, **kwargs)
        o_trades = oracle_extract_with_mode(o_sig, ora.stop_loss, **kwargs)
        assert p_trades == o_trades
        p_metrics = _metrics_from_trades(p_trades, 100)
        o_metrics = oracle_metrics_from_trades(o_trades, 100)
        tkey = f"{name}|AAVE/USDT|{direction}|{mode_name}|{i}"
        expected = _sha()["trial"][tkey]
        assert sha256_trades(p_trades) == expected["trades"]
        assert sha256_metrics(p_metrics) == expected["metrics"]
        assert sha256_metrics(o_metrics) == expected["metrics"]


def test_fast_1d_extract_matches_oracle(inch_1d):
    td = _template_data("ema_rsi")
    params = _r1()["ema_rsi"][0]
    prod = _strategy(ComboStrategy, td, params, direction="short")
    ora = _strategy(LegacyComboStrategy, td, params, direction="short")
    p_sig = prod.generate_signals(inch_1d[OHLCV_COLS].copy())
    o_sig = ora.generate_signals(inch_1d[OHLCV_COLS].copy())
    p_trades = extract_trades_from_signals(p_sig, prod.stop_loss, "short")
    o_trades = oracle_extract_trades(o_sig, ora.stop_loss, "short")
    assert p_trades == o_trades


def test_representative_winner_holdout_go_nogo(inch_1d, inch_15m, monkeypatch):
    import concurrent.futures

    from app.services import combo_optimizer as co

    td = _template_data("multi_ma_crossover")

    class FakeService:
        def get_template_metadata(self, _name):
            return metadata_from_export(_TEMPLATES["multi_ma_crossover"])

        def create_strategy(self, template_name, parameters=None):
            return _strategy(ComboStrategy, td, parameters or {}, direction="long")

    class FakeProvider:
        def fetch_ohlcv(self, **_kwargs):
            return inch_1d.copy()

    class FakeLoader:
        def fetch_intraday_data(self, **_kwargs):
            return inch_15m.copy()

        def check_intraday_availability(self, *_a, **_k):
            return {
                "available": True,
                "coverage": {"end": str(inch_15m.index.max())},
            }

    class InlinePool:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def submit(self, fn, *args, **kwargs):
            fut = concurrent.futures.Future()
            try:
                fut.set_result(fn(*args, **kwargs))
            except Exception as exc:
                fut.set_exception(exc)
            return fut

        def shutdown(self, wait=True):
            return None

    optimizer = co.ComboOptimizer.__new__(co.ComboOptimizer)
    optimizer.checkpoint_dir = Path("/tmp/card-945-checkpoints")
    optimizer.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    optimizer.combo_service = FakeService()
    optimizer.loader = FakeLoader()

    monkeypatch.setattr(co, "get_market_data_provider", lambda *_a, **_k: FakeProvider())
    monkeypatch.setattr(co, "resolve_data_source_for_symbol", lambda *_a, **_k: "ccxt")
    monkeypatch.setattr(co, "validate_data_source_timeframe", lambda *_a, **_k: "ccxt")
    monkeypatch.setattr(co.concurrent.futures, "ProcessPoolExecutor", InlinePool)
    monkeypatch.setattr(co, "_worker_get_15m_cache", lambda *_a, **_k: inch_15m)
    orig_extract = co.extract_trades_with_mode

    def _extract_with_fixture(*args, **kwargs):
        kwargs.setdefault("df_15m_cache", inch_15m)
        return orig_extract(*args, **kwargs)

    monkeypatch.setattr(co, "extract_trades_with_mode", _extract_with_fixture)

    kwargs = dict(
        template_name="multi_ma_crossover",
        symbol="1INCH/USDT",
        timeframe="1d",
        data_source="ccxt",
        start_date=str(inch_1d.index.min().date()),
        end_date=str(inch_1d.index.max().date()),
        direction="long",
        deep_backtest=True,
        split_train_ratio=0.7,
    )
    result_a = optimizer.run_optimization(**kwargs)
    result_b = optimizer.run_optimization(**kwargs)
    for key in ("best_parameters", "best_metrics", "oos_metrics", "oos_verdict"):
        assert result_a[key] == result_b[key]

    params = dict(result_a["best_parameters"])
    direction = params.get("direction", "long")
    train, holdout = split_train_holdout(inch_1d, 0.7)
    burn = max(50, 250)
    holdout_frame = pd.concat([train.iloc[-burn:], holdout])
    holdout_eval_start = holdout.index.min()
    skip = {"avg_atr", "avg_adx", "error"}

    def _eval_window(cls, extract_fn, metrics_fn, df_window):
        strat = _strategy(cls, td, params, direction=direction)
        df_sig = strat.generate_signals(df_window[OHLCV_COLS].copy())
        trades = extract_fn(
            df_sig,
            strat.stop_loss,
            deep_backtest=True,
            symbol="1INCH/USDT",
            since_str=str(df_window.index.min().date()),
            until_str=str(df_window.index.max().date()),
            df_15m_cache=inch_15m,
            direction=direction,
        )
        return trades, metrics_fn(trades, 100)

    def _holdout_trades(trades):
        kept = []
        for trade in trades:
            entry = trade.get("entry_time")
            if not entry:
                continue
            if pd.Timestamp(entry) >= holdout_eval_start:
                kept.append(trade)
        return kept

    def _core(prod, ora):
        keys = sorted(set(ora) - skip)
        return {k: _jsonable(prod.get(k)) for k in keys}, {k: _jsonable(ora.get(k)) for k in keys}

    prod_train_trades, prod_train_metrics = _eval_window(
        ComboStrategy, extract_trades_with_mode, _metrics_from_trades, train
    )
    ora_train_trades, ora_train_metrics = _eval_window(
        LegacyComboStrategy, oracle_extract_with_mode, oracle_metrics_from_trades, train
    )
    assert prod_train_trades == ora_train_trades
    left, right = _core(prod_train_metrics, ora_train_metrics)
    assert left == right
    assert sha256_metrics(prod_train_metrics) == sha256_metrics(ora_train_metrics)
    left, right = _core(result_a["best_metrics"] or {}, ora_train_metrics)
    assert left == right

    prod_h_raw, _ = _eval_window(
        ComboStrategy, extract_trades_with_mode, _metrics_from_trades, holdout_frame
    )
    ora_h_raw, _ = _eval_window(
        LegacyComboStrategy, oracle_extract_with_mode, oracle_metrics_from_trades, holdout_frame
    )
    prod_holdout = _holdout_trades(prod_h_raw)
    ora_holdout = _holdout_trades(ora_h_raw)
    assert prod_holdout == ora_holdout
    ora_oos = oracle_metrics_from_trades(ora_holdout, 100)
    left, right = _core(result_a.get("oos_metrics") or {}, ora_oos)
    assert left == right
    assert sha256_metrics(ora_oos) == sha256_metrics(
        {k: (result_a.get("oos_metrics") or {}).get(k) for k in ora_oos}
    )

    from app.metrics.criteria import evaluate_walk_forward

    ora_verdict = evaluate_walk_forward(ora_train_metrics, ora_oos)
    assert result_a["best_parameters"]
    assert result_a["oos_verdict"] is not None
    assert result_a["oos_verdict"]["status"] == ora_verdict.status


def _jsonable(value):
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, (np.floating, float)):
        return float(value)
    if isinstance(value, (np.integer, int)) and not isinstance(value, bool):
        return int(value)
    if value is None or isinstance(value, (str, bool)):
        return value
    return str(value)


def test_legacy_kill_switch_env_default_is_fast():
    assert os.getenv("COMBO_OPTIMIZER_LEGACY", "0") != "1"
