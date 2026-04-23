"""
Dynamic Indicator Schema Generator

Builds optimization schemas from metadata introspection and a curated list of
known defaults.
"""

from typing import Dict, Any, Optional

from app.services.pandas_ta_inspector import get_all_indicators_metadata


KNOWN_DEFAULTS = {
    "rsi": {"length": 14},
    "macd": {"fast": 12, "slow": 26, "signal": 9},
    "stoch": {"k": 14, "d": 3, "smooth_k": 3},
    "adx": {"length": 14},
    "cci": {"length": 14},
    "mfi": {"length": 14},
    "willr": {"length": 14},
    "sma": {"length": 20},
    "ema": {"length": 12},
    "wma": {"length": 20},
    "dema": {"length": 20},
    "tema": {"length": 20},
    "bbands": {"length": 20, "std": 2.0},
    "atr": {"length": 14},
    "natr": {"length": 14},
    "obv": {},
    "cmf": {"length": 20},
}

IGNORED_PARAMS = [
    "offset",
    "drift",
    "scalar",
    "mamode",
    "talib",
    "tvmode",
    "use_nans",
    "as_mode",
    "ddof",
    "presma",
    "prenan",
    "adjust",
    "sma",
    "fillna",
    "fill_method",
    "lower_std",
    "upper_std",
]


RISK_MANAGEMENT_SCHEMA = {
    "stop_loss": {
        "default": 0.015,
        "optimization_range": {"min": 0.005, "max": 0.05, "step": 0.005},
        "market_standard": "Most traders use 1-2%. Range 0.5%-5% covers conservative to aggressive.",
        "description": "Stop-loss percentage (decimal format)",
    },
    "stop_gain": {
        "default": None,
        "options": [None, 0.01, 0.02, 0.03, 0.04, 0.05, 0.075, 0.10],
        "market_standard": "Many traders don't use take-profit. Test all options to find best.",
        "description": "Take-profit percentage (optional, None = no take-profit)",
    },
}


def generate_optimization_range(param_name: str, param_type: str, default_value: Any) -> Optional[Dict[str, float]]:
    param_name = str(param_name or "").lower()
    param_lower = param_name.lower()
    if param_type not in ["int", "float", "number"]:
        if any(
            key in param_lower
            for key in [
                "length",
                "period",
                "window",
                "fast",
                "slow",
                "signal",
                "std",
                "mult",
                "factor",
                "percent",
                "threshold",
            ]
        ):
            pass
        else:
            return None

    try:
        default = float(default_value)
    except (ValueError, TypeError):
        return None

    if any(
        keyword in param_lower
        for keyword in [
            "period",
            "length",
            "window",
            "span",
            "fast",
            "slow",
            "signal",
            "k",
            "d",
            "smooth",
        ]
    ):
        base = int(default)
        if base <= 5:
            return {"min": max(2, base - 2), "max": base + 5, "step": 1}
        if base <= 20:
            return {"min": max(5, base - 5), "max": base + 10, "step": 1}
        if base <= 50:
            return {"min": max(10, base - 10), "max": base + 20, "step": 2}
        return {"min": max(20, base - 20), "max": base + 40, "step": 5}

    if any(keyword in param_lower for keyword in ["multiplier", "factor", "mult", "std"]):
        if default < 1:
            return {"min": max(0.1, default - 0.3), "max": default + 0.5, "step": 0.1}
        return {"min": max(0.5, default - 1.0), "max": default + 2.0, "step": 0.1}

    if any(
        keyword in param_lower
        for keyword in ["threshold", "overbought", "oversold", "upper", "lower"]
    ):
        return {"min": max(0, int(default - 15)), "max": min(100, int(default + 15)), "step": 1}

    if any(keyword in param_lower for keyword in ["percent", "pct", "ratio"]):
        return {"min": max(0, default - 0.1), "max": default + 0.1, "step": 0.01}

    if isinstance(default_value, int) or (isinstance(default_value, str) and str(default_value).isdigit()):
        return {"min": max(1, int(default * 0.5)), "max": int(default * 1.5), "step": 1}

    return {"min": max(0.1, default * 0.5), "max": default * 1.5, "step": 0.1}


def generate_market_standard(param_name: str, default_value: Any) -> str:
    param_lower = str(param_name or "").lower()
    if any(k in param_lower for k in ["period", "length", "fast", "slow"]):
        return f"Most traders use {default_value}. Standard range tests sensitivity around this value."
    if "multiplier" in param_lower or "std" in param_lower:
        return f"Standard is {default_value}. Adjust based on volatility."
    if "overbought" in param_lower:
        return f"Standard Overbought is {default_value}. Higher = fewer but stronger signals."
    if "oversold" in param_lower:
        return f"Standard Oversold is {default_value}. Lower = fewer but stronger signals."
    return f"Default: {default_value}. Optimize to find best value."


