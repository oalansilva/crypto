import json
from pathlib import Path

import numpy as np
import pandas as pd

from app.services.strategy_secret_visibility import redact_favorite_strategy_payload
from app.services.strategy_transparency import (
    attach_timestamped_series,
    build_strategy_transparency,
    build_strategy_transparency_from_candles,
    normalize_strategy_transparency_colors,
    transparency_matrix,
)
from app.schemas.strategy_transparency import StrategyTransparency


def _template(*indicators, entry_logic="", exit_logic="", stop_loss=0.02):
    return {
        "indicators": list(indicators),
        "entry_logic": entry_logic,
        "exit_logic": exit_logic,
        "stop_loss": stop_loss,
    }


def test_ema_rsi_legacy_key_never_announces_fibonacci():
    manifest = build_strategy_transparency(
        "ema_rsi_fibonacci",
        _template(
            {"type": "ema", "alias": "trend", "params": {"length": 200}},
            {"type": "rsi", "params": {"length": 14}},
            entry_logic="close > trend and RSI_14 > 40",
            exit_logic="close < trend or RSI_14 > 70",
        ),
        timeframe="1d",
    )

    payload = manifest.model_dump(mode="json")
    assert manifest.status == "available"
    assert "Fibonacci" not in json.dumps(payload, ensure_ascii=False)
    assert {item.type for item in manifest.indicators} == {"ema", "rsi"}


def test_timestamped_series_allowlist_roc_finite_gaps_and_diagnostics():
    manifest = build_strategy_transparency(
        "quant_btc_1d_roc_ema_momentum_guard_long_v3",
        _template(
            {"type": "roc", "alias": "momentum", "params": {"length": 20}},
            {"type": "ema", "alias": "trend", "params": {"length": 50}},
            entry_logic="momentum > 0 and close > trend",
            exit_logic="momentum < 0 or close < trend",
        ),
        timeframe="1d",
    )
    frame = pd.DataFrame(
        {
            "momentum": [np.nan, 1.25, np.inf, -0.5],
            "ROC_20": [999, 999, 999, 999],
            "trend": [100, 101, 102, 103],
            "raw_diagnostic": ["secret"] * 4,
        },
        index=pd.date_range("2026-01-01", periods=4, tz="UTC"),
    )

    attach_timestamped_series(manifest, frame, timeframe="1d")

    roc = next(item for item in manifest.indicators if item.type == "roc")
    assert roc.execution_columns == ["momentum"]
    assert [point.value for point in roc.series] == [1.25, -0.5]
    assert all("raw_diagnostic" not in item.execution_columns for item in manifest.indicators)


def test_unknown_identity_and_timeframe_mismatch_are_explicit():
    unknown = build_strategy_transparency(
        "research_winner_20260710",
        _template(
            {"type": "ema", "alias": "fast", "params": {"length": 9}}, entry_logic="close > fast"
        ),
        timeframe="1d",
    )
    assert unknown.status == "unavailable"
    assert unknown.display_name is None

    manifest = build_strategy_transparency(
        "ema_rsi",
        _template(
            {"type": "ema", "alias": "fast", "params": {"length": 9}}, entry_logic="close > fast"
        ),
        timeframe="1d",
    )
    attach_timestamped_series(
        manifest,
        pd.DataFrame({"fast": [1.0]}, index=pd.date_range("2026-01-01", periods=1, tz="UTC")),
        timeframe="4h",
    )
    assert manifest.status == "timeframe_mismatch"
    assert manifest.indicators[0].series == []


def test_common_user_redaction_keeps_public_manifest_but_removes_secrets():
    manifest = build_strategy_transparency(
        "ema_rsi",
        _template(
            {"type": "ema", "alias": "fast", "params": {"length": 9}}, entry_logic="close > fast"
        ),
        timeframe="1d",
    ).model_dump(mode="json")
    redacted = redact_favorite_strategy_payload(
        {
            "strategy_name": "ema_rsi",
            "parameters": {"private": "secret"},
            "strategy_transparency": manifest,
        },
        include_secrets=False,
    )
    assert redacted["parameters"] == {}
    assert redacted["strategy_transparency"] == manifest
    assert "entry_logic" not in json.dumps(manifest)


