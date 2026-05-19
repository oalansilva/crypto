from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import AutoBacktestRun, FavoriteStrategy
from app.services.combo_optimizer import ComboOptimizer
from app.services.market_data_providers import resolve_data_source_for_symbol

logger = logging.getLogger(__name__)

REFRESH_STATUS_RUNNING = "RUNNING"
REFRESH_STATUS_SUCCESS = "SUCCESS"
REFRESH_STATUS_FAILED = "FAILED"


def _utcnow() -> datetime:
    return datetime.utcnow()


def _decode_jsonish(value: Any) -> Any:
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return value
        if isinstance(parsed, str):
            try:
                return json.loads(parsed)
            except json.JSONDecodeError:
                return parsed
        return parsed
    return value


def _fixed_optimization_ranges(parameters: dict[str, Any]) -> dict[str, dict[str, Any]]:
    ranges: dict[str, dict[str, Any]] = {}
    for key, value in parameters.items():
        if key in {"data_source", "direction"} or isinstance(value, bool):
            continue
        if isinstance(value, int):
            ranges[key] = {"min": value, "max": value, "step": 1}
        elif isinstance(value, float):
            ranges[key] = {"min": value, "max": value, "step": 0.0001}
    return ranges


def _favorite_direction(parameters: dict[str, Any]) -> str:
    direction = str(parameters.get("direction") or "long").lower()
    return direction if direction in {"long", "short"} else "long"


def _error_text(exc: Exception) -> str:
    return str(exc)[:2000] or exc.__class__.__name__


class FavoriteBacktestRefreshService:
    def __init__(self, db_factory=SessionLocal, optimizer_factory=ComboOptimizer):
        self._db_factory = db_factory
        self._optimizer_factory = optimizer_factory

    def _run_optimization(self, favorite: FavoriteStrategy) -> dict[str, Any]:
        parameters = _decode_jsonish(favorite.parameters)
        parameters = parameters if isinstance(parameters, dict) else {}
        data_source = parameters.get("data_source") or resolve_data_source_for_symbol(
            favorite.symbol, None
        )
        optimizer = self._optimizer_factory()
        return optimizer.run_optimization(
            template_name=favorite.strategy_name,
            symbol=favorite.symbol,
            timeframe=favorite.timeframe,
            data_source=data_source,
            start_date=favorite.start_date,
            end_date=_utcnow().date().isoformat(),
            custom_ranges=_fixed_optimization_ranges(parameters),
            deep_backtest=True,
            direction=_favorite_direction(parameters),
        )

    def refresh_favorite(self, favorite_id: int, *, db: Session | None = None) -> dict[str, Any]:
        owns_session = db is None
        session = db or self._db_factory()
        now = _utcnow()
        run_id = f"favorite-refresh-{favorite_id}-{uuid.uuid4().hex[:12]}"
        run: AutoBacktestRun | None = None

        try:
            favorite = (
                session.query(FavoriteStrategy)
                .filter(FavoriteStrategy.id == favorite_id)
                .with_for_update()
                .first()
            )
            if not favorite:
                raise ValueError(f"Favorite {favorite_id} not found")

            run = AutoBacktestRun(
                run_id=run_id,
                symbol=favorite.symbol,
                strategy=favorite.strategy_name,
                status=REFRESH_STATUS_RUNNING,
                favorite_id=favorite.id,
                created_at=now,
                updated_at=now,
            )
            session.add(run)
            favorite.auto_refresh_status = REFRESH_STATUS_RUNNING
            favorite.auto_refresh_error = None
            favorite.auto_refresh_started_at = now
            favorite.auto_refresh_completed_at = None
            favorite.auto_refresh_run_id = run_id
            session.commit()

            result = self._run_optimization(favorite)
            refreshed_metrics = result.get("best_metrics") or result.get("metrics") or {}
            current_metrics = _decode_jsonish(favorite.metrics)
            current_metrics = current_metrics if isinstance(current_metrics, dict) else {}
            updated_metrics = {
                **current_metrics,
                **refreshed_metrics,
                "trades": result.get("trades") or [],
                "trades_history_cached": True,
                "analysis_candles": (
                    result.get("candles") if isinstance(result.get("candles"), list) else []
                ),
                "analysis_indicator_data": (
                    result.get("indicator_data")
                    if isinstance(result.get("indicator_data"), dict)
                    else {}
                ),
                "analysis_execution_mode": result.get("execution_mode"),
                "auto_refreshed_at": _utcnow().isoformat(),
                "auto_refresh_run_id": run_id,
            }

            completed_at = _utcnow()
            favorite.metrics = updated_metrics
            favorite.auto_refresh_status = REFRESH_STATUS_SUCCESS
            favorite.auto_refresh_error = None
            favorite.auto_refresh_completed_at = completed_at
            run.status = REFRESH_STATUS_SUCCESS
            run.stage_3_result = {
                "favorite_id": favorite.id,
                "metrics": refreshed_metrics,
                "trades_count": len(updated_metrics["trades"]),
            }
            run.updated_at = completed_at
            run.completed_at = completed_at
            session.commit()
            return {"favorite_id": favorite.id, "status": REFRESH_STATUS_SUCCESS, "run_id": run_id}
        except Exception as exc:
            session.rollback()
            failed_at = _utcnow()
            error = _error_text(exc)
            favorite = (
                session.query(FavoriteStrategy).filter(FavoriteStrategy.id == favorite_id).first()
            )
            if favorite:
                favorite.auto_refresh_status = REFRESH_STATUS_FAILED
                favorite.auto_refresh_error = error
                favorite.auto_refresh_completed_at = failed_at
                favorite.auto_refresh_run_id = run_id
                if favorite.auto_refresh_started_at is None:
                    favorite.auto_refresh_started_at = now
            run = session.query(AutoBacktestRun).filter(AutoBacktestRun.run_id == run_id).first()
            if run is None and favorite:
                run = AutoBacktestRun(
                    run_id=run_id,
                    symbol=favorite.symbol,
                    strategy=favorite.strategy_name,
                    status=REFRESH_STATUS_FAILED,
                    favorite_id=favorite.id,
                    created_at=now,
                )
                session.add(run)
            if run is not None:
                run.status = REFRESH_STATUS_FAILED
                run.error_message = error
                run.updated_at = failed_at
                run.completed_at = failed_at
            session.commit()
            logger.warning("Favorite backtest refresh failed for %s: %s", favorite_id, error)
            return {"favorite_id": favorite_id, "status": REFRESH_STATUS_FAILED, "error": error}
        finally:
            if owns_session:
                session.close()

    def run_due_refreshes(
        self,
        *,
        now: datetime | None = None,
        interval_seconds: int | None = None,
        running_timeout_seconds: int | None = None,
        max_favorites: int | None = None,
    ) -> dict[str, int]:
        now = now or _utcnow()
        interval_seconds = interval_seconds or int(
            os.getenv("FAVORITE_BACKTEST_REFRESH_INTERVAL_SECONDS", "86400")
        )
        running_timeout_seconds = running_timeout_seconds or int(
            os.getenv("FAVORITE_BACKTEST_REFRESH_RUNNING_TIMEOUT_SECONDS", "1800")
        )
        cutoff = now - timedelta(seconds=interval_seconds)
        running_cutoff = now - timedelta(seconds=running_timeout_seconds)
        session = self._db_factory()
        try:
            rows = session.query(FavoriteStrategy).all()
        finally:
            session.close()

        def _priority(row: FavoriteStrategy) -> tuple[int, float]:
            if row.auto_refresh_completed_at is None:
                created_at = row.created_at or datetime.min
                return (0, -created_at.timestamp())
            return (1, row.auto_refresh_completed_at.timestamp())

        due_ids: list[int] = []
        for row in sorted(rows, key=_priority):
            if row.auto_refresh_status == REFRESH_STATUS_RUNNING:
                if row.auto_refresh_started_at and row.auto_refresh_started_at > running_cutoff:
                    continue
            elif row.auto_refresh_completed_at and row.auto_refresh_completed_at > cutoff:
                continue
            due_ids.append(int(row.id))
            if max_favorites and len(due_ids) >= max_favorites:
                break

        summary = {"due": len(due_ids), "success": 0, "failed": 0}
        for favorite_id in due_ids:
            result = self.refresh_favorite(favorite_id)
            if result.get("status") == REFRESH_STATUS_SUCCESS:
                summary["success"] += 1
            else:
                summary["failed"] += 1
        return summary