def get_dynamic_indicator_schema(strategy_name: str) -> Optional[Dict[str, Any]]:
    """Generate schema from TA-Lib metadata for a specific indicator/strategy."""
    normalized = str(strategy_name or "").lower()

    if normalized == "cruzamentomedias":
        return {
            "name": "CRUZAMENTOMEDIAS",
            "parameters": {
                "media_curta": {
                    "default": 6,
                    "description": "EMA period for short moving average",
                    "market_standard": "Most traders use 6-12 for short-term EMA.",
                    "optimization_range": {"min": 3, "max": 15, "step": 1},
                },
                "media_longa": {
                    "default": 38,
                    "description": "SMA period for long moving average",
                    "market_standard": "Most traders use 30-50 for long-term SMA.",
                    "optimization_range": {"min": 25, "max": 60, "step": 2},
                },
                "media_inter": {
                    "default": 21,
                    "description": "SMA period for intermediate moving average",
                    "market_standard": "Most traders use 20-30 for intermediate SMA.",
                    "optimization_range": {"min": 15, "max": 35, "step": 1},
                },
            },
            "risk_management": RISK_MANAGEMENT_SCHEMA,
        }

    if normalized == "emarsivolume":
        return {
            "name": "EMA_RSI_VOLUME",
            "parameters": {
                "ema_fast": {
                    "default": 50,
                    "description": "Fast EMA period for pullback entries",
                    "market_standard": "Most traders use 50 for fast EMA. Range 20-100 covers short to medium-term.",
                    "optimization_range": {"min": 20, "max": 100, "step": 10},
                },
                "ema_slow": {
                    "default": 200,
                    "description": "Slow EMA period for trend filter",
                    "market_standard": "Most traders use 200 for trend filter. This is the industry standard.",
                    "optimization_range": {"min": 100, "max": 300, "step": 50},
                },
                "rsi_period": {
                    "default": 14,
                    "description": "RSI calculation period",
                    "market_standard": "Most traders use 14. Range 10-20 is commonly tested.",
                    "optimization_range": {"min": 10, "max": 20, "step": 2},
                },
                "rsi_min": {
                    "default": 40,
                    "description": "Minimum RSI for buy signal",
                    "market_standard": "40 indicates healthy pullback (not oversold). Range 30-45 tested.",
                    "optimization_range": {"min": 30, "max": 45, "step": 5},
                },
                "rsi_max": {
                    "default": 50,
                    "description": "Maximum RSI for buy signal",
                    "market_standard": "50 is neutral momentum. Range 45-60 covers pullback to neutral zone.",
                    "optimization_range": {"min": 45, "max": 60, "step": 5},
                },
            },
            "risk_management": RISK_MANAGEMENT_SCHEMA,
        }

    if normalized == "fibonacciema":
        return {
            "name": "FIBONACCI_EMA",
            "parameters": {
                "ema_period": {
                    "default": 200,
                    "description": "EMA period for trend filter",
                    "market_standard": "Most traders use 200 for trend filter. This is the industry standard.",
                    "optimization_range": {"min": 100, "max": 300, "step": 50},
                },
                "swing_lookback": {
                    "default": 20,
                    "description": "Bars to look back for swing detection",
                    "market_standard": "20 bars captures meaningful swings without being too sensitive.",
                    "optimization_range": {"min": 10, "max": 40, "step": 5},
                },
                "fib_level_1": {
                    "default": 0.5,
                    "description": "First Fibonacci retracement level",
                    "market_standard": "0.5 (50%) is a psychological level widely watched by traders.",
                    "optimization_range": {"min": 0.382, "max": 0.618, "step": 0.05},
                },
                "fib_level_2": {
                    "default": 0.618,
                    "description": "Second Fibonacci retracement level",
                    "market_standard": "0.618 (golden ratio) is the institutional favorite.",
                    "optimization_range": {"min": 0.5, "max": 0.786, "step": 0.05},
                },
                "level_tolerance": {
                    "default": 0.005,
                    "description": "Tolerance for price touching Fibonacci level",
                    "market_standard": "0.5% tolerance balances precision and flexibility.",
                    "optimization_range": {"min": 0.001, "max": 0.01, "step": 0.001},
                },
            },
            "risk_management": RISK_MANAGEMENT_SCHEMA,
        }

    all_indicators = get_all_indicators_metadata()
    for _category, indicators in all_indicators.items():
        for indicator in indicators:
            if indicator.get("id", "").lower() != normalized:
                continue

            schema = {
                "name": indicator["name"],
                "parameters": {},
                "risk_management": RISK_MANAGEMENT_SCHEMA,
            }

            known_defaults = KNOWN_DEFAULTS.get(normalized, {})

            for param in indicator.get("params", []):
                param_name = param.get("name")
                if not param_name:
                    continue
                if param_name in IGNORED_PARAMS and param_name not in known_defaults:
                    continue

                default_value = known_defaults.get(param_name, param.get("default"))
                if default_value is None:
                    continue

                opt_range = generate_optimization_range(param_name, param.get("type", "int"), default_value)
                param_schema = {
                    "default": default_value,
                    "description": f"{param_name} parameter for {indicator['name']}",
                    "market_standard": generate_market_standard(param_name, default_value),
                }
                if opt_range:
                    param_schema["optimization_range"] = opt_range
                schema["parameters"][param_name] = param_schema

            return schema

    return None

