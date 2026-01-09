"""
Dynamic Indicator Schema Generator

Generates optimization schemas dynamically from pandas_ta metadata.
This replaces hardcoded schemas and works for ALL pandas_ta indicators.
"""

from typing import Dict, Any, Optional
from app.services.pandas_ta_inspector import get_all_indicators_metadata



# Valid Defaults for common indicators - ALL MARKET STANDARDS
# We ONLY list parameters here that we explicitly want to support/show defaults for.
# This also acts as an "AllowList" for noise parameters if they are listed here.
KNOWN_DEFAULTS = {
    # Momentum Indicators (Market Standards)
    "rsi": {"length": 14},  # Market standard: 14 periods (most common)
    "rsi_reversal": {"rsi_length": 14, "rsi_u": 70, "rsi_d": 30},  # Standard RSI thresholds
    "macd": {"fast": 12, "slow": 26, "signal": 9},  # Market standard: 12/26/9 (Appel's original)
    "stoch": {"k": 14, "d": 3, "smooth_k": 3},  # Market standard: 14/3/3
    "adx": {"length": 14, "lensig": 14},  # Market standard: 14 periods (Wilder's original)
    "cci": {"length": 14, "c": 0.015},  # Market standard: 14 periods, 0.015 constant
    "mfi": {"length": 14},  # Market standard: 14 periods
    "willr": {"length": 14},  # Market standard: 14 periods
    
    # Trend/Moving Average Indicators (Market Standards)
    "sma": {"length": 20},  # Market standard: 20 for short-term, 50/200 for long-term
    "ema": {"length": 12},  # Market standard: 12 or 26 (MACD components), 9 for short-term
    "hma": {"length": 20},  # Market standard: 20 periods
    "wma": {"length": 20},  # Market standard: 20 periods
    "dema": {"length": 20},  # Market standard: 20 periods
    "tema": {"length": 20},  # Market standard: 20 periods
    
    # Volatility Indicators (Market Standards)
    "bbands": {"length": 20, "std": 2.0},  # Market standard: 20 period, 2 std dev (Bollinger's original)
    "atr": {"length": 14},  # Market standard: 14 periods (Wilder's original)
    "natr": {"length": 14},  # Market standard: 14 periods (normalized ATR)
    "kc": {"length": 20, "scalar": 2},  # Market standard: 20 period, 2x ATR
    
    # Volume Indicators (Market Standards)
    "obv": {},  # No parameters - cumulative volume
    "cmf": {"length": 20},  # Market standard: 20 periods
    "vwap": {}  # No parameters - intraday only
}

# Parameters to hide by default (Noise) unless explicitly in KNOWN_DEFAULTS
IGNORED_PARAMS = [
    'offset', 'drift', 'scalar', 'mamode', 'talib', 'tvmode', 
    'use_nans', 'as_mode', 'ddof', 'presma', 'prenan',
    'adjust', 'sma', 'fillna', 'fill_method',
    'lower_std', 'upper_std'
]

def generate_optimization_range(param_name: str, param_type: str, default_value: Any) -> Optional[Dict[str, float]]:
    """
    Generate optimization range based on parameter name and type.
    Now more robust to missing/unknown types.
    """
    param_lower = param_name.lower()
    
    # Robust Type Inference: If type is unknown but name implies logic
    if param_type not in ['int', 'float', 'number']:
        if any(k in param_lower for k in ['length', 'period', 'window', 'fast', 'slow', 'signal', 'std', 'mult', 'factor', 'percent', 'threshold']):
            # Assume it's optimizable
            pass
        else:
            return None
    
    # Must have a value to base range on
    if default_value is None:
        return None
    
    try:
        default = float(default_value)
    except (ValueError, TypeError):
        return None
    
    # Period/Length parameters (most common)
    if any(keyword in param_lower for keyword in ['period', 'length', 'window', 'span', 'fast', 'slow', 'signal', 'k', 'd', 'smooth']):
        default_int = int(default)
        if default_int <= 5:
            return {"min": max(2, default_int - 2), "max": default_int + 5, "step": 1}
        elif default_int <= 20:
            return {"min": max(5, default_int - 5), "max": default_int + 10, "step": 1}
        elif default_int <= 50:
            return {"min": max(10, default_int - 10), "max": default_int + 20, "step": 2}
        else:
            return {"min": max(20, default_int - 20), "max": default_int + 40, "step": 5}
    
    # Multiplier/Factor parameters
    if any(keyword in param_lower for keyword in ['multiplier', 'factor', 'mult', 'std']):
        if default < 1:
            return {"min": max(0.1, default - 0.3), "max": default + 0.5, "step": 0.1}
        else:
            return {"min": max(0.5, default - 1.0), "max": default + 2.0, "step": 0.1}
    
    # Threshold parameters (0-100 usually)
    if any(keyword in param_lower for keyword in ['threshold', 'overbought', 'oversold', 'upper', 'lower', 'rsi_u', 'rsi_d']):
        return {"min": max(0, int(default - 15)), "max": min(100, int(default + 15)), "step": 1}
    
    # Percentage parameters
    if any(keyword in param_lower for keyword in ['percent', 'pct', 'ratio']):
        return {"min": max(0, default - 0.1), "max": default + 0.1, "step": 0.01}
    
    # Default numeric fallback
    if isinstance(default_value, int) or (isinstance(default_value, str) and default_value.isdigit()):
        return {"min": max(1, int(default * 0.5)), "max": int(default * 1.5), "step": 1}
    else:
        return {"min": max(0.1, default * 0.5), "max": default * 1.5, "step": 0.1}


