"""Histórico de candles com uma só autoridade (card #1118).

PostgreSQL guarda séries identificadas por ativo, fonte, sessão, ajuste e
timeframe. Gráfico e análises leem pelo mesmo ``HistoryService``; o Parquet é
cache derivado e reconstruível.
"""

from __future__ import annotations

import os


def _flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() not in {"", "0", "false", "no", "off"}


def unified_enabled() -> bool:
    """``MARKET_HISTORY_UNIFIED=1``: consumidores leem pelo ``HistoryService``.

    Desligado, gráfico e análises voltam ao caminho antigo (rollback do design).
    """

    return _flag("MARKET_HISTORY_UNIFIED", "0")