def run_due_favorite_backtest_refresh(
    db_factory=SessionLocal,
    *,
    now: datetime | None = None,
    interval_seconds: int | None = None,
    running_timeout_seconds: int | None = None,
    max_favorites: int | None = None,
) -> dict[str, int]:
    return FavoriteBacktestRefreshService(db_factory=db_factory).run_due_refreshes(
        now=now,
        interval_seconds=interval_seconds,
        running_timeout_seconds=running_timeout_seconds,
        max_favorites=max_favorites,
    )


async def favorite_backtest_refresh_loop(
    stop_event: asyncio.Event,
    *,
    db_factory=SessionLocal,
    interval_seconds: int | None = None,
    initial_delay_seconds: int | None = None,
    max_favorites: int | None = None,
) -> None:
    interval_seconds = interval_seconds or int(
        os.getenv("FAVORITE_BACKTEST_REFRESH_INTERVAL_SECONDS", "86400")
    )
    initial_delay_seconds = (
        initial_delay_seconds
        if initial_delay_seconds is not None
        else int(os.getenv("FAVORITE_BACKTEST_REFRESH_INITIAL_DELAY_SECONDS", "300"))
    )
    max_favorites = max_favorites or (
        int(os.environ["FAVORITE_BACKTEST_REFRESH_MAX_FAVORITES"])
        if os.getenv("FAVORITE_BACKTEST_REFRESH_MAX_FAVORITES")
        else None
    )
    service = FavoriteBacktestRefreshService(db_factory=db_factory)

    if initial_delay_seconds > 0:
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=initial_delay_seconds)
            return
        except asyncio.TimeoutError:
            pass

    while not stop_event.is_set():
        try:
            summary = await asyncio.to_thread(
                service.run_due_refreshes,
                interval_seconds=interval_seconds,
                max_favorites=max_favorites,
            )
            logger.info("Favorite backtest refresh run completed: %s", summary)
        except Exception:  # pragma: no cover - defensive runtime path
            logger.exception("Favorite backtest refresh loop failed.")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            continue
