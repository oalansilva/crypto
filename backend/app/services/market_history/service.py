"""``HistoryService``: leitura com cobertura e coleta que retoma (card #1118).

* ``read`` nunca chama a Binance: devolve candles e cobertura honesta.
* ``ensure`` coleta só o que falta. Falha da Binance vira estado de falha na
  cobertura, nunca lista vazia nem período completo.
* Cripto continua pela CCXT; ação e ETF pela rota do gráfico (adaptador isolado).
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.services.market_history import nyse_calendar as cal
from app.services.market_history import store
from app.services.market_history.equity_provider import (
    BinanceCircuitOpen,
    BinanceEquityError,
    BinanceEquityProvider,
    BinanceFormatChanged,
    EquityBar,
    EquityPage,
    NATIVE_TIMEFRAMES,
    UnsupportedTimeframe,
)
from app.services.market_history.model import (
    ADJ_ADJUSTED,
    CLASS_CRYPTO,
    EQUITY_DERIVED,
    EQUITY_NATIVE_TIMEFRAMES,
    ORIGIN_DERIVED,
    SESSION_24X7,
    SOURCE_EQUITY,
    SOURCE_SPOT,
    HistoryError,
    SeriesNotSupported,
    SeriesRef,
    SeriesSpec,
    crypto_spec,
    iso,
    legacy_source_label,
    series_note,
    timeframe_delta,
    to_utc,
)
from app.services.market_history.rate_limit import CollectionLease, PostgresRateLimiter

logger = logging.getLogger(__name__)

# Tolerância 1e-9 relativa (design, decisão 11).
CHANGE_TOLERANCE = 1e-9
DEFAULT_EQUITY_INTRADAY_DAYS = 365
MAX_PAGES_PER_CALL = 400
# Coleta "em andamento" sem sinal há mais que isso não conta como andamento.
RUNNING_FRESH_SECONDS = 180
UPDATE_TTL_SECONDS = 30.0
CRYPTO_INTRADAY_LIMIT_DAYS = 900
CRYPTO_INCEPTION = pd.Timestamp("2017-01-01", tz="UTC")
# A atualização rebusca uma página (1.000 candles) já guardada e a compara com o que existe.
CRYPTO_VERIFY_CANDLES = 1000


@dataclass
class EnsureResult:
    status: str  # ok | failed | waiting | paused
    pages: int = 0
    candles_written: int = 0
    version_changed: bool = False
    error_code: str | None = None
    error: str | None = None


@dataclass
class HistoryResult:
    series: SeriesRef
    candles: pd.DataFrame
    coverage: dict[str, Any]
    ensure: EnsureResult | None = None

    @property
    def data_version(self) -> int:
        return self.series.data_version


def _close_enough(a: float, b: float) -> bool:
    if a == b:
        return True
    scale = max(abs(a), abs(b), 1e-12)
    return abs(a - b) / scale <= CHANGE_TOLERANCE


PRICE_COLUMNS = ("open", "high", "low", "close")
ALL_COLUMNS = ("open", "high", "low", "close", "volume")


def frames_differ(
    stored: pd.DataFrame, fresh: pd.DataFrame, columns: tuple[str, ...] = ALL_COLUMNS
) -> bool:
    """True se algum candle presente nos dois lados mudou (acima da tolerância)."""

    common = stored.index.intersection(fresh.index)
    if len(common) == 0:
        return False
    a = stored.loc[common]
    b = fresh.loc[common]
    for column in columns:
        for x, y in zip(a[column].tolist(), b[column].tolist()):
            if not _close_enough(float(x), float(y)):
                return True
    return False


def _bars_frame(bars: list[EquityBar]) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "candle_time": pd.to_datetime([b.t for b in bars], unit="ms", utc=True),
            "open": [b.o for b in bars],
            "high": [b.h for b in bars],
            "low": [b.l for b in bars],
            "close": [b.c for b in bars],
            "volume": [b.v for b in bars],
            "ct": [b.ct for b in bars],
        }
    )
    return frame.set_index("candle_time")


def equity_candles(bars: list[EquityBar], timeframe: str, now_ms: int) -> pd.DataFrame:
    """Candles que entram na série: fechados e dentro do pregão regular (decisão 8).

    Pré, pós-mercado, noturno e dias sem pregão ficam de fora sem virar lacuna.
    """

    empty = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    empty.index = pd.DatetimeIndex([], tz="UTC", name="candle_time")
    if not bars:
        return empty
    frame = _bars_frame(bars)
    frame = frame[frame["ct"] < now_ms].drop(columns=["ct"])
    if frame.empty:
        return empty
    idx = pd.DatetimeIndex(frame.index)
    if timeframe == "5m":
        mask = cal.regular_5m_mask(idx).to_numpy()
    elif timeframe == "1d":
        table = cal.session_table()
        keep = []
        for ts in idx:
            local_day = ts.tz_convert(cal.NY).date()
            keep.append(local_day in table.index and ts == cal.ny_midnight_utc(local_day))
        mask = pd.Series(keep).to_numpy()
    else:
        raise UnsupportedTimeframe(f"Timeframe {timeframe} não é coletado para ações e ETFs.")
    return frame[mask]


class CcxtOhlcvClient:
    """Cliente CCXT da Binance Spot (cripto continua por aqui; ``enableRateLimit``)."""

    def __init__(self) -> None:
        self._exchange = None

    def _ex(self):
        if self._exchange is None:
            import ccxt

            self._exchange = ccxt.binance({"enableRateLimit": True})
        return self._exchange

    def fetch(
        self, symbol: str, timeframe: str, since_ms: int, limit: int = 1000
    ) -> list[list[float]]:
        return self._ex().fetch_ohlcv(symbol, timeframe, since=since_ms, limit=limit)


class HistoryService:
    def __init__(
        self,
        engine: Engine | None = None,
        *,
        equity_provider: BinanceEquityProvider | None = None,
        ccxt_client: Any | None = None,
        limiter: PostgresRateLimiter | None = None,
        clock: Callable[[], datetime] | None = None,
        lease_wait_seconds: float = 30.0,
        update_ttl_seconds: float = UPDATE_TTL_SECONDS,
    ) -> None:
        if engine is None:
            from app.database import engine as app_engine

            engine = app_engine
        self.engine = engine
        self._equity = equity_provider
        self._ccxt = ccxt_client
        self._limiter = limiter
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self.lease_wait_seconds = lease_wait_seconds
        self.update_ttl_seconds = update_ttl_seconds

    # -- dependências preguiçosas ----------------------------------------------

    @property
    def equity_provider(self) -> BinanceEquityProvider:
        if self._equity is None:
            limiter = self._limiter or PostgresRateLimiter(self.engine)
            self._equity = BinanceEquityProvider(limiter=limiter)
        return self._equity

    @property
    def ccxt_client(self) -> Any:
        if self._ccxt is None:
            self._ccxt = CcxtOhlcvClient()
        return self._ccxt

    def _now(self) -> pd.Timestamp:
        return pd.Timestamp(self._clock()).tz_convert("UTC")

    # -- identidade --------------------------------------------------------------

    def resolve(self, spec: SeriesSpec) -> SeriesRef:
        self._validate_spec(spec)
        with self.engine.begin() as conn:
            return store.get_or_create_series(conn, spec)

    def find(self, spec: SeriesSpec) -> SeriesRef | None:
        with self.engine.connect() as conn:
            return store.find_series(conn, spec)

    @staticmethod
    def _validate_spec(spec: SeriesSpec) -> None:
        if spec.source == SOURCE_EQUITY:
            if (
                spec.timeframe not in EQUITY_NATIVE_TIMEFRAMES
                and spec.timeframe not in EQUITY_DERIVED
            ):
                raise SeriesNotSupported(
                    f"Timeframe {spec.timeframe} de ação/ETF entra com as análises dessas classes.",
                    code="timeframe_not_supported",
                )
        elif spec.source == SOURCE_SPOT:
            timeframe_delta(spec.timeframe)

    # -- leitura -----------------------------------------------------------------

    def read(
        self,
        series: SeriesRef,
        start: Any = None,
        end: Any = None,
        *,
        limit: int | None = None,
    ) -> HistoryResult:
        start_ts, end_ts = to_utc(start), to_utc(end)
        with self.engine.connect() as conn:
            series = store.refresh_series(conn, series)
            if series.is_derived:
                pad = pd.Timedelta(minutes=15)
                raw_start = start_ts - pad if start_ts is not None else None
                five = store.read_frame(conn, series.series_id, raw_start, end_ts)
                coverage_row = store.get_coverage(conn, series.series_id)
                up_to = (
                    pd.Timestamp(coverage_row["last_candle"]) + pd.Timedelta(minutes=5)
                    if coverage_row and coverage_row["last_candle"] is not None
                    else None
                )
                derived = cal.derive_15m(five, up_to=up_to)
                candles = derived.candles
                if start_ts is not None:
                    candles = candles[candles.index >= start_ts]
                if end_ts is not None:
                    candles = candles[candles.index <= end_ts]
                if limit:
                    candles = candles.iloc[-int(limit) :]
                incomplete = [
                    (a, b, n)
                    for a, b, n in derived.incomplete
                    if (start_ts is None or b > start_ts) and (end_ts is None or a <= end_ts)
                ]
            else:
                candles = store.read_frame(conn, series.series_id, start_ts, end_ts, limit=limit)
                incomplete = []
            coverage = self._coverage(conn, series, start_ts, end_ts, candles, incomplete)
        return HistoryResult(series=series, candles=candles, coverage=coverage)

    def _coverage(
        self,
        conn,
        series: SeriesRef,
        start: pd.Timestamp | None,
        end: pd.Timestamp | None,
        candles: pd.DataFrame,
        incomplete: list[tuple[pd.Timestamp, pd.Timestamp, int]],
    ) -> dict[str, Any]:
        cov = store.get_coverage(conn, series.series_id)
        fetch = store.get_fetch(conn, series.series_id) or {}
        return build_coverage(series, cov, fetch, start, end, candles, incomplete, now=self._now())

    # -- coleta ------------------------------------------------------------------

    def history(
        self,
        series: SeriesRef,
        start: Any = None,
        end: Any = None,
        *,
        limit: int | None = None,
        ensure: bool = True,
        budget_seconds: float | None = None,
        allow_large_backfill: bool = False,
        full_history_if_empty: bool = True,
    ) -> HistoryResult:
        outcome = None
        if ensure:
            outcome = self.ensure(
                series,
                start,
                end,
                budget_seconds=budget_seconds,
                allow_large_backfill=allow_large_backfill,
                full_history_if_empty=full_history_if_empty,
            )
        result = self.read(series, start, end, limit=limit)
        result.ensure = outcome
        return result

    def ensure(
        self,
        series: SeriesRef,
        start: Any = None,
        end: Any = None,
        *,
        budget_seconds: float | None = None,
        allow_large_backfill: bool = False,
        full_history_if_empty: bool = True,
        force_update: bool = False,
    ) -> EnsureResult:
        start_ts, end_ts = to_utc(start), to_utc(end)
        if series.is_equity:
            return self._ensure_equity(series, start_ts, end_ts, budget_seconds, force_update)
        return self._ensure_crypto(
            series, start_ts, end_ts, allow_large_backfill, full_history_if_empty, force_update
        )

    # ---- ação e ETF ------------------------------------------------------------

    def _equity_window_start(
        self, series: SeriesRef, start: pd.Timestamp | None
    ) -> pd.Timestamp | None:
        if start is not None:
            return start
        if series.physical_timeframe == "5m":
            return self._now() - pd.Timedelta(days=DEFAULT_EQUITY_INTRADAY_DAYS)
        return None  # 1d: o histórico inteiro

    def _record_failure(self, series_id: int, exc: BaseException, code: str) -> None:
        try:
            with self.engine.begin() as conn:
                fetch = store.get_fetch(conn, series_id) or {}
                store.set_fetch(
                    conn,
                    series_id,
                    state="failed",
                    last_error_code=code,
                    last_error=str(exc)[:500],
                    attempts=int(fetch.get("attempts") or 0) + 1,
                )
        except Exception:  # pragma: no cover - o erro original importa mais
            logger.exception("Não foi possível registrar a falha da coleta %s", series_id)

    def _ensure_equity(
        self,
        series: SeriesRef,
        start: pd.Timestamp | None,
        end: pd.Timestamp | None,
        budget_seconds: float | None,
        force_update: bool,
    ) -> EnsureResult:
        phys = series if not series.is_derived else series
        window_start = self._equity_window_start(series, start)
        deadline = time.monotonic() + budget_seconds if budget_seconds else None
        result = EnsureResult(status="ok")
        with CollectionLease(
            self.engine, series.series_id, wait_seconds=self.lease_wait_seconds
        ) as lease:
            if not lease.acquired:
                result.status = "waiting"
                return result
            now = self._now()
            with self.engine.begin() as conn:
                fetch = store.get_fetch(conn, series.series_id) or {}
                store.set_fetch(
                    conn,
                    series.series_id,
                    state="running",
                    started_at=now,
                    requested_since=window_start,
                    requested_until=end,
                    requested_at=now,
                )
                store.record_request(conn, series, window_start, end)
            try:
                self._equity_update_tail(series, result, deadline, force_update, fetch)
                self._equity_backfill(series, window_start, result, deadline)
                state = "paused" if result.status == "paused" else "idle"
                with self.engine.begin() as conn:
                    store.recompute_coverage(conn, store.refresh_series(conn, series))
                    updates: dict[str, Any] = {"state": state}
                    if state == "idle":
                        updates.update(last_error_code=None, last_error=None, attempts=0)
                    store.set_fetch(conn, series.series_id, **updates)
            except BinanceEquityError as exc:
                result.status = "failed"
                result.error_code, result.error = exc.code, str(exc)
                self._record_failure(series.series_id, exc, exc.code)
                self._safe_recompute(series)
            except Exception as exc:
                logger.exception("Coleta de %s falhou", series.asset_id)
                result.status = "failed"
                result.error_code, result.error = "internal_error", str(exc)
                self._record_failure(series.series_id, exc, "internal_error")
                self._safe_recompute(series)
        return result

    def _safe_recompute(self, series: SeriesRef) -> None:
        try:
            with self.engine.begin() as conn:
                store.recompute_coverage(conn, store.refresh_series(conn, series))
        except Exception:  # pragma: no cover
            logger.exception("Cobertura de %s não pôde ser recalculada", series.series_id)

    def _write_equity_page(
        self,
        series: SeriesRef,
        candles: pd.DataFrame,
        *,
        cursor: int | None,
        pages_inc: int,
        expect_cursor_change: bool = True,
    ) -> int:
        """Grava os candles da página e avança o cursor na mesma transação."""

        with self.engine.begin() as conn:
            written = store.upsert_candles(conn, series, candles, legacy_source="binance_equity")
            if cursor is not None:
                fetch = store.get_fetch(conn, series.series_id) or {}
                store.set_fetch(
                    conn,
                    series.series_id,
                    cursor_end_ms=cursor,
                    pages_done=int(fetch.get("pages_done") or 0) + pages_inc,
                )
        return written

    def _equity_update_tail(
        self,
        series: SeriesRef,
        result: EnsureResult,
        deadline: float | None,
        force_update: bool,
        fetch: dict[str, Any],
    ) -> None:
        """Página mais recente primeiro; anda para trás até sobrepor o que existe."""

        provider = self.equity_provider
        tf = series.physical_timeframe
        now = self._now()
        with self.engine.connect() as conn:
            first_stored, last_stored, count = store.stored_extent(conn, series.series_id)
        checked = to_utc(fetch.get("checked_at")) if fetch else None
        if (
            count
            and not force_update
            and checked is not None
            and (now - checked).total_seconds() < self.update_ttl_seconds
        ):
            return
        now_ms = int(now.timestamp() * 1000)
        page = provider.fetch_page(series.symbol, tf, end_time=None, adjustment=series.adjustment)
        result.pages += page.requests
        if not page.bars:
            # Sem nenhum candle: a Binance não tem este ativo/timeframe.
            with self.engine.begin() as conn:
                store.set_fetch(conn, series.series_id, reached_start=True, checked_at=now)
            return
        candles = equity_candles(page.bars, tf, now_ms)
        if count == 0:
            written = self._write_equity_page(series, candles, cursor=page.min_t - 1, pages_inc=1)
            result.candles_written += written
            with self.engine.begin() as conn:
                store.set_fetch(conn, series.series_id, checked_at=now)
            return

        last_ts = pd.Timestamp(last_stored).tz_convert("UTC")
        last_ms = int(last_ts.timestamp() * 1000)
        guard = 0
        while True:
            guard += 1
            if guard > MAX_PAGES_PER_CALL:
                raise BinanceFormatChanged("a atualização não alcançou o que já estava guardado")
            if candles.empty:
                stored = candles
            else:
                with self.engine.connect() as conn:
                    stored = store.read_frame(conn, series.series_id, candles.index.min(), last_ts)
                # Preço de candle antigo mudou (split, dividendo, correção): recoleta com nova versão.
                if frames_differ(stored, candles[candles.index <= last_ts], PRICE_COLUMNS):
                    self._equity_rebuild(series, result, deadline, first_stored)
                    return
            fresh = candles[(candles.index > last_ts) | (~candles.index.isin(stored.index))]
            # Volume revisado de candle já guardado é atualizado no lugar (sem nova versão).
            revised = candles[candles.index.isin(stored.index)]
            if not fresh.empty or not revised.empty:
                result.candles_written += self._write_equity_page(
                    series, pd.concat([fresh, revised]).sort_index(), cursor=None, pages_inc=0
                )
            if page.min_t <= last_ms:
                break
            if deadline and time.monotonic() > deadline:
                result.status = "paused"
                return
            page = provider.fetch_page(
                series.symbol, tf, end_time=page.min_t - 1, adjustment=series.adjustment
            )
            result.pages += page.requests
            if not page.bars:
                break
            candles = equity_candles(page.bars, tf, now_ms)
        with self.engine.begin() as conn:
            store.set_fetch(conn, series.series_id, checked_at=now)

    def _equity_backfill(
        self,
        series: SeriesRef,
        window_start: pd.Timestamp | None,
        result: EnsureResult,
        deadline: float | None,
    ) -> None:
        if result.status == "paused":
            return
        provider = self.equity_provider
        tf = series.physical_timeframe
        now_ms = int(self._now().timestamp() * 1000)
        with self.engine.connect() as conn:
            fetch = store.get_fetch(conn, series.series_id) or {}
            first_stored, _, count = store.stored_extent(conn, series.series_id)
        if fetch.get("reached_start"):
            return
        cursor = fetch.get("cursor_end_ms")
        if cursor is None:
            if count == 0:
                return
            cursor = int(pd.Timestamp(first_stored).timestamp() * 1000) - 1
        start_ms = int(window_start.timestamp() * 1000) if window_start is not None else None
        # Já cobre o pedido: nada a buscar.
        if (
            start_ms is not None
            and count
            and int(pd.Timestamp(first_stored).timestamp() * 1000) <= start_ms
        ):
            return
        guard = 0
        while True:
            guard += 1
            if guard > MAX_PAGES_PER_CALL:
                result.status = "paused"
                return
            if deadline and time.monotonic() > deadline:
                result.status = "paused"
                return
            page = provider.fetch_page(
                series.symbol, tf, end_time=cursor, adjustment=series.adjustment
            )
            result.pages += page.requests
            if not page.bars:
                if page.confirmed_empty:
                    with self.engine.begin() as conn:
                        first, _, _ = store.stored_extent(conn, series.series_id)
                        store.set_fetch(
                            conn,
                            series.series_id,
                            reached_start=True,
                            binance_earliest=first,
                        )
                return
            if page.min_t - 1 >= cursor:
                raise BinanceFormatChanged("a paginação não andou para trás")
            candles = equity_candles(page.bars, tf, now_ms)
            cursor = page.min_t - 1
            result.candles_written += self._write_equity_page(
                series, candles, cursor=cursor, pages_inc=1
            )
            if start_ms is not None and page.min_t <= start_ms:
                return

    def _equity_rebuild(
        self,
        series: SeriesRef,
        result: EnsureResult,
        deadline: float | None,
        first_stored: Any,
    ) -> None:
        """Correção/split/dividendo: recoleta numa tabela de preparo e troca numa transação."""

        provider = self.equity_provider
        tf = series.physical_timeframe
        token = uuid.uuid4().hex
        now_ms = int(self._now().timestamp() * 1000)
        floor_ms = int(pd.Timestamp(first_stored).timestamp() * 1000)
        end_time: int | None = None
        pages = 0
        reached = False
        try:
            while True:
                pages += 1
                if pages > MAX_PAGES_PER_CALL:
                    raise BinanceFormatChanged("a recoleta não terminou")
                page = provider.fetch_page(
                    series.symbol, tf, end_time=end_time, adjustment=series.adjustment
                )
                result.pages += page.requests
                if not page.bars:
                    reached = page.confirmed_empty
                    break
                candles = equity_candles(page.bars, tf, now_ms)
                if not candles.empty:
                    with self.engine.begin() as conn:
                        for start in range(0, len(candles), 2000):
                            chunk = candles.iloc[start : start + 2000]
                            conn.execute(
                                text(
                                    "INSERT INTO market_series_stage "
                                    "(series_id, stage_token, candle_time, open, high, low, close, volume) "
                                    "VALUES (:s, :t, :c, :o, :h, :l, :cl, :v) "
                                    "ON CONFLICT DO NOTHING"
                                ),
                                [
                                    {
                                        "s": series.series_id,
                                        "t": token,
                                        "c": ts.to_pydatetime(),
                                        "o": o,
                                        "h": h,
                                        "l": l,
                                        "cl": c,
                                        "v": v,
                                    }
                                    for ts, o, h, l, c, v in zip(
                                        chunk.index,
                                        chunk["open"],
                                        chunk["high"],
                                        chunk["low"],
                                        chunk["close"],
                                        chunk["volume"],
                                    )
                                ],
                            )
                end_time = page.min_t - 1
                if page.min_t <= floor_ms:
                    break
            with self.engine.begin() as conn:
                table = store.ohlcv_table(conn)
                conn.execute(
                    text(f"DELETE FROM {table} WHERE series_id = :s"), {"s": series.series_id}
                )
                conn.execute(
                    text(
                        f"INSERT INTO {table} (series_id, candle_time, open, high, low, close, volume, "
                        "symbol, timeframe, source) "
                        "SELECT series_id, candle_time, open, high, low, close, volume, "
                        ":sym, :tf, :src FROM market_series_stage "
                        "WHERE series_id = :s AND stage_token = :t"
                    ),
                    {
                        "s": series.series_id,
                        "t": token,
                        "sym": series.symbol,
                        "tf": tf,
                        "src": "binance_equity",
                    },
                )
                new_series = store.bump_version(conn, series)
                first, _, count = store.stored_extent(conn, series.series_id)
                fetch_updates: dict[str, Any] = {
                    "cursor_end_ms": (
                        int(pd.Timestamp(first).timestamp() * 1000) - 1 if count else None
                    ),
                    "checked_at": self._now(),
                }
                if reached:
                    fetch_updates.update(reached_start=True, binance_earliest=first)
                store.set_fetch(conn, series.series_id, **fetch_updates)
                store.recompute_coverage(conn, new_series)
            result.version_changed = True
        finally:
            with self.engine.begin() as conn:
                conn.execute(
                    text(
                        "DELETE FROM market_series_stage WHERE series_id = :s AND stage_token = :t"
                    ),
                    {"s": series.series_id, "t": token},
                )

    # ---- cripto ----------------------------------------------------------------

    def _download_crypto(
        self, symbol: str, timeframe: str, since_ms: int, until_ms: int
    ) -> pd.DataFrame:
        client = self.ccxt_client
        rows: list[list[float]] = []
        current = since_ms
        guard = 0
        while current < until_ms:
            guard += 1
            if guard > 5000:
                break
            batch = None
            for attempt in range(3):
                try:
                    batch = client.fetch(symbol, timeframe, current, 1000)
                    break
                except Exception as exc:  # rede/limite da exchange
                    if attempt == 2:
                        raise HistoryError(
                            f"Binance Spot indisponível: {exc}", code="binance_unavailable"
                        ) from exc
                    time.sleep(1.0 + attempt)
            if not batch:
                break
            rows.extend(batch)
            last_ts = int(batch[-1][0])
            if last_ts + 1 <= current:
                break
            current = last_ts + 1
            if len(batch) < 1000:
                break
        if not rows:
            empty = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
            empty.index = pd.DatetimeIndex([], tz="UTC", name="candle_time")
            return empty
        frame = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close", "volume"])
        frame = frame.drop_duplicates("ts", keep="last").sort_values("ts")
        frame["candle_time"] = pd.to_datetime(frame["ts"], unit="ms", utc=True)
        return frame.drop(columns=["ts"]).set_index("candle_time")

    def _ensure_crypto(
        self,
        series: SeriesRef,
        start: pd.Timestamp | None,
        end: pd.Timestamp | None,
        allow_large_backfill: bool,
        full_history_if_empty: bool,
        force_update: bool,
    ) -> EnsureResult:
        tf = series.physical_timeframe
        step = pd.Timedelta(timeframe_delta(tf))
        result = EnsureResult(status="ok")
        now = self._now()
        with CollectionLease(
            self.engine, series.series_id, slots=None, wait_seconds=self.lease_wait_seconds
        ) as lease:
            if not lease.acquired:
                result.status = "waiting"
                return result
            with self.engine.begin() as conn:
                first_stored, last_stored, count = store.stored_extent(conn, series.series_id)
                fetch = store.get_fetch(conn, series.series_id) or {}
                store.set_fetch(
                    conn,
                    series.series_id,
                    state="running",
                    started_at=now,
                    requested_since=start,
                    requested_until=end,
                    requested_at=now,
                )
                store.record_request(conn, series, start, end)
            try:
                until_ms = (
                    int((end or now).timestamp() * 1000)
                    if end is not None
                    else int(now.timestamp() * 1000)
                )
                until_ms = max(until_ms, int(now.timestamp() * 1000)) if end is None else until_ms
                # cauda
                if count == 0:
                    if start is not None:
                        since = start
                    elif full_history_if_empty:
                        since = CRYPTO_INCEPTION
                    else:
                        since = now - pd.Timedelta(days=CRYPTO_INTRADAY_LIMIT_DAYS)
                    fresh = self._download_crypto(
                        series.symbol, tf, int(since.timestamp() * 1000), until_ms
                    )
                    result.pages += 1
                    self._write_crypto(series, fresh, None, result)
                    if (
                        start is not None
                        and not fresh.empty
                        and fresh.index.min() > start + 2 * step
                    ):
                        with self.engine.begin() as conn:
                            store.set_fetch(
                                conn,
                                series.series_id,
                                reached_start=True,
                                binance_earliest=fresh.index.min(),
                            )
                else:
                    last_ts = pd.Timestamp(last_stored).tz_convert("UTC")
                    needs_tail = force_update or (now - last_ts) >= step
                    if needs_tail:
                        since = last_ts - step * (CRYPTO_VERIFY_CANDLES - 1)
                        if first_stored is not None:
                            since = max(since, pd.Timestamp(first_stored).tz_convert("UTC"))
                        fresh = self._download_crypto(
                            series.symbol, tf, int(since.timestamp() * 1000), until_ms
                        )
                        result.pages += 1
                        self._write_crypto(series, fresh, last_ts, result)
                    # cabeça
                    requested_days = ((end or now) - start).days if start is not None else 0
                    head_allowed = (
                        start is not None
                        and pd.Timestamp(first_stored) > start + step
                        and not fetch.get("reached_start")
                        and (
                            not (tf.endswith("m") or tf.endswith("h"))
                            or requested_days <= CRYPTO_INTRADAY_LIMIT_DAYS
                            or allow_large_backfill
                        )
                    )
                    if head_allowed:
                        old = self._download_crypto(
                            series.symbol,
                            tf,
                            int(start.timestamp() * 1000),
                            int(pd.Timestamp(first_stored).timestamp() * 1000),
                        )
                        result.pages += 1
                        older = (
                            old[old.index < pd.Timestamp(first_stored)] if not old.empty else old
                        )
                        self._write_crypto(series, older, None, result)
                        reached = older.empty or older.index.min() > start + 2 * step
                        if reached:
                            with self.engine.begin() as conn:
                                new_first, _, _ = store.stored_extent(conn, series.series_id)
                                store.set_fetch(
                                    conn,
                                    series.series_id,
                                    reached_start=True,
                                    binance_earliest=new_first,
                                )
                with self.engine.begin() as conn:
                    store.set_fetch(
                        conn,
                        series.series_id,
                        state="idle",
                        last_error_code=None,
                        last_error=None,
                        attempts=0,
                        checked_at=now,
                    )
                    conn.execute(
                        text(
                            "UPDATE market_series_coverage SET updated_at = now() WHERE series_id = :s"
                        ),
                        {"s": series.series_id},
                    )
            except HistoryError as exc:
                result.status = "failed"
                result.error_code, result.error = exc.code, str(exc)
                self._record_failure(series.series_id, exc, exc.code)
            except Exception as exc:
                logger.exception("Coleta de %s falhou", series.asset_id)
                result.status = "failed"
                result.error_code, result.error = "internal_error", str(exc)
                self._record_failure(series.series_id, exc, "internal_error")
        return result

    def ingest_frame(self, series: SeriesRef, frame: pd.DataFrame) -> int:
        """Entrada do escritor canônico de cripto: grava, detecta correção e estende a cobertura."""

        with self.engine.connect() as conn:
            _, last, _ = store.stored_extent(conn, series.series_id)
        previous_last = pd.Timestamp(last).tz_convert("UTC") if last is not None else None
        result = EnsureResult(status="ok")
        self._write_crypto(series, frame, previous_last, result)
        return result.candles_written

    def _write_crypto(
        self,
        series: SeriesRef,
        frame: pd.DataFrame,
        previous_last: pd.Timestamp | None,
        result: EnsureResult,
    ) -> None:
        if frame is None or frame.empty:
            return
        with self.engine.begin() as conn:
            changed = False
            if previous_last is not None:
                older = frame[frame.index < previous_last]
                if not older.empty:
                    stored = store.read_frame(
                        conn, series.series_id, older.index.min(), older.index.max()
                    )
                    changed = frames_differ(stored, older)
            result.candles_written += store.upsert_candles(
                conn, series, frame, legacy_source=legacy_source_label(series.source)
            )
            current = series
            if changed:
                current = store.bump_version(conn, series)
                result.version_changed = True
            store.extend_coverage_tail(conn, current, frame.index)
            if changed:
                conn.execute(
                    text(
                        "UPDATE market_series_coverage SET data_version = :v WHERE series_id = :s"
                    ),
                    {"v": current.data_version, "s": series.series_id},
                )


def build_coverage(
    series: SeriesRef,
    cov: dict[str, Any] | None,
    fetch: dict[str, Any],
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
    candles: pd.DataFrame,
    incomplete: list[tuple[pd.Timestamp, pd.Timestamp, int]],
    *,
    now: pd.Timestamp,
) -> dict[str, Any]:
    """Dicionário de cobertura devolvido por toda consulta (spec ``market-history``)."""

    cov = cov or {}
    first = to_utc(cov.get("first_candle"))
    last = to_utc(cov.get("last_candle"))
    gaps = list(cov.get("gaps") or [])
    gap_count = int(cov.get("gap_count") or 0)
    inherited: list[dict[str, Any]] = []
    if series.is_derived:
        inherited = inherit_gaps_15m(gaps)
        # Blocos incompletos vistos na janela lida entram se ainda não estão na lista.
        known = {g["start"] for g in inherited}
        for a, b, n in incomplete:
            key = a.strftime("%Y-%m-%dT%H:%M:%SZ")
            if key not in known:
                inherited.append(
                    {
                        "start": key,
                        "end": (b - pd.Timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "count": 1,
                        "inherited_from": "5m",
                    }
                )
        gaps = inherited
        gap_count = 0  # herdadas não somam no resumo da linha (decisão 9)
    window_gaps = [g for g in gaps if _gap_in_window(g, start, end)]

    state = fetch.get("state") or "idle"
    updated = to_utc(fetch.get("updated_at"))
    running_fresh = (
        state == "running"
        and updated is not None
        and (now - updated).total_seconds() < RUNNING_FRESH_SECONDS
    )
    reached = bool(fetch.get("reached_start"))
    tolerance = (
        pd.Timedelta(days=5)
        if series.session != SESSION_24X7
        else pd.Timedelta(timeframe_delta(series.physical_timeframe)) * 2
    )
    insufficient = bool(
        start is not None and first is not None and reached and first > start + tolerance
    )
    incomplete_flag = bool(
        start is not None and first is not None and not reached and first > start + tolerance
    )
    if first is None:
        status = "collecting" if running_fresh else ("failed" if state == "failed" else "empty")
    elif running_fresh:
        status = "collecting"
    elif state == "failed":
        status = "failed"
    elif insufficient or incomplete_flag or state == "paused":
        status = "partial"
    else:
        status = "covered"

    error = None
    if state == "failed":
        error = {
            "code": fetch.get("last_error_code"),
            "message": fetch.get("last_error"),
            "at": iso(fetch.get("updated_at")),
        }

    version = series.data_version
    from app.services.market_history.nyse_calendar import DERIVED_15M_RULE_VERSION

    return {
        "series": series.as_dict(),
        "requested": {"start": iso(start), "end": iso(end)},
        "covered": {
            "start": iso(first),
            "end": iso(last),
            "candles": (
                int(len(candles)) if candles is not None else int(cov.get("candle_count") or 0)
            ),
            "total_candles": int(cov.get("candle_count") or 0),
        },
        "gaps": window_gaps,
        "gap_count": gap_count if not series.is_derived else 0,
        "inherited_gap_count": len(inherited) if series.is_derived else 0,
        "updated_at": iso(cov.get("updated_at")),
        "data_version": version,
        "version_label": (
            f"{version}+r{DERIVED_15M_RULE_VERSION}" if series.is_derived else str(version)
        ),
        "rule_version": DERIVED_15M_RULE_VERSION if series.is_derived else None,
        "origin": series.origin,
        "derived_from": series.physical_timeframe if series.is_derived else None,
        "insufficient": insufficient,
        "incomplete": incomplete_flag or state == "paused",
        "status": status,
        "history_starts_at": iso(fetch.get("binance_earliest")) if reached else None,
        "reached_start": reached,
        "collection": {
            "state": state,
            "pages_done": int(fetch.get("pages_done") or 0),
            "requested_at": iso(fetch.get("requested_at")),
            "checked_at": iso(fetch.get("checked_at")),
        },
        "error": error,
        "note": series_note(series),
        "calendar_timezone": cal.NY.key if series.session != SESSION_24X7 else None,
    }


def _gap_in_window(
    gap: dict[str, Any], start: pd.Timestamp | None, end: pd.Timestamp | None
) -> bool:
    g_start, g_end = to_utc(gap["start"]), to_utc(gap["end"])
    if start is not None and g_end < start:
        return False
    if end is not None and g_start > end:
        return False
    return True


def inherit_gaps_15m(gaps_5m: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Lacuna do 5m vista como bloco de 15m: "herdada do 5m" (decisão 9)."""

    out: list[dict[str, Any]] = []
    block = pd.Timedelta(minutes=15)
    for gap in gaps_5m:
        g_start, g_end = to_utc(gap["start"]), to_utc(gap["end"])
        day = g_start.tz_convert(cal.NY).date()
        window = cal.session_window(day)
        if window is None:
            continue
        first_block = window.open_utc + block * int((g_start - window.open_utc) // block)
        end_day = g_end.tz_convert(cal.NY).date()
        end_window = cal.session_window(end_day) or window
        last_block_start = end_window.open_utc + block * int((g_end - end_window.open_utc) // block)
        last_block_end = min(last_block_start + block, end_window.close_utc)
        out.append(
            {
                "start": first_block.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end": last_block_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "block_end": last_block_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "count": max(1, int((last_block_start - first_block) / block) + 1),
                "inherited_from": "5m",
            }
        )
    return out
