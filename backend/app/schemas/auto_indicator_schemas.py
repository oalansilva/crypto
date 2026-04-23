"""
Auto-generate indicator schemas from TA-Lib inspection.

This module builds `IndicatorSchema` objects from the metadata returned by
`get_all_indicators_metadata()` and keeps manual parameter definitions as source
of truth when present.
"""

from typing import Dict, Any, Optional

from app.schemas.indicator_params import IndicatorSchema, ParameterSchema, OptimizationRange, INDICATOR_SCHEMAS
from app.services.pandas_ta_inspector import get_all_indicators_metadata


# Default optimization ranges by parameter name pattern
DEFAULT_PARAM_RANGES = {
    "length": OptimizationRange(min=7, max=50, step=1),
    "period": OptimizationRange(min=7, max=50, step=1),
    "fast": OptimizationRange(min=6, max=18, step=1),
    "slow": OptimizationRange(min=20, max=32, step=1),
    "signal": OptimizationRange(min=6, max=12, step=1),
    "k": OptimizationRange(min=10, max=20, step=1),
    "d": OptimizationRange(min=2, max=5, step=1),
    "smooth_k": OptimizationRange(min=1, max=5, step=1),
    "std": OptimizationRange(min=1.5, max=3.0, step=0.1),
    "lower_std": OptimizationRange(min=1.5, max=3.0, step=0.1),
    "upper_std": OptimizationRange(min=1.5, max=3.0, step=0.1),
    "overbought": OptimizationRange(min=65, max=80, step=1),
    "oversold": OptimizationRange(min=20, max=35, step=1),
    "signal_length": OptimizationRange(min=10, max=20, step=1),
    "adxr_length": OptimizationRange(min=10, max=20, step=1),
}


# Default values by parameter name (market standards)
DEFAULT_PARAM_VALUES = {
    "length": 14,
    "period": 14,
    "fast": 12,
    "slow": 26,
    "signal": 9,
    "k": 14,
    "d": 3,
    "smooth_k": 3,
    "std": 2.0,
    "overbought": 70,
    "oversold": 30,
    "signal_length": 14,
    "adxr_length": 14,
}


MARKET_STANDARDS = {
    "length": "Common values: 9, 14, 21, 50, 200. Range 7-50 covers short to medium-term.",
    "period": "Common values: 9, 14, 21, 50. Standard period for most indicators.",
    "fast": "Most traders use 12. Range 6-18 covers fast to moderate speeds.",
    "slow": "Most traders use 26. Range 20-32 covers standard variations.",
    "signal": "Most traders use 9. Range 6-12 covers common signal periods.",
    "k": "Most traders use 14. Range 10-20 is commonly tested.",
    "d": "Most traders use 3. Range 2-5 for signal smoothing.",
    "smooth_k": "Most traders use 3. Range 1-5 for stochastic smoothing.",
    "std": "Most traders use 2.0. Range 1.5-3.0 covers tight to wide bands.",
    "overbought": "Most traders use 70. Some use 80 for stronger signals.",
    "oversold": "Most traders use 30. Some use 20 for stronger signals.",
}


# Parameters to skip (not useful for optimization)
SKIP_PARAMS = {
    "close",
    "open",
    "high",
    "low",
    "volume",
    "offset",
    "drift",
    "kwargs",
    "mamode",
    "ddof",
    "presma",
    "prenan",
    "scalar",
    "tvmode",
    "c",
    "adjust",
    "sma",
    "fillna",
    "fill_method",
    "lower_std",
    "upper_std",
}


def _build_parameter_schema(param_name: str, value: Any) -> ParameterSchema:
    param_range = DEFAULT_PARAM_RANGES.get(param_name)
    return ParameterSchema(
        default=value,
        optimization_range=param_range,
        market_standard=MARKET_STANDARDS.get(
            param_name, f"Parameter for {param_name.replace('_', ' ').upper()} indicator"
        ),
        description=f"{param_name.replace('_', ' ').title()} parameter",
    )


def generate_indicator_schema(indicator_name: str) -> Optional[IndicatorSchema]:
    """
    Auto-generate an IndicatorSchema for a TA-Lib indicator.

    Args:
        indicator_name: Name of the indicator (e.g., 'ema', 'rsi', 'macd')
    Returns:
        IndicatorSchema if successful, None if indicator not found or no params.
    """
    name = str(indicator_name or "").strip().lower()
    if name in INDICATOR_SCHEMAS:
        return INDICATOR_SCHEMAS[name]

    all_metadata = get_all_indicators_metadata()
    for indicators in all_metadata.values():
        for indicator in indicators:
            if indicator.get("id", "").lower() != name:
                continue

            parameters: Dict[str, ParameterSchema] = {}
            for param in indicator.get("params", []):
                param_name = param.get("name")
                if not param_name or param_name in SKIP_PARAMS:
                    continue

                default = param.get("default", DEFAULT_PARAM_VALUES.get(param_name))
                if default is None:
                    continue

                # Preserve known manual defaults when inspector metadata changes.
                default = DEFAULT_PARAM_VALUES.get(param_name, default)
                parameters[param_name] = _build_parameter_schema(param_name, default)

            if not parameters:
                return None
            return IndicatorSchema(name=indicator["name"], parameters=parameters)

    return None


def get_all_auto_schemas() -> Dict[str, IndicatorSchema]:
    """Generate schemas for common TA-Lib indicators."""
    common_indicators = [
        "ema",
        "sma",
        "wma",
        "dema",
        "tema",
        "rsi",
        "stoch",
        "stochf",
        "stochrsi",
        "macd",
        "ppo",
        "apo",
        "bbands",
        "kc",
        "donchian",
        "atr",
        "natr",
        "adx",
        "aroon",
        "cci",
        "mfi",
        "willr",
        "obv",
        "cmf",
        "vwap",
    ]

    schemas: Dict[str, IndicatorSchema] = {}
    for indicator_name in common_indicators:
        schema = generate_indicator_schema(indicator_name)
        if schema:
            schemas[indicator_name] = schema

    return schemas

