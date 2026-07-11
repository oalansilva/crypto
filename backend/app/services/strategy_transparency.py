"""Derive safe public strategy manifests from executable combo configuration."""

from __future__ import annotations

import math
import re
from copy import deepcopy
from typing import Any, Iterable

import pandas as pd

from app.schemas.strategy_transparency import (
    IndicatorPoint,
    IndicatorReference,
    StrategyIndicatorTransparency,
    StrategyLogicBlock,
    StrategyTransparency,
)
from app.services.strategy_descriptions import (
    PUBLIC_STRATEGY_DESCRIPTIONS,
    PUBLIC_STRATEGY_DISPLAY_NAMES,
    normalize_strategy_key,
)
from app.strategies.combos.combo_strategy import ComboStrategy

_INDICATOR_META: dict[str, dict[str, Any]] = {
    "ema": {
        "label": "EMA",
        "function": "Mostra a direção recente com maior peso nos preços atuais.",
        "panel": "price",
        "scale": "price",
        "color": "#fcd535",
    },
    "sma": {
        "label": "SMA",
        "function": "Suaviza o preço para tornar a tendência mais legível.",
        "panel": "price",
        "scale": "price",
        "color": "#74b9ff",
    },
    "rsi": {
        "label": "RSI",
        "function": "Compara força compradora e vendedora para medir o ritmo do movimento.",
        "panel": "oscillator",
        "scale": "oscillator",
        "color": "#a970ff",
    },
    "adx": {
        "label": "ADX",
        "function": "Mede a intensidade da tendência, sem definir sua direção.",
        "panel": "oscillator",
        "scale": "oscillator",
        "color": "#ff9f43",
    },
    "roc": {
        "label": "ROC",
        "function": "Mede a variação percentual do preço ao longo do período configurado.",
        "panel": "oscillator",
        "scale": "percent",
        "color": "#00d2d3",
    },
    "macd": {
        "label": "MACD",
        "function": "Compara médias para acompanhar direção e mudança de momentum.",
        "panel": "macd",
        "scale": "oscillator",
        "color": "#54a0ff",
    },
    "bbands": {
        "label": "Bandas de Bollinger",
        "function": "Mostra a faixa dinâmica de volatilidade ao redor do preço.",
        "panel": "price",
        "scale": "price",
        "color": "#c8d6e5",
    },
    "bollinger": {
        "label": "Bandas de Bollinger",
        "function": "Mostra a faixa dinâmica de volatilidade ao redor do preço.",
        "panel": "price",
        "scale": "price",
        "color": "#c8d6e5",
    },
    "atr": {
        "label": "ATR",
        "function": "Mede a amplitude recente do mercado para contextualizar volatilidade e risco.",
        "panel": "atr",
        "scale": "price",
        "color": "#ff6b6b",
    },
    "volume_sma": {
        "label": "Média de volume",
        "function": "Compara o volume atual com sua participação média recente.",
        "panel": "volume",
        "scale": "volume",
        "color": "#10ac84",
    },
}

_OUTPUT_ROLES = {
    "_upper": ("Banda superior", "#ff9f43"),
    "_middle": ("Banda central", "#c8d6e5"),
    "_lower": ("Banda inferior", "#54a0ff"),
    "_macd": ("Linha MACD", "#54a0ff"),
    "_signal": ("Linha de sinal", "#ff9f43"),
    "_histogram": ("Histograma", "#10ac84"),
}

_MOVING_AVERAGE_ROLE_COLORS = {
    "short": "#f6465d",
    "medium": "#ff9f43",
    "long": "#3b82f6",
}
_MOVING_AVERAGE_ROLE_TOKENS = {
    "short": ("short", "fast", "curta", "rapida", "rápida"),
    "medium": ("medium", "mid", "intermediate", "intermediaria", "intermediária"),
    "long": ("long", "slow", "longa", "lenta"),
}


def _public_parameters(indicator: dict[str, Any]) -> dict[str, Any]:
    params = indicator.get("params")
    if not isinstance(params, dict):
        return {}
    return {
        str(key): value
        for key, value in params.items()
        if isinstance(value, (int, float, bool)) and not isinstance(value, complex)
    }


