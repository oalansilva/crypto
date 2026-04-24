from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

SOURCE_NAME = "chart_pattern_service"
__all__ = ["ChartPatternConfig", "detect_chart_pattern_events", "detect_chart_patterns"]


@dataclass(frozen=True)
class ChartPatternConfig:
    pivot_window: int = 2
    min_pivot_separation: int = 5
    max_pattern_width: int = 80
    max_confirmation_bars: int = 20
    price_tolerance_pct: float = 0.03
    min_neckline_depth_pct: float = 0.015
    dedupe_window_bars: int = 10


@dataclass(frozen=True)
class Pivot:
    index: int
    kind: str
    price: float


def detect_chart_patterns(
    df: pd.DataFrame,
    config: ChartPatternConfig | None = None,
) -> pd.Series:
    """
    Return a Series aligned to df.index where each row contains zero or more
    chart-pattern event dictionaries.
    """
    cfg = config or ChartPatternConfig()
    events_by_pos: list[list[dict[str, Any]]] = [[] for _ in range(len(df))]

    if df.empty:
        return pd.Series([], index=df.index, dtype=object)

    events = _detect_moving_average_crosses(df)
    events.extend(_detect_double_patterns(df, cfg))
    for event in _dedupe_events(events, cfg.dedupe_window_bars):
        events_by_pos[event.pop("_pos")].append(event)

    return pd.Series(events_by_pos, index=df.index, dtype=object)


def detect_chart_pattern_events(
    df: pd.DataFrame,
    config: ChartPatternConfig | None = None,
) -> list[list[dict[str, Any]]]:
    """Return chart-pattern events as a plain list aligned to dataframe rows."""
    return detect_chart_patterns(df, config).tolist()


def _detect_moving_average_crosses(df: pd.DataFrame) -> list[dict[str, Any]]:
    if "sma_20" not in df.columns or "sma_50" not in df.columns:
        return []

    fast = pd.to_numeric(df["sma_20"], errors="coerce")
    slow = pd.to_numeric(df["sma_50"], errors="coerce")
    close = _numeric_column(df, "close", fallback=(fast + slow) / 2)
    events: list[dict[str, Any]] = []

    for pos in range(1, len(df)):
        values = (fast.iat[pos - 1], slow.iat[pos - 1], fast.iat[pos], slow.iat[pos])
        if any(pd.isna(value) for value in values):
            continue

        previous_delta = float(values[0] - values[1])
        current_delta = float(values[2] - values[3])
        if previous_delta <= 0 < current_delta:
            events.append(
                _make_event(
                    pos=pos,
                    df=df,
                    pattern="golden_cross",
                    direction="bullish",
                    confidence=100.0,
                    reference_price=close.iat[pos],
                    dedupe_key=f"golden_cross:{pos}",
                    metadata={
                        "fast_ma": "sma_20",
                        "slow_ma": "sma_50",
                        "fast_value": values[2],
                        "slow_value": values[3],
                    },
                )
            )
        elif previous_delta >= 0 > current_delta:
            events.append(
                _make_event(
                    pos=pos,
                    df=df,
                    pattern="death_cross",
                    direction="bearish",
                    confidence=100.0,
                    reference_price=close.iat[pos],
                    dedupe_key=f"death_cross:{pos}",
                    metadata={
                        "fast_ma": "sma_20",
                        "slow_ma": "sma_50",
                        "fast_value": values[2],
                        "slow_value": values[3],
                    },
                )
            )

    return events


def _detect_double_patterns(df: pd.DataFrame, cfg: ChartPatternConfig) -> list[dict[str, Any]]:
    if not {"high", "low", "close"}.issubset(df.columns):
        return []

    high = _numeric_column(df, "high")
    low = _numeric_column(df, "low")
    close = _numeric_column(df, "close")
    pivot_highs = _find_pivots(high, kind="high", window=cfg.pivot_window)
    pivot_lows = _find_pivots(low, kind="low", window=cfg.pivot_window)

    events = _detect_double_top(df, low, close, pivot_highs, cfg)
    events.extend(_detect_double_bottom(df, high, close, pivot_lows, cfg))
    return events


