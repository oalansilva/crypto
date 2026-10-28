"""Comparação com referência escolhida depois de rodar (card #1123, decisões 4 a 6).

* ``POST /api/benchmark-comparisons``: grava uma comparação nova.
  - ``owner = result``: a rodada nova (admin, como ``/combos/optimize`` e ``/backtest``). O corpo traz
    o contexto da estratégia (símbolo, ativo, execução, trades) e a referência.
  - ``owner = favorite``: o servidor monta o lado da estratégia com os trades e a janela gravados no
    favorito, grava, troca o ponteiro do favorito e solta a amostra da referência anterior.
* ``GET /api/benchmark-comparisons/{id}``: leitura do que foi gravado. Nunca chama o cálculo.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user, is_admin_user
from app.models import FavoriteStrategy, User
from app.services import benchmark_comparison as bench

router = APIRouter(prefix="/api/benchmark-comparisons", tags=["benchmark"])


class ComparisonRequest(BaseModel):
    owner: str = Field(pattern="^(result|favorite)$")
    reference_symbol: Optional[str] = None
    favorite_id: Optional[int] = None
    context: Optional[dict[str, Any]] = None


def _user(db: Session, user_id: str) -> Optional[User]:
    try:
        return db.query(User).filter(User.id == uuid.UUID(str(user_id))).first()
    except (ValueError, TypeError):
        return None


def _is_admin(db: Session, user_id: str) -> bool:
    return is_admin_user(_user(db, user_id))


def _decode(value: Any) -> Any:
    from app.routes.favorites import _decode_jsonish

    return _decode_jsonish(value)


def strategy_from_context(context: dict[str, Any]) -> bench.StrategySide:
    try:
        return bench.strategy_from_context(context)
    except bench.BenchmarkError as exc:
        raise HTTPException(status_code=422, detail=exc.detail())


def strategy_from_favorite(favorite: FavoriteStrategy) -> bench.StrategySide:
    return bench.strategy_from_favorite(favorite)


def switch_favorite_comparison(
    db: Session, favorite: FavoriteStrategy, payload: dict[str, Any]
) -> None:
    bench.switch_favorite_comparison(db, favorite, payload)


def _collection_error(exc: bench.BenchmarkCollectionError) -> HTTPException:
    return HTTPException(status_code=422, detail=exc.detail())


@router.post("", status_code=201)
@router.post("/", status_code=201, include_in_schema=False)
async def create_benchmark_comparison(
    req: ComparisonRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if req.owner == "result":
        if not _is_admin(db, current_user_id):
            raise HTTPException(status_code=403, detail="Admin access required")
        if not isinstance(req.context, dict):
            raise HTTPException(status_code=422, detail="Informe o contexto do resultado.")
        strategy = strategy_from_context(req.context)

        def run() -> dict[str, Any]:
            return bench.create_comparison(
                db,
                strategy,
                req.reference_symbol,
                owner_kind="result",
                user_id=current_user_id,
                trigger="choice",
            )

        try:
            return await asyncio.to_thread(run)
        except bench.BenchmarkCollectionError as exc:
            raise _collection_error(exc)
        except bench.BenchmarkError as exc:
            raise HTTPException(status_code=422, detail=exc.detail())

    if req.favorite_id is None:
        raise HTTPException(status_code=422, detail="Informe o favorito.")
    favorite = db.query(FavoriteStrategy).filter(FavoriteStrategy.id == req.favorite_id).first()
    if favorite is None or str(favorite.user_id) != str(current_user_id):
        raise HTTPException(status_code=404, detail="Favorite not found")
    strategy = strategy_from_favorite(favorite)

    def run_favorite() -> dict[str, Any]:
        payload = bench.create_comparison(
            db,
            strategy,
            req.reference_symbol,
            owner_kind="favorite",
            user_id=current_user_id,
            trigger="choice",
            favorite_id=favorite.id,
            commit=False,
        )
        switch_favorite_comparison(db, favorite, payload)
        db.commit()
        return payload

    try:
        return await asyncio.to_thread(run_favorite)
    except bench.BenchmarkCollectionError as exc:
        db.rollback()
        raise _collection_error(exc)
    except bench.BenchmarkError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=exc.detail())


def can_read(db: Session, payload: dict[str, Any], user_id: str) -> bool:
    if str(payload.get("user_id") or "") == str(user_id):
        return True
    if _is_admin(db, user_id):
        return True
    # Favorito da vitrine do catálogo (dono admin) que aponta para esta comparação.
    from app.routes.favorites import _admin_catalog_user_ids

    owners = set(_admin_catalog_user_ids(db, exclude_user_id=user_id))
    if not owners:
        return False
    found = (
        db.query(FavoriteStrategy.id)
        .filter(
            FavoriteStrategy.benchmark_comparison_id == payload.get("id"),
            FavoriteStrategy.user_id.in_(sorted(owners)),
        )
        .first()
    )
    return found is not None


@router.get("/{comparison_id}")
def read_benchmark_comparison(
    comparison_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload = bench.get_comparison(db, comparison_id)
    if payload is None or not can_read(db, payload, current_user_id):
        raise HTTPException(status_code=404, detail="Comparison not found")
    return JSONResponse(content=payload)
