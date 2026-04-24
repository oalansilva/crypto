from __future__ import annotations

import pandas as pd

from app.services.chart_pattern_service import ChartPatternConfig, detect_chart_patterns


def _events(df: pd.DataFrame, config: ChartPatternConfig | None = None) -> list[dict]:
    return [
        event for row_events in detect_chart_patterns(df, config).tolist() for event in row_events
    ]


def test_detects_golden_and_death_cross_with_confidence_bounds() -> None:
    df = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=4, freq="D", tz="UTC"),
            "close": [100.0, 101.0, 102.0, 99.0],
            "sma_20": [9.0, 10.0, 11.0, 9.0],
            "sma_50": [10.0, 10.0, 10.0, 10.0],
        }
    )

    events = _events(df)

    assert [event["pattern"] for event in events] == ["golden_cross", "death_cross"]
    assert [event["direction"] for event in events] == ["bullish", "bearish"]
    assert all(0 <= event["confidence"] <= 100 for event in events)
    assert events[0]["metadata"] == {
        "fast_ma": "sma_20",
        "slow_ma": "sma_50",
        "fast_value": 11.0,
        "slow_value": 10.0,
    }


def test_deduplicates_repeated_nearby_crosses() -> None:
    df = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=5, freq="D", tz="UTC"),
            "close": [100.0, 101.0, 100.0, 102.0, 103.0],
            "sma_20": [9.0, 11.0, 9.0, 11.0, 12.0],
            "sma_50": [10.0, 10.0, 10.0, 10.0, 10.0],
        }
    )

    events = _events(df, ChartPatternConfig(dedupe_window_bars=10))

    assert [event["pattern"] for event in events] == ["golden_cross", "death_cross"]


def test_detects_confirmed_double_top() -> None:
    df = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=7, freq="D", tz="UTC"),
            "high": [10.0, 15.0, 12.0, 15.2, 13.0, 11.0, 10.0],
            "low": [9.0, 10.0, 8.0, 11.0, 10.0, 9.0, 8.0],
            "close": [10.0, 14.0, 9.0, 14.0, 12.0, 7.8, 7.0],
        }
    )

    events = _events(df, ChartPatternConfig(pivot_window=1, min_pivot_separation=2))

    assert len(events) == 1
    event = events[0]
    assert event["pattern"] == "double_top"
    assert event["direction"] == "bearish"
    assert 0 <= event["confidence"] <= 100
    assert event["metadata"]["neckline"] == 8.0
    assert event["reference_price"] == 7.8


def test_detects_confirmed_double_bottom() -> None:
    df = pd.DataFrame(
        {
            "ts": pd.date_range("2026-01-01", periods=7, freq="D", tz="UTC"),
            "high": [16.0, 15.0, 17.0, 15.0, 16.0, 18.0, 19.0],
            "low": [15.0, 10.0, 12.0, 10.1, 11.0, 14.0, 16.0],
            "close": [15.0, 11.0, 16.0, 11.0, 13.0, 18.2, 19.0],
        }
    )

    events = _events(df, ChartPatternConfig(pivot_window=1, min_pivot_separation=2))

    assert len(events) == 1
    event = events[0]
    assert event["pattern"] == "double_bottom"
    assert event["direction"] == "bullish"
    assert 0 <= event["confidence"] <= 100
    assert event["metadata"]["neckline"] == 17.0
    assert event["reference_price"] == 18.2
