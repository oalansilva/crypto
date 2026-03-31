from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_admin
from app.services.system_preferences_service import (
    MINIMAX_API_KEY_KEY,
    delete_system_preference_value,
    get_system_preference_value,
    mask_secret,
    set_system_preference_value,
)

router = APIRouter(prefix="/api/system/preferences", tags=["system-preferences"])


class SystemPreferencesResponse(BaseModel):
    minimax_api_key_configured: bool
    minimax_api_key_masked: str | None = None


class MinimaxApiKeyPayload(BaseModel):
    minimax_api_key: str = Field(..., min_length=10, max_length=512)


@router.get("", response_model=SystemPreferencesResponse)
def get_system_preferences(
    _admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    value = get_system_preference_value(db, MINIMAX_API_KEY_KEY)
    return SystemPreferencesResponse(
        minimax_api_key_configured=bool(value),
        minimax_api_key_masked=mask_secret(value),
    )


@router.put("", response_model=SystemPreferencesResponse)
def put_system_preferences(
    payload: MinimaxApiKeyPayload,
    admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    pref = set_system_preference_value(
        db,
        key=MINIMAX_API_KEY_KEY,
        value=payload.minimax_api_key,
        updated_by_user_id=admin_user_id,
    )
    return SystemPreferencesResponse(
        minimax_api_key_configured=bool(pref.value),
        minimax_api_key_masked=mask_secret(pref.value),
    )


@router.delete("")
def delete_system_preferences(
    _admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    delete_system_preference_value(db, key=MINIMAX_API_KEY_KEY)
    return {"message": "System preferences cleared"}
