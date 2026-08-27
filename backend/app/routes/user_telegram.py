from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.routes.user_profile import _load_user
from app.services.user_telegram_service import (
    create_link_token,
    process_link_command,
    serialize_telegram_settings,
    update_telegram_settings,
)

router = APIRouter(prefix="/api/users/me", tags=["user-telegram"])


class TelegramSettingsResponse(BaseModel):
    telegramUsername: str | None = None
    telegramAlertsEnabled: bool = False
    linked: bool = False
    linkedAt: str | None = None
    usernameMismatch: bool = False
    botUsername: str | None = None
    hasPendingLinkToken: bool = False


class UpdateTelegramSettingsRequest(BaseModel):
    telegramUsername: str | None = Field(default=None, max_length=32)
    telegramAlertsEnabled: bool | None = None


class LinkTokenResponse(BaseModel):
    token: str
    command: str
    expiresAt: str | None = None


@router.get("/telegram-settings", response_model=TelegramSettingsResponse)
def get_telegram_settings(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _load_user(db, current_user_id)
    return TelegramSettingsResponse(**serialize_telegram_settings(user))


@router.patch("/telegram-settings", response_model=TelegramSettingsResponse)
def patch_telegram_settings(
    payload: UpdateTelegramSettingsRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _load_user(db, current_user_id)
    try:
        user = update_telegram_settings(
            db,
            user,
            telegram_username=payload.telegramUsername,
            telegram_alerts_enabled=payload.telegramAlertsEnabled,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return TelegramSettingsResponse(**serialize_telegram_settings(user))


@router.post("/telegram-settings/link-token", response_model=LinkTokenResponse)
def post_telegram_link_token(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _load_user(db, current_user_id)
    try:
        token_payload = create_link_token(db, user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return LinkTokenResponse(**token_payload)


webhook_router = APIRouter(prefix="/api/telegram", tags=["telegram-webhook"])


@webhook_router.post("/webhook")
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    expected = (os.getenv("TELEGRAM_WEBHOOK_SECRET") or "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")
    if x_telegram_bot_api_secret_token != expected:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    payload = await request.json()
    message = payload.get("message") or {}
    text = str(message.get("text") or "").strip()
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    from_user = message.get("from") or {}
    username = from_user.get("username")

    if not text.startswith("/link") or chat_id is None:
        return {"ok": True, "ignored": True}

    parts = text.split(maxsplit=1)
    token = parts[1] if len(parts) > 1 else ""
    ok, reply = process_link_command(
        db,
        token=token,
        chat_id=str(chat_id),
        from_username=username,
    )
    bot_token = (os.getenv("MONITOR_TELEGRAM_BOT_TOKEN") or "").strip()
    if bot_token:
        import requests

        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": reply},
            timeout=10,
        )
    return {"ok": ok, "message": reply}
