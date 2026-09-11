"""Flatten discovery promotion snapshots onto Favorites grid keys (card #897)."""

from __future__ import annotations

from typing import Any

DISCOVERY_ORIGIN_TYPES = frozenset({"discovery_sweep", "discovery"})

GRID_METRIC_KEYS = (
    "sharpe_ratio",
    "win_rate",
    "max_drawdown",
    "total_return",
    "total_return_pct",
    "total_trades",
    "profit_factor",
)

PROVENANCE_KEYS = (
    "origin_type",
    "sweep_id",
    "result_id",
    "strategy_identity_key",
    "evidence_fingerprint",
    "template_version",
    "metrics_snapshot",
    "promoted_at",
)


def is_discovery_origin(metrics: Any) -> bool:
    return isinstance(metrics, dict) and metrics.get("origin_type") in DISCOVERY_ORIGIN_TYPES


def snapshot_from_metrics(metrics: Any) -> dict[str, Any]:
    if not isinstance(metrics, dict):
        return {}
    snapshot = metrics.get("metrics_snapshot")
    return snapshot if isinstance(snapshot, dict) else {}


def _numeric(value: Any) -> float | int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value != value:  # NaN
            return None
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number:
        return None
    if number.is_integer():
        return int(number)
    return number


def _first_present(source: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in source and source[key] is not None:
            return source[key]
    return None


def grid_metrics_from_snapshot(
    snapshot: Any,
    *,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source: dict[str, Any] = {}
    if extras:
        source.update(extras)
    if isinstance(snapshot, dict):
        source.update(snapshot)

    grid: dict[str, Any] = {}
    sharpe = _numeric(_first_present(source, "sharpe_ratio", "sharpe"))
    if sharpe is not None:
        grid["sharpe_ratio"] = sharpe

    win_rate = _numeric(_first_present(source, "win_rate"))
    if win_rate is not None:
        grid["win_rate"] = win_rate

    max_drawdown = _numeric(_first_present(source, "max_drawdown"))
    if max_drawdown is None:
        max_drawdown_pct = _numeric(_first_present(source, "max_drawdown_pct"))
        if max_drawdown_pct is not None:
            max_drawdown = (
                max_drawdown_pct / 100.0 if abs(max_drawdown_pct) > 1 else max_drawdown_pct
            )
    if max_drawdown is not None:
        grid["max_drawdown"] = max_drawdown

    total_return = _numeric(_first_present(source, "total_return"))
    total_return_pct = _numeric(_first_present(source, "total_return_pct"))
    if total_return_pct is not None:
        grid["total_return_pct"] = total_return_pct
        if total_return is None:
            total_return = total_return_pct / 100.0
    if total_return is not None:
        grid["total_return"] = total_return
        if "total_return_pct" not in grid:
            grid["total_return_pct"] = total_return * 100.0

    trades = _first_present(source, "total_trades", "trades_count", "num_trades")
    if isinstance(trades, list):
        trades = None
    trades_n = _numeric(trades)
    if trades_n is not None:
        grid["total_trades"] = int(trades_n)

    profit_factor = _numeric(_first_present(source, "profit_factor"))
    if profit_factor is not None:
        grid["profit_factor"] = profit_factor

    return grid


def flatten_discovery_grid_metrics(metrics: Any) -> Any:
    """Copy snapshot numbers onto the keys the Favorites grid already reads."""
    if not isinstance(metrics, dict) or not is_discovery_origin(metrics):
        return metrics
    grid = grid_metrics_from_snapshot(snapshot_from_metrics(metrics))
    if not grid:
        return metrics
    out = dict(metrics)
    out.update(grid)
    return out


def overlay_snapshot_grid_metrics(
    metrics: Any,
    *,
    source: dict[str, Any] | None = None,
) -> Any:
    """Restore snapshot grid keys after a regenerated-trades merge."""
    origin = source if isinstance(source, dict) else metrics
    if not is_discovery_origin(origin) and not is_discovery_origin(metrics):
        return metrics
    if not isinstance(metrics, dict):
        return metrics
    snapshot = snapshot_from_metrics(origin) or snapshot_from_metrics(metrics)
    grid = grid_metrics_from_snapshot(snapshot)
    if not grid:
        return metrics
    out = dict(metrics)
    for key in PROVENANCE_KEYS:
        if isinstance(origin, dict) and key in origin:
            out[key] = origin[key]
    out.update(grid)
    return out


def result_metric_extras(result: Any) -> dict[str, Any]:
    extras: dict[str, Any] = {}
    for attr, key in (
        ("sharpe_ratio", "sharpe_ratio"),
        ("win_rate", "win_rate"),
        ("max_drawdown", "max_drawdown"),
        ("profit_factor", "profit_factor"),
        ("trades_count", "total_trades"),
    ):
        value = getattr(result, attr, None)
        if value is not None:
            extras[key] = value
    return extras


def build_promoted_favorite_metrics(result: Any, *, promoted_at: str) -> dict[str, Any]:
    snapshot = result.metrics if isinstance(result.metrics, dict) else {}
    payload: dict[str, Any] = {
        "origin_type": "discovery_sweep",
        "sweep_id": result.sweep_id,
        "result_id": result.id,
        "strategy_identity_key": result.strategy_identity_key,
        "evidence_fingerprint": result.evidence_fingerprint,
        "template_version": result.template_version,
        "parameters": result.parameters,
        "metrics_snapshot": snapshot,
        "promoted_at": promoted_at,
    }
    payload.update(grid_metrics_from_snapshot(snapshot, extras=result_metric_extras(result)))
    return payload
