from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import AutoBacktestRun, FavoriteStrategy
from app.services.combo_optimizer import ComboOptimizer
from app.services.discovery_favorite_metrics import uses_operational_period
from app.services.market_data_providers import (
    BINANCE_EQUITY_SOURCE,
    CCXT_SOURCE,
    STOOQ_SOURCE,
    get_market_data_provider,
    resolve_data_source_for_symbol,
)

logger = logging.getLogger(__name__)

REFRESH_STATUS_RUNNING = "RUNNING"
REFRESH_STATUS_SUCCESS = "SUCCESS"
REFRESH_STATUS_FAILED = "FAILED"
# Card #1122: série curta ("Aguardando dados: N de M candles"), nunca "Falha".
REFRESH_STATUS_INSUFFICIENT = "INSUFFICIENT"
DEFAULT_REFRESH_INTERVAL_SECONDS = 86400
DEFAULT_REFRESH_LOOP_SECONDS = 3600
DEFAULT_REFRESH_RUNNING_TIMEOUT_SECONDS = 1800
DEFAULT_REFRESH_CPU_LIMIT_PERCENT = 60.0
DEFAULT_REFRESH_CPU_PAUSE_SECONDS = 30.0
DEFAULT_REFRESH_MAX_FAVORITES = 12
DEFAULT_REFRESH_INITIAL_DELAY_SECONDS = 300
DEFAULT_REFRESH_DELETE_DELISTED_BINANCE = True
DEFAULT_BINANCE_EXCHANGE_INFO_TTL_SECONDS = 3600
BINANCE_EXCHANGE_INFO_URL = "https://api.binance.com/api/v3/exchangeInfo"


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


PREVIOUS_NUMBER_KEYS = (
    "total_return",
    "total_return_pct",
    "win_rate",
    "max_drawdown",
    "max_drawdown_pct",
    "total_trades",
    "sharpe_ratio",
    "profit_factor",
    "cagr",
    "calmar_ratio",
    "auto_refreshed_at",
)


def _previous_number(metrics: dict[str, Any]) -> dict[str, Any]:
    """Resumo do número que o refresh vai substituir (sem a lista de trades)."""
    return {key: metrics[key] for key in PREVIOUS_NUMBER_KEYS if key in metrics}


def _favorite_direction(parameters: dict[str, Any]) -> str:
    direction = str(parameters.get("direction") or "long").lower()
    return direction if direction in {"long", "short"} else "long"


def _error_text(exc: Exception) -> str:
    return str(exc)[:2000] or exc.__class__.__name__


def favorite_refresh_state_path() -> Path:
    return Path(
        os.getenv(
            "FAVORITE_BACKTEST_REFRESH_STATE_FILE",
            "/tmp/crypto-favorite-refresh-state.json",
        )
    )


def _write_refresh_state(state: dict[str, Any]) -> None:
    path = favorite_refresh_state_path()
    payload = {
        **state,
        "updated_at": _utcnow().isoformat(),
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, default=str, sort_keys=True), encoding="utf-8")
    except Exception:
        logger.exception("Could not write favorite refresh state.")


def _load_average_cpu_percent() -> float | None:
    try:
        load_1m = os.getloadavg()[0]
    except (AttributeError, OSError):
        return None
    cpu_count = os.cpu_count() or 1
    return max(0.0, min(100.0, (load_1m / cpu_count) * 100.0))


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _binance_symbol_code(symbol: str) -> str:
    return str(symbol or "").strip().upper().replace("/", "")


def _fetch_binance_trading_symbols() -> set[str]:
    response = httpx.get(
        os.getenv("BINANCE_EXCHANGE_INFO_URL", BINANCE_EXCHANGE_INFO_URL),
        timeout=float(os.getenv("BINANCE_EXCHANGE_INFO_TIMEOUT_SECONDS", "20")),
    )
    response.raise_for_status()
    payload = response.json()
    symbols = payload.get("symbols") if isinstance(payload, dict) else []
    return {
        str(item.get("symbol") or "").upper()
        for item in symbols
        if isinstance(item, dict) and item.get("status") == "TRADING"
    }


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


