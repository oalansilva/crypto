"""
Auto-generate indicator schemas from pandas-ta introspection.

This module automatically creates IndicatorSchema objects for all pandas-ta indicators
by introspecting their function signatures and applying sensible defaults.
"""

import inspect
import pandas_ta as ta
from typing import Dict, Any, Optional
from app.schemas.indicator_params import (
    IndicatorSchema,
    ParameterSchema,
    OptimizationRange
)


# Default optimization ranges by parameter name pattern
DEFAULT_PARAM_RANGES = {
    # Length-based parameters (most common)
    'length': OptimizationRange(min=7, max=50, step=1),
    'period': OptimizationRange(min=7, max=50, step=1),
    
    # MACD-specific
    'fast': OptimizationRange(min=6, max=18, step=1),
    'slow': OptimizationRange(min=20, max=32, step=1),
    'signal': OptimizationRange(min=6, max=12, step=1),
    
    # Stochastic
    'k': OptimizationRange(min=10, max=20, step=1),
    'd': OptimizationRange(min=2, max=5, step=1),
    'smooth_k': OptimizationRange(min=1, max=5, step=1),
    
    # Bollinger Bands
    'std': OptimizationRange(min=1.5, max=3.0, step=0.1),
    'lower_std': OptimizationRange(min=1.5, max=3.0, step=0.1),
    'upper_std': OptimizationRange(min=1.5, max=3.0, step=0.1),
    
    # RSI thresholds
    'overbought': OptimizationRange(min=65, max=80, step=1),
    'oversold': OptimizationRange(min=20, max=35, step=1),
    
    # ADX
    'signal_length': OptimizationRange(min=10, max=20, step=1),
    'adxr_length': OptimizationRange(min=10, max=20, step=1),
}


# Default values by parameter name (ALL MARKET STANDARDS)
DEFAULT_PARAM_VALUES = {
    # Length/Period parameters
    'length': 14,  # Market standard for most oscillators (RSI, ADX, ATR, etc.)
    'period': 14,  # Same as length
    
    # MACD parameters (Appel's original settings)
    'fast': 12,  # Fast EMA for MACD
    'slow': 26,  # Slow EMA for MACD
    'signal': 9,  # Signal line for MACD
    
    # Stochastic parameters
    'k': 14,  # %K period (market standard)
    'd': 3,  # %D smoothing (market standard)
    'smooth_k': 3,  # %K smoothing (market standard)
    
    # Bollinger Bands parameters (Bollinger's original settings)
    'std': 2.0,  # Standard deviation multiplier
    
    # RSI/Oscillator thresholds
    'overbought': 70,  # Standard overbought level
    'oversold': 30,  # Standard oversold level
    
    # ADX parameters
    'signal_length': 14,  # ADX signal length
    'adxr_length': 14,  # ADXR length
}


# Market standard descriptions
MARKET_STANDARDS = {
    'length': "Common values: 9, 14, 21, 50, 200. Range 7-50 covers short to medium-term.",
    'period': "Common values: 9, 14, 21, 50. Standard period for most indicators.",
    'fast': "Most traders use 12. Range 6-18 covers fast to moderate speeds.",
    'slow': "Most traders use 26. Range 20-32 covers standard variations.",
    'signal': "Most traders use 9. Range 6-12 covers common signal periods.",
    'k': "Most traders use 14. Range 10-20 is commonly tested.",
    'd': "Most traders use 3. Range 2-5 for signal smoothing.",
    'smooth_k': "Most traders use 3. Range 1-5 for stochastic smoothing.",
    'std': "Most traders use 2.0. Range 1.5-3.0 covers tight to wide bands.",
    'overbought': "Most traders use 70. Some use 80 for stronger signals.",
    'oversold': "Most traders use 30. Some use 20 for stronger signals.",
}


# Parameters to skip (not useful for optimization)
SKIP_PARAMS = {
    'close', 'open', 'high', 'low', 'volume',  # OHLCV data
    'talib', 'offset', 'drift', 'kwargs',       # Technical params
    'mamode', 'ddof', 'presma', 'prenan',       # Mode/preprocessing
    'scalar', 'tvmode', 'c',                     # Misc technical
    'adjust', 'sma', 'fillna', 'fill_method',   # EMA/SMA preprocessing
    'lower_std', 'upper_std',                   # Skip redundant BBands params (use std)
}


