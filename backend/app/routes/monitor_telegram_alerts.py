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
        description=(
            "Deprecated and ignored: the scan covers every eligible user, each with the own "
            "starred strategies whose alert is on in the Monitor (card #1122)."
        ),
    )
    dry_run: bool = Field(
        default=False,
        description="Force dry-run even when Telegram delivery is fully configured.",
    )


class MonitorTelegramAlertRunResponse(BaseModel):
    enabled: bool
    dry_run: bool
    eligible_users: int = 0
    candidates: int
    sent: int
    dry_run_count: int
    duplicates: int
    rate_limited: int
    skipped: int
    failed: int
    # Card #1122: eventos por favorito, avisos de atraso e de transição, reservas sem resultado.
    favorites_evaluated: int = 0
    signal_events: int = 0
    delay_notices: int = 0
    transition_notices: int = 0
    baselines: int = 0
    held_by_delay: int = 0
    unknown: int = 0
    # Card #1122 (d2): o filtro de estrelas do sistema preenchido, que a varredura ignora.
    tier_filter_ignored: str | None = None
    token_configured: bool | None = None
    can_send: bool | None = None
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
