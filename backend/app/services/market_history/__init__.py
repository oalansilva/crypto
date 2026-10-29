"""Histórico de candles com uma só autoridade (card #1118).

PostgreSQL guarda séries identificadas por ativo, fonte, sessão, ajuste e
timeframe. Gráfico e análises leem pelo mesmo ``HistoryService``; o Parquet é
cache derivado e reconstruível.
"""

from __future__ import annotations

import contextlib
import contextvars
import os

# Card #1120 (decisão 11): o lote liga o caminho unificado por ativo, para que a cripto também
# congele a amostra, mesmo com ``MARKET_HISTORY_UNIFIED`` desligado no ambiente.
_FORCED_UNIFIED: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "market_history_forced_unified", default=False
)


def _flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() not in {"", "0", "false", "no", "off"}


def unified_enabled() -> bool:
    """``MARKET_HISTORY_UNIFIED=1``: consumidores leem pelo ``HistoryService``.

    Desligado, gráfico e análises voltam ao caminho antigo (rollback do design).
    """

    return _FORCED_UNIFIED.get() or _flag("MARKET_HISTORY_UNIFIED", "0")


@contextlib.contextmanager
def force_unified():
    """Liga o caminho unificado neste contexto (thread/tarefa), sem tocar no ambiente."""

    token = _FORCED_UNIFIED.set(True)
    try:
        yield
    finally:
        _FORCED_UNIFIED.reset(token)
