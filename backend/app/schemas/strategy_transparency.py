"""Public, typed contract for strategy behavior and chart series."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

TransparencyStatus = Literal["available", "unavailable", "timeframe_mismatch"]


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


class StrategyTransparency(BaseModel):
    status: TransparencyStatus
    strategy_key: str
    display_name: str | None = None
    description: str | None = None
    timeframe: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    indicators: list[StrategyIndicatorTransparency] = Field(default_factory=list)
    logic_blocks: list[StrategyLogicBlock] = Field(default_factory=list)
    unavailable_reason: str | None = None
