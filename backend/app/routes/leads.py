from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, status
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.beta_access import record_lead_submission
from app.services.beta_invites import validate_invite
from app.services.landing_leads import (
    admin_telegram_chat_ids,
    save_landing_lead,
    send_lead_notices,
)

router = APIRouter(prefix="/api/leads", tags=["leads"])


class LeadAccessRequest(BaseModel):
    # Card #1160: ``step`` 1 saves the lead (name + e-mail), ``step`` 2 only
    # enriches it (WhatsApp, level, difficulty, all optional).  Without ``step``
    # (the v4 page and the landing commit-base) it is step 1 + 2 together.
    step: Literal[1, 2] | None = None
    name: str | None = Field(default=None, max_length=120)
    email: EmailStr
    inviteToken: str | None = Field(default=None, max_length=512)
    whatsapp: str | None = Field(default=None, max_length=40)
    profile: str | None = Field(default=None, max_length=80)
    pain: str | None = Field(default=None, max_length=500)
    origin: str = Field(default="landing", max_length=500)
    utm_source: str | None = Field(default=None, max_length=500)
    utm_medium: str | None = Field(default=None, max_length=500)
    utm_campaign: str | None = Field(default=None, max_length=500)
    utm_content: str | None = Field(default=None, max_length=500)
    utm_term: str | None = Field(default=None, max_length=500)
    referrer: str | None = Field(default=None, max_length=500)
    landing_path: str | None = Field(default=None, max_length=500)
    first_seen_at: str | None = Field(default=None, max_length=80)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @model_validator(mode="after")
    def require_name_on_step_one(self) -> "LeadAccessRequest":
        if self.step in (None, 1) and not self.name:
            raise ValueError("Name cannot be empty")
        return self

    @field_validator("origin")
    @classmethod
    def validate_origin(cls, value: str) -> str:
        normalized = value.strip() or "landing"
        return normalized[:80]

    def attribution_payload(self) -> dict[str, str]:
        payload = {
            "utm_source": self.utm_source,
            "utm_medium": self.utm_medium,
            "utm_campaign": self.utm_campaign,
            "utm_content": self.utm_content,
            "utm_term": self.utm_term,
            "referrer": self.referrer,
            "landing_path": self.landing_path,
            "first_seen_at": self.first_seen_at,
        }
        return {key: value for key, value in payload.items() if value}


class LeadAccessResponse(BaseModel):
    status: str
    message: str


@router.post("", response_model=LeadAccessResponse, status_code=status.HTTP_202_ACCEPTED)
def create_lead_access(
    payload: LeadAccessRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,  # type: ignore[assignment]  # injected by FastAPI
):
    # The landing validates the invite (when one is carried) for the submitted
    # address but NEVER consumes it and never creates or modifies an account
    # (D10).  The 202 stays neutral for every eligible submission.
    invite_state = None
    invite_token = str(payload.inviteToken or "").strip()
    if invite_token:
        decision = validate_invite(db, token=invite_token, email=str(payload.email))
        invite_state = decision.state

    # Card #1160 (D1): the lead row is saved in the same transaction as the
    # #689 audit, which commits it.
    lead = save_landing_lead(
        db,
        step=payload.step,
        email=str(payload.email),
        name=payload.name,
        whatsapp=payload.whatsapp,
        profile=payload.profile,
        pain=payload.pain,
        origin=payload.origin,
        attribution=payload.attribution_payload(),
    )
    record_lead_submission(
        db,
        email=str(payload.email),
        whatsapp=payload.whatsapp,
        profile=payload.profile,
        pain=payload.pain,
        origin=payload.origin,
        attribution=payload.attribution_payload(),
        invite_state=invite_state,
        step=payload.step,
    )

    # D3: the Telegram notice runs after the commit and outside the response;
    # a failure only logs (without personal data) and never fails the lead.
    if lead.notices:
        try:
            chat_ids = admin_telegram_chat_ids(db)
        except Exception:  # noqa: BLE001 - the lead is already saved
            chat_ids = []
        if background_tasks is not None:
            background_tasks.add_task(send_lead_notices, chat_ids, lead.notices)
        else:
            send_lead_notices(chat_ids, lead.notices)

    return LeadAccessResponse(
        status="accepted",
        message="If eligible, beta access instructions will be sent by email.",
    )
