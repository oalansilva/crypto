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
    is_readonly: bool = False
    indicators: List[IndicatorConfig]
    entry_logic: str
    exit_logic: str
    stop_loss: Dict[str, Any] = Field(default_factory=lambda: {"default": 0.015})
    optimization_schema: Optional[Dict[str, Any]] = Field(None, description="Optimization ranges for parameters")


class ComboBacktestRequest(BaseModel):
    """Request to run a combo strategy backtest."""
    template_name: str = Field(..., description="Name of the combo template")
    symbol: str = Field(..., description="Trading pair (e.g., BTC/USDT)")
    timeframe: str = Field(..., description="Timeframe (e.g., 1h, 4h)")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Custom parameter values")
    stop_loss: Optional[float] = Field(None, description="Stop loss percentage")
    deep_backtest: bool = Field(True, description="Enable Deep Backtesting with 15m intraday precision (default: True for 1D strategies)")
    initial_capital: float = Field(100, description="Initial capital in USD for metrics calculation (default: $100, TradingView-style)")


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
    execution_mode: str = Field(default="fast_1d", description="Execution mode: 'fast_1d' or 'deep_15m'")


class ComboOptimizationRequest(BaseModel):
    """Request to run combo strategy optimization."""
    template_name: str
    symbol: str
    timeframe: str = Field(default="1h")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    deep_backtest: bool = Field(
        default=True,
        description="Use Deep Backtesting (15m precision) for realistic stop-loss simulation"
    )
    custom_ranges: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Custom optimization ranges for parameters"
    )
    initial_capital: float = Field(100, description="Initial capital in USD for metrics calculation (default: $100, TradingView-style)")


class ComboOptimizationResponse(BaseModel):
    """Response from combo strategy optimization."""
    job_id: str
    template_name: str
    symbol: str
    timeframe: str
    stages: List[Dict[str, Any]]
    best_parameters: Dict[str, Any]
    best_metrics: Dict[str, Any]
    # Complete backtest data for visualization
    trades: List[Dict[str, Any]] = Field(default_factory=list)
    candles: List[Dict[str, Any]] = Field(default_factory=list)
    indicator_data: Dict[str, List[Optional[float]]] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)  # Alias for best_parameters


class UpdateTemplateRequest(BaseModel):
    """Request to update a combo template."""
    description: Optional[str] = Field(None, description="Template description")
    optimization_schema: Optional[Dict[str, Any]] = Field(None, description="Optimization ranges for parameters")
    template_data: Optional[Dict[str, Any]] = Field(None, description="Full template data (for advanced editing)")


class CloneTemplateRequest(BaseModel):
    """Request to clone a combo template."""
    new_name: str = Field(..., description="Name for the cloned template", min_length=3, max_length=100)


class ComboBatchBacktestRequest(BaseModel):
    """Request to run batch backtests for multiple symbols."""
    template_name: str = Field(..., description="Name of the combo template")
    symbols: List[str] = Field(..., min_length=1, description="List of symbols to run (e.g. ['BTC/USDT', 'ETH/USDT'])")
    timeframe: str = Field(default="1d")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period_type: Optional[str] = Field(None, description="'6m' | '2y' | 'all'; used for skip logic")
    deep_backtest: bool = Field(
        default=True,
        description="Use Deep Backtesting (15m precision) for realistic stop-loss simulation"
    )
    custom_ranges: Optional[Dict[str, Dict[str, Any]]] = Field(None)
    initial_capital: float = Field(100)


class ComboBatchBacktestResponse(BaseModel):
    """Response from starting a batch backtest job."""
    job_id: str = Field(..., description="Job ID to poll for progress")


class ComboBatchProgressResponse(BaseModel):
    """Progress and result of a batch backtest job."""
    job_id: str
    status: str = Field(..., description="running | completed | failed")
    processed: int = 0
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = Field(0, description="Skipped (already in favorites)")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Per-symbol errors")
    started_at: Optional[str] = None
    elapsed_sec: float = 0.0
    estimated_remaining_sec: Optional[float] = None
    current_symbol: Optional[str] = Field(None, description="Symbol currently being optimized")


class TemplateListResponse(BaseModel):
    """Response listing available combo templates."""
    prebuilt: List[Dict[str, Any]]
    examples: List[Dict[str, Any]]
    custom: List[Dict[str, Any]]
