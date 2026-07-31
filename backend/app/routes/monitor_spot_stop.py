from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.services.binance_spot_orders import (
    BinanceOrderError,
    cancel_protective_stop,
    get_protective_status,
    place_protective_stop,
)
from app.services.user_exchange_credentials import BINANCE_PROVIDER, get_user_exchange_credential

router = APIRouter(prefix="/api/monitor", tags=["monitor"])


class SpotStopPlacePayload(BaseModel):
    symbol: str = Field(..., min_length=3, max_length=32)
    opportunity_id: str = Field(..., min_length=1, max_length=64)
    stop_price: float = Field(..., gt=0)
    direction: str = Field(default="long", max_length=16)


def _require_user_binance_creds(db: Session, user_id: str):
    cred = get_user_exchange_credential(db, user_id, BINANCE_PROVIDER)
    if cred is None or not str(cred.api_key or "").strip() or not str(cred.api_secret or "").strip():
        raise HTTPException(
            status_code=400,
            detail="Configure a chave Binance em Meu Perfil. Para Proteger stop, habilite Spot Trading (sem withdraw).",
        )
    return cred


def _raise_order_error(exc: BinanceOrderError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/spot-stop-order")
def get_spot_stop_order(
    symbol: str = Query(..., min_length=3, max_length=32),
    opportunity_id: str = Query(..., min_length=1, max_length=64),
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cred = _require_user_binance_creds(db, current_user_id)
    try:
        return get_protective_status(
            api_key=cred.api_key,
            api_secret=cred.api_secret,
            user_id=current_user_id,
            symbol=symbol,
            opportunity_id=opportunity_id,
        )
    except BinanceOrderError as exc:
        _raise_order_error(exc)


@router.post("/spot-stop-order")
def post_spot_stop_order(
    payload: SpotStopPlacePayload,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cred = _require_user_binance_creds(db, current_user_id)
    try:
        return place_protective_stop(
            api_key=cred.api_key,
            api_secret=cred.api_secret,
            user_id=current_user_id,
            symbol=payload.symbol,
            opportunity_id=payload.opportunity_id,
            stop_price=payload.stop_price,
            direction=payload.direction,
        )
    except BinanceOrderError as exc:
        _raise_order_error(exc)


@router.delete("/spot-stop-order")
def delete_spot_stop_order(
    symbol: str = Query(..., min_length=3, max_length=32),
    opportunity_id: str = Query(..., min_length=1, max_length=64),
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cred = _require_user_binance_creds(db, current_user_id)
    try:
        return cancel_protective_stop(
            api_key=cred.api_key,
            api_secret=cred.api_secret,
            user_id=current_user_id,
            symbol=symbol,
            opportunity_id=opportunity_id,
        )
    except BinanceOrderError as exc:
        _raise_order_error(exc)