def _ensure_fresh_candles(
    result: dict[str, Any], favorite: FavoriteStrategy, now: datetime
) -> None:
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


def _ensure_trade_events_within_candles(result: dict[str, Any], favorite: FavoriteStrategy) -> None:
    """Prevent a refresh from persisting trade events beyond candle coverage."""
    candles = result.get("candles") if isinstance(result.get("candles"), list) else []
    latest = _latest_candle_timestamp(candles)
    if latest is None:
        return

    timeframe = str(favorite.timeframe or "1d").strip().lower()
    if timeframe.endswith("m") and timeframe[:-1].isdigit():
        coverage_step = timedelta(minutes=int(timeframe[:-1]))
    elif timeframe.endswith("h") and timeframe[:-1].isdigit():
        coverage_step = timedelta(hours=int(timeframe[:-1]))
    elif timeframe.endswith("d") and timeframe[:-1].isdigit():
        coverage_step = timedelta(days=int(timeframe[:-1]))
    else:
        coverage_step = timedelta(days=1)
    coverage_end = latest + coverage_step

    trades = result.get("trades") if isinstance(result.get("trades"), list) else []
    for trade in trades:
        if not isinstance(trade, dict):
            continue
        for field in ("entry_time", "exit_time"):
            if not trade.get(field):
                continue
            event_time = _parse_candle_timestamp(trade[field])
            if event_time is None or event_time >= coverage_end:
                raise RuntimeError(
                    f"Trade event outside candle coverage for "
                    f"{favorite.symbol} {favorite.timeframe}: {field}={trade[field]}"
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


def _ensure_frame_covers_target(
    frame: Any,
    *,
    symbol: str,
    timeframe: str,
    target: datetime,
) -> None:
    if frame is None or getattr(frame, "empty", True):
        raise RuntimeError(f"No candles available for {symbol} {timeframe}")

    latest = _latest_frame_timestamp(frame)
    if latest is None:
        raise RuntimeError(f"No valid candle timestamp available for {symbol} {timeframe}")

    if latest < target:
        raise RuntimeError(
            f"Stale candles for {symbol} {timeframe}: "
            f"latest={latest.date().isoformat()}, required={target.date().isoformat()}"
        )


class RefreshUpToDate(Exception):
    """Nenhum candle fechou desde a última atualização: o ciclo pula a otimização (card #1122)."""


class RefreshInsufficient(Exception):
    """Menos candles fechados do que a análise precisa (card #1122): ``INSUFFICIENT``."""

    def __init__(self, available: int, required: int):
        super().__init__(f"{available} de {required} candles")
        self.available = int(available)
        self.required = int(required)


def _is_equity_source(data_source: str | None) -> bool:
    return str(data_source or "").strip().lower() in {BINANCE_EQUITY_SOURCE, STOOQ_SOURCE}


def _calendar_timeframe(data_source: str, timeframe: str) -> str:
    # A fonte antiga (Stooq) só tem diário.
    return "1d" if data_source == STOOQ_SOURCE else str(timeframe or "1d").strip().lower()


def last_closed_session_date(timeframe: str, now: datetime) -> str:
    """Data do último pregão fechado de NY (o fim de "todo o histórico" de ação/ETF)."""

    from app.services.market_history import nyse_calendar

    start = nyse_calendar.last_closed_start("1d", pd.Timestamp(now, tz="UTC"))
    return (start + pd.Timedelta(hours=12)).tz_convert(nyse_calendar.NY).date().isoformat()


def _ensure_calendar_fresh(
    frame_last: Any, *, data_source: str, symbol: str, timeframe: str, now: datetime
) -> None:
    """Ação/ETF: o último candle fechado esperado pelo calendário está presente (decisão 14).

    Fim de semana, feriado e fora do pregão nunca são falha; o atraso real é, com o motivo.
    """

    from app.services import market_state

    check = market_state.check_series(
        data_source=data_source,
        symbol=symbol,
        timeframe=_calendar_timeframe(data_source, timeframe),
        last_candle=frame_last,
        now=pd.Timestamp(now, tz="UTC"),
    )
    if check.stale:
        expected = check.expected_candle
        last = check.last_candle
        raise RuntimeError(
            f"Dados atrasados para {symbol} {timeframe}: falta o candle esperado "
            f"{expected.isoformat() if expected is not None else '?'} "
            f"(último recebido {last.isoformat() if last is not None else 'nenhum'})"
        )


def _closed_count(frame: Any, *, data_source: str, timeframe: str, now: datetime) -> int:
    if frame is None or getattr(frame, "empty", True):
        return 0
    if _is_equity_source(data_source):
        from app.services import market_state

        return len(
            market_state.cut_to_closed(
                frame, _calendar_timeframe(data_source, timeframe), pd.Timestamp(now, tz="UTC")
            )
        )
    return max(len(frame) - 1, 0)


def _frame_last_utc(frame: Any) -> pd.Timestamp | None:
    if frame is None or getattr(frame, "empty", True):
        return None
    try:
        last = pd.Timestamp(pd.DatetimeIndex(frame.index).max())
    except Exception:
        return None
    return last.tz_localize("UTC") if last.tzinfo is None else last.tz_convert("UTC")


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
        cpu_sampler=_load_average_cpu_percent,
        sleep_fn=time.sleep,
        binance_trading_symbols_provider=_fetch_binance_trading_symbols,
    ):
        self._db_factory = db_factory
        self._optimizer_factory = optimizer_factory
        self._market_data_provider_factory = market_data_provider_factory
        self._cpu_sampler = cpu_sampler
        self._sleep_fn = sleep_fn
        self._binance_trading_symbols_provider = binance_trading_symbols_provider
        self._binance_trading_symbols_cache: set[str] | None = None
        self._binance_trading_symbols_cached_at: datetime | None = None

    def _current_cpu_percent(self) -> float | None:
        try:
            value = self._cpu_sampler()
        except Exception:
            logger.exception("Favorite refresh CPU sampler failed.")
            return None
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _binance_trading_symbols(self) -> set[str]:
        ttl_seconds = int(
            os.getenv(
                "BINANCE_EXCHANGE_INFO_TTL_SECONDS",
                str(DEFAULT_BINANCE_EXCHANGE_INFO_TTL_SECONDS),
            )
        )
        now = _utcnow()
        if (
            self._binance_trading_symbols_cache is not None
            and self._binance_trading_symbols_cached_at is not None
            and (now - self._binance_trading_symbols_cached_at).total_seconds() < ttl_seconds
        ):
            return self._binance_trading_symbols_cache

        symbols = self._binance_trading_symbols_provider()
        self._binance_trading_symbols_cache = set(symbols)
        self._binance_trading_symbols_cached_at = now
        return self._binance_trading_symbols_cache

    def delete_delisted_binance_favorites(self) -> dict[str, Any]:
        trading_symbols = self._binance_trading_symbols()
        session = self._db_factory()
        try:
            rows = session.query(FavoriteStrategy).filter(FavoriteStrategy.symbol.like("%/%")).all()
            delisted = [
                row for row in rows if _binance_symbol_code(row.symbol) not in trading_symbols
            ]
            delisted_ids = [int(row.id) for row in delisted]
            delisted_symbols = sorted({str(row.symbol) for row in delisted})
            deleted_runs = 0
            if delisted_ids:
                from app.services.market_history import snapshots as history_snapshots

                for row in delisted:
                    if row.snapshot_id:
                        history_snapshots.release(session, row.snapshot_id)
                deleted_runs = (
                    session.query(AutoBacktestRun)
                    .filter(AutoBacktestRun.favorite_id.in_(delisted_ids))
                    .delete(synchronize_session=False)
                )
                (
                    session.query(FavoriteStrategy)
                    .filter(FavoriteStrategy.id.in_(delisted_ids))
                    .delete(synchronize_session=False)
                )
            session.commit()
            if delisted_ids:
                logger.info(
                    "Deleted %d delisted Binance favorites (%d runs): %s",
                    len(delisted_ids),
                    deleted_runs,
                    ", ".join(delisted_symbols),
                )
            return {
                "deleted_delisted_favorites": len(delisted_ids),
                "deleted_delisted_runs": int(deleted_runs or 0),
                "delisted_symbols": delisted_symbols,
            }
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _prepare_market_data(
        self,
        favorite: FavoriteStrategy,
        *,
        data_source: str,
        start_date: str | None,
        end_date: str,
    ) -> dict[str, Any] | None:
        now = _utcnow()
        parameters = _decode_jsonish(favorite.parameters)
        parameters = parameters if isinstance(parameters, dict) else {}
        collection = None
        if data_source == BINANCE_EQUITY_SOURCE:
            # Card #1122 (decisão 14): a série do tempo gráfico e o 5m do intrabar pelo caminho do
            # #1118; sem 15m a otimização roda com precisão diária marcada (como no lote).
            from app.services.equity_backtest import prepare_equity_history
            from app.services.market_data_providers import BinanceEquityMarketDataProvider

            prep = prepare_equity_history(
                favorite.symbol, favorite.timeframe, start_date, end_date, intrabar=True
            )
            collection = prep.collection
            provider = BinanceEquityMarketDataProvider(ensure=False)
            frame = provider.fetch_ohlcv(
                symbol=favorite.symbol,
                timeframe=favorite.timeframe,
                since_str=start_date,
                until_str=end_date,
            )
        else:
            provider = self._market_data_provider_factory(data_source)
            frame = _fetch_ohlcv(
                provider,
                symbol=favorite.symbol,
                timeframe=favorite.timeframe,
                since_str=start_date,
                until_str=end_date,
                full_history_if_empty=True,
            )
        if _is_equity_source(data_source):
            if frame is None or getattr(frame, "empty", True):
                raise RuntimeError(
                    f"No candles available for {favorite.symbol} {favorite.timeframe}"
                )
            _ensure_calendar_fresh(
                _frame_last_utc(frame),
                data_source=data_source,
                symbol=favorite.symbol,
                timeframe=favorite.timeframe,
                now=now,
            )
        else:
            _ensure_fresh_frame(
                frame,
                symbol=favorite.symbol,
                timeframe=favorite.timeframe,
                now=now,
            )

        from app.services.favorite_configuration import required_candles

        # Série curta de ação/ETF (ticker novo): "Aguardando dados", nunca "Falha". A cripto segue
        # as regras de hoje.
        if _is_equity_source(data_source):
            needed = required_candles(parameters)
            available = _closed_count(
                frame, data_source=data_source, timeframe=favorite.timeframe, now=now
            )
            if needed and available < needed:
                raise RefreshInsufficient(available, needed)

        info: dict[str, Any] = {"collection": collection}
        if _is_equity_source(data_source):
            from app.services import market_state

            closed = market_state.cut_to_closed(
                frame,
                _calendar_timeframe(data_source, favorite.timeframe),
                pd.Timestamp(now, tz="UTC"),
            )
            last_closed = _frame_last_utc(closed)
            info["last_closed_candle"] = (
                last_closed.isoformat() if last_closed is not None else None
            )
            metrics = _decode_jsonish(favorite.metrics)
            metrics = metrics if isinstance(metrics, dict) else {}
            previous = metrics.get("analysis_last_closed_candle")
            if (
                previous
                and info["last_closed_candle"]
                and getattr(self, "_previous_refresh_status", favorite.auto_refresh_status)
                == REFRESH_STATUS_SUCCESS
                and pd.Timestamp(previous) >= pd.Timestamp(info["last_closed_candle"])
            ):
                # Sem candle fechado novo desde a última atualização: mantém o SUCCESS.
                raise RefreshUpToDate()
            return info

        if data_source != CCXT_SOURCE:
            return info

        intraday_since = start_date
        latest_daily = _latest_frame_timestamp(frame)
        if latest_daily is None:
            raise RuntimeError(
                f"No valid candle timestamp available for {favorite.symbol} {favorite.timeframe}"
            )
        if start_date is None:
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
        _ensure_frame_covers_target(
            intraday_frame,
            symbol=favorite.symbol,
            timeframe="15m",
            target=latest_daily,
        )
        return info

    def _run_optimization(self, favorite: FavoriteStrategy) -> dict[str, Any]:
        parameters = _decode_jsonish(favorite.parameters)
        parameters = parameters if isinstance(parameters, dict) else {}
        data_source = parameters.get("data_source") or resolve_data_source_for_symbol(
            favorite.symbol, None
        )
        data_source = str(data_source).strip().lower()
        now = _utcnow()
        end_date = now.date().isoformat()
        if _is_equity_source(data_source):
            # Card #1122 (decisão 14): o fim de ação/ETF é o último pregão fechado.
            try:
                end_date = last_closed_session_date(favorite.timeframe, now)
            except Exception:
                logger.warning("Calendário de NY indisponível; fim do período = hoje")
        info = self._prepare_market_data(
            favorite,
            data_source=data_source,
            start_date=favorite.start_date,
            end_date=end_date,
        )
        self._last_prepare_info = {**(info or {}), "end_date": end_date}
        optimizer = self._optimizer_factory()
        if data_source == BINANCE_EQUITY_SOURCE and info is not None:
            from app.services.market_data_providers import BinanceEquityMarketDataProvider

            # Coleta feita: a otimização lê só o guardado (como o lote e o #1119).
            optimizer._provider = BinanceEquityMarketDataProvider(ensure=False)
            optimizer.collection_note = info.get("collection")
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

    def _refresh_comparison(self, session: Session, favorite_id: int) -> None:
        """Refaz a comparação gravada; falha nunca derruba o refresh já gravado."""

        refresher = getattr(self, "comparison_refresher", None)
        if refresher is None:
            from app.services.benchmark_comparison import (
                auto_record_enabled,
                refresh_favorite_comparison,
            )

            if not auto_record_enabled():
                return
            refresher = refresh_favorite_comparison
        try:
            refresher(session, favorite_id)
        except Exception as exc:
            session.rollback()
            logger.warning(
                "Comparison refresh failed for favorite %s: %s", favorite_id, exc, exc_info=True
            )

    def refresh_favorite(self, favorite_id: int, *, db: Session | None = None) -> dict[str, Any]:
        owns_session = db is None
        session = db or self._db_factory()
        now = _utcnow()
        run_id = f"favorite-refresh-{favorite_id}-{uuid.uuid4().hex[:12]}"
        run: AutoBacktestRun | None = None
        attempt_snapshot_id: str | None = None

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
            # Card #1122: o pulo "sem candle fechado novo" só vale depois de um SUCCESS.
            self._previous_refresh_status = favorite.auto_refresh_status
            favorite.auto_refresh_status = REFRESH_STATUS_RUNNING
            favorite.auto_refresh_error = None
            favorite.auto_refresh_started_at = now
            favorite.auto_refresh_completed_at = None
            favorite.auto_refresh_run_id = run_id
            session.commit()

            self._last_prepare_info = {}
            try:
                result = self._run_optimization(favorite)
            except RefreshUpToDate:
                return self._finish_up_to_date(session, favorite, run, run_id)
            except RefreshInsufficient as exc:
                return self._finish_insufficient(session, favorite, run, run_id, exc)
            prepare_info = dict(getattr(self, "_last_prepare_info", {}) or {})
            attempt_snapshot_id = result.get("snapshot_id") if isinstance(result, dict) else None
            parameters_now = _decode_jsonish(favorite.parameters)
            source_now = str(
                (parameters_now or {}).get("data_source")
                if isinstance(parameters_now, dict)
                else ""
            ).lower() or resolve_data_source_for_symbol(favorite.symbol, None)
            if _is_equity_source(source_now):
                candles = result.get("candles") if isinstance(result.get("candles"), list) else []
                if not candles:
                    raise RuntimeError(
                        f"No candles returned for {favorite.symbol} {favorite.timeframe}"
                    )
                latest = max(
                    (
                        pd.Timestamp(c.get("timestamp_utc") or c.get("timestamp"))
                        for c in candles
                        if c.get("timestamp_utc") or c.get("timestamp")
                    ),
                    default=None,
                )
                _ensure_calendar_fresh(
                    latest,
                    data_source=source_now,
                    symbol=favorite.symbol,
                    timeframe=favorite.timeframe,
                    now=_utcnow(),
                )
            else:
                _ensure_fresh_candles(result, favorite, _utcnow())
            _ensure_trade_events_within_candles(result, favorite)
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
                "analysis_strategy_transparency": (
                    result.get("strategy_transparency")
                    if isinstance(result.get("strategy_transparency"), dict)
                    else None
                ),
                "analysis_execution_mode": result.get("execution_mode"),
                # Card #1119 (decisão 12): precisão efetiva, convenções e identidade no favorito.
                "analysis_execution": result.get("execution"),
                "analysis_conventions": result.get("conventions"),
                "analysis_asset": result.get("asset"),
                # Card #1122: último candle fechado e último pregão (status de ação/ETF).
                "analysis_last_closed_candle": prepare_info.get("last_closed_candle"),
                "analysis_last_session": (
                    prepare_info.get("end_date") if _is_equity_source(source_now) else None
                ),
                "auto_refreshed_at": _utcnow().isoformat(),
                "auto_refresh_run_id": run_id,
            }

            completed_at = _utcnow()
            favorite.metrics = updated_metrics
            if attempt_snapshot_id:
                # Card #1118 (decisão 18): no mesmo commit que grava o número de /favorites, o
                # favorito passa a apontar para a amostra deste refresh (fixada), o run guarda a
                # mesma amostra e a anterior segue por 30 dias a partir da troca.
                from app.services.market_history import snapshots as history_snapshots

                previous_snapshot_id = favorite.snapshot_id
                favorite.snapshot_id = attempt_snapshot_id
                run.snapshot_id = attempt_snapshot_id
                history_snapshots.pin(session, attempt_snapshot_id)
                if previous_snapshot_id and previous_snapshot_id != attempt_snapshot_id:
                    history_snapshots.release(session, previous_snapshot_id, completed_at)
            if uses_operational_period(current_metrics) and favorite.period_type == "all":
                favorite.end_date = (
                    prepare_info.get("end_date")
                    if _is_equity_source(source_now) and prepare_info.get("end_date")
                    else completed_at.date().isoformat()
                )
            favorite.auto_refresh_status = REFRESH_STATUS_SUCCESS
            favorite.auto_refresh_error = None
            favorite.auto_refresh_completed_at = completed_at
            run.status = REFRESH_STATUS_SUCCESS
            run.stage_3_result = {
                "favorite_id": favorite.id,
                "metrics": refreshed_metrics,
                "trades_count": len(updated_metrics["trades"]),
                # Card #1119 (tarefa 6.2): a regra do gap pode piorar o número do favorito de cripto;
                # o número anterior fica no histórico de runs, sem aviso novo em /favorites.
                "previous_metrics": _previous_number(current_metrics),
                "gap_stops": (
                    (result.get("execution") or {}).get("gap_stops")
                    if isinstance(result.get("execution"), dict)
                    else None
                ),
            }
            run.updated_at = completed_at
            run.completed_at = completed_at
            session.commit()
            # Card #1123 (decisão 5): o único recálculo da comparação, com a mesma referência.
            self._refresh_comparison(session, favorite.id)
            return {"favorite_id": favorite.id, "status": REFRESH_STATUS_SUCCESS, "run_id": run_id}
        except Exception as exc:
            session.rollback()
            failed_at = _utcnow()
            error = _error_text(exc)
            if attempt_snapshot_id:
                # Refresh que falha não troca nada: a amostra da tentativa não sustenta número algum.
                try:
                    from app.database import engine as history_engine
                    from app.services.market_history import snapshots as history_snapshots

                    history_snapshots.expire(history_engine, attempt_snapshot_id, failed_at)
                except Exception:  # pragma: no cover - limpeza nunca esconde o erro original
                    logger.exception("Could not release the failed refresh sample")
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

    def _finish_up_to_date(
        self, session: Session, favorite: FavoriteStrategy, run: Any, run_id: str
    ) -> dict[str, Any]:
        """Sem candle fechado novo: o número fica, o status segue ``SUCCESS`` (card #1122)."""

        completed_at = _utcnow()
        favorite.auto_refresh_status = REFRESH_STATUS_SUCCESS
        favorite.auto_refresh_error = None
        favorite.auto_refresh_completed_at = completed_at
        if run is not None:
            run.status = REFRESH_STATUS_SUCCESS
            run.stage_3_result = {"favorite_id": favorite.id, "skipped": "no_new_closed_candle"}
            run.updated_at = completed_at
            run.completed_at = completed_at
        session.commit()
        return {
            "favorite_id": favorite.id,
            "status": REFRESH_STATUS_SUCCESS,
            "run_id": run_id,
            "skipped": "no_new_closed_candle",
        }

    def _finish_insufficient(
        self,
        session: Session,
        favorite: FavoriteStrategy,
        run: Any,
        run_id: str,
        exc: RefreshInsufficient,
    ) -> dict[str, Any]:
        """Série curta: ``INSUFFICIENT`` com "N de M candles", nunca "Falha" (card #1122)."""

        completed_at = _utcnow()
        favorite.auto_refresh_status = REFRESH_STATUS_INSUFFICIENT
        favorite.auto_refresh_error = f"{exc.available} de {exc.required} candles"
        favorite.auto_refresh_completed_at = completed_at
        if run is not None:
            run.status = REFRESH_STATUS_INSUFFICIENT
            run.error_message = favorite.auto_refresh_error
            run.updated_at = completed_at
            run.completed_at = completed_at
        session.commit()
        return {
            "favorite_id": favorite.id,
            "status": REFRESH_STATUS_INSUFFICIENT,
            "run_id": run_id,
            "available": exc.available,
            "required": exc.required,
        }

    def run_due_refreshes(
        self,
        *,
        now: datetime | None = None,
        interval_seconds: int | None = None,
        running_timeout_seconds: int | None = None,
        max_favorites: int | None = None,
        cpu_limit_percent: float | None = None,
        cpu_pause_seconds: float | None = None,
        delete_delisted_binance_favorites: bool | None = None,
    ) -> dict[str, Any]:
        now = now or _utcnow()
        interval_seconds = interval_seconds or int(
            os.getenv(
                "FAVORITE_BACKTEST_REFRESH_INTERVAL_SECONDS",
                str(DEFAULT_REFRESH_INTERVAL_SECONDS),
            )
        )
        running_timeout_seconds = running_timeout_seconds or int(
            os.getenv(
                "FAVORITE_BACKTEST_REFRESH_RUNNING_TIMEOUT_SECONDS",
                str(DEFAULT_REFRESH_RUNNING_TIMEOUT_SECONDS),
            )
        )
        max_favorites = (
            max_favorites
            if max_favorites is not None
            else int(
                os.getenv(
                    "FAVORITE_BACKTEST_REFRESH_MAX_FAVORITES",
                    str(DEFAULT_REFRESH_MAX_FAVORITES),
                )
            )
        )
        cpu_limit_percent = (
            cpu_limit_percent
            if cpu_limit_percent is not None
            else float(
                os.getenv(
                    "FAVORITE_BACKTEST_REFRESH_CPU_LIMIT_PERCENT",
                    str(DEFAULT_REFRESH_CPU_LIMIT_PERCENT),
                )
            )
        )
        cpu_pause_seconds = (
            cpu_pause_seconds
            if cpu_pause_seconds is not None
            else float(
                os.getenv(
                    "FAVORITE_BACKTEST_REFRESH_CPU_PAUSE_SECONDS",
                    str(DEFAULT_REFRESH_CPU_PAUSE_SECONDS),
                )
            )
        )
        delete_delisted_binance_favorites = (
            delete_delisted_binance_favorites
            if delete_delisted_binance_favorites is not None
            else _env_bool(
                "FAVORITE_BACKTEST_DELETE_DELISTED_BINANCE",
                DEFAULT_REFRESH_DELETE_DELISTED_BINANCE,
            )
        )
        delisted_summary = {
            "deleted_delisted_favorites": 0,
            "deleted_delisted_runs": 0,
            "delisted_symbols": [],
        }
        if delete_delisted_binance_favorites:
            try:
                delisted_summary = self.delete_delisted_binance_favorites()
            except Exception as exc:
                logger.warning("Could not delete delisted Binance favorites: %s", exc)

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

        selected_ids = due_ids[:max_favorites] if max_favorites and max_favorites > 0 else due_ids
        summary: dict[str, Any] = {
            "status": "completed",
            "due": len(due_ids),
            "selected": len(selected_ids),
            "success": 0,
            "failed": 0,
            "skipped_cpu": 0,
            "skipped_limit": max(0, len(due_ids) - len(selected_ids)),
            "cpu_limit_percent": cpu_limit_percent,
            "last_cpu_percent": None,
            "pause_seconds": 0.0,
            "reason": None,
            "started_at": now.isoformat(),
            **delisted_summary,
        }
        _write_refresh_state(summary)

        for index, favorite_id in enumerate(selected_ids):
            cpu_percent = self._current_cpu_percent()
            if cpu_percent is not None:
                summary["last_cpu_percent"] = round(cpu_percent, 2)
            if (
                cpu_limit_percent is not None
                and cpu_percent is not None
                and cpu_percent > cpu_limit_percent
            ):
                remaining = len(selected_ids) - index
                summary["status"] = "paused_cpu"
                summary["skipped_cpu"] = remaining
                summary["reason"] = f"CPU {cpu_percent:.1f}% above limit {cpu_limit_percent:.1f}%"
                if cpu_pause_seconds > 0:
                    self._sleep_fn(cpu_pause_seconds)
                    summary["pause_seconds"] = float(cpu_pause_seconds)
                break
            result = self.refresh_favorite(favorite_id)
            if result.get("status") == REFRESH_STATUS_SUCCESS:
                summary["success"] += 1
            elif result.get("status") == REFRESH_STATUS_INSUFFICIENT:
                summary["insufficient"] = summary.get("insufficient", 0) + 1
            else:
                summary["failed"] += 1
            _write_refresh_state(summary)
        summary["completed_at"] = _utcnow().isoformat()
        _write_refresh_state(summary)
        return summary