def _effective_indicators(
    template_data: dict[str, Any], effective_parameters: dict[str, Any] | None
) -> list[dict[str, Any]]:
    indicators = deepcopy(template_data.get("indicators") or [])
    overrides = effective_parameters if isinstance(effective_parameters, dict) else {}
    for indicator in indicators:
        params = indicator.get("params")
        if not isinstance(params, dict):
            params = {}
            indicator["params"] = params
        alias = str(indicator.get("alias") or indicator.get("type") or "").strip()
        ind_type = str(indicator.get("type") or "").strip().lower()
        for param_key in list(params):
            candidates = (f"{alias}_{param_key}", f"{ind_type}_{alias}")
            for candidate in candidates:
                if candidate in overrides:
                    params[param_key] = overrides[candidate]
                    break
    return indicators


def _logic_mentions(logic: str, tokens: Iterable[str]) -> bool:
    lowered = str(logic or "").lower()
    return any(
        re.search(rf"(?<![a-z0-9_]){re.escape(str(token).lower())}(?![a-z0-9_])", lowered)
        for token in tokens
        if token
    )


def _references(ind_type: str) -> list[IndicatorReference]:
    if ind_type == "rsi":
        return [
            IndicatorReference(value=30, label="Sobrevenda"),
            IndicatorReference(value=70, label="Sobrecompra"),
        ]
    if ind_type == "adx":
        return [IndicatorReference(value=20, label="Tendência ganhando força")]
    if ind_type in {"roc", "macd"}:
        return [IndicatorReference(value=0, label="Linha zero")]
    return []


def _output_label(base: str, column: str) -> tuple[str, str | None]:
    lowered = column.lower()
    for suffix, (role, color) in _OUTPUT_ROLES.items():
        if lowered.endswith(suffix):
            return f"{base} — {role}", color
    return base, None


def _moving_average_period(indicator: StrategyIndicatorTransparency) -> float | None:
    for key in ("length", "period", "window"):
        value = indicator.parameters.get(key)
        try:
            period = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(period) and period > 0:
            return period
    return None


def _moving_average_role(indicator: StrategyIndicatorTransparency) -> str | None:
    identity = " ".join([indicator.key, indicator.label, *indicator.execution_columns]).lower()
    for role, tokens in _MOVING_AVERAGE_ROLE_TOKENS.items():
        if any(
            re.search(rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])", identity) for token in tokens
        ):
            return role
    return None


def normalize_strategy_transparency_colors(
    manifest: StrategyTransparency,
) -> StrategyTransparency:
    """Apply stable semantic colors to moving averages, including stored legacy manifests."""

    moving_averages = [
        indicator
        for indicator in manifest.indicators
        if indicator.type.lower() in {"ema", "sma"} and indicator.panel == "price"
    ]
    unresolved: list[StrategyIndicatorTransparency] = []
    for indicator in moving_averages:
        role = _moving_average_role(indicator)
        if role:
            indicator.color = _MOVING_AVERAGE_ROLE_COLORS[role]
        else:
            unresolved.append(indicator)

    ranked = sorted(
        (
            (period, indicator)
            for indicator in moving_averages
            if (period := _moving_average_period(indicator)) is not None
        ),
        key=lambda item: item[0],
    )
    period_counts: dict[float, int] = {}
    for period, _indicator in ranked:
        period_counts[period] = period_counts.get(period, 0) + 1
    distinct_periods = sorted(period_counts)
    if len(distinct_periods) > 1:
        shortest = distinct_periods[0]
        longest = distinct_periods[-1]
        for period, indicator in ranked:
            if indicator not in unresolved or period_counts[period] > 1:
                continue
            role = "short" if period == shortest else "long" if period == longest else "medium"
            indicator.color = _MOVING_AVERAGE_ROLE_COLORS[role]
    return manifest


def _unavailable(strategy_key: str, timeframe: str | None, reason: str) -> StrategyTransparency:
    return StrategyTransparency(
        status="unavailable",
        strategy_key=strategy_key,
        timeframe=timeframe,
        unavailable_reason=reason,
    )


