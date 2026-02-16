import sys
from pathlib import Path

import pandas as pd
import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.strategies.combos.combo_strategy import ComboStrategy


def _sample_df(rows: int = 30) -> pd.DataFrame:
    data = {
        "open": [100 + i for i in range(rows)],
        "high": [101 + i for i in range(rows)],
        "low": [99 + i for i in range(rows)],
        "close": [100 + i for i in range(rows)],
        "volume": [1000 + i for i in range(rows)],
    }
    return pd.DataFrame(data)


def test_derived_feature_lag() -> None:
    df = _sample_df()
    strategy = ComboStrategy(
        indicators=[{"type": "rsi", "alias": "rsi", "params": {"length": 14}}],
        entry_logic="rsi > 50",
        exit_logic="rsi < 50",
        derived_features=[{"name": "rsi_prev", "source": "rsi", "transform": "lag", "params": {"period": 1}}],
    )

    out = strategy.calculate_indicators(df)
    assert "rsi" in out.columns
    assert "rsi_prev" in out.columns
    assert out["rsi_prev"].equals(out["rsi"].shift(1))


def test_derived_feature_invalid_transform() -> None:
    df = _sample_df()
    strategy = ComboStrategy(
        indicators=[{"type": "ema", "alias": "ema", "params": {"length": 10}}],
        entry_logic="ema > close",
        exit_logic="ema < close",
        derived_features=[{"name": "ema_weird", "source": "ema", "transform": "weird"}],
    )

    with pytest.raises(RuntimeError, match="Unsupported derived transform"):
        strategy.calculate_indicators(df)
