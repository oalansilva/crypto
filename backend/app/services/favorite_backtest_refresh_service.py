from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import AutoBacktestRun, FavoriteStrategy
from app.services.combo_optimizer import ComboOptimizer
from app.services.market_data_providers import (
    CCXT_SOURCE,
    get_market_data_provider,
    resolve_data_source_for_symbol,
)

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


def _parse_candle_timestamp(value: Any) -> datetime | None:
    if isinstance(value, pd.Timestamp):
        parsed = value.to_pydatetime()
    elif isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            parsed = None
    else:
        parsed = None

    if parsed is None:
        try:
            parsed_value = pd.to_datetime(value, utc=True, errors="coerce")
        except Exception:
            return None
        if pd.isna(parsed_value):
            return None
        parsed = parsed_value.to_pydatetime()

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone().replace(tzinfo=None)
    return parsed


def _max_candle_age(timeframe: str) -> timedelta:
    normalized = str(timeframe or "").strip().lower()
    if normalized.endswith("m"):
        try:
            minutes = int(normalized[:-1])
        except ValueError:
            return timedelta(hours=6)
        return timedelta(minutes=max(minutes * 4, 30))
    if normalized.endswith("h"):
        try:
            hours = int(normalized[:-1])
        except ValueError:
            return timedelta(hours=24)
        return timedelta(hours=max(hours * 3, 12))
    if normalized.endswith("d"):
        return timedelta(days=7)
    return timedelta(days=7)


def _latest_candle_timestamp(candles: list[dict[str, Any]]) -> datetime | None:
    parsed = [
        _parse_candle_timestamp(candle.get("timestamp_utc") or candle.get("timestamp"))
        for candle in candles
    ]
    valid = [timestamp for timestamp in parsed if timestamp is not None]
    return max(valid) if valid else None


def _latest_frame_timestamp(frame: Any) -> datetime | None:
    if frame is None or getattr(frame, "empty", True):
        return None
    if "timestamp_utc" in frame.columns:
        values = frame["timestamp_utc"]
    else:
        values = frame.index
    try:
        parsed = [_parse_candle_timestamp(value) for value in values]
    except Exception:
        return None
    valid = [timestamp for timestamp in parsed if timestamp is not None]
    return max(valid) if valid else None


def _ensure_fresh_candles(result: dict[str, Any], favorite: FavoriteStrategy, now: datetime) -> None:
    candles = result.get("candles") if isinstance(result.get("candles"), list) else []
    if not candles:
        raise RuntimeError(f"No candles returned for {favorite.symbol} {favorite.timeframe}")

    latest = _latest_candle_timestamp(candles)
    if latest is None:
        raise RuntimeError(
            f"No valid candle timestamp returned for {favorite.symbol} {favorite.timeframe}"
        )

    max_age = _max_candle_age(favorite.timeframe)
    if latest < now - max_age:
        raise RuntimeError(
            f"Stale candles for {favorite.symbol} {favorite.timeframe}: "
            f"latest={latest.date().isoformat()}, max_age_days={max_age.days}"
        )


def _ensure_fresh_frame(frame: Any, *, symbol: str, timeframe: str, now: datetime) -> None:
    if frame is None or getattr(frame, "empty", True):
        raise RuntimeError(f"No candles available for {symbol} {timeframe}")

    latest = _latest_frame_timestamp(frame)
    if latest is None:
        raise RuntimeError(f"No valid candle timestamp available for {symbol} {timeframe}")

    max_age = _max_candle_age(timeframe)
    if latest < now - max_age:
        raise RuntimeError(
            f"Stale candles for {symbol} {timeframe}: "
            f"latest={latest.date().isoformat()}, max_age_days={max_age.days}"
        )


def _fetch_ohlcv(provider: Any, **kwargs: Any) -> Any:
    try:
        return provider.fetch_ohlcv(**kwargs)
    except TypeError as exc:
        if "full_history_if_empty" not in kwargs:
            raise
        kwargs.pop("full_history_if_empty", None)
        try:
            return provider.fetch_ohlcv(**kwargs)
        except TypeError:
            raise exc


class FavoriteBacktestRefreshService:
    def __init__(
        self,
        db_factory=SessionLocal,
        optimizer_factory=ComboOptimizer,
        market_data_provider_factory=get_market_data_provider,
    ):
        self._db_factory = db_factory
        self._optimizer_factory = optimizer_factory
        self._market_data_provider_factory = market_data_provider_factory

    def _prepare_market_data(
        self,
        favorite: FavoriteStrategy,
        *,
        data_source: str,
        start_date: str | None,
        end_date: str,
    ) -> None:
        provider = self._market_data_provider_factory(data_source)
        frame = _fetch_ohlcv(
            provider,
            symbol=favorite.symbol,
            timeframe=favorite.timeframe,
            since_str=start_date,
            until_str=end_date,
            full_history_if_empty=True,
        )
        _ensure_fresh_frame(
            frame,
            symbol=favorite.symbol,
            timeframe=favorite.timeframe,
            now=_utcnow(),
        )

        if data_source != CCXT_SOURCE:
            return

        intraday_since = start_date
        latest_daily_start = _latest_frame_timestamp(frame)
        if start_date is None and latest_daily_start is not None:
            try:
                first_value = frame.index.min()
                parsed_first = _parse_candle_timestamp(first_value)
                if parsed_first is not None:
                    intraday_since = parsed_first.date().isoformat()
            except Exception:
                pass

        intraday_frame = _fetch_ohlcv(
            provider,
            symbol=favorite.symbol,
            timeframe="15m",
            since_str=intraday_since,
            until_str=end_date,
            full_history_if_empty=True,
        )
        _ensure_fresh_frame(
            intraday_frame,
            symbol=favorite.symbol,
            timeframe="15m",
            now=_utcnow(),
        )

    def _run_optimization(self, favorite: FavoriteStrategy) -> dict[str, Any]:
        parameters = _decode_jsonish(favorite.parameters)
        parameters = parameters if isinstance(parameters, dict) else {}
        data_source = parameters.get("data_source") or resolve_data_source_for_symbol(
            favorite.symbol, None
        )
        end_date = _utcnow().date().isoformat()
        self._prepare_market_data(
            favorite,
            data_source=data_source,
            start_date=favorite.start_date,
            end_date=end_date,
        )
        optimizer = self._optimizer_factory()
        return optimizer.run_optimization(
            template_name=favorite.strategy_name,
            symbol=favorite.symbol,
            timeframe=favorite.timeframe,
            data_source=data_source,
            start_date=favorite.start_date,
            end_date=end_date,
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
            _ensure_fresh_candles(result, favorite, _utcnow())
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
