import json
import math
from pathlib import Path

import pandas as pd

from app.services.strategy_secret_visibility import redact_opportunity_payload
from app.services.strategy_transparency import build_strategy_transparency
from app.services.strategy_transparency import build_strategy_transparency_from_serialized
from app.services.trade_explanations import explain_signal_history, explain_trades
from app.strategies.combos.combo_strategy import ComboStrategy


def _manifest(*, direction: str = "long", with_series: bool = True):
    frame = pd.DataFrame(
        {
            "open": [100.0, 101.0, 103.0, 104.0, 102.0],
            "high": [102.0, 103.0, 105.0, 106.0, 104.0],
            "low": [99.0, 100.0, 102.0, 101.0, 100.0],
            "close": [101.0, 102.0, 104.0, 102.0, 101.0],
            "fast": [99.0, 101.5, 103.5, 102.5, 100.5],
            "slow": [100.0, 101.0, 102.0, 103.0, 102.0],
            "volume": [1000.0] * 5,
        },
        index=pd.date_range("2026-07-10", periods=5, tz="UTC"),
    )
    return build_strategy_transparency(
        "multi_ma_crossover",
        {
            "indicators": [
                {"type": "ema", "alias": "fast", "params": {"length": 18}},
                {"type": "sma", "alias": "slow", "params": {"length": 35}},
            ],
            "entry_logic": "crossover(fast, slow)",
            "exit_logic": "crossunder(fast, slow)",
            "stop_loss": 0.04,
        },
        effective_parameters={"direction": direction, "stop_loss": 0.04},
        timeframe="1d",
        dataframe=frame if with_series else None,
    )


def test_closed_long_trade_uses_previous_decision_candles_and_historical_values():
    trade = {
        "entry_time": "2026-07-12T00:00:00+00:00",
        "entry_price": 103.0,
        "exit_time": "2026-07-14T00:00:00+00:00",
        "exit_price": 102.0,
        "exit_reason": "exit_logic",
    }

    explained = explain_trades([trade], _manifest(), direction="long", timeframe="1d")[0]

    assert explained["entry_explanation"]["status"] == "available"
    assert explained["entry_explanation"]["action"] == "Compra"
    assert explained["entry_explanation"]["decision_candle_time"] == "2026-07-11T00:00:00+00:00"
    assert explained["exit_explanation"]["action"] == "Venda"
    assert explained["exit_explanation"]["trigger"] == "exit_rule"
    assert explained["exit_explanation"]["decision_candle_time"] == "2026-07-13T00:00:00+00:00"
    assert {item["timestamp_utc"] for item in explained["entry_explanation"]["evidence"]} == {
        "2026-07-11T00:00:00+00:00"
    }


def test_open_short_trade_explains_sell_entry_cover_exit_and_stop_above_entry():
    open_trade = {
        "entry_time": "2026-07-12T00:00:00+00:00",
        "entry_price": 103.0,
    }
    explained = explain_trades(
        [open_trade], _manifest(direction="short"), direction="short", timeframe="1d"
    )[0]

    assert explained["entry_explanation"]["action"] == "Venda/Short"
    assert explained["current_state_explanation"]["action"] == "Venda/Short ativa"
    assert explained["current_state_explanation"]["rule_summary"].startswith("A saída é confirmada")
    assert "stop de proteção" in explained["current_state_explanation"]["risk_summary"]
    assert "Compra/Cobertura" not in explained["entry_explanation"]["summary"]
    risk = next(
        block
        for block in _manifest(direction="short").logic_blocks
        if block.participation == "risk"
    )
    assert "acima do preço para short" in risk.description

    stopped = explain_trades(
        [
            {
                **open_trade,
                "exit_time": "2026-07-13T12:00:00+00:00",
                "exit_price": 107.12,
                "exit_reason": "stop_loss_15m",
            }
        ],
        _manifest(direction="short"),
        direction="short",
        timeframe="1d",
    )[0]
    assert stopped["exit_explanation"]["action"] == "Compra/Cobertura"
    assert stopped["exit_explanation"]["trigger"] == "stop_loss"

    target_named = explain_trades(
        [
            {
                **open_trade,
                "exit_time": "2026-07-13T00:00:00+00:00",
                "exit_price": 99.0,
                "exit_reason": "target_legacy",
            }
        ],
        _manifest(direction="short"),
        direction="short",
        timeframe="1d",
    )[0]
    assert target_named["exit_explanation"]["trigger"] == "exit_rule"


def test_trade_without_historical_series_is_explicitly_unavailable():
    explained = explain_trades(
        [{"entry_time": "2026-07-12T00:00:00+00:00", "entry_price": 103.0}],
        _manifest(with_series=False),
        direction="long",
        timeframe="1d",
    )[0]

    assert explained["entry_explanation"]["status"] == "unavailable"
    assert "trade histórico" in explained["entry_explanation"]["summary"]
    assert explained["entry_explanation"]["evidence"] == []