def test_exported_active_templates_have_specific_drift_safe_manifests():
    exported = json.loads(
        Path("backend/config/combo_templates_export.json").read_text(encoding="utf-8")
    )
    matrix_keys = {row["strategy_key"] for row in transparency_matrix()}

    for template in exported:
        manifest = build_strategy_transparency(
            template["name"], template["template_data"], timeframe="1d"
        )
        assert manifest.strategy_key in matrix_keys
        assert manifest.status == "available", template["name"]
        assert manifest.indicators, template["name"]
        assert not any(
            token in (manifest.display_name or "").lower() for token in ("winner", "chain")
        )
        assert all(item.panel and item.participation for item in manifest.indicators)


def test_multi_ma_colors_follow_semantic_roles_and_period_fallback():
    manifest = build_strategy_transparency(
        "multi_ma_crossoverV2",
        _template(
            {"type": "ema", "alias": "short", "params": {"length": 16}},
            {"type": "sma", "alias": "average_17", "params": {"length": 17}},
            {"type": "sma", "alias": "long", "params": {"length": 33}},
            entry_logic="short > long and average_17 > long",
            exit_logic="short < long",
        ),
        timeframe="1d",
    )

    assert [item.color for item in manifest.indicators] == [
        "#f6465d",
        "#ff9f43",
        "#3b82f6",
    ]


def test_stored_legacy_manifest_colors_are_normalized():
    manifest = StrategyTransparency.model_validate(
        build_strategy_transparency(
            "multi_ma_crossoverV2",
            _template(
                {"type": "ema", "alias": "short", "params": {"length": 16}},
                {"type": "sma", "alias": "medium", "params": {"length": 17}},
                {"type": "sma", "alias": "long", "params": {"length": 33}},
                entry_logic="short > medium and medium > long",
                exit_logic="short < long",
            ),
            timeframe="1d",
        ).model_dump()
    )
    for indicator in manifest.indicators:
        indicator.color = "#74b9ff"

    normalize_strategy_transparency_colors(manifest)

    assert [item.color for item in manifest.indicators] == [
        "#f6465d",
        "#ff9f43",
        "#3b82f6",
    ]


def test_unresolved_single_or_ambiguous_moving_average_keeps_type_color():
    single = build_strategy_transparency(
        "ema_rsi",
        _template(
            {"type": "ema", "alias": "trend", "params": {"length": 20}},
            entry_logic="close > trend",
            exit_logic="close < trend",
        ),
        timeframe="1d",
    )
    duplicates = build_strategy_transparency(
        "multi_ma_crossoverV2",
        _template(
            {"type": "sma", "alias": "average_a", "params": {"length": 20}},
            {"type": "sma", "alias": "average_b", "params": {"length": 20}},
            entry_logic="average_a > average_b",
            exit_logic="average_a < average_b",
        ),
        timeframe="1d",
    )

    assert [item.color for item in single.indicators] == ["#fcd535"]
    assert [item.color for item in duplicates.indicators] == ["#74b9ff", "#74b9ff"]


def test_current_candle_helper_calculates_declared_series_with_exact_utc_timestamps():
    candles = [
        {
            "timestamp_utc": timestamp.isoformat(),
            "open": float(index + 99),
            "high": float(index + 101),
            "low": float(index + 98),
            "close": float(index + 100),
            "volume": 1000.0,
        }
        for index, timestamp in enumerate(pd.date_range("2026-06-01", periods=42, tz="UTC"))
    ]
    manifest = build_strategy_transparency_from_candles(
        "multi_ma_crossoverV2",
        _template(
            {"type": "ema", "alias": "short", "params": {"length": 16}},
            {"type": "sma", "alias": "medium", "params": {"length": 17}},
            {"type": "sma", "alias": "long", "params": {"length": 33}},
            entry_logic="short > medium and medium > long",
            exit_logic="short < long",
        ),
        effective_parameters={"ema_short": 16, "sma_medium": 17, "sma_long": 33},
        timeframe="1d",
        candles=candles,
    )

    assert all(item.series_status == "available" for item in manifest.indicators)
    assert all(
        item.series[-1].timestamp_utc == "2026-07-12T00:00:00+00:00" for item in manifest.indicators
    )
    assert {column for item in manifest.indicators for column in item.execution_columns} == {
        "short",
        "medium",
        "long",
    }