def generate_market_standard(param_name: str, default_value: Any) -> str:
    """Generate market standard description."""
    param_lower = param_name.lower()
    
    if any(k in param_lower for k in ['period', 'length', 'fast', 'slow']):
        return f"Most traders use {default_value}. Standard range tests sensitivity around this value."
    elif 'multiplier' in param_lower or 'std' in param_lower:
        return f"Standard is {default_value}. Adjust based on volatility."
    elif 'overbought' in param_lower or 'rsi_u' in param_lower:
        return f"Standard Overbought is {default_value}. Higher = fewer but stronger signals."
    elif 'oversold' in param_lower or 'rsi_d' in param_lower:
        return f"Standard Oversold is {default_value}. Lower = fewer but stronger signals."
    else:
        return f"Default: {default_value}. Optimize to find best value."


def get_dynamic_indicator_schema(strategy_name: str) -> Optional[Dict[str, Any]]:
    """Generates schema with fallback for known defaults."""
    # Check if it's CRUZAMENTOMEDIAS first
    if strategy_name.lower() == 'cruzamentomedias':
        return {
            "name": "CRUZAMENTOMEDIAS",
            "parameters": {
                "media_curta": {
                    "default": 6,
                    "description": "EMA period for short moving average",
                    "market_standard": "Most traders use 6-12 for short-term EMA.",
                    "optimization_range": {"min": 3, "max": 15, "step": 1}
                },
                "media_longa": {
                    "default": 38,
                    "description": "SMA period for long moving average",
                    "market_standard": "Most traders use 30-50 for long-term SMA.",
                    "optimization_range": {"min": 25, "max": 60, "step": 2}
                },
                "media_inter": {
                    "default": 21,
                    "description": "SMA period for intermediate moving average",
                    "market_standard": "Most traders use 20-30 for intermediate SMA.",
                    "optimization_range": {"min": 15, "max": 35, "step": 1}
                }
            },
            "risk_management": RISK_MANAGEMENT_SCHEMA
        }
    
    # Check if it's EMA_RSI_VOLUME
    if strategy_name.lower() == 'emarsivolume':
        return {
            "name": "EMA_RSI_VOLUME",
            "parameters": {
                "ema_fast": {
                    "default": 50,
                    "description": "Fast EMA period for pullback entries",
                    "market_standard": "Most traders use 50 for fast EMA. Range 20-100 covers short to medium-term.",
                    "optimization_range": {"min": 20, "max": 100, "step": 10}
                },
                "ema_slow": {
                    "default": 200,
                    "description": "Slow EMA period for trend filter (only trade above this)",
                    "market_standard": "Most traders use 200 for trend filter. This is the industry standard.",
                    "optimization_range": {"min": 100, "max": 300, "step": 50}
                },
                "rsi_period": {
                    "default": 14,
                    "description": "RSI calculation period",
                    "market_standard": "Most traders use 14. Range 10-20 is commonly tested.",
                    "optimization_range": {"min": 10, "max": 20, "step": 2}
                },
                "rsi_min": {
                    "default": 40,
                    "description": "Minimum RSI for buy signal (pullback zone lower bound)",
                    "market_standard": "40 indicates healthy pullback (not oversold). Range 30-45 tested.",
                    "optimization_range": {"min": 30, "max": 45, "step": 5}
                },
                "rsi_max": {
                    "default": 50,
                    "description": "Maximum RSI for buy signal (pullback zone upper bound)",
                    "market_standard": "50 is neutral momentum. Range 45-60 covers pullback to neutral zone.",
                    "optimization_range": {"min": 45, "max": 60, "step": 5}
                }
            },
            "risk_management": RISK_MANAGEMENT_SCHEMA
        }
    
    # Check if it's FIBONACCI_EMA
    if strategy_name.lower() == 'fibonacciema':
        return {
            "name": "FIBONACCI_EMA",
            "parameters": {
                "ema_period": {
                    "default": 200,
                    "description": "EMA period for trend filter (only trade above this)",
                    "market_standard": "Most traders use 200 for trend filter. This is the industry standard.",
                    "optimization_range": {"min": 100, "max": 300, "step": 50}
                },
                "swing_lookback": {
                    "default": 20,
                    "description": "Bars to look back for swing high/low detection",
                    "market_standard": "20 bars captures meaningful swings without being too sensitive.",
                    "optimization_range": {"min": 10, "max": 40, "step": 5}
                },
                "fib_level_1": {
                    "default": 0.5,
                    "description": "First Fibonacci retracement level",
                    "market_standard": "0.5 (50%) is a psychological level widely watched by traders.",
                    "optimization_range": {"min": 0.382, "max": 0.618, "step": 0.05}
                },
                "fib_level_2": {
                    "default": 0.618,
                    "description": "Second Fibonacci retracement level (golden ratio)",
                    "market_standard": "0.618 (golden ratio) is the institutional favorite for pullback entries.",
                    "optimization_range": {"min": 0.5, "max": 0.786, "step": 0.05}
                },
                "level_tolerance": {
                    "default": 0.005,
                    "description": "Tolerance for price touching Fibonacci level (0.005 = 0.5%)",
                    "market_standard": "0.5% tolerance balances precision and flexibility for level detection.",
                    "optimization_range": {"min": 0.001, "max": 0.01, "step": 0.001}
                }
            },
            "risk_management": RISK_MANAGEMENT_SCHEMA
        }
    
    # Get all indicators from pandas_ta
    all_indicators = get_all_indicators_metadata()
    
    # Search for the indicator
    strategy_lower = strategy_name.lower()
    
    for category, indicators in all_indicators.items():
        for indicator in indicators:
            if indicator['id'].lower() == strategy_lower:
                # Found the indicator
                schema = {
                    "name": indicator['name'],
                    "parameters": {},
                    # We inject Risk Management defaults in route or service, 
                    # but here we can leave them empty/defaults for now.
                    # This function focuses on the INDICATOR parameters.
                    "risk_management": RISK_MANAGEMENT_SCHEMA
                }
                
                # Check for Known Defaults to override/fill gaps
                known_defaults = KNOWN_DEFAULTS.get(strategy_lower, {})
                
                # Generate parameter schemas
                for param in indicator['params']:
                    param_name = param['name']
                    param_type = param['type']
                    default_value = param['default']
                    
                    # --- NOISE FILTER LOGIC ---
                    # Skip parameters defined as noise, UNLESS explicitly required by known_defaults
                    if param_name in IGNORED_PARAMS and param_name not in known_defaults:
                        continue
                    
                    # 1. ALWAYS use Known Default if available (overrides pandas_ta default)
                    if param_name in known_defaults:
                        default_value = known_defaults[param_name]
                    
                    # Generate optimization range
                    opt_range = generate_optimization_range(param_name, param_type, default_value)
                    
                    # Build parameter schema
                    param_schema = {
                        "default": default_value,
                        "description": f"{param_name} parameter for {indicator['name']}",
                        "market_standard": generate_market_standard(param_name, default_value)
                    }
                    
                    if opt_range:
                        param_schema["optimization_range"] = opt_range
                    
                    schema["parameters"][param_name] = param_schema
                
                return schema
    
    return None


# Risk management schema (same for all indicators)
RISK_MANAGEMENT_SCHEMA = {
    "stop_loss": {
        "default": 0.015,
        "optimization_range": {"min": 0.005, "max": 0.05, "step": 0.005},
        "market_standard": "Most traders use 1-2%. Range 0.5%-5% covers conservative to aggressive.",
        "description": "Stop-loss percentage (decimal format)"
    },
    "stop_gain": {
        "default": None,
        "options": [None, 0.01, 0.02, 0.03, 0.04, 0.05, 0.075, 0.10],
        "market_standard": "Many traders don't use take-profit. Test all options to find best.",
        "description": "Take-profit percentage (optional, None = no take-profit)"
    }
}
