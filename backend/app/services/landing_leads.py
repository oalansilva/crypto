"""Landing leads saved at step 1 and enriched at step 2 (card #1160, D1/D3).

``POST /api/leads`` keeps the neutral 202 and the #689 audit; this module adds
the lead row itself (``landing_leads``) and the Telegram notice to the admins.

- step 1: name and e-mail; creates or updates the lead of the e-mail without
  clearing fields from an earlier step 2;
- step 2: WhatsApp, level and difficulty, all optional; enriches the lead of
  the same e-mail (creates it when there is none);
- no step (the v4 page and the landing commit-base): step 1 + step 2 together.

The notice goes through the Cripto Farol bot (``MONITOR_TELEGRAM_BOT_TOKEN``)
to every admin with a linked Telegram chat, after the commit and outside the
response.  A failure only logs, without personal data.

DEV shares the PROD bot token, and DEV must not use the PROD bot
(``docs/monitor-telegram-alerts.md``): with
``CRYPTO_TELEGRAM_ALERT_SCAN_BLOCK_PROD_BOT=1`` no notice is sent, the lead is
saved and the request answers 202 as usual.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import logging
import os

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import LandingLead, User
from app.services.beta_access import _normalize_email, _sanitize_attribution

logger = logging.getLogger(__name__)

STEP_ONE = 1
STEP_TWO = 2

FIELD_LIMITS = {
    "name": 120,
    "whatsapp": 40,
    "profile": 80,
    "pain": 500,
    "origin": 80,
}
STEP_TWO_FIELDS = ("whatsapp", "profile", "pain")
CAMPAIGN_KEYS = ("utm_source", "utm_medium", "utm_campaign")


@dataclass
class LeadNotice:
    """What the admins are told after the commit (``kind`` = new | completed)."""

    kind: str
    lines: list[tuple[str, str]] = field(default_factory=list)

    def text(self) -> str:
        title = (
            "Cripto Farol - Novo lead na landing"
            if self.kind == "new"
            else "Cripto Farol - Lead completou o cadastro"
        )
        body = "\n".join(f"{label}: {value}" for label, value in self.lines if value)
        return f"{title}\n\n{body}" if body else title


@dataclass
class LandingLeadResult:
    created: bool
    step_reached: int
    notices: list[LeadNotice]


def _clean(value: object, limit: int) -> str | None:
    normalized = str(value or "").strip()
    if not normalized:
        return None
    return normalized[:limit]


def _campaign_label(attribution: dict[str, str]) -> str:
    return " / ".join(attribution[key] for key in CAMPAIGN_KEYS if attribution.get(key))


def _new_lead_notice(
    lead: LandingLead, attribution: dict[str, str], *, with_step_two: bool
) -> LeadNotice:
    lines = [
        ("Nome", lead.name or ""),
        ("E-mail", lead.email),
        ("Origem", lead.origin or ""),
        ("Campanha", _campaign_label(attribution)),
    ]
    if with_step_two:
        lines += [
            ("WhatsApp", lead.whatsapp or ""),
            ("Nível", lead.profile or ""),
            ("Dificuldade", lead.pain or ""),
        ]
    return LeadNotice(kind="new", lines=lines)


def _completed_notice(lead: LandingLead) -> LeadNotice:
    return LeadNotice(
        kind="completed",
        lines=[
            ("E-mail", lead.email),
            ("WhatsApp", lead.whatsapp or "-"),
            ("Nível", lead.profile or "-"),
            ("Dificuldade", lead.pain or "-"),
        ],
    )


def _find_lead(db: Session, email: str) -> LandingLead | None:
    return db.query(LandingLead).filter(LandingLead.email == email).first()


def _merge_attribution(current: object, incoming: dict[str, str]) -> dict[str, str] | None:
    merged: dict[str, str] = dict(current) if isinstance(current, dict) else {}
    for key, value in incoming.items():
        # First touch wins: an earlier value stays, a missing one is filled.
        merged.setdefault(key, value)
    return merged or None


def save_landing_lead(
    db: Session,
    *,
    step: int | None,
    email: str,
    name: str | None = None,
    whatsapp: str | None = None,
    profile: str | None = None,
    pain: str | None = None,
    origin: str | None = None,
    attribution: dict | None = None,
    now: datetime | None = None,
) -> LandingLeadResult:
    """Upsert the lead of ``email`` for ``step`` (``None`` = step 1 + 2).

    Does not commit: the caller commits together with the #689 audit.
    """

    now = now or datetime.utcnow()
    normalized_email = _normalize_email(email)
    carries_step_one = step in (None, STEP_ONE)
    carries_step_two = step in (None, STEP_TWO)

    clean_name = _clean(name, FIELD_LIMITS["name"]) if carries_step_one else None
    clean_origin = _clean(origin, FIELD_LIMITS["origin"])
    step_two_values = {
        key: _clean(value, FIELD_LIMITS[key])
        for key, value in (("whatsapp", whatsapp), ("profile", profile), ("pain", pain))
    }
    if not carries_step_two:
        step_two_values = {key: None for key in step_two_values}
    sanitized_attribution = _sanitize_attribution(attribution)
    has_step_two_data = any(step_two_values.values())

    lead = _find_lead(db, normalized_email)
    created = False
    if lead is None:
        lead = LandingLead(
            email=normalized_email,
            name=clean_name,
            origin=clean_origin or "landing",
            attribution_json=sanitized_attribution or None,
            step_reached=(
                STEP_TWO if step == STEP_TWO or (step is None and has_step_two_data) else STEP_ONE
            ),
            created_at=now,
            updated_at=now,
            **step_two_values,
        )
        try:
            with db.begin_nested():
                db.add(lead)
                db.flush()
            created = True
        except IntegrityError:
            # A concurrent submission created the same e-mail: enrich it instead.
            lead = _find_lead(db, normalized_email)
            if lead is None:
                raise

    if not created:
        if clean_name:
            lead.name = clean_name
        if clean_origin and not lead.origin:
            lead.origin = clean_origin
        for key, value in step_two_values.items():
            if value:
                setattr(lead, key, value)
        lead.attribution_json = _merge_attribution(lead.attribution_json, sanitized_attribution)
        if step == STEP_TWO or (step is None and has_step_two_data):
            lead.step_reached = max(int(lead.step_reached or STEP_ONE), STEP_TWO)
        lead.updated_at = now
        db.flush()

    notices: list[LeadNotice] = []
    if created:
        # New lead (step 1, or the old single-step page): one notice, with the
        # step 2 fields when the same submission carried them.
        notices.append(
            _new_lead_notice(
                lead, sanitized_attribution, with_step_two=step is None and has_step_two_data
            )
        )
        if step == STEP_TWO and has_step_two_data:
            notices.append(_completed_notice(lead))
    elif carries_step_two and has_step_two_data:
        # Step 2 enriched an existing lead; a repeated step 1 says nothing.
        notices.append(_completed_notice(lead))

    return LandingLeadResult(created=created, step_reached=int(lead.step_reached), notices=notices)


def admin_telegram_chat_ids(db: Session) -> list[str]:
    rows = (
        db.query(User.telegram_chat_id)
        .filter(
            func.lower(func.coalesce(User.role, "")) == "admin",
            User.telegram_chat_id.isnot(None),
            User.telegram_chat_id != "",
            User.is_banned.isnot(True),
        )
        .all()
    )
    return sorted({str(row[0]).strip() for row in rows if str(row[0] or "").strip()})


def _block_prod_bot() -> bool:
    # Same rule as ``_block_prod_bot()`` in ``ops/run_monitor_telegram_alert_scan.py``.
    return os.getenv("CRYPTO_TELEGRAM_ALERT_SCAN_BLOCK_PROD_BOT", "").strip() == "1"


def _bot_token() -> str | None:
    return (os.getenv("MONITOR_TELEGRAM_BOT_TOKEN") or "").strip() or None


def send_lead_notices(chat_ids: list[str], notices: list[LeadNotice]) -> int:
    """Send each notice to each admin chat.  Never raises; logs without personal data."""

    if not notices:
        return 0
    if _block_prod_bot():
        logger.warning(
            "landing lead notice skipped: PROD bot blocked in this environment (notices=%d)",
            len(notices),
        )
        return 0
    token = _bot_token()
    if not token:
        logger.warning(
            "landing lead notice skipped: bot token not configured (notices=%d)", len(notices)
        )
        return 0
    if not chat_ids:
        logger.warning("landing lead notice skipped: no admin with linked Telegram (sem destino)")
        return 0

    from app.services.monitor_telegram_alerts import send_telegram_message

    sent = 0
    for notice in notices:
        for chat_id in chat_ids:
            try:
                send_telegram_message(bot_token=token, chat_id=chat_id, text=notice.text())
                sent += 1
            except Exception as exc:  # noqa: BLE001 - a notice never fails the lead
                logger.warning(
                    "landing lead notice failed: kind=%s error=%s",
                    notice.kind,
                    type(exc).__name__,
                )
    return sent