def build_strategy_transparency(
    strategy_name: Any,
    template_data: dict[str, Any] | None,
    *,
    effective_parameters: dict[str, Any] | None = None,
    timeframe: str | None = None,
    dataframe: pd.DataFrame | None = None,
) -> StrategyTransparency:
    """Build a manifest without exposing raw logic or diagnostic columns."""

    key = normalize_strategy_key(strategy_name)
    if key not in PUBLIC_STRATEGY_DISPLAY_NAMES or key not in PUBLIC_STRATEGY_DESCRIPTIONS:
        return _unavailable(key, timeframe, "Identidade pública específica não cadastrada.")
    if not isinstance(template_data, dict) or not isinstance(template_data.get("indicators"), list):
        return _unavailable(key, timeframe, "Configuração executada não pôde ser comprovada.")

    entry_logic = str(template_data.get("entry_logic") or "")
    exit_logic = str(template_data.get("exit_logic") or "")
    indicators: list[StrategyIndicatorTransparency] = []
    seen_columns: set[str] = set()

    for indicator in _effective_indicators(template_data, effective_parameters):
        ind_type = str(indicator.get("type") or "").lower()
        meta = _INDICATOR_META.get(ind_type)
        if not meta:
            continue
        columns = ComboStrategy._required_columns(indicator)
        alias = str(indicator.get("alias") or "")
        logic_tokens = [alias, ind_type, *columns]
        participation: list[str] = []
        if _logic_mentions(entry_logic, logic_tokens):
            participation.append("entry")
        if _logic_mentions(exit_logic, logic_tokens):
            participation.append("exit")
        if ind_type == "atr":
            participation.append("risk")
        if not participation:
            continue

        for column in columns:
            normalized_column = str(column).lower()
            # ComboStrategy exposes compatibility MACD aliases after canonical outputs.
            if normalized_column in seen_columns or normalized_column.startswith(
                ("macds_", "macdh_")
            ):
                continue
            seen_columns.add(normalized_column)
            label, role_color = _output_label(meta["label"], str(column))
            indicators.append(
                StrategyIndicatorTransparency(
                    key=normalize_strategy_key(column),
                    type=ind_type,
                    label=label,
                    parameters=_public_parameters(indicator),
                    function=meta["function"],
                    panel=meta["panel"],
                    scale=meta["scale"],
                    color=role_color or meta["color"],
                    participation=list(dict.fromkeys(participation)),
                    references=_references(ind_type),
                    execution_columns=[str(column)],
                    series_status="unavailable",
                    unavailable_reason="Série timestampada ainda não disponível.",
                )
            )

    if not indicators:
        return _unavailable(
            key, timeframe, "Nenhum indicador executado pôde ser resolvido com segurança."
        )

    public_params: dict[str, Any] = {}
    for indicator in indicators:
        for param_key, value in indicator.parameters.items():
            public_params[f"{indicator.key}_{param_key}"] = value
    stop_loss = (effective_parameters or {}).get("stop_loss", template_data.get("stop_loss"))
    if isinstance(stop_loss, dict):
        stop_loss = stop_loss.get("default")
    if isinstance(stop_loss, (int, float)):
        public_params["stop_loss"] = stop_loss

    manifest = StrategyTransparency(
        status="available",
        strategy_key=key,
        display_name=PUBLIC_STRATEGY_DISPLAY_NAMES[key],
        description=PUBLIC_STRATEGY_DESCRIPTIONS[key],
        timeframe=timeframe,
        parameters=public_params,
        indicators=indicators,
        logic_blocks=[
            StrategyLogicBlock(
                participation="entry",
                description="A entrada combina os indicadores marcados como entrada.",
            ),
            StrategyLogicBlock(
                participation="exit",
                description="A saída combina os indicadores marcados como saída.",
            ),
            StrategyLogicBlock(
                participation="risk",
                description="O risco usa o stop configurado para limitar a exposição.",
            ),
        ],
    )
    normalize_strategy_transparency_colors(manifest)
    if dataframe is not None:
        attach_timestamped_series(manifest, dataframe, timeframe=timeframe)
    return manifest


def attach_timestamped_series(
    manifest: StrategyTransparency,
    dataframe: pd.DataFrame,
    *,
    timeframe: str | None,
) -> StrategyTransparency:
    """Attach finite points by dataframe timestamp, only for declared columns."""

    if manifest.timeframe and timeframe and manifest.timeframe != timeframe:
        manifest.status = "timeframe_mismatch"
        manifest.unavailable_reason = "As séries disponíveis pertencem a outro timeframe."
        for indicator in manifest.indicators:
            indicator.series_status = "timeframe_mismatch"
            indicator.series = []
            indicator.unavailable_reason = manifest.unavailable_reason
        return manifest
    if dataframe is None or dataframe.empty:
        return manifest

    frame = dataframe.copy()
    if "timestamp_utc" in frame.columns:
        timestamps = pd.to_datetime(frame["timestamp_utc"], utc=True, errors="coerce")
    elif isinstance(frame.index, pd.DatetimeIndex):
        timestamps = pd.to_datetime(frame.index, utc=True, errors="coerce")
    else:
        return manifest

    for indicator in manifest.indicators:
        column = next((col for col in indicator.execution_columns if col in frame.columns), None)
        if column is None:
            indicator.unavailable_reason = "A execução não produziu a coluna declarada."
            continue
        points: list[IndicatorPoint] = []
        for timestamp, raw_value in zip(timestamps, frame[column], strict=False):
            if pd.isna(timestamp) or pd.isna(raw_value):
                continue
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                continue
            if not math.isfinite(value):
                continue
            points.append(IndicatorPoint(timestamp_utc=timestamp.isoformat(), value=value))
        if points:
            indicator.series = points
            indicator.series_status = "available"
            indicator.unavailable_reason = None
        else:
            indicator.unavailable_reason = "A série não contém pontos finitos timestampados."
    return manifest