def _detect_double_top(
    df: pd.DataFrame,
    low: pd.Series,
    close: pd.Series,
    pivots: list[Pivot],
    cfg: ChartPatternConfig,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for left_pos, first in enumerate(pivots):
        for second in pivots[left_pos + 1 :]:
            if not _valid_pivot_pair(first, second, cfg):
                continue

            similarity = _price_similarity(first.price, second.price)
            if similarity < 1 - cfg.price_tolerance_pct:
                continue

            neckline_values = low.iloc[first.index : second.index + 1].to_numpy(dtype=float)
            valid_neckline_values = neckline_values[np.isfinite(neckline_values)]
            if valid_neckline_values.size == 0:
                continue
            neckline_offset = int(np.nanargmin(neckline_values))
            neckline_pos = first.index + neckline_offset
            neckline = float(low.iat[neckline_pos])
            peak = max(first.price, second.price)
            depth_pct = _safe_ratio(peak - neckline, peak)
            if depth_pct < cfg.min_neckline_depth_pct:
                continue

            confirm_pos = _first_confirming_close(
                close,
                start=second.index + 1,
                end=min(len(df) - 1, second.index + cfg.max_confirmation_bars),
                threshold=neckline,
                direction="below",
            )
            if confirm_pos is None:
                continue

            confirmation_strength = _safe_ratio(neckline - float(close.iat[confirm_pos]), neckline)
            confidence = _double_pattern_confidence(
                similarity=similarity,
                depth_pct=depth_pct,
                confirmation_strength=confirmation_strength,
            )
            signature = f"{first.index}-{second.index}-{neckline_pos}"
            events.append(
                _make_event(
                    pos=confirm_pos,
                    df=df,
                    pattern="double_top",
                    direction="bearish",
                    confidence=confidence,
                    reference_price=close.iat[confirm_pos],
                    dedupe_key=f"double_top:bearish:{signature}",
                    metadata={
                        "first_pivot_index": first.index,
                        "second_pivot_index": second.index,
                        "first_pivot_price": first.price,
                        "second_pivot_price": second.price,
                        "neckline_index": neckline_pos,
                        "neckline": neckline,
                        "similarity": similarity,
                        "depth_pct": depth_pct,
                        "confirmation_close": close.iat[confirm_pos],
                    },
                )
            )
    return events


def _detect_double_bottom(
    df: pd.DataFrame,
    high: pd.Series,
    close: pd.Series,
    pivots: list[Pivot],
    cfg: ChartPatternConfig,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for left_pos, first in enumerate(pivots):
        for second in pivots[left_pos + 1 :]:
            if not _valid_pivot_pair(first, second, cfg):
                continue

            similarity = _price_similarity(first.price, second.price)
            if similarity < 1 - cfg.price_tolerance_pct:
                continue

            neckline_values = high.iloc[first.index : second.index + 1].to_numpy(dtype=float)
            valid_neckline_values = neckline_values[np.isfinite(neckline_values)]
            if valid_neckline_values.size == 0:
                continue
            neckline_offset = int(np.nanargmax(neckline_values))
            neckline_pos = first.index + neckline_offset
            neckline = float(high.iat[neckline_pos])
            trough = min(first.price, second.price)
            depth_pct = _safe_ratio(neckline - trough, neckline)
            if depth_pct < cfg.min_neckline_depth_pct:
                continue

            confirm_pos = _first_confirming_close(
                close,
                start=second.index + 1,
                end=min(len(df) - 1, second.index + cfg.max_confirmation_bars),
                threshold=neckline,
                direction="above",
            )
            if confirm_pos is None:
                continue

            confirmation_strength = _safe_ratio(float(close.iat[confirm_pos]) - neckline, neckline)
            confidence = _double_pattern_confidence(
                similarity=similarity,
                depth_pct=depth_pct,
                confirmation_strength=confirmation_strength,
            )
            signature = f"{first.index}-{second.index}-{neckline_pos}"
            events.append(
                _make_event(
                    pos=confirm_pos,
                    df=df,
                    pattern="double_bottom",
                    direction="bullish",
                    confidence=confidence,
                    reference_price=close.iat[confirm_pos],
                    dedupe_key=f"double_bottom:bullish:{signature}",
                    metadata={
                        "first_pivot_index": first.index,
                        "second_pivot_index": second.index,
                        "first_pivot_price": first.price,
                        "second_pivot_price": second.price,
                        "neckline_index": neckline_pos,
                        "neckline": neckline,
                        "similarity": similarity,
                        "depth_pct": depth_pct,
                        "confirmation_close": close.iat[confirm_pos],
                    },
                )
            )
    return events


def _find_pivots(series: pd.Series, *, kind: str, window: int) -> list[Pivot]:
    values = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float)
    pivots: list[Pivot] = []
    if window < 1 or len(values) < window * 2 + 1:
        return pivots

    for pos in range(window, len(values) - window):
        value = values[pos]
        if not np.isfinite(value):
            continue
        neighborhood = values[pos - window : pos + window + 1]
        if np.any(~np.isfinite(neighborhood)):
            continue
        if (
            kind == "high"
            and value == np.max(neighborhood)
            and np.count_nonzero(neighborhood == value) == 1
        ):
            pivots.append(Pivot(index=pos, kind=kind, price=float(value)))
        elif (
            kind == "low"
            and value == np.min(neighborhood)
            and np.count_nonzero(neighborhood == value) == 1
        ):
            pivots.append(Pivot(index=pos, kind=kind, price=float(value)))
    return pivots


def _valid_pivot_pair(first: Pivot, second: Pivot, cfg: ChartPatternConfig) -> bool:
    distance = second.index - first.index
    return cfg.min_pivot_separation <= distance <= cfg.max_pattern_width


def _first_confirming_close(
    close: pd.Series,
    *,
    start: int,
    end: int,
    threshold: float,
    direction: str,
) -> int | None:
    if start > end:
        return None
    for pos in range(start, end + 1):
        value = close.iat[pos]
        if pd.isna(value):
            continue
        if direction == "below" and float(value) < threshold:
            return pos
        if direction == "above" and float(value) > threshold:
            return pos
    return None


def _dedupe_events(events: list[dict[str, Any]], window: int) -> list[dict[str, Any]]:
    if window < 1:
        return sorted(
            events, key=lambda event: (event["_pos"], event["pattern"], event["direction"])
        )

    deduped: list[dict[str, Any]] = []
    last_by_key: dict[tuple[str, str], int] = {}
    seen_structures: set[str] = set()
    for event in sorted(
        events, key=lambda event: (event["_pos"], event["pattern"], event["direction"])
    ):
        structure_key = str(event.get("dedupe_key", ""))
        if structure_key in seen_structures:
            continue

        key = (str(event["pattern"]), str(event["direction"]))
        previous_pos = last_by_key.get(key)
        if previous_pos is not None and event["_pos"] - previous_pos <= window:
            continue

        seen_structures.add(structure_key)
        last_by_key[key] = int(event["_pos"])
        deduped.append(event)
    return deduped


def _double_pattern_confidence(
    *,
    similarity: float,
    depth_pct: float,
    confirmation_strength: float,
) -> float:
    similarity_score = max(0.0, min(1.0, similarity)) * 45.0
    depth_score = max(0.0, min(1.0, depth_pct / 0.08)) * 35.0
    confirmation_score = max(0.0, min(1.0, confirmation_strength / 0.03)) * 20.0
    return _clamp_confidence(similarity_score + depth_score + confirmation_score)


def _make_event(
    *,
    pos: int,
    df: pd.DataFrame,
    pattern: str,
    direction: str,
    confidence: float,
    reference_price: Any,
    dedupe_key: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "_pos": pos,
        "pattern": pattern,
        "direction": direction,
        "confidence": _clamp_confidence(confidence),
        "ts": _row_timestamp(df, pos),
        "reference_price": _json_float(reference_price),
        "source": SOURCE_NAME,
        "dedupe_key": dedupe_key,
        "metadata": _jsonify(metadata),
    }


def _row_timestamp(df: pd.DataFrame, pos: int) -> str | None:
    for column in ("ts", "timestamp", "timestamp_utc"):
        if column in df.columns:
            value = df[column].iat[pos]
            if pd.isna(value):
                return None
            parsed = pd.to_datetime(value, utc=True, errors="coerce")
            if pd.isna(parsed):
                return str(value)
            return parsed.isoformat().replace("+00:00", "Z")
    index_value = df.index[pos]
    if isinstance(index_value, (int, float, np.integer, np.floating)):
        return None
    parsed = pd.to_datetime(index_value, utc=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.isoformat().replace("+00:00", "Z")


def _numeric_column(df: pd.DataFrame, column: str, fallback: pd.Series | None = None) -> pd.Series:
    if column in df.columns:
        return pd.to_numeric(df[column], errors="coerce")
    if fallback is not None:
        return pd.to_numeric(fallback, errors="coerce")
    return pd.Series(np.nan, index=df.index, dtype=float)


def _price_similarity(first: float, second: float) -> float:
    denominator = max(abs(first), abs(second))
    if denominator <= 0:
        return 0.0
    return 1.0 - min(1.0, abs(first - second) / denominator)


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0 or not np.isfinite(denominator):
        return 0.0
    ratio = numerator / denominator
    return float(ratio) if np.isfinite(ratio) else 0.0


def _clamp_confidence(value: float) -> float:
    if not np.isfinite(value):
        return 0.0
    return round(float(max(0.0, min(100.0, value))), 2)


def _json_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    parsed = float(value)
    return parsed if np.isfinite(parsed) else None


def _jsonify(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonify(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonify(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonify(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return _json_float(value)
    if isinstance(value, float):
        return _json_float(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat().replace("+00:00", "Z")
    return value
