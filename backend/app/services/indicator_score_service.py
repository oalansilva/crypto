from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

DEFAULT_RULESET_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "indicator_score_rules.v1.json"
)


@dataclass(frozen=True)
class IndicatorScore:
    name: str
    score: float
    rule_version: str
    rule_type: str
    inputs: dict[str, float]

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "score": self.score,
            "rule_version": self.rule_version,
            "rule_type": self.rule_type,
            "inputs": dict(self.inputs),
        }


def _clamp_score(value: float) -> float:
    return round(max(0.0, min(10.0, float(value))), 4)


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _polarity(rule: dict[str, Any]) -> float:
    return -1.0 if str(rule.get("polarity") or "normal").lower() == "inverse" else 1.0


def _linear_score(value: float, low: float, high: float, polarity: float) -> float | None:
    if high == low:
        return None
    normalized = (value - low) / (high - low)
    if polarity < 0:
        normalized = 1.0 - normalized
    return _clamp_score(normalized * 10.0)


def _required_inputs(row: dict[str, Any], rule: dict[str, Any]) -> dict[str, float] | None:
    raw_inputs = rule.get("inputs")
    if not isinstance(raw_inputs, dict) or not raw_inputs:
        return None

    values: dict[str, float] = {}
    for input_name, column in raw_inputs.items():
        parsed = _float_or_none(row.get(str(column)))
        if parsed is None:
            return None
        values[str(input_name)] = parsed
    return values


def load_indicator_score_rules(path: str | Path | None = None) -> dict[str, Any]:
    configured_path = path or os.getenv("INDICATOR_SCORE_RULES_PATH") or DEFAULT_RULESET_PATH
    ruleset_path = Path(configured_path)
    with ruleset_path.open("r", encoding="utf-8") as fh:
        ruleset = json.load(fh)

    version = str(ruleset.get("version") or "").strip()
    rules = ruleset.get("indicators")
    if not version:
        raise ValueError("indicator score ruleset must define a non-empty version")
    if not isinstance(rules, list) or not rules:
        raise ValueError("indicator score ruleset must define a non-empty indicators list")

    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValueError(f"indicator score rule #{index} must be an object")
        if not str(rule.get("name") or "").strip():
            raise ValueError(f"indicator score rule #{index} must define name")
        if not str(rule.get("type") or "").strip():
            raise ValueError(f"indicator score rule {rule.get('name')} must define type")
        if not isinstance(rule.get("inputs"), dict) or not rule["inputs"]:
            raise ValueError(f"indicator score rule {rule.get('name')} must define inputs")

    return ruleset


class IndicatorScoreService:
    def __init__(self, ruleset: dict[str, Any] | None = None) -> None:
        self.ruleset = ruleset or load_indicator_score_rules()
        self.version = str(self.ruleset["version"])
        self.rules = list(self.ruleset["indicators"])

    def score_row(self, row: dict[str, Any]) -> list[IndicatorScore]:
        scores: list[IndicatorScore] = []
        for rule in self.rules:
            inputs = _required_inputs(row, rule)
            if inputs is None:
                continue

            value = self._score_rule(rule, inputs)
            if value is None:
                continue

            scores.append(
                IndicatorScore(
                    name=str(rule["name"]),
                    score=value,
                    rule_version=self.version,
                    rule_type=str(rule["type"]),
                    inputs=inputs,
                )
            )
        return scores

    def score_row_as_dicts(self, row: dict[str, Any]) -> list[dict[str, Any]]:
        return [score.as_dict() for score in self.score_row(row)]

    def score_rows(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        scored_rows: list[dict[str, Any]] = []
        for row in rows:
            scored_rows.append(
                {
                    "symbol": row.get("symbol"),
                    "timeframe": row.get("timeframe"),
                    "ts": row.get("ts"),
                    "rule_version": self.version,
                    "scores": self.score_row_as_dicts(row),
                }
            )
        return scored_rows

    def _score_rule(self, rule: dict[str, Any], inputs: dict[str, float]) -> float | None:
        rule_type = str(rule.get("type") or "").lower()
        polarity = _polarity(rule)

        if rule_type == "linear":
            low = _float_or_none(rule.get("min"))
            high = _float_or_none(rule.get("max"))
            if low is None or high is None:
                return None
            return _linear_score(inputs["value"], low, high, polarity)

        if rule_type == "centered_tanh":
            center = _float_or_none(rule.get("center")) or 0.0
            scale = _float_or_none(rule.get("scale"))
            if scale is None or scale <= 0:
                return None
            distance = (inputs["value"] - center) / scale
            return _clamp_score(5.0 + (math.tanh(distance) * 5.0 * polarity))

        if rule_type == "crossover":
            slow = inputs["slow"]
            if slow == 0:
                return None
            percent_scale = _float_or_none(rule.get("percent_scale")) or 1.0
            if percent_scale <= 0:
                return None
            delta_percent = ((inputs["fast"] - slow) / abs(slow)) * 100.0
            return _clamp_score(5.0 + (math.tanh(delta_percent / percent_scale) * 5.0))

        if rule_type == "band_width":
            middle = inputs["middle"]
            if middle == 0:
                return None
            width_percent = ((inputs["upper"] - inputs["lower"]) / abs(middle)) * 100.0
            low = _float_or_none(rule.get("min_percent"))
            high = _float_or_none(rule.get("max_percent"))
            if low is None or high is None:
                return None
            return _linear_score(width_percent, low, high, polarity)

        if rule_type == "ratio_linear":
            denominator = inputs["denominator"]
            if denominator == 0:
                return None
            ratio_percent = (inputs["numerator"] / abs(denominator)) * 100.0
            low = _float_or_none(rule.get("min_percent"))
            high = _float_or_none(rule.get("max_percent"))
            if low is None or high is None:
                return None
            return _linear_score(ratio_percent, low, high, polarity)

        if rule_type == "range_width":
            center = inputs["center"]
            if center == 0:
                return None
            width_percent = ((inputs["upper"] - inputs["lower"]) / abs(center)) * 100.0
            low = _float_or_none(rule.get("min_percent"))
            high = _float_or_none(rule.get("max_percent"))
            if low is None or high is None:
                return None
            return _linear_score(width_percent, low, high, polarity)

        return None


@lru_cache()
def get_indicator_score_service() -> IndicatorScoreService:
    return IndicatorScoreService()
