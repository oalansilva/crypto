from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class RiskProfile(str, Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"


class BollingerBandsPayload(BaseModel):
    upper: float = Field(description="Upper Bollinger Band value")
    middle: float = Field(description="Middle Bollinger Band value")
    lower: float = Field(description="Lower Bollinger Band value")


class SignalIndicators(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rsi: float = Field(alias="RSI", description="Relative Strength Index")
    macd: str = Field(alias="MACD", description="MACD directional sentiment")
    bollinger_bands: BollingerBandsPayload = Field(
        alias="BollingerBands",
        description="Bollinger Bands snapshot",
    )


class ConfidenceBreakdown(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rsi_contribution: float = Field(
        alias="rsiContribution", ge=0, le=100, description="RSI share of the displayed confidence"
    )
    macd_contribution: float = Field(
        alias="macdContribution", ge=0, le=100, description="MACD share of the displayed confidence"
    )
    sentiment_contribution: float = Field(
        alias="sentimentContribution",
        ge=-100,
        le=100,
        description="Sentiment adjustment applied to the technical confidence",
    )
    display_total: float = Field(
        alias="displayTotal",
        ge=0,
        le=100,
        description="Displayed confidence after technical and sentiment composition",
    )


class Signal(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "d2ad2419-c849-55c4-9824-719c639afc7d",
                "asset": "BTCUSDT",
                "type": "BUY",
                "confidence": 82,
                "target_price": 97500.0,
                "stop_loss": 91000.0,
                "indicators": {
                    "RSI": 35.0,
                    "MACD": "bullish",
                    "BollingerBands": {
                        "upper": 98000.0,
                        "middle": 95000.0,
                        "lower": 92000.0,
                    },
                },
                "created_at": "2026-03-26T12:00:00Z",
                "risk_profile": "moderate",
                "breakdown": {
                    "rsi_contribution": 40.18,
                    "macd_contribution": 17.22,
                    "sentiment_contribution": 22.2,
                    "display_total": 79.6,
                },
            }
        }
    )

    id: str = Field(description="Stable UUID for the computed signal")
    asset: str = Field(description="Binance symbol, e.g. BTCUSDT")
    type: SignalType = Field(description="Trading signal type")
    confidence: int = Field(ge=0, le=100, description="Confidence score from 0 to 100")
    target_price: float = Field(gt=0, description="Target price in quote currency")
    stop_loss: float = Field(gt=0, description="Stop loss price in quote currency")
    indicators: SignalIndicators
    created_at: datetime = Field(description="Signal creation timestamp in UTC")
    risk_profile: RiskProfile = Field(description="Risk profile used to compute the signal")
    entry_price: float | None = Field(
        default=None,
        description="Entry price when signal was generated (close price at signal creation)",
    )
    current_price: float | None = Field(
        default=None, description="Latest observed market price for the signal asset"
    )
    pnl_percent: float | None = Field(
        default=None, description="Open PnL percentage versus the tracked entry price"
    )
    is_open_position: bool = Field(
        default=False,
        description="True when the signal already maps to an active open BUY position",
    )
    breakdown: ConfidenceBreakdown | None = Field(
        default=None, description="Optional confidence composition details"
    )


class SignalListResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "signals": [],
                "total": 0,
                "cached_at": "2026-03-26T12:05:00Z",
                "is_stale": False,
                "available_assets": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            }
        }
    )

    signals: list[Signal] = Field(default_factory=list)
    total: int = Field(ge=0)
    cached_at: datetime | None = Field(
        default=None, description="Last successful Binance fetch timestamp"
    )
    is_stale: bool = Field(default=False, description="True when stale cached data was served")
    available_assets: list[str] = Field(
        default_factory=list, description="Assets available for filtering"
    )