def test_signal_explanation_survives_common_user_redaction_without_raw_logic():
    history = explain_signal_history(
        [
            {
                "timestamp": "2026-07-12T00:00:00+00:00",
                "signal": 1,
                "type": "entry",
                "reason": "entry",
                "price": 103.0,
            }
        ],
        _manifest(),
        direction="long",
        timeframe="1d",
    )
    history[0]["explanation"]["private_diagnostic"] = "secret"
    redacted = redact_opportunity_payload(
        {
            "template_name": "multi_ma_crossover",
            "name": "Favorita",
            "parameters": {"secret": 1},
            "indicator_values": {"fast": 1},
            "details": {"raw": "secret"},
            "message": "raw",
            "status": "HOLD",
            "is_holding": True,
            "signal_history": history,
        },
        include_secrets=False,
    )

    assert redacted["signal_history"][0]["explanation"]["status"] == "available"
    serialized = json.dumps(redacted["signal_history"], ensure_ascii=False)
    assert "entry_logic" not in serialized
    assert "secret" not in serialized


def test_exported_catalog_has_specific_entry_exit_rule_summaries():
    exported = json.loads(
        Path("backend/config/combo_templates_export.json").read_text(encoding="utf-8")
    )

    for template in exported:
        manifest = build_strategy_transparency(
            template["name"], template["template_data"], timeframe="1d"
        )
        blocks = {block.participation: block for block in manifest.logic_blocks}
        assert blocks["entry"].description, template["name"]
        assert blocks["exit"].description, template["name"]
        assert "combina os indicadores marcados" not in blocks["entry"].description
        assert blocks["entry"].condition_count > 0, template["name"]
        assert blocks["exit"].condition_count > 0, template["name"]
        assert blocks["risk"].description, template["name"]


def test_mixed_rules_preserve_boolean_grouping_in_public_summary():
    manifest = build_strategy_transparency(
        "multi_ma_crossoverV2",
        {
            "indicators": [
                {"type": "ema", "alias": "short", "params": {"length": 18}},
                {"type": "sma", "alias": "medium", "params": {"length": 20}},
                {"type": "sma", "alias": "long", "params": {"length": 35}},
            ],
            "entry_logic": "(short > long) & (crossover(short, long) | crossover(short, medium))",
            "exit_logic": "crossunder(short, long)",
            "stop_loss": 0.04,
        },
        timeframe="1d",
    )
    entry = next(block for block in manifest.logic_blocks if block.participation == "entry")

    assert entry.operator == "mixed"
    assert (
        "(EMA 18 maior que SMA 35) e (EMA 18 cruza acima de SMA 35 ou EMA 18 cruza acima de SMA 20)"
        in entry.description
    )


def test_every_exported_strategy_produces_event_time_entry_and_exit_evidence():
    periods = 320
    timestamps = pd.date_range("2025-01-01", periods=periods, tz="UTC")
    close = [100 + index * 0.1 + math.sin(index / 7) * 3 for index in range(periods)]
    frame = pd.DataFrame(
        {
            "open": [value - 0.2 for value in close],
            "high": [value + 1 for value in close],
            "low": [value - 1 for value in close],
            "close": close,
            "volume": [1000 + (index % 20) * 50 for index in range(periods)],
        },
        index=timestamps,
    )
    exported = json.loads(
        Path("backend/config/combo_templates_export.json").read_text(encoding="utf-8")
    )

    for template in exported:
        data = template["template_data"]
        calculated = ComboStrategy(
            indicators=data["indicators"],
            entry_logic=data["entry_logic"],
            exit_logic=data["exit_logic"],
            stop_loss=data.get("stop_loss", 0.04),
            force_recompute=False,
        ).calculate_indicators(frame.copy())
        manifest = build_strategy_transparency(
            template["name"], data, timeframe="1d", dataframe=calculated
        )
        history = explain_signal_history(
            [
                {
                    "timestamp": timestamps[-2].isoformat(),
                    "signal": 1,
                    "type": "entry",
                    "reason": "entry",
                    "price": close[-2],
                },
                {
                    "timestamp": timestamps[-1].isoformat(),
                    "signal": -1,
                    "type": "exit",
                    "reason": "exit_logic",
                    "price": close[-1],
                },
            ],
            manifest,
            direction="long",
            timeframe="1d",
        )

        for event in history:
            explanation = event["explanation"]
            assert explanation["status"] in {"available", "partial"}, template["name"]
            assert explanation["decision_candle_time"], template["name"]
            assert explanation["evidence"], template["name"]


def test_serialized_candles_preserve_price_only_exit_evidence():
    template = next(
        item
        for item in json.loads(
            Path("backend/config/combo_templates_export.json").read_text(encoding="utf-8")
        )
        if item["name"] == "Example: Breakout with Volume"
    )
    candles = [
        {
            "timestamp_utc": timestamp.isoformat(),
            "open": 100 + index,
            "high": 102 + index,
            "low": 99 + index,
            "close": 101 + index,
        }
        for index, timestamp in enumerate(pd.date_range("2026-07-01", periods=8, tz="UTC"))
    ]
    manifest = build_strategy_transparency_from_serialized(
        template["name"],
        template["template_data"],
        effective_parameters={},
        timeframe="1d",
        candles=candles,
        indicator_data={},
    )
    explained = explain_signal_history(
        [
            {
                "timestamp": candles[-1]["timestamp_utc"],
                "signal": -1,
                "type": "exit",
                "reason": "exit_logic",
                "price": candles[-1]["open"],
            }
        ],
        manifest,
        direction="long",
        timeframe="1d",
    )[0]["explanation"]

    assert explained["status"] == "available"
    assert explained["decision_candle_time"] == candles[-2]["timestamp_utc"]
    assert any(item["key"] == "close" for item in explained["evidence"])
