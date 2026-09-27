"""Authenticated scalp switch and panel status. Never returns TypeSafe/Jev secrets."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.services.scalp_jev_calibration import revert_to_previous, set_calibration_paused
from app.services.scalp_service import set_switch, status_payload

router = APIRouter(prefix="/api/scalp", tags=["scalp"])


class ScalpSwitchPayload(BaseModel):
    enabled: bool


class ScalpCalibrationPayload(BaseModel):
    paused: Optional[bool] = None
    enabled: Optional[bool] = None


def _assert_no_secrets(payload: dict) -> dict:
    blob = str(payload).lower()
    for token in ("typesafe_api_key", "jev_api_key", "bearer "):
        if token in blob:
            raise RuntimeError("scalp status leaked a secret field")
    return payload


@router.get("/status")
def get_scalp_status(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload = status_payload(db, current_user_id)
    return _assert_no_secrets(payload)


@router.post("/switch")
def post_scalp_switch(
    body: ScalpSwitchPayload,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        set_switch(db, current_user_id, enabled=bool(body.enabled))
    except PermissionError:
        raise HTTPException(
            status_code=400,
            detail="Configure a chave Spot em Meu Perfil. Sem chave Spot este scalp não envia.",
        ) from None
    payload = status_payload(db, current_user_id)
    return _assert_no_secrets(payload)


@router.post("/calibration")
def post_scalp_calibration(
    body: ScalpCalibrationPayload,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Pause or enable automatic calibration. Does not turn the scalper on."""
    paused = body.paused
    if paused is None and body.enabled is not None:
        paused = not bool(body.enabled)
    if paused is None:
        paused = True
    set_calibration_paused(db, paused=bool(paused))
    payload = status_payload(db, current_user_id)
    return _assert_no_secrets(payload)


@router.post("/revert")
def post_scalp_revert(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revert to the previous registered version. Next entry; no 200 wait."""
    revert_to_previous(db)
    payload = status_payload(db, current_user_id)
    return _assert_no_secrets(payload)