def run_due_favorite_backtest_refresh(
    db_factory=SessionLocal,
    *,
    now: datetime | None = None,
    interval_seconds: int | None = None,
    running_timeout_seconds: int | None = None,
    max_favorites: int | None = None,
    cpu_limit_percent: float | None = None,
    cpu_pause_seconds: float | None = None,
    delete_delisted_binance_favorites: bool | None = None,
) -> dict[str, Any]:
    return FavoriteBacktestRefreshService(db_factory=db_factory).run_due_refreshes(
        now=now,
        interval_seconds=interval_seconds,
        running_timeout_seconds=running_timeout_seconds,
        max_favorites=max_favorites,
        cpu_limit_percent=cpu_limit_percent,
        cpu_pause_seconds=cpu_pause_seconds,
        delete_delisted_binance_favorites=delete_delisted_binance_favorites,
    )


async def favorite_backtest_refresh_loop(
    stop_event: asyncio.Event,
    *,
    db_factory=SessionLocal,
    interval_seconds: int | None = None,
    loop_sleep_seconds: int | None = None,
    initial_delay_seconds: int | None = None,
    max_favorites: int | None = None,
) -> None:
    interval_seconds = interval_seconds or int(
        os.getenv(
            "FAVORITE_BACKTEST_REFRESH_INTERVAL_SECONDS",
            str(DEFAULT_REFRESH_INTERVAL_SECONDS),
        )
    )
    loop_sleep_seconds = loop_sleep_seconds or int(
        os.getenv(
            "FAVORITE_BACKTEST_REFRESH_LOOP_SECONDS",
            str(DEFAULT_REFRESH_LOOP_SECONDS),
        )
    )
    initial_delay_seconds = (
        initial_delay_seconds
        if initial_delay_seconds is not None
        else int(
            os.getenv(
                "FAVORITE_BACKTEST_REFRESH_INITIAL_DELAY_SECONDS",
                str(DEFAULT_REFRESH_INITIAL_DELAY_SECONDS),
            )
        )
    )
    max_favorites = max_favorites or (
        int(os.environ["FAVORITE_BACKTEST_REFRESH_MAX_FAVORITES"])
        if os.getenv("FAVORITE_BACKTEST_REFRESH_MAX_FAVORITES")
        else DEFAULT_REFRESH_MAX_FAVORITES
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
            await asyncio.wait_for(stop_event.wait(), timeout=loop_sleep_seconds)
        except asyncio.TimeoutError:
            continue
