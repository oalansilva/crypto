import inspect
import logging
from typing import Any, Dict, List

try:
    import talib as ta  # type: ignore
except Exception:  # pragma: no cover
    ta = None  # type: ignore


logger = logging.getLogger(__name__)


TA_LIB_CATEGORIES = {
    "trend": ["ema", "sma", "wma", "dema", "tema", "adx", "cci", "roc", "sar", "mom"],
    "momentum": ["rsi", "stoch", "stochf", "macd", "ppo", "willr", "mfi"],
    "volatility": ["bbands", "atr", "natr"],
    "volume": ["obv", "ad", "adosc", "mfi"],
    "price_transform": ["ema", "sma", "wma", "dema", "tema"],
}

PARAM_ALIASES = {
    "timeperiod": "length",
    "timeperiod2": "timeperiod2",
    "fastperiod": "fast",
    "slowperiod": "slow",
    "signalperiod": "signal",
    "nbdevup": "std",
    "nbdevdn": "std",
    "fastk_period": "k",
    "fastd_period": "d",
    "slowk_period": "smooth_k",
    "slowd_period": "d",
}

SKIP_PARAMS = {
    "close",
    "open",
    "high",
    "low",
    "volume",
    "open_",
    "high_",
    "low_",
    "close_",
    "volume_",
    "real",
    "timeperiod2",
    "timeperiod",
    "offset",
    "drift",
    "scalar",
    "mamode",
    "t3",
    "sma",
    "kwargs",
    "talib",
}


def _simplify_type(annotation):
    """Simplifies complex type hints into string representations for JSON."""
    if annotation == inspect.Parameter.empty:
        return "any"

    s = str(annotation)
    if "Union" in s:
        if "int" in s and "float" in s:
            return "number"
        if "int" in s:
            return "int"
        if "float" in s:
            return "float"
        if "str" in s:
            return "string"
        return "any"

    if "int" in s:
        return "int"
    if "float" in s:
        return "float"
    if "str" in s:
        return "string"
    if "bool" in s:
        return "bool"
    return "any"


def _extract_default(param_name: str, param: inspect.Parameter):
    default = param.default
    standard = {
        "length": 14,
        "fast": 12,
        "slow": 26,
        "signal": 9,
        "std": 2,
        "period": 10,
        "lookback": 14,
        "k": 14,
        "d": 3,
        "smooth_k": 3,
        "lower": 30,
        "upper": 70,
        "offset": 0,
    }
    if default == inspect.Parameter.empty or default is None:
        return standard.get(param_name, None)
    if isinstance(default, (int, float, str, bool)):
        return default
    return str(default)


def _to_param_name(raw_name: str) -> str:
    return PARAM_ALIASES.get(raw_name, raw_name)


def _param_name_already_exists(params: List[Dict[str, Any]], name: str) -> bool:
    return any(p.get("name") == name for p in params)


def _derive_params_for_indicator(indicator_name: str) -> List[str]:
    indicator_name = indicator_name.lower()
    if indicator_name in {
        "ema",
        "sma",
        "wma",
        "dema",
        "tema",
        "atr",
        "adx",
        "cci",
        "rsi",
        "willr",
        "mfi",
        "obv",
        "natr",
        "ad",
        "adosc",
    }:
        return ["length"]
    if indicator_name == "macd":
        return ["fast", "slow", "signal"]
    if indicator_name in {"stoch", "stochf"}:
        return ["k", "d", "smooth_k"]
    if indicator_name == "bbands":
        return ["length", "std"]
    return ["length"]


def get_all_indicators_metadata():
    """
    Introspects TA-Lib functions to return a structured dictionary of available
    indicators by category.
    """
    metadata: Dict[str, List[Dict[str, Any]]] = {}

    if ta is None:
        logger.info("TA-Lib not available; returning fallback metadata map")

    category_map = TA_LIB_CATEGORIES
    if ta is not None and isinstance(getattr(ta, "Category", None), dict):
        runtime_map = getattr(ta, "Category")
        if runtime_map:
            category_map = {k: list(v) for k, v in runtime_map.items() if v}

    for category, indicators in category_map.items():
        metadata[category] = []

        for name in indicators:
            if not ta:
                # Fallback path when TA-Lib is unavailable.
                pass
            elif not hasattr(ta, name):
                # If a runtime TA map advertises an unknown indicator, ignore it.
                continue

            if not ta:
                params = []
                for mapped_name in _derive_params_for_indicator(name):
                    default = _extract_default(
                        mapped_name,
                        inspect.Parameter(
                            mapped_name, inspect.Parameter.POSITIONAL_OR_KEYWORD, default=0
                        ),
                    )
                    if default is None:
                        continue
                    params.append({"name": mapped_name, "type": "number", "default": default})

                metadata[category].append(
                    {
                        "id": name,
                        "name": name.upper(),
                        "category": category,
                        "description": "TA-Lib compatible indicator",
                        "params": params,
                    }
                )
                continue

            func = getattr(ta, name)
            if not callable(func):
                continue

            try:
                sig = inspect.signature(func)
                doc = inspect.getdoc(func) or ""
                summary = doc.split("\n")[0] if doc else ""

                params = []
                for param_name, param in sig.parameters.items():
                    normalized_name = _to_param_name(param_name)
                    if (
                        param_name.lower() in SKIP_PARAMS
                        or normalized_name in SKIP_PARAMS
                        or param.kind
                        in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                    ):
                        continue

                    if _param_name_already_exists(params, normalized_name):
                        continue

                    default = _extract_default(normalized_name, param)
                    if default is None:
                        continue

                    params.append(
                        {
                            "name": normalized_name,
                            "type": _simplify_type(param.annotation),
                            "default": default,
                        }
                    )

                metadata[category].append(
                    {
                        "id": name,
                        "name": name.upper(),
                        "category": category,
                        "description": summary,
                        "params": params,
                    }
                )

            except Exception as e:  # pragma: no cover
                logger.debug("Failed to inspect %s: %s", name, e)
                continue

    from app.schemas.indicator_params import INDICATOR_SCHEMAS

    for category in metadata.values():
        for indicator in category:
            name = indicator["id"].lower()
            if name in INDICATOR_SCHEMAS:
                schema = INDICATOR_SCHEMAS[name]
                manual_params = []
                for p_name, p_schema in schema.parameters.items():
                    p_type = "string"
                    if isinstance(p_schema.default, int):
                        p_type = "int"
                    elif isinstance(p_schema.default, float):
                        p_type = "float"
                    elif isinstance(p_schema.default, bool):
                        p_type = "bool"

                    manual_params.append(
                        {
                            "name": p_name,
                            "type": p_type,
                            "default": p_schema.default,
                            "description": p_schema.description,
                        }
                    )

                indicator["params"] = manual_params

    return metadata
