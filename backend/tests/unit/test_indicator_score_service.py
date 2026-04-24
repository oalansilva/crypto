from __future__ import annotations

import json

from app.services.indicator_score_service import (
    IndicatorScoreService,
    load_indicator_score_rules,
)


def _complete_indicator_row() -> dict[str, float | str]:
    return {
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "ts": "2026-04-24T00:00:00Z",
        "ema_9": 102.0,
        "ema_21": 100.0,
        "sma_20": 101.0,
        "sma_50": 100.0,
        "rsi_14": 45.0,
        "macd_histogram": 0.5,
        "bb_upper_20_2": 106.0,
        "bb_middle_20_2": 100.0,
        "bb_lower_20_2": 94.0,
        "atr_14": 2.0,
        "stoch_k_14_3_3": 40.0,
        "ichimoku_tenkan_9": 101.5,
        "ichimoku_kijun_26": 100.0,
        "pivot_point": 100.0,
        "support_1": 98.0,
        "resistance_1": 102.0,
    }


def test_default_indicator_scores_are_bounded_and_versioned() -> None:
    service = IndicatorScoreService()

    scores = service.score_row_as_dicts(_complete_indicator_row())

    assert len(scores) == 9
    assert {score["rule_version"] for score in scores} == {"technical-normalization/v1"}
    assert all(0.0 <= score["score"] <= 10.0 for score in scores)
    assert {score["name"] for score in scores} >= {
        "ema_trend",
        "rsi_14",
        "macd_histogram",
        "pivot_range",
    }


def test_missing_or_null_inputs_skip_only_the_affected_score() -> None:
    service = IndicatorScoreService()
    row = _complete_indicator_row()
    row["rsi_14"] = None

    scores = service.score_row_as_dicts(row)

    assert "rsi_14" not in {score["name"] for score in scores}
    assert "ema_trend" in {score["name"] for score in scores}
    assert all(0.0 <= score["score"] <= 10.0 for score in scores)


def test_override_ruleset_preserves_configured_version(tmp_path) -> None:
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(
        json.dumps(
            {
                "version": "test-rules/v2",
                "indicators": [
                    {
                        "name": "custom_rsi",
                        "type": "linear",
                        "inputs": {"value": "rsi_14"},
                        "min": 0,
                        "max": 100,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    ruleset = load_indicator_score_rules(rules_path)
    service = IndicatorScoreService(ruleset=ruleset)

    scores = service.score_row_as_dicts(_complete_indicator_row())

    assert scores == [
        {
            "name": "custom_rsi",
            "score": 4.5,
            "rule_version": "test-rules/v2",
            "rule_type": "linear",
            "inputs": {"value": 45.0},
        }
    ]


def test_admin_latest_scores_endpoint_uses_persisted_indicator_rows(monkeypatch) -> None:
    from app.routes import admin_market_indicators as route

    class FakeMarketIndicatorService:
        def get_latest(self, symbol: str, timeframe: str, limit: int):
            assert symbol == "BTCUSDT"
            assert timeframe == "1h"
            assert limit == 1
            return [_complete_indicator_row()]

    monkeypatch.setattr(route, "get_market_indicator_service", lambda: FakeMarketIndicatorService())
    monkeypatch.setattr(route, "get_indicator_score_service", lambda: IndicatorScoreService())

    response = route.get_latest_indicator_scores(
        symbol="BTCUSDT",
        timeframe="1h",
        limit=1,
        _admin_user_id="admin",
    )

    assert response.items[0].rule_version == "technical-normalization/v1"
    assert len(response.items[0].scores) == 9
    assert all(0.0 <= score.score <= 10.0 for score in response.items[0].scores)
