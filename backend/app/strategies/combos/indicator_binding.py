"""Explicit, immutable producer binding for the approved original template."""

from dataclasses import dataclass


class IndicatorReferenceError(ValueError):
    code = "indicator_reference_error"


@dataclass(frozen=True)
class IndicatorBinding:
    policy: str
    producers: tuple

    def context(self, indicators, frame):
        values = {}
        for symbol, index, kind in self.producers:
            try:
                indicator = indicators[index]
                length = int(indicator["params"]["length"])
            except (IndexError, KeyError, TypeError, ValueError, OverflowError) as exc:
                raise IndicatorReferenceError(
                    "indicator_reference_error: missing/invalid effective producer"
                ) from exc
            if indicator.get("type", "").lower() != kind or indicator.get("alias"):
                raise IndicatorReferenceError(
                    "indicator_reference_error: producer identity changed"
                )
            columns = [f"{kind.upper()}_{length}"]
            column = columns[0]
            # A physical bound symbol is valid only if this producer owns it.
            if symbol in frame and symbol != column:
                raise IndicatorReferenceError(
                    "indicator_reference_error: conflicting symbol origin"
                )
            if column not in frame or list(frame.columns).count(column) != 1:
                raise IndicatorReferenceError(
                    "indicator_reference_error: missing/duplicate effective series"
                )
            for other_index, other in enumerate(indicators):
                if other_index == index:
                    continue
                from .combo_strategy import ComboStrategy

                if column in ComboStrategy._required_columns(
                    other
                ) or symbol in ComboStrategy._required_columns(other):
                    raise IndicatorReferenceError("indicator_reference_error: duplicate producer")
            values[symbol] = frame[column]
        return values


def capture_binding(template_name, original_indicators, derived_features=()):
    """Call before overrides. Other templates retain their existing semantics."""
    if template_name != "long_ma_pullback_rsi_adx":
        return None
    if any(
        isinstance(item, dict) and item.get("name") in ("RSI_14", "ADX_14")
        for item in (derived_features or ())
    ):
        raise IndicatorReferenceError("indicator_reference_error: conflicting derived producer")
    producers = []
    for kind in ("rsi", "adx"):
        matches = [
            (index, item)
            for index, item in enumerate(original_indicators)
            if str(item.get("type", "")).lower() == kind
        ]
        if len(matches) != 1:
            raise IndicatorReferenceError(
                "indicator_reference_error: ambiguous original declaration"
            )
        index, item = matches[0]
        if item.get("alias") or item.get("params", {}).get("length") != 14:
            raise IndicatorReferenceError(
                "indicator_reference_error: incompatible original declaration"
            )
        producers.append((f"{kind.upper()}_14", index, kind))
    return IndicatorBinding("long_ma_pullback_rsi_adx/effective-indicators-v1", tuple(producers))
