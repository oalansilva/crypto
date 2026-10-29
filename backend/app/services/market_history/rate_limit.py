"""Limitador compartilhado da Binance de ações e travas de coleta (card #1118).

* Balde de fichas numa linha de ``market_rate_limit`` (uma por fonte),
  ``SELECT ... FOR UPDATE``: vale entre processos e workers (design, decisão 7).
* 429/418 respeitam ``Retry-After``; três falhas seguidas abrem o circuito por
  5 minutos.
* No máximo 2 séries coletando ao mesmo tempo e uma coleta por série, por
  advisory locks de sessão: caem sozinhos se o processo morre.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.services.market_history.equity_provider import (
    BinanceCircuitOpen,
    BinanceRateLimited,
)
from app.services.market_history.schema import LOCK_NAMESPACE_SERIES, LOCK_NAMESPACE_SLOT

logger = logging.getLogger(__name__)

EQUITY_SOURCE = "binance_equity"
DEFAULT_RATE_PER_SECOND = 2.0
DEFAULT_CIRCUIT_SECONDS = 300.0
DEFAULT_FAILURE_THRESHOLD = 3
DEFAULT_RETRY_AFTER_SECONDS = 60.0
MAX_CONCURRENT_SERIES = 2


class PostgresRateLimiter:
    """Balde de fichas: ``rate`` requisições por segundo, sem rajada acima de 1."""

    def __init__(
        self,
        engine: Engine,
        *,
        source: str = EQUITY_SOURCE,
        rate_per_second: float = DEFAULT_RATE_PER_SECOND,
        capacity: float = 1.0,
        failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
        circuit_seconds: float = DEFAULT_CIRCUIT_SECONDS,
        clock: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.engine = engine
        self.source = source
        self.rate = float(rate_per_second)
        self.capacity = float(capacity)
        self.failure_threshold = int(failure_threshold)
        self.circuit_seconds = float(circuit_seconds)
        self.clock = clock
        self.sleep = sleep

    def _lock_row(self, conn):
        conn.execute(
            text(
                "INSERT INTO market_rate_limit (source, tokens, refilled_at) "
                "VALUES (:s, :cap, 0) ON CONFLICT (source) DO NOTHING"
            ),
            {"s": self.source, "cap": self.capacity},
        )
        return conn.execute(
            text(
                "SELECT tokens, refilled_at, blocked_until, consecutive_failures, "
                "circuit_open_until FROM market_rate_limit WHERE source = :s FOR UPDATE"
            ),
            {"s": self.source},
        ).one()

    def acquire(self) -> None:
        """Espera a próxima ficha. Bloqueio por ``Retry-After`` ou circuito levanta."""

        while True:
            with self.engine.begin() as conn:
                row = self._lock_row(conn)
                now = self.clock()
                if row.circuit_open_until > now:
                    raise BinanceCircuitOpen(row.circuit_open_until)
                if row.blocked_until > now:
                    raise BinanceRateLimited(429, row.blocked_until - now)
                refilled_at = row.refilled_at if row.refilled_at else now - 1.0 / self.rate
                tokens = min(self.capacity, row.tokens + max(0.0, now - refilled_at) * self.rate)
                if tokens >= 1.0:
                    conn.execute(
                        text(
                            "UPDATE market_rate_limit SET tokens = :t, refilled_at = :n "
                            "WHERE source = :s"
                        ),
                        {"t": tokens - 1.0, "n": now, "s": self.source},
                    )
                    return
                wait = (1.0 - tokens) / self.rate
                conn.execute(
                    text(
                        "UPDATE market_rate_limit SET tokens = :t, refilled_at = :n "
                        "WHERE source = :s"
                    ),
                    {"t": tokens, "n": now, "s": self.source},
                )
            self.sleep(max(0.01, wait))

    def success(self) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE market_rate_limit SET consecutive_failures = 0 WHERE source = :s "
                    "AND consecutive_failures <> 0"
                ),
                {"s": self.source},
            )

    def _register_failure(self, conn, reason: str, blocked_for: float | None) -> None:
        row = self._lock_row(conn)
        now = self.clock()
        failures = int(row.consecutive_failures) + 1
        circuit_until = row.circuit_open_until
        if failures >= self.failure_threshold:
            circuit_until = now + self.circuit_seconds
            failures = 0
            logger.warning(
                "Circuito da Binance de ações aberto por %.0f s (%s).", self.circuit_seconds, reason
            )
        blocked_until = row.blocked_until
        if blocked_for is not None:
            blocked_until = max(blocked_until, now + blocked_for)
        conn.execute(
            text(
                "UPDATE market_rate_limit SET consecutive_failures = :f, blocked_until = :b, "
                "circuit_open_until = :c, last_reason = :r WHERE source = :s"
            ),
            {
                "f": failures,
                "b": blocked_until,
                "c": circuit_until,
                "r": reason[:64],
                "s": self.source,
            },
        )

    def throttled(self, retry_after: float | None, status: int) -> None:
        with self.engine.begin() as conn:
            self._register_failure(
                conn,
                f"http_{status}",
                retry_after if retry_after is not None else DEFAULT_RETRY_AFTER_SECONDS,
            )

    def failure(self, reason: str) -> None:
        with self.engine.begin() as conn:
            self._register_failure(conn, reason, None)

    def circuit_state(self) -> dict[str, float | int | str | None]:
        with self.engine.begin() as conn:
            row = conn.execute(
                text(
                    "SELECT blocked_until, circuit_open_until, consecutive_failures, last_reason "
                    "FROM market_rate_limit WHERE source = :s"
                ),
                {"s": self.source},
            ).first()
        if row is None:
            return {"blocked_until": 0.0, "circuit_open_until": 0.0, "failures": 0, "reason": None}
        return {
            "blocked_until": row.blocked_until,
            "circuit_open_until": row.circuit_open_until,
            "failures": row.consecutive_failures,
            "reason": row.last_reason,
        }


class CollectionLease:
    """Uma coleta por série e no máximo ``slots`` séries ao mesmo tempo.

    Uso::

        with CollectionLease(engine, series_id) as lease:
            if lease.acquired: ...coleta...

    Quem não pega a trava espera até ``wait_seconds`` (lendo o que já foi gravado,
    a cargo do chamador) e sai com ``acquired = False``.
    """

    def __init__(
        self,
        engine: Engine,
        series_id: int,
        *,
        slots: int | None = MAX_CONCURRENT_SERIES,
        wait_seconds: float = 30.0,
        poll_seconds: float = 0.5,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.engine = engine
        self.series_id = int(series_id)
        self.slots = slots
        self.wait_seconds = wait_seconds
        self.poll_seconds = poll_seconds
        self.clock = clock
        self.sleep = sleep
        self.acquired = False
        self.waited = 0.0
        self._conn = None
        self._slot: int | None = None

    def _try(self, namespace: int, key: int) -> bool:
        return bool(
            self._conn.exec_driver_sql(
                "SELECT pg_try_advisory_lock(%s, %s)", (namespace, key)
            ).scalar()
        )

    def __enter__(self) -> "CollectionLease":
        started = self.clock()
        deadline = started + self.wait_seconds
        conn = self.engine.connect().execution_options(isolation_level="AUTOCOMMIT")
        self._conn = conn
        try:
            while True:
                if self._try(LOCK_NAMESPACE_SERIES, self.series_id):
                    if self.slots is None:
                        self.acquired = True
                        break
                    slot = next(
                        (s for s in range(self.slots) if self._try(LOCK_NAMESPACE_SLOT, s)), None
                    )
                    if slot is not None:
                        self._slot = slot
                        self.acquired = True
                        break
                    # Série livre, mas as 2 vagas estão ocupadas: solta a série e espera.
                    conn.exec_driver_sql(
                        "SELECT pg_advisory_unlock(%s, %s)",
                        (LOCK_NAMESPACE_SERIES, self.series_id),
                    )
                if self.clock() >= deadline:
                    break
                self.sleep(self.poll_seconds)
        except BaseException:
            self._release()
            raise
        self.waited = self.clock() - started
        if not self.acquired:
            self._release()
        return self

    def _release(self) -> None:
        conn, self._conn = self._conn, None
        if conn is None:
            return
        try:
            if self.acquired:
                if self._slot is not None:
                    conn.exec_driver_sql(
                        "SELECT pg_advisory_unlock(%s, %s)", (LOCK_NAMESPACE_SLOT, self._slot)
                    )
                conn.exec_driver_sql(
                    "SELECT pg_advisory_unlock(%s, %s)", (LOCK_NAMESPACE_SERIES, self.series_id)
                )
        finally:
            self.acquired = False
            conn.close()

    def __exit__(self, *exc) -> None:
        self._release()
