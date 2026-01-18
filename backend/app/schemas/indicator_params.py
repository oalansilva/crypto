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
            optimization_range=OptimizationRange(min=6, max=16, step=1),
            market_standard="Most traders use 9. Range 6-16 covers common variations.",
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


# CRUZAMENTOMEDIAS Schema
CRUZAMENTOMEDIAS_SCHEMA = IndicatorSchema(
    name="CRUZAMENTOMEDIAS",
    parameters={
        "media_curta": ParameterSchema(
            default=6,
            optimization_range=OptimizationRange(min=3, max=15, step=1),
            market_standard="Most traders use 6-12 for short-term EMA.",
            description="EMA period for short moving average"
        ),
        "media_longa": ParameterSchema(
            default=38,
            optimization_range=OptimizationRange(min=25, max=60, step=2),
            market_standard="Most traders use 30-50 for long-term SMA.",
            description="SMA period for long moving average"
        ),
        "media_inter": ParameterSchema(
            default=21,
            optimization_range=OptimizationRange(min=15, max=35, step=1),
            market_standard="Most traders use 20-30 for intermediate SMA.",
            description="SMA period for intermediate moving average"
        )
    }
)


# EMA RSI VOLUME Schema
EMA_RSI_VOLUME_SCHEMA = IndicatorSchema(
    name="EMA_RSI_VOLUME",
    parameters={
        "ema_fast": ParameterSchema(
            default=50,
            optimization_range=OptimizationRange(min=20, max=100, step=10),
            market_standard="Most traders use 50 for fast EMA. Range 20-100 covers short to medium-term.",
            description="Fast EMA period for pullback entries"
        ),
        "ema_slow": ParameterSchema(
            default=200,
            optimization_range=OptimizationRange(min=100, max=300, step=50),
            market_standard="Most traders use 200 for trend filter. This is the industry standard.",
            description="Slow EMA period for trend filter (only trade above this)"
        ),
        "rsi_period": ParameterSchema(
            default=14,
            optimization_range=OptimizationRange(min=10, max=20, step=2),
            market_standard="Most traders use 14. Range 10-20 is commonly tested.",
            description="RSI calculation period"
        ),
        "rsi_min": ParameterSchema(
            default=40,
            optimization_range=OptimizationRange(min=30, max=45, step=5),
            market_standard="40 indicates healthy pullback (not oversold). Range 30-45 tested.",
            description="Minimum RSI for buy signal (pullback zone lower bound)"
        ),
        "rsi_max": ParameterSchema(
            default=50,
            optimization_range=OptimizationRange(min=45, max=60, step=5),
            market_standard="50 is neutral momentum. Range 45-60 covers pullback to neutral zone.",
            description="Maximum RSI for buy signal (pullback zone upper bound)"
        )
    }
)


# FIBONACCI EMA Schema
FIBONACCI_EMA_SCHEMA = IndicatorSchema(
    name="FIBONACCI_EMA",
    parameters={
        "ema_period": ParameterSchema(
            default=200,
            optimization_range=OptimizationRange(min=100, max=300, step=50),
            market_standard="Most traders use 200 for trend filter. This is the industry standard.",
            description="EMA period for trend filter (only trade above this)"
        ),
        "swing_lookback": ParameterSchema(
            default=20,
            optimization_range=OptimizationRange(min=10, max=40, step=5),
            market_standard="20 bars captures meaningful swings without being too sensitive.",
            description="Bars to look back for swing high/low detection"
        ),
        "fib_level_1": ParameterSchema(
            default=0.5,
            optimization_range=OptimizationRange(min=0.382, max=0.618, step=0.05),
            market_standard="0.5 (50%) is a psychological level widely watched by traders.",
            description="First Fibonacci retracement level"
        ),
        "fib_level_2": ParameterSchema(
            default=0.618,
            optimization_range=OptimizationRange(min=0.5, max=0.786, step=0.05),
            market_standard="0.618 (golden ratio) is the institutional favorite for pullback entries.",
            description="Second Fibonacci retracement level (golden ratio)"
        ),
        "level_tolerance": ParameterSchema(
            default=0.005,
            optimization_range=OptimizationRange(min=0.001, max=0.01, step=0.001),
            market_standard="0.5% tolerance balances precision and flexibility for level detection.",
            description="Tolerance for price touching Fibonacci level (0.005 = 0.5%)"
        )
    }
)


# ICHIMOKU Schema
ICHIMOKU_SCHEMA = IndicatorSchema(
    name="ICHIMOKU",
    parameters={
        "tenkan": ParameterSchema(
            default=9,
            optimization_range=OptimizationRange(min=7, max=12, step=1),
            market_standard="Most traders use 9 (Conversion Line). Range 7-12 covers common variations.",
            description="Tenkan-sen (Conversion Line) period - short-term trend"
        ),
        "kijun": ParameterSchema(
            default=26,
            optimization_range=OptimizationRange(min=20, max=32, step=2),
            market_standard="Most traders use 26 (Base Line). Standard value from Hosoda's original formula.",
            description="Kijun-sen (Base Line) period - medium-term trend"
        ),
        "senkou": ParameterSchema(
            default=52,
            optimization_range=OptimizationRange(min=44, max=60, step=4),
            market_standard="Most traders use 52 (Leading Span B). Represents 2x Kijun period.",
            description="Senkou Span B period - long-term trend and cloud boundary"
        )
    }
)


# Registry of all indicator schemas
INDICATOR_SCHEMAS: Dict[str, IndicatorSchema] = {
    "macd": MACD_SCHEMA,
    "rsi": RSI_SCHEMA,
    "bollinger": BOLLINGER_SCHEMA,
    "cruzamentomedias": CRUZAMENTOMEDIAS_SCHEMA,
    "emarsivolume": EMA_RSI_VOLUME_SCHEMA,
    "fibonacciema": FIBONACCI_EMA_SCHEMA,
    "ichimoku": ICHIMOKU_SCHEMA,
}


def get_indicator_schema(strategy_name: str) -> Optional[IndicatorSchema]:
    """
    Get indicator schema by strategy name.
    
    First checks manual schemas (MACD, RSI, Bollinger), then falls back to auto-generation
    for all other pandas-ta indicators.
    
    Args:
        strategy_name: Name of the strategy (case-insensitive)
        
    Returns:
        IndicatorSchema if found, None otherwise
    """
    strategy_lower = strategy_name.lower()
    
    # Check manual schemas first (these have custom market standards)
    if strategy_lower in INDICATOR_SCHEMAS:
        return INDICATOR_SCHEMAS[strategy_lower]
    
    # Auto-generate schema for pandas-ta indicators
    from app.schemas.auto_indicator_schemas import generate_indicator_schema
    return generate_indicator_schema(strategy_lower)



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
