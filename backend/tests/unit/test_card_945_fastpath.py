"""Andar B checks: kill-switch, callers, `_legacy_*` aliases. Not wall-clock."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.combo_optimizer import ComboOptimizer
from app.services.discovery_service import OUTBOX_MAX_PER_SWEEP
from oracles._build_card_945 import OHLCV_COLS, load_ohlcv
from test_card_945_goldens import _r1, _strategy, _template_data


@pytest.fixture(scope="module")
def inch_1d():
    return load_ohlcv("1INCH/USDT", "1d")


def test_kill_switch_calls_legacy_position_loop(inch_1d, monkeypatch):
    from app.strategies.combos.combo_strategy import ComboStrategy as CS

    td = _template_data("multi_ma_crossover")
    params = _r1()["multi_ma_crossover"][0]
    monkeypatch.setenv("COMBO_OPTIMIZER_LEGACY", "1")
    strat = _strategy(CS, td, params)
    called = {"legacy": 0}
    orig = CS._legacy_generate_signals

    def wrapped(self, df):
        called["legacy"] += 1
        return orig(self, df)

    monkeypatch.setattr(CS, "_legacy_generate_signals", wrapped)
    strat.generate_signals(inch_1d[OHLCV_COLS].copy())
    assert called["legacy"] == 1


def test_engine_callers_share_combo_optimizer():
    import app.routes.combo_routes as lab
    import app.services.batch_backtest_service as batch
    import app.services.favorite_backtest_refresh_service as regen
    import app.services.walk_forward_revalidation as reval
    import app.tasks.discovery_tasks as scan

    assert lab.ComboOptimizer is ComboOptimizer
    assert batch.ComboOptimizer is ComboOptimizer
    assert reval.ComboOptimizer is ComboOptimizer
    assert regen.ComboOptimizer is ComboOptimizer
    src = Path(scan.__file__).read_text()
    assert "ComboOptimizer" in src
    assert "run_optimization" in src
    assert OUTBOX_MAX_PER_SWEEP == 1


def test_rewritten_functions_keep_legacy_aliases():
    from app.services import combo_optimizer as co
    from app.services import deep_backtest as db
    from app.strategies.combos.combo_strategy import ComboStrategy

    assert callable(ComboStrategy._legacy_generate_signals)
    assert callable(ComboStrategy._fast_position_loop)
    assert callable(co._legacy_extract_trades_from_signals)
    assert callable(co._fast_extract_trades_from_signals)
    assert callable(co._legacy_run_backtest_logic)
    assert callable(db._legacy_simulate_execution_with_15m)
    assert callable(db._fast_simulate_execution_with_15m)
    assert callable(co._indicator_cache_key)
    assert callable(co._window_identity)
