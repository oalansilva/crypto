from __future__ import annotations

import hashlib
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import FavoriteStrategy


def _direction_of(parameters: dict[str, Any] | None) -> str:
    return str((parameters or {}).get("direction") or "long").lower()


def find_existing_favorite(
    db: Session,
    *,
    user_id: str | None,
    strategy_name: str,
    symbol: str,
    timeframe: str,
    period_type: str | None,
    start_date: str | None,
    end_date: str | None,
    direction: str | None,
    data_source: str | None = None,
    asset: dict[str, Any] | None = None,
) -> FavoriteStrategy | None:
    """Favorito que já cobre (estratégia, símbolo, tempo, período, direção) — "já nos favoritos".

    ``data_source`` e ``asset`` (card #1120, decisão 12) são o contrato com o #1122: ele estende a
    chave com fonte, sessão e ajuste sem mudar esta assinatura. Hoje cada ticker tem uma só fonte
    por classe, então não entram na comparação.
    """

    query = db.query(FavoriteStrategy).filter(
        FavoriteStrategy.user_id == user_id,
        FavoriteStrategy.strategy_name == strategy_name,
        FavoriteStrategy.symbol == symbol,
        FavoriteStrategy.timeframe == timeframe,
    )
    if period_type is not None:
        query = query.filter(FavoriteStrategy.period_type == period_type)
    else:
        query = (
            query.filter(FavoriteStrategy.start_date.is_(None))
            if start_date is None
            else query.filter(FavoriteStrategy.start_date == start_date)
        )
        query = (
            query.filter(FavoriteStrategy.end_date.is_(None))
            if end_date is None
            else query.filter(FavoriteStrategy.end_date == end_date)
        )
    want = (direction or "long").lower()
    if want not in ("long", "short"):
        want = "long"
    return next(
        (row for row in query.all() if _direction_of(row.parameters) == want),
        None,
    )


def lock_and_find_duplicate(
    db: Session,
    *,
    user_id: str,
    strategy_name: str,
    symbol: str,
    timeframe: str,
    period_type: str | None,
    start_date: str | None,
    end_date: str | None,
    parameters: dict[str, Any],
    data_source: str | None = None,
    asset: dict[str, Any] | None = None,
) -> FavoriteStrategy | None:
    direction = str(parameters.get("direction") or "long").lower()
    duplicate_key = "|".join(
        str(value or "")
        for value in (
            user_id,
            strategy_name,
            symbol,
            timeframe,
            period_type,
            start_date if period_type is None else None,
            end_date if period_type is None else None,
            direction,
        )
    )
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        lock_id = int.from_bytes(
            hashlib.sha256(duplicate_key.encode()).digest()[:8], "big", signed=True
        )
        db.execute(text("SELECT pg_advisory_xact_lock(:lock_id)"), {"lock_id": lock_id})

    query = db.query(FavoriteStrategy).filter(
        FavoriteStrategy.user_id == user_id,
        FavoriteStrategy.strategy_name == strategy_name,
        FavoriteStrategy.symbol == symbol,
        FavoriteStrategy.timeframe == timeframe,
        FavoriteStrategy.period_type == period_type,
    )
    if period_type is None:
        query = query.filter(
            FavoriteStrategy.start_date == start_date,
            FavoriteStrategy.end_date == end_date,
        )
    rows = query.all()
    return next(
        (row for row in rows if _direction_of(row.parameters) == direction),
        None,
    )
