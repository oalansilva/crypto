from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.services.user_exchange_credentials import (
    BINANCE_PROVIDER,
    delete_user_exchange_credential,
    get_user_exchange_credential,
    upsert_user_exchange_credential,
)

router = APIRouter(prefix="/api/user", tags=["user"])


class BinanceCredentialPayload(BaseModel):
    api_key: str = Field(..., min_length=5, max_length=256)
    api_secret: str = Field(..., min_length=10, max_length=256)


class BinanceCredentialStatusResponse(BaseModel):
    configured: bool
    api_key_masked: str | None = None


def _mask_api_key(api_key: str | None) -> str | None:
    value = str(api_key or "").strip()
    if not value:
        return None
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


@router.get("/binance-credentials", response_model=BinanceCredentialStatusResponse)
def get_binance_credentials_status(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cred = get_user_exchange_credential(db, current_user_id, BINANCE_PROVIDER)
    return BinanceCredentialStatusResponse(
        configured=cred is not None,
        api_key_masked=_mask_api_key(cred.api_key if cred else None),
    )


@router.put("/binance-credentials", response_model=BinanceCredentialStatusResponse)
def put_binance_credentials(
    payload: BinanceCredentialPayload,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cred = upsert_user_exchange_credential(
        db,
        user_id=current_user_id,
        provider=BINANCE_PROVIDER,
        api_key=payload.api_key.strip(),
        api_secret=payload.api_secret.strip(),
    )
    return BinanceCredentialStatusResponse(
        configured=True,
        api_key_masked=_mask_api_key(cred.api_key),
    )


@router.delete("/binance-credentials")
def delete_binance_credentials(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = delete_user_exchange_credential(
        db, user_id=current_user_id, provider=BINANCE_PROVIDER
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Binance credentials not found")
    return {"message": "Binance credentials deleted"}