def generate_indicator_schema(indicator_name: str) -> Optional[IndicatorSchema]:
    """
    Auto-generate an IndicatorSchema for a pandas-ta indicator.
    
    Args:
        indicator_name: Name of the indicator (e.g., 'ema', 'rsi', 'macd')
        
    Returns:
        IndicatorSchema if successful, None if indicator not found or error
    """
    try:
        # Get the indicator function
        if not hasattr(ta, indicator_name):
            return None
            
        indicator_func = getattr(ta, indicator_name)
        
        # Skip if not callable or is a class
        if not callable(indicator_func) or inspect.isclass(indicator_func):
            return None
        
        # Get function signature
        sig = inspect.signature(indicator_func)
        
        # Build parameters dict
        parameters = {}
        
        if indicator_name == 'bbands':
            print(f"DEBUG: Generating schema for BBANDS. SKIP_PARAMS: {SKIP_PARAMS}")
        
        for param_name, param in sig.parameters.items():
            # Skip unwanted parameters
            if param_name in SKIP_PARAMS:
                if indicator_name == 'bbands':
                    print(f"DEBUG: Skipping param {param_name}")
                continue
            
            # Get default value
            default = param.default
            if default == inspect.Parameter.empty:
                continue  # Skip required params (OHLCV data)
            
            # Skip None defaults that aren't in our known params
            if default is None and param_name not in DEFAULT_PARAM_VALUES:
                continue
            
            # Use our default if available, otherwise use function's default
            param_default = DEFAULT_PARAM_VALUES.get(param_name, default)
            
            # Get optimization range if available
            opt_range = DEFAULT_PARAM_RANGES.get(param_name)
            
            # Get market standard description
            market_std = MARKET_STANDARDS.get(
                param_name,
                f"Parameter for {indicator_name.upper()} indicator"
            )
            
            # Create parameter schema
            parameters[param_name] = ParameterSchema(
                default=param_default,
                optimization_range=opt_range,
                market_standard=market_std,
                description=f"{param_name.replace('_', ' ').title()} parameter"
            )
        
        # Only create schema if we have parameters to optimize
        if not parameters:
            return None
        
        return IndicatorSchema(
            name=indicator_name.upper(),
            parameters=parameters
        )
        
    except Exception as e:
        print(f"Error generating schema for {indicator_name}: {e}")
        return None


def get_all_auto_schemas() -> Dict[str, IndicatorSchema]:
    """
    Generate schemas for all common pandas-ta indicators.
    
    Returns:
        Dictionary mapping indicator names to their schemas
    """
    # List of common indicators to auto-generate
    common_indicators = [
        'ema', 'sma', 'wma', 'dema', 'tema', 'hma',  # Moving averages
        'rsi', 'stoch', 'stochf', 'stochrsi',         # Oscillators
        'macd', 'ppo', 'apo',                         # MACD family
        'bbands', 'kc', 'donchian',                   # Bands
        'atr', 'natr',                                # Volatility
        'adx', 'aroon', 'cci', 'mfi', 'willr',       # Trend/Momentum
        'obv', 'cmf', 'vwap',                         # Volume
    ]
    
    schemas = {}
    
    for indicator_name in common_indicators:
        schema = generate_indicator_schema(indicator_name)
        if schema:
            schemas[indicator_name] = schema
    
    return schemas


if __name__ == "__main__":
    # Test the auto-generation
    print("Testing Auto-Schema Generation")
    print("="*60)
    
    # Test EMA
    ema_schema = generate_indicator_schema('ema')
    if ema_schema:
        print(f"\nEMA Schema:")
        print(f"  Name: {ema_schema.name}")
        print(f"  Parameters: {list(ema_schema.parameters.keys())}")
        for param_name, param_schema in ema_schema.parameters.items():
            print(f"    - {param_name}: default={param_schema.default}, range={param_schema.optimization_range}")
    
    # Test all common indicators
    print(f"\n\n{'='*60}")
    print("All Auto-Generated Schemas:")
    print(f"{'='*60}")
    
    all_schemas = get_all_auto_schemas()
    for ind_name, schema in all_schemas.items():
        params = list(schema.parameters.keys())
        print(f"{ind_name:12s}: {', '.join(params)}")
    
    print(f"\nTotal schemas generated: {len(all_schemas)}")
