"""
Indicator Parameter Schemas

Defines optimization parameters and market best practices for all indicators.
Each schema includes:
- default: Default parameter value (market standard)
- optimization_range: Range to test during optimization
- market_standard: Description of common market usage
- description: Parameter description
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class OptimizationRange(BaseModel):
    """Range specification for parameter optimization"""
    min: float
    max: float
    step: float


class ParameterSchema(BaseModel):
    """Schema for a single indicator parameter"""
    default: Any
    optimization_range: Optional[OptimizationRange] = None
    options: Optional[List[Any]] = None  # For discrete options (e.g., stop-gain)
    market_standard: str
    description: str


class IndicatorSchema(BaseModel):
    """Complete schema for an indicator"""
    name: str
    parameters: Dict[str, ParameterSchema]


# MACD Indicator Schema
MACD_SCHEMA = IndicatorSchema(
    name="MACD",
    parameters={
        "fast": ParameterSchema(
            default=12,
            optimization_range=OptimizationRange(min=6, max=18, step=1),
            market_standard="Most traders use 12. 70% use values between 10-14.",
            description="Fast EMA period for MACD calculation"
        ),
        "slow": ParameterSchema(
            default=26,
            optimization_range=OptimizationRange(min=20, max=32, step=1),
            market_standard="Most traders use 26. Conservative range captures most variations.",
            description="Slow EMA period for MACD calculation"
        ),
        "signal": ParameterSchema(
            default=9,
            optimization_range=OptimizationRange(min=6, max=12, step=1),
            market_standard="Most traders use 9. Range 6-12 covers common variations.",
            description="Signal line period for MACD"
        )
    }
)


# RSI Indicator Schema
RSI_SCHEMA = IndicatorSchema(
    name="RSI",
    parameters={
        "length": ParameterSchema(
            default=14,
            optimization_range=OptimizationRange(min=10, max=20, step=1),
            market_standard="Most traders use 14. Range 10-20 is commonly tested.",
            description="RSI calculation period"
        ),
        "overbought": ParameterSchema(
            default=70,
            optimization_range=OptimizationRange(min=65, max=80, step=1),
            market_standard="Most traders use 70. Some use 80 for stronger signals.",
            description="Overbought threshold level"
        ),
        "oversold": ParameterSchema(
            default=30,
            optimization_range=OptimizationRange(min=20, max=35, step=1),
            market_standard="Most traders use 30. Some use 20 for stronger signals.",
            description="Oversold threshold level"
        )
    }
)


# Bollinger Bands Schema
BOLLINGER_SCHEMA = IndicatorSchema(
    name="Bollinger Bands",
    parameters={
        "length": ParameterSchema(
            default=20,
            optimization_range=OptimizationRange(min=15, max=25, step=1),
            market_standard="Most traders use 20. Standard deviation period.",
            description="Moving average period for Bollinger Bands"
        ),
        "std": ParameterSchema(
            default=2.0,
            optimization_range=OptimizationRange(min=1.5, max=3.0, step=0.1),
            market_standard="Most traders use 2.0. Range 1.5-3.0 covers tight to wide bands.",
            description="Standard deviation multiplier"
        )
    }
)


# Risk Management Schema
RISK_MANAGEMENT_SCHEMA = {
    "stop_loss": ParameterSchema(
        default=0.015,  # 1.5%
        optimization_range=OptimizationRange(min=0.005, max=0.05, step=0.005),
        market_standard="Most traders use 1-2%. Range 0.5%-5% covers conservative to aggressive.",
        description="Stop-loss percentage (decimal format)"
    ),
    "stop_gain": ParameterSchema(
        default=None,  # No take-profit by default
        options=[None, 0.01, 0.02, 0.03, 0.04, 0.05, 0.075, 0.10],
        market_standard="Many traders don't use take-profit. Test all options to find best.",
        description="Take-profit percentage (optional, None = no take-profit)"
    )
}


# Timeframe options (always tested in Stage 1)
TIMEFRAME_OPTIONS = ["5m", "15m", "30m", "1h", "2h", "4h", "1d"]


# Registry of all indicator schemas
INDICATOR_SCHEMAS: Dict[str, IndicatorSchema] = {
    "macd": MACD_SCHEMA,
    "rsi": RSI_SCHEMA,
    "bollinger": BOLLINGER_SCHEMA,
}


def get_indicator_schema(strategy_name: str) -> Optional[IndicatorSchema]:
    """
    Get indicator schema by strategy name.
    
    Args:
        strategy_name: Name of the strategy (case-insensitive)
        
    Returns:
        IndicatorSchema if found, None otherwise
    """
    return INDICATOR_SCHEMAS.get(strategy_name.lower())


def calculate_total_stages(indicator_schema: IndicatorSchema) -> int:
    """
    Calculate total number of optimization stages for an indicator.
    
    Formula: 1 (timeframe) + N (indicator params) + 2 (stop-loss + stop-gain)
    
    Args:
        indicator_schema: The indicator schema
        
    Returns:
        Total number of stages
    """
    return 1 + len(indicator_schema.parameters) + 2


def estimate_total_tests(indicator_schema: IndicatorSchema) -> int:
    """
    Estimate total number of tests for sequential optimization.
    
    Args:
        indicator_schema: The indicator schema
        
    Returns:
        Estimated total test count
    """
    total = len(TIMEFRAME_OPTIONS)  # Stage 1: timeframes
    
    # Indicator parameter stages
    for param in indicator_schema.parameters.values():
        if param.optimization_range:
            range_size = int((param.optimization_range.max - param.optimization_range.min) / param.optimization_range.step) + 1
            total += range_size
    
    # Stop-loss stage
    sl_param = RISK_MANAGEMENT_SCHEMA["stop_loss"]
    sl_range_size = int((sl_param.optimization_range.max - sl_param.optimization_range.min) / sl_param.optimization_range.step) + 1
    total += sl_range_size
    
    # Stop-gain stage
    sg_param = RISK_MANAGEMENT_SCHEMA["stop_gain"]
    total += len(sg_param.options)
    
    return total
