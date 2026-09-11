"""Single-use beta invite service (card #689).

The invite is the authorization that lets one specific address create one
account during the closed beta.  The clear token exists only in the issuance
HTTP response and in the copyable link; at rest only a SHA-256 digest is
persisted.  Consumption is a single atomic transition bound to the invited
address:

    consumed_at IS NULL AND revoked_at IS NULL AND expires_at > now()

The transition runs **only** on the invite link's own ``POST`` or on the
register path that consumes it for the same address.  ``POST /api/leads``
validates without consuming (D10).
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import BetaInvite, User
from app.services.beta_access import hash_password, record_beta_access_audit

SOURCE_ADMIN_INVITE = "admin_invite"
SOURCE_INVITE_LINK = "invite_link"
SOURCE_REGISTER_INVITE = "register_invite"
SOURCE_LANDING_INVITE = "landing_invite"

ACTION_INVITE_ISSUED = "beta_invite_issued"
ACTION_INVITE_REISSUED = "beta_invite_reissued"
ACTION_INVITE_CONSUMED = "beta_invite_consumed"
ACTION_INVITE_CONSUME_FAILED = "beta_invite_consume_failed"

RESULT_ISSUED = "issued"
RESULT_SUPERSEDED = "superseded"
RESULT_CONSUMED = "consumed"

STATE_VALID = "valid"
STATE_NOT_FOUND = "not_found"
STATE_ALREADY_CONSUMED = "already_consumed"
STATE_EXPIRED = "expired"
STATE_REVOKED = "revoked"
STATE_EMAIL_MISMATCH = "email_mismatch"

TOKEN_BYTES = 32
DEFAULT_TTL_HOURS = 72
MIN_TTL_HOURS = 1
MAX_TTL_HOURS = 720
INVITE_PATH_PREFIX = "/beta-invite/"

# Actionable, dedicated refusals.  A dedicated message per state keeps the
# failure explicit instead of collapsing into a generic server error.
STATE_MESSAGES = {
    STATE_NOT_FOUND: (
        "Convite não encontrado. Confira o link recebido ou peça um novo convite ao operador."
    ),
    STATE_ALREADY_CONSUMED: (
        "Este convite já foi utilizado. Se precisar de acesso, peça um novo link ao operador."
    ),
    STATE_EXPIRED: "Convite expirado. Peça um novo link ao operador.",
    STATE_REVOKED: ("Este convite foi substituído. Use o link mais recente enviado pelo operador."),
    STATE_EMAIL_MISMATCH: (
        "Este convite pertence a outro endereço. Use o link enviado para o seu próprio e-mail."
    ),
}

# HTTP status of each refusal.  Details of Apply (P3): the failure is explicit
# and dedicated, never a generic 500.
STATE_STATUS_CODES = {
    STATE_NOT_FOUND: 404,
    STATE_ALREADY_CONSUMED: 409,
    STATE_EXPIRED: 410,
    STATE_REVOKED: 410,
    STATE_EMAIL_MISMATCH: 403,
}


class InviteConsumptionError(Exception):
    """Explicit consumption refusal carrying its own state and status code."""

    def __init__(self, state: str, message: str | None = None, status_code: int | None = None):
        self.state = state
        self.message = message or STATE_MESSAGES.get(state, "Convite inválido.")
        self.status_code = status_code or STATE_STATUS_CODES.get(state, 400)
        super().__init__(self.message)


@dataclass(frozen=True)
class InviteDecision:
    """Result of a read-only invite validation (never consumes)."""

    state: str
    invite: BetaInvite | None = None

    @property
    def is_valid(self) -> bool:
        return self.state == STATE_VALID


@dataclass(frozen=True)
class InviteConsumption:
    """Result of a successful atomic consumption."""

    invite: BetaInvite
    user: User
    account_created: bool


def normalize_email(email: str | None) -> str:
    return str(email or "").strip().lower()


def invite_base_url() -> str:
    raw = os.getenv("BETA_INVITE_BASE_URL", "https://criptofarol.com.br").strip()
    return raw.rstrip("/")


def default_ttl_hours() -> int:
    raw = os.getenv("BETA_INVITE_TTL_HOURS", str(DEFAULT_TTL_HOURS)).strip()
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return DEFAULT_TTL_HOURS
    return min(max(value, MIN_TTL_HOURS), MAX_TTL_HOURS)


def resolve_ttl_hours(ttl_hours: int | None) -> int:
    if ttl_hours is None:
        return default_ttl_hours()
    if not isinstance(ttl_hours, int) or isinstance(ttl_hours, bool):
        raise ValueError("ttlHours must be an integer number of hours")
    if ttl_hours < MIN_TTL_HOURS or ttl_hours > MAX_TTL_HOURS:
        raise ValueError(f"ttlHours must be between {MIN_TTL_HOURS} and {MAX_TTL_HOURS}")
    return ttl_hours


def generate_invite_token() -> str:
    return secrets.token_urlsafe(TOKEN_BYTES)


def hash_invite_token(token: str) -> str:
    return hashlib.sha256(str(token or "").encode("utf-8")).hexdigest()


def build_invite_path(token: str) -> str:
    return f"{INVITE_PATH_PREFIX}{token}"


def build_invite_url(token: str) -> str:
    return f"{invite_base_url()}{build_invite_path(token)}"


def find_invite_by_token(db: Session, token: str | None) -> BetaInvite | None:
    """Look the invite up by digest and keep the comparison constant time."""

    candidate = str(token or "").strip()
    if not candidate:
        return None

    digest = hash_invite_token(candidate)
    invite = db.query(BetaInvite).filter(BetaInvite.token_hash == digest).first()
    if invite is None:
        return None
    if not hmac.compare_digest(str(invite.token_hash), digest):
        return None
    return invite


def classify_invite(
    db: Session,
    invite: BetaInvite | None,
    *,
    email: str | None,
    now: datetime | None = None,
) -> str:
    """Classify an invite without touching its state."""

    if invite is None:
        return STATE_NOT_FOUND

    current = now or datetime.utcnow()
    if invite.revoked_at is not None:
        return STATE_REVOKED
    if invite.consumed_at is not None:
        return STATE_ALREADY_CONSUMED
    if _as_naive(invite.expires_at) <= current:
        return STATE_EXPIRED
    if email is not None and normalize_email(invite.email) != normalize_email(email):
        return STATE_EMAIL_MISMATCH
    return STATE_VALID


def validate_invite(
    db: Session,
    *,
    token: str | None,
    email: str | None,
    now: datetime | None = None,
) -> InviteDecision:
    """Read-only validation used by the doors that must not consume."""

    invite = find_invite_by_token(db, token)
    state = classify_invite(db, invite, email=email, now=now)
    return InviteDecision(state=state, invite=invite)


def _as_naive(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def record_invite_refusal(
    db: Session,
    *,
    invite: BetaInvite | None,
    email: str,
    state: str,
    source: str,
    now: datetime | None = None,
) -> None:
    """Audit a refusal without ever writing the token.

    The metadata carries the refusal classification only; the clear token is
    never persisted, logged, or written to audit.  An unknown token reached on
    a surface with no address to record (the invite-link ``GET``) leaves no
    audit row: there is no identity to classify.
    """

    normalized = normalize_email(email)
    if invite is None and not normalized:
        return

    record_beta_access_audit(
        db,
        email=normalized,
        user_id=str(invite.consumed_user_id) if invite and invite.consumed_user_id else None,
        source=source,
        action=ACTION_INVITE_CONSUME_FAILED,
        result=state,
        metadata={"invite_id": str(invite.id) if invite else None},
    )


def _find_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(func.lower(User.email) == normalize_email(email)).first()


def issue_invite(
    db: Session,
    *,
    email: str,
    created_by_user_id: str | None = None,
    ttl_hours: int | None = None,
    now: datetime | None = None,
    source: str = SOURCE_ADMIN_INVITE,
) -> tuple[BetaInvite, str]:
    """Issue a new invite, superseding the open invites of the same address.

    Returns the persisted invite and the clear token (only the caller may put
    it in the issuance response).
    """

    normalized = normalize_email(email)
    current = now or datetime.utcnow()
    ttl = resolve_ttl_hours(ttl_hours)
    token = generate_invite_token()

    open_filter = (
        func.lower(BetaInvite.email) == normalized,
        BetaInvite.consumed_at.is_(None),
        BetaInvite.revoked_at.is_(None),
        BetaInvite.expires_at > current,
    )
    # Serialize concurrent reissue for the same address: lock the live
    # rows before inserting the replacement.  Re-read after the lock so a
    # waiter sees the invite the preceding issuer just committed.
    db.query(BetaInvite).filter(*open_filter).with_for_update().all()
    open_invites = db.query(BetaInvite).filter(*open_filter).all()

    invite = BetaInvite(
        id=uuid.uuid4(),
        email=normalized,
        token_hash=hash_invite_token(token),
        created_at=current,
        expires_at=current + timedelta(hours=ttl),
        created_by_user_id=str(created_by_user_id) if created_by_user_id else None,
    )
    db.add(invite)
    db.flush()

    for previous in open_invites:
        previous.revoked_at = current
        previous.revoked_reason = RESULT_SUPERSEDED
        previous.superseded_by_id = invite.id

    invited_user = _find_user_by_email(db, normalized)
    record_beta_access_audit(
        db,
        email=normalized,
        user_id=str(invited_user.id) if invited_user else None,
        source=source,
        action=ACTION_INVITE_ISSUED,
        result=RESULT_ISSUED,
        metadata={
            "invite_id": str(invite.id),
            "ttl_hours": ttl,
            "expires_at": invite.expires_at.isoformat(),
        },
    )
    if open_invites:
        record_beta_access_audit(
            db,
            email=normalized,
            user_id=str(invited_user.id) if invited_user else None,
            source=source,
            action=ACTION_INVITE_REISSUED,
            result=RESULT_SUPERSEDED,
            metadata={
                "invite_id": str(invite.id),
                "superseded_by_id": str(invite.id),
                "revoked_invite_ids": [str(previous.id) for previous in open_invites],
            },
        )

    return invite, token


def consume_invite(
    db: Session,
    *,
    token: str | None,
    email: str,
    password: str,
    name: str | None = None,
    source: str = SOURCE_INVITE_LINK,
    now: datetime | None = None,
) -> InviteConsumption:
    """Consume the invite once and create the account or reset the password.

    Runs in the caller's transaction: the invite transition and the account
    write are committed together by the caller.  A refusal raises
    :class:`InviteConsumptionError` and writes its audit row.
    """

    current = now or datetime.utcnow()
    normalized = normalize_email(email)

    invite = find_invite_by_token(db, token)
    state = classify_invite(db, invite, email=normalized, now=current)
    if state != STATE_VALID or invite is None:
        record_invite_refusal(
            db,
            invite=invite,
            email=normalized,
            state=state,
            source=source,
            now=current,
        )
        db.commit()
        raise InviteConsumptionError(state)

    # Atomic guard: lock the invite row so two concurrent consumptions cannot
    # both succeed, and re-check the transition under the lock.
    locked = db.query(BetaInvite).filter(BetaInvite.id == invite.id).with_for_update().one()
    locked_state = classify_invite(db, locked, email=normalized, now=current)
    if locked_state != STATE_VALID:
        record_invite_refusal(
            db,
            invite=locked,
            email=normalized,
            state=locked_state,
            source=source,
            now=current,
        )
        db.commit()
        raise InviteConsumptionError(locked_state)

    account_created = False
    user = _find_user_by_email(db, normalized)
    if user is None:
        user = User(
            id=uuid.uuid4(),
            email=normalized,
            password_hash=hash_password(password),
            name=(str(name or "").strip() or normalized.split("@", 1)[0] or normalized),
            role="user",
            status="active",
            must_change_password=False,
            access_invitation_source=SOURCE_ADMIN_INVITE,
            access_invitation_created_at=current,
            created_at=current,
        )
        db.add(user)
        db.flush()
        account_created = True
    else:
        # Owner's password reset through the invite's own flow.  Role, status
        # and ban state are never changed here (D8).
        user.password_hash = hash_password(password)
        user.password_changed_at = current
        user.must_change_password = False
        user.temporary_password_expires_at = None
        db.add(user)

    locked.consumed_at = current
    locked.consumed_user_id = str(user.id)

    record_beta_access_audit(
        db,
        email=normalized,
        user_id=str(user.id),
        source=source,
        action=ACTION_INVITE_CONSUMED,
        result=RESULT_CONSUMED,
        metadata={
            "invite_id": str(locked.id),
            "account_created": account_created,
            "channel": source,
        },
    )
    return InviteConsumption(invite=locked, user=user, account_created=account_created)