def build_strategy_transparency_from_serialized(
    strategy_name: Any,
    template_data: dict[str, Any] | None,
    *,
    effective_parameters: dict[str, Any] | None,
    timeframe: str | None,
    candles: Any,
    indicator_data: Any,
) -> StrategyTransparency:
    """Build series for a new result only when arrays match its source candle timestamps."""

    manifest = build_strategy_transparency(
        strategy_name,
        template_data,
        effective_parameters=effective_parameters,
        timeframe=timeframe,
    )
    if not isinstance(candles, list) or not isinstance(indicator_data, dict) or not candles:
        return manifest
    timestamps = [item.get("timestamp_utc") if isinstance(item, dict) else None for item in candles]
    frame_data: dict[str, Any] = {"timestamp_utc": timestamps}
    for indicator in manifest.indicators:
        column = indicator.execution_columns[0] if indicator.execution_columns else ""
        values = indicator_data.get(column)
        if isinstance(values, list) and len(values) == len(timestamps):
            frame_data[column] = values
    return attach_timestamped_series(manifest, pd.DataFrame(frame_data), timeframe=timeframe)


def build_strategy_transparency_from_candles(
    strategy_name: Any,
    template_data: dict[str, Any] | None,
    *,
    effective_parameters: dict[str, Any] | None,
    timeframe: str | None,
    candles: Any,
) -> StrategyTransparency:
    """Calculate only declared indicators over timestamped OHLCV candles; never generate signals."""

    manifest = build_strategy_transparency(
        strategy_name,
        template_data,
        effective_parameters=effective_parameters,
        timeframe=timeframe,
    )
    if manifest.status != "available" or not isinstance(template_data, dict):
        return manifest
    if not isinstance(candles, list) or not candles:
        return manifest

    rows: list[dict[str, Any]] = []
    timestamps: list[pd.Timestamp] = []
    for candle in candles:
        if not isinstance(candle, dict):
            continue
        timestamp = pd.to_datetime(candle.get("timestamp_utc"), utc=True, errors="coerce")
        if pd.isna(timestamp):
            continue
        row: dict[str, Any] = {}
        for key in ("open", "high", "low", "close", "volume"):
            if key in candle:
                row[key] = pd.to_numeric(candle.get(key), errors="coerce")
        if "close" not in row or pd.isna(row["close"]):
            continue
        rows.append(row)
        timestamps.append(timestamp)
    if not rows:
        return manifest

    frame = pd.DataFrame(rows, index=pd.DatetimeIndex(timestamps, name="timestamp_utc"))
    frame = frame[~frame.index.duplicated(keep="last")].sort_index()
    try:
        strategy = ComboStrategy(
            indicators=_effective_indicators(template_data, effective_parameters),
            entry_logic=str(template_data.get("entry_logic") or ""),
            exit_logic=str(template_data.get("exit_logic") or ""),
            derived_features=template_data.get("derived_features"),
        )
        calculated = strategy.calculate_indicators(frame)
    except Exception:
        return manifest
    return attach_timestamped_series(manifest, calculated, timeframe=timeframe)


def transparency_matrix() -> list[dict[str, str]]:
    """Auditable identity matrix used by drift tests and operational inspection."""

    return [
        {
            "strategy_key": key,
            "display_name": PUBLIC_STRATEGY_DISPLAY_NAMES[key],
            "description": description,
        }
        for key, description in sorted(PUBLIC_STRATEGY_DESCRIPTIONS.items())
        if key in PUBLIC_STRATEGY_DISPLAY_NAMES
    ]
