from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.beta_access import create_beta_access_for_lead

router = APIRouter(prefix="/api/leads", tags=["leads"])

BETA_TOTAL_SPOTS = 50


class LeadAccessRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    whatsapp: str | None = Field(default=None, max_length=40)
    profile: str | None = Field(default=None, max_length=80)
    pain: str | None = Field(default=None, max_length=500)
    origin: str = Field(default="landing", max_length=80)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Name cannot be empty")
        return normalized

    @field_validator("origin")
    @classmethod
    def validate_origin(cls, value: str) -> str:
        normalized = value.strip() or "landing"
        return normalized[:80]


class LeadAccessResponse(BaseModel):
    status: str
    message: str


class LeadStatsResponse(BaseModel):
    totalSpots: int
    registered: int
    spotsLeft: int


@router.get("/stats", response_model=LeadStatsResponse)
def get_lead_stats(db: Session = Depends(get_db)):
    registered = (
        db.query(User)
        .filter(
            User.status != "banned",
            User.is_banned.is_(False),
        )
        .count()
    )
    capped_registered = min(BETA_TOTAL_SPOTS, registered)
    return LeadStatsResponse(
        totalSpots=BETA_TOTAL_SPOTS,
        registered=capped_registered,
        spotsLeft=max(0, BETA_TOTAL_SPOTS - capped_registered),
    )


@router.post("", response_model=LeadAccessResponse, status_code=status.HTTP_202_ACCEPTED)
def create_lead_access(payload: LeadAccessRequest, db: Session = Depends(get_db)):
    create_beta_access_for_lead(
        db,
        name=payload.name,
        email=str(payload.email),
        whatsapp=payload.whatsapp,
        profile=payload.profile,
        pain=payload.pain,
        origin=payload.origin,
    )
    return LeadAccessResponse(
        status="accepted",
        message="If eligible, beta access instructions will be sent by email.",
    )
