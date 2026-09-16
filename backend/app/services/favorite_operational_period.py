"""Operational favorite period after walk-forward 70/30 (card #949)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from app.services.combo_optimizer import ComboOptimizer
from app.services.favorite_backtest_refresh_service import (
    _fixed_optimization_ranges,
    _favorite_direction,
)
from app.services.market_data_providers import (
    get_market_data_provider,
    resolve_data_source_for_symbol,
    validate_data_source_timeframe,
)
from app.tasks.discovery_tasks import resolve_optimizer_date_range

logger = logging.getLogger(__name__)

OPERATIONAL_PERIOD_FLAG = "operational_period_after_walk_forward"


def uses_operational_period(metrics: Any) -> bool:
    return isinstance(metrics, dict) and metrics.get(OPERATIONAL_PERIOD_FLAG) is True


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _first_candle_iso(symbol: str, timeframe: str) -> str | None:
    try:
        data_source = validate_data_source_timeframe(
            resolve_data_source_for_symbol(symbol, None),
            timeframe,
        )
        provider = get_market_data_provider(data_source)
        end = _utcnow().date().isoformat()
        frame = provider.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since_str="2017-01-01",
            until_str=end,
        )
        if frame is None or frame.empty:
            return None
        first = frame.index.min()
        return first.date().isoformat() if hasattr(first, "date") else str(first)[:10]
    except Exception as exc:
        logger.warning("first candle lookup failed for %s %s: %s", symbol, timeframe, exc)
        return None


def resolve_chosen_period(
    *,
    period_type: str | None,
    start_date: str | None,
    end_date: str | None,
    symbol: str,
    timeframe: str,
    now: datetime | None = None,
) -> tuple[str | None, str | None, str | None]:
    """Map UI/sweep period to persisted favorite window (complete chosen period)."""
    now_dt = now or _utcnow()
    today = now_dt.date().isoformat()

    if period_type is None and start_date and end_date:
        return None, start_date, end_date

    normalized_type = period_type or ("all" if not start_date and not end_date else period_type)

    if normalized_type in (None, "all"):
        start = start_date or _first_candle_iso(symbol, timeframe)
        end = end_date or today
        return "all", start, end

    snap = {"period_type": normalized_type, "start_date": start_date, "end_date": end_date}
    resolved_start, resolved_end = resolve_optimizer_date_range(snap, now=now_dt)
    return normalized_type, resolved_start or start_date, resolved_end or end_date or today


def run_operational_backtest(
    *,
    template_name: str,
    symbol: str,
    timeframe: str,
    parameters: dict[str, Any],
    start_date: str | None,
    end_date: str | None,
    deep_backtest: bool = True,
) -> dict[str, Any]:
    """Single backtest on the complete chosen window (no train/holdout split)."""
    params = dict(parameters or {})
    data_source = params.get("data_source") or resolve_data_source_for_symbol(symbol, None)
    optimizer = ComboOptimizer()
    return optimizer.run_optimization(
        template_name=template_name,
        symbol=symbol,
        timeframe=timeframe,
        data_source=data_source,
        start_date=start_date,
        end_date=end_date,
        custom_ranges=_fixed_optimization_ranges(params),
        deep_backtest=deep_backtest,
        direction=_favorite_direction(params),
        split_train_ratio=None,
    )


def operational_metrics_from_backtest(result: dict[str, Any]) -> dict[str, Any]:
    metrics = dict(result.get("best_metrics") or result.get("metrics") or {})
    trades = result.get("trades") if isinstance(result.get("trades"), list) else []
    if trades:
        metrics["trades"] = trades
    return metrics


def apply_operational_period_to_metrics(
    metrics: dict[str, Any],
    *,
    operational: dict[str, Any],
    portrait: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Store training portrait in metrics_snapshot; grid keys = operational period."""
    from app.services.discovery_favorite_metrics import grid_metrics_from_snapshot

    out = dict(metrics)
    if portrait:
        out["metrics_snapshot"] = portrait
    grid = grid_metrics_from_snapshot(operational)
    out.update(grid)
    if isinstance(operational.get("trades"), list):
        out["trades"] = operational["trades"]
    out[OPERATIONAL_PERIOD_FLAG] = True
    return out


def enrich_walk_forward_favorite_create(
    *,
    strategy_name: str,
    symbol: str,
    timeframe: str,
    parameters: dict[str, Any],
    period_type: str | None,
    start_date: str | None,
    end_date: str | None,
    metrics: dict[str, Any],
    portrait_metrics: dict[str, Any] | None = None,
) -> tuple[str | None, str | None, str | None, dict[str, Any]]:
    """Resolve dates + rerun backtest for post-70/30 saves (Combo or Discovery promote)."""
    ptype, op_start, op_end = resolve_chosen_period(
        period_type=period_type,
        start_date=start_date,
        end_date=end_date,
        symbol=symbol,
        timeframe=timeframe,
    )
    portrait = portrait_metrics if isinstance(portrait_metrics, dict) else metrics
    backtest = run_operational_backtest(
        template_name=strategy_name,
        symbol=symbol,
        timeframe=timeframe,
        parameters=parameters,
        start_date=op_start,
        end_date=op_end,
    )
    operational = operational_metrics_from_backtest(backtest)
    enriched = apply_operational_period_to_metrics(
        metrics,
        operational=operational,
        portrait=portrait,
    )
    return ptype, op_start, op_end, enriched
