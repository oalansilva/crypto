"""Apoio dos testes do card #1118: schema privado e Binance de ações simulada."""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from decimal import Decimal
from typing import Callable

import pandas as pd
from sqlalchemy import create_engine, text

from app.services.market_history import nyse_calendar as cal
from app.services.market_history import store
from app.services.market_history.equity_provider import (
    NATIVE_TIMEFRAMES,
    BinanceBusinessError,
    BinanceEquityProvider,
    BinanceRateLimited,
    BinanceUnavailable,
    EquityBar,
    EquityPage,
)
from app.services.market_history.schema import (
    LIVE_OHLCV_TABLE,
    execute_all,
    ohlcv_table_sql,
    side_table_statements,
)


@contextmanager
def history_schema(database_url: str, *, table: str = LIVE_OHLCV_TABLE):
    """Engine ligado a um schema descartável com todas as tabelas do histórico."""

    admin = create_engine(database_url)
    schema = "hist1118_" + uuid.uuid4().hex[:10]
    with admin.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA {schema}"))
    engine = create_engine(database_url, connect_args={"options": f"-csearch_path={schema}"})
    store.reset_table_cache()
    try:
        with engine.begin() as conn:
            execute_all(conn, side_table_statements())
            execute_all(conn, ohlcv_table_sql(table))
        yield engine
    finally:
        engine.dispose()
        store.reset_table_cache()
        with admin.begin() as conn:
            conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        admin.dispose()


def _dec(value: float) -> Decimal:
    return Decimal(f"{value:.4f}")


class FakeEquityProvider(BinanceEquityProvider):
    """Série sintética no formato da rota do gráfico (dia estendido, pregão dentro)."""

    def __init__(
        self,
        *,
        sessions: pd.DatetimeIndex | None = None,
        timeframe: str = "5m",
        page_size: int = 1000,
        price: Callable[[pd.Timestamp], float] | None = None,
        drop: set[int] | None = None,
        history_start: pd.Timestamp | None = None,
        now: pd.Timestamp | None = None,
    ) -> None:
        super().__init__()
        self.timeframe = timeframe
        self.page_size = page_size
        self.price = price or (lambda ts: 100.0 + (ts.value // 10**9 % 1000) / 100.0)
        self.requests: list[dict] = []
        self.fail_with: Exception | None = None
        self.fail_after: int | None = None
        self.empty_payload_once = False
        self.drop = drop or set()
        self.history_start = history_start
        self.bars: list[EquityBar] = []
        self.now = now

    def build(self, start: pd.Timestamp, end: pd.Timestamp) -> None:
        """Gera candles de ``start`` a ``end`` (UTC), com extensão antes e depois do pregão."""

        out: list[EquityBar] = []
        if self.timeframe == "5m":
            step = pd.Timedelta(minutes=5)
            for day in cal.sessions_between(start, end):
                window = cal.session_window(day)
                t = window.open_utc - pd.Timedelta(hours=5, minutes=30)
                stop = window.close_utc + pd.Timedelta(hours=4)
                while t < stop:
                    out.append(self._bar(t, step))
                    t += step
        else:
            for day in cal.sessions_between(start, end):
                t = cal.ny_midnight_utc(day)
                out.append(self._bar(t, pd.Timedelta(days=1)))
        out = [b for b in out if b.t not in self.drop]
        if self.history_start is not None:
            floor = int(self.history_start.timestamp() * 1000)
            out = [b for b in out if b.t >= floor]
        self.bars = sorted(out, key=lambda b: b.t)

    def _bar(self, ts: pd.Timestamp, step: pd.Timedelta) -> EquityBar:
        p = self.price(ts)
        t = int(ts.timestamp() * 1000)
        return EquityBar(
            t=t,
            ct=t + int(step.total_seconds() * 1000) - 1,
            o=_dec(p),
            h=_dec(p + 0.5),
            l=_dec(p - 0.5),
            c=_dec(p + 0.1),
            v=Decimal(1000 + (t // 1000) % 97),
            session="ETH" if self.timeframe == "5m" else None,
        )

    def fetch_page_once(
        self, symbol, timeframe, *, end_time=None, adjustment="adjusted", limit=1000
    ):
        self.requests.append(
            {"symbol": symbol, "tf": timeframe, "end": end_time, "adjustment": adjustment}
        )
        if self.fail_with is not None and (
            self.fail_after is None or len(self.requests) > self.fail_after
        ):
            raise self.fail_with
        pool = [b for b in self.bars if end_time is None or b.t <= end_time]
        now_ms = int((self.now or pd.Timestamp.now(tz="UTC")).timestamp() * 1000)
        pool = [b for b in pool if b.t <= now_ms]
        page = pool[-min(limit, self.page_size) :]
        return EquityPage(symbol=symbol, timeframe=timeframe, bars=list(page), end_time=end_time)


class FakeCcxt:
    """CCXT simulado: entrega candles pré-gerados a partir de ``since``."""

    def __init__(self, frames: dict[tuple[str, str], pd.DataFrame]) -> None:
        self.frames = frames
        self.calls: list[tuple[str, str, int]] = []
        self.fail = False

    def fetch(self, symbol: str, timeframe: str, since_ms: int, limit: int = 1000):
        self.calls.append((symbol, timeframe, since_ms))
        if self.fail:
            raise RuntimeError("exchange fora do ar")
        frame = self.frames.get((symbol, timeframe))
        if frame is None:
            return []
        since = pd.Timestamp(since_ms, unit="ms", tz="UTC")
        chunk = frame[frame.index >= since].iloc[:limit]
        return [
            [int(ts.timestamp() * 1000), r.open, r.high, r.low, r.close, r.volume]
            for ts, r in chunk.iterrows()
        ]


def crypto_frame(start: str, periods: int, freq: str, base: float = 100.0) -> pd.DataFrame:
    idx = pd.date_range(start, periods=periods, freq=freq, tz="UTC", name="candle_time")
    vals = base + pd.Series(range(periods), index=idx) * 0.01
    return pd.DataFrame(
        {"open": vals, "high": vals + 1, "low": vals - 1, "close": vals + 0.5, "volume": 10.0}
    )
