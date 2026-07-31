from __future__ import annotations

import os
import uuid
import hmac
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.models import User


@dataclass(frozen=True)
class WorkflowActor:
    user_id: str
    email: str


def design_approver_emails() -> set[str]:
    return {
        email.strip().lower()
        for email in os.getenv("DESIGN_APPROVER_EMAILS", "o.alan.silva@gmail.com").split(",")
        if email.strip()
    }


def homologation_approver_emails() -> set[str]:
    raw = os.getenv(
        "WORKFLOW_HOMOLOGATION_APPROVER_EMAILS",
        os.getenv("DESIGN_APPROVER_EMAILS", "o.alan.silva@gmail.com"),
    )
    return {email.strip().lower() for email in raw.split(",") if email.strip()}


def release_approver_emails() -> set[str]:
    raw = os.getenv(
        "WORKFLOW_RELEASE_APPROVER_EMAILS",
        os.getenv(
            "WORKFLOW_HOMOLOGATION_APPROVER_EMAILS",
            os.getenv("DESIGN_APPROVER_EMAILS", "o.alan.silva@gmail.com"),
        ),
    )
    return {email.strip().lower() for email in raw.split(",") if email.strip()}


def get_trusted_qa_actor(
    x_workflow_qa_token: str | None = Header(default=None, alias="X-Workflow-QA-Token"),
) -> WorkflowActor:
    expected = os.getenv("WORKFLOW_QA_APPROVAL_TOKEN", "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="Trusted QA approval is not configured")
    supplied = (x_workflow_qa_token or "").strip()
    if not supplied or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Invalid trusted QA approval token")
    return WorkflowActor(user_id="trusted-ci-qa", email="ci-qa@workflow.local")


def get_workflow_actor(
    current_user_id: str = Depends(get_current_user),
    auth_db: Session = Depends(get_db),
) -> WorkflowActor:
    try:
        user_uuid = uuid.UUID(current_user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid authenticated workflow user") from exc
    user = auth_db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=401, detail="Authenticated workflow user not found")
    return WorkflowActor(user_id=str(user.id), email=str(user.email).strip().lower())
