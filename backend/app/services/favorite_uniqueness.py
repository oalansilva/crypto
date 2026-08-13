from __future__ import annotations

import hashlib
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import FavoriteStrategy


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
        (
            row
            for row in rows
            if str((row.parameters or {}).get("direction") or "long").lower() == direction
        ),
        None,
    )
