"""
Pydantic schemas for combo strategy API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class IndicatorConfig(BaseModel):
    """Configuration for a single indicator in a combo."""
    type: str = Field(..., description="Indicator type (ema, sma, rsi, etc.)")
    alias: Optional[str] = Field(None, description="Alias for the indicator")
    params: Dict[str, Any] = Field(default_factory=dict, description="Indicator parameters")
    optimization_range: Optional[Dict[str, Any]] = Field(None, description="Optimization range (min, max, step)")


class ComboTemplateMetadata(BaseModel):
    """Metadata for a combo template."""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    is_example: bool = False
    is_prebuilt: bool = False
    indicators: List[IndicatorConfig]
    entry_logic: str
    exit_logic: str
    stop_loss: Dict[str, Any] = Field(default_factory=lambda: {"default": 0.015})


class ComboBacktestRequest(BaseModel):
    """Request to run a combo strategy backtest."""
    template_name: str = Field(..., description="Name of the combo template")
    symbol: str = Field(..., description="Trading pair (e.g., BTC/USDT)")
    timeframe: str = Field(..., description="Timeframe (e.g., 1h, 4h)")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Custom parameter values")
    stop_loss: Optional[float] = Field(None, description="Stop loss percentage")


class ComboBacktestResponse(BaseModel):
    """Response from combo strategy backtest."""
    template_name: str
    symbol: str
    timeframe: str
    parameters: Dict[str, Any]
    metrics: Dict[str, Any]
    trades: List[Dict[str, Any]]
    indicator_data: Dict[str, List[Optional[float]]]  # Allow None for NaN values
    candles: List[Dict[str, Any]] = Field(default_factory=list, description="OHLCV data for chart")


class ComboOptimizationRequest(BaseModel):
    """Request to run combo strategy optimization."""
    template_name: str
    symbol: str
    timeframe: str = Field(default="1h")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    custom_ranges: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Custom optimization ranges for parameters"
    )


class ComboOptimizationResponse(BaseModel):
    """Response from combo strategy optimization."""
    job_id: str
    template_name: str
    symbol: str
    stages: List[Dict[str, Any]]
    best_parameters: Dict[str, Any]
    best_metrics: Dict[str, Any]


class TemplateListResponse(BaseModel):
    """Response listing available combo templates."""
    prebuilt: List[Dict[str, str]]
    examples: List[Dict[str, str]]
    custom: List[Dict[str, str]]
