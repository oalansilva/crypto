"""Public, typed contract for strategy behavior and chart series."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

TransparencyStatus = Literal["available", "unavailable", "timeframe_mismatch"]
ExplanationStatus = Literal["available", "partial", "unavailable", "inconsistent"]
TradeExplanationTrigger = Literal[
    "entry_rule", "exit_rule", "stop_loss", "take_profit", "open_position"
]


class IndicatorPoint(BaseModel):
    timestamp_utc: str
    value: float


class IndicatorReference(BaseModel):
    value: float
    label: str


class StrategyIndicatorTransparency(BaseModel):
    key: str
    type: str
    label: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    function: str
    panel: Literal["price", "volume", "oscillator", "macd", "atr"]
    scale: Literal["price", "volume", "percent", "oscillator"]
    color: str
    participation: list[Literal["entry", "exit", "risk"]] = Field(default_factory=list)
    references: list[IndicatorReference] = Field(default_factory=list)
    execution_columns: list[str] = Field(default_factory=list)
    series_status: TransparencyStatus = "unavailable"
    series: list[IndicatorPoint] = Field(default_factory=list)
    unavailable_reason: str | None = None


class StrategyLogicBlock(BaseModel):
    participation: Literal["entry", "exit", "risk"]
    description: str
    status: Literal["available", "partial", "unavailable"] = "available"
    operator: Literal["all", "any", "mixed", "sequence"] = "all"
    condition_count: int = 0


class TradeEvidenceItem(BaseModel):
    key: str
    label: str
    value: float | str | None = None
    timestamp_utc: str | None = None
    state: Literal["confirmed", "pending", "reference"] = "reference"


class TradeExplanation(BaseModel):
    status: ExplanationStatus
    direction: Literal["long", "short"]
    timeframe: str | None = None
    action: str
    trigger: TradeExplanationTrigger
    summary: str
    rule_summary: str | None = None
    risk_summary: str | None = None
    decision_candle_time: str | None = None
    execution_time: str | None = None
    execution_price: float | None = None
    evidence: list[TradeEvidenceItem] = Field(default_factory=list)
    unavailable_reason: str | None = None


class StrategyTransparency(BaseModel):
    status: TransparencyStatus
    strategy_key: str
    display_name: str | None = None
    description: str | None = None
    timeframe: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    indicators: list[StrategyIndicatorTransparency] = Field(default_factory=list)
    # Runtime-only decision context. Excluded to avoid duplicating OHLC payloads.
    market_series: dict[str, list[IndicatorPoint]] = Field(default_factory=dict, exclude=True)
    logic_blocks: list[StrategyLogicBlock] = Field(default_factory=list)
    unavailable_reason: str | None = None
