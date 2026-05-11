from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_admin
from app.services.monitor_telegram_alerts import (
    load_monitor_telegram_alert_settings,
    run_monitor_telegram_alert_scan,
)

router = APIRouter(
    prefix="/api/admin/monitor-telegram-alerts",
    tags=["admin-monitor-telegram-alerts"],
)


class MonitorTelegramAlertRunRequest(BaseModel):
    user_id: str | None = Field(
        default=None,
        description="Optional user id whose Monitor opportunities should be scanned. Defaults to admin caller.",
    )
    dry_run: bool = Field(
        default=False,
        description="Force dry-run even when Telegram delivery is fully configured.",
    )


class MonitorTelegramAlertRunResponse(BaseModel):
    enabled: bool
    dry_run: bool
    candidates: int
    sent: int
    dry_run_count: int
    duplicates: int
    rate_limited: int
    skipped: int
    failed: int
    destination_allowed: bool
    results: list[dict]


@router.post("/run", response_model=MonitorTelegramAlertRunResponse)
def run_monitor_telegram_alerts(
    payload: MonitorTelegramAlertRunRequest | None = None,
    admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    request = payload or MonitorTelegramAlertRunRequest()
    settings = load_monitor_telegram_alert_settings(db)
    return run_monitor_telegram_alert_scan(
        db,
        user_id=request.user_id or admin_user_id,
        settings=settings,
        force_dry_run=request.dry_run,
    )
