from __future__ import annotations

import pandas as pd

from app.services.opportunity_service import (
    _build_market_indicator_mappings,
    _hydrate_with_stored_indicators,
)


def test_advanced_indicator_mappings_are_available_for_stored_indicator_hydration() -> None:
    mappings = _build_market_indicator_mappings(
        [
            {"type": "bbands", "alias": "bb", "params": {"length": 20, "std": 2}},
            {"type": "atr", "params": {"length": 14}},
            {"type": "stoch", "params": {"k": 14, "d": 3, "smooth_k": 3}},
            {"type": "obv", "params": {}},
            {"type": "ichimoku", "params": {"tenkan": 9, "kijun": 26, "senkou": 52}},
        ]
    )

    assert mappings == {
        "bb_upper_20_2": "bb_upper",
        "bb_middle_20_2": "bb_middle",
        "bb_lower_20_2": "bb_lower",
        "atr_14": "ATR_14",
        "stoch_k_14_3_3": "STOCH14_3_3",
        "stoch_d_14_3_3": "STOCHd_14_3_3",
        "obv": "OBV",
        "ichimoku_tenkan_9": "ITS_9",
        "ichimoku_kijun_26": "IKS_26",
        "ichimoku_senkou_a_9_26_52": "ISA_9",
        "ichimoku_senkou_b_9_26_52": "ISB_26",
        "ichimoku_chikou_26": "ICHI_9_26_52",
    }


def test_advanced_stored_indicators_hydrate_without_inline_recalculation() -> None:
    ts = pd.Timestamp("2026-04-23T00:00:00Z")
    df = pd.DataFrame({"close": [100.0]}, index=[ts])
    rows = [
        {
            "ts": ts,
            "bb_upper_20_2": 110.0,
            "bb_middle_20_2": 100.0,
            "bb_lower_20_2": 90.0,
            "atr_14": 5.0,
            "stoch_k_14_3_3": 70.0,
            "stoch_d_14_3_3": 65.0,
            "obv": 12345.0,
            "ichimoku_tenkan_9": 99.0,
            "ichimoku_kijun_26": 98.0,
            "ichimoku_senkou_a_9_26_52": 98.5,
            "ichimoku_senkou_b_9_26_52": 97.0,
            "ichimoku_chikou_26": 100.0,
        }
    ]
    mappings = {
        "bb_upper_20_2": "bb_upper",
        "atr_14": "ATR_14",
        "stoch_k_14_3_3": "STOCH14_3_3",
        "obv": "OBV",
        "ichimoku_tenkan_9": "ITS_9",
    }

    hydrated, used_stored = _hydrate_with_stored_indicators(df, rows, mappings)

    assert used_stored is True
    assert hydrated.loc[ts, "bb_upper"] == 110.0
    assert hydrated.loc[ts, "ATR_14"] == 5.0
    assert hydrated.loc[ts, "STOCH14_3_3"] == 70.0
    assert hydrated.loc[ts, "OBV"] == 12345.0
    assert hydrated.loc[ts, "ITS_9"] == 99.0
