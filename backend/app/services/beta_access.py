from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from email.message import EmailMessage
import os
from pathlib import Path
import secrets
import smtplib
import subprocess
import uuid
from typing import Callable

import bcrypt
from sqlalchemy.orm import Session

from app.models import BetaAccessAuditLog, User

BETA_ACCESS_DEFAULT_EXPIRY_HOURS = int(os.getenv("BETA_ACCESS_EXPIRY_HOURS", "72"))
BETA_ACCESS_APP_URL = os.getenv("BETA_ACCESS_APP_URL", "https://criptofarol.com.br/login")
BETA_ACCESS_GOG_ENV_FILE = os.getenv(
    "BETA_ACCESS_GOG_ENV_FILE",
    "/root/.openclaw/workspace/cripto-farol-landing/.env.leads",
)
RESERVED_EMAIL_DOMAINS = {"example.com", "example.net", "example.org"}


@dataclass
class BetaLeadAccessResult:
    email: str
    user_created: bool
    must_change_password: bool
    temporary_password_expires_at: datetime | None
    welcome_email_sent: bool
    result: str


@dataclass
class WelcomeEmail:
    to_email: str
    name: str
    login_url: str
    temporary_password: str
    expires_at: datetime


EmailSender = Callable[[WelcomeEmail], bool]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def generate_temporary_password() -> str:
    return secrets.token_urlsafe(18)


def _normalize_email(email: str) -> str:
    return str(email or "").strip().lower()


def _is_reserved_email_domain(email: str) -> bool:
    domain = _normalize_email(email).rsplit("@", 1)[-1]
    return domain in RESERVED_EMAIL_DOMAINS


def _metadata_for_lead(
    *, whatsapp: str | None, profile: str | None, pain: str | None, origin: str
) -> dict:
    return {
        "origin": origin,
        "has_whatsapp": bool(str(whatsapp or "").strip()),
        "has_profile": bool(str(profile or "").strip()),
        "has_pain": bool(str(pain or "").strip()),
    }


def record_beta_access_audit(
    db: Session,
    *,
    email: str,
    user_id: str | None,
    source: str,
    action: str,
    result: str,
    metadata: dict | None = None,
) -> BetaAccessAuditLog:
    row = BetaAccessAuditLog(
        email=_normalize_email(email),
        user_id=user_id,
        source=source,
        action=action,
        result=result,
        metadata_json=metadata or {},
    )
    db.add(row)
    return row


def send_welcome_email_smtp(message: WelcomeEmail) -> bool:
    host = os.getenv("SMTP_HOST", "").strip()
    from_email = os.getenv("SMTP_FROM_EMAIL", "").strip()
    if not host or not from_email:
        return False

    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    use_tls = os.getenv("SMTP_USE_TLS", "1").strip().lower() not in {"0", "false", "no", "off"}

    email = EmailMessage()
    email["From"] = from_email
    email["To"] = message.to_email
    email["Subject"] = "Seu acesso beta do Cripto Farol"
    email.set_content(
        "\n".join(
            [
                f"Olá, {message.name}.",
                "",
                "Seu acesso inicial ao beta do Cripto Farol foi criado.",
                f"Link: {message.login_url}",
                f"Senha temporária: {message.temporary_password}",
                f"Validade: {message.expires_at.isoformat()} UTC",
                "",
                "Ao entrar, troque a senha temporária por uma senha própria.",
                "Não compartilhe essa senha.",
            ]
        )
    )

    with smtplib.SMTP(host, port, timeout=10) as smtp:
        if use_tls:
            smtp.starttls()
        if username:
            smtp.login(username, password)
        smtp.send_message(email)
    return True


def _load_env_file(path: str) -> dict[str, str]:
    env: dict[str, str] = {}
    env_path = Path(path)
    if not env_path.exists():
        return env

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def send_welcome_email_gog(message: WelcomeEmail) -> bool:
    body = [
        f"Olá, {message.name}.",
        "",
        "Sua inscrição no beta fechado do Cripto Farol foi recebida.",
        "",
        "Link de acesso:",
        message.login_url,
        "",
        "Acesso temporário:",
        f"E-mail: {message.to_email}",
        f"Senha temporária: {message.temporary_password}",
        "",
        "Use essa senha apenas para o primeiro acesso e altere assim que entrar.",
        f"Validade: {message.expires_at.isoformat()} UTC",
        "",
        "O beta ainda é controlado. A ideia é testar o monitor em uso real e coletar feedback direto.",
        "",
        "Cripto Farol",
    ]
    args = [
        "gog",
        "gmail",
        "send",
        "--to",
        message.to_email,
        "--subject",
        "Bem-vindo ao beta fechado do Cripto Farol",
        "--body",
        "\n".join(body),
        "--json",
    ]
    cc_email = os.getenv("BETA_ACCESS_WELCOME_EMAIL_CC", os.getenv("EMAIL_TO", "")).strip()
    if cc_email:
        args.extend(["--cc", cc_email])

    command_env = os.environ.copy()
    command_env.update(_load_env_file(BETA_ACCESS_GOG_ENV_FILE))
    completed = subprocess.run(
        args,
        env=command_env,
        timeout=30,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


def send_welcome_email(message: WelcomeEmail) -> bool:
    if _is_reserved_email_domain(message.to_email):
        return False

    provider = os.getenv("BETA_ACCESS_EMAIL_PROVIDER", "gog").strip().lower()
    if provider == "smtp":
        return send_welcome_email_smtp(message)
    if provider == "none":
        return False
    return send_welcome_email_gog(message)


def create_beta_access_for_lead(
    db: Session,
    *,
    name: str,
    email: str,
    whatsapp: str | None = None,
    profile: str | None = None,
    pain: str | None = None,
    origin: str = "landing",
    now: datetime | None = None,
    temporary_password: str | None = None,
    email_sender: EmailSender | None = None,
) -> BetaLeadAccessResult:
    normalized_email = _normalize_email(email)
    current_time = now or datetime.utcnow()
    source = "landing"
    lead_metadata = _metadata_for_lead(
        whatsapp=whatsapp,
        profile=profile,
        pain=pain,
        origin=origin,
    )

    existing = db.query(User).filter(User.email == normalized_email).first()
    if existing:
        record_beta_access_audit(
            db,
            email=normalized_email,
            user_id=str(existing.id),
            source=source,
            action="lead_access_requested",
            result="existing_user_preserved",
            metadata=lead_metadata,
        )
        db.commit()
        return BetaLeadAccessResult(
            email=normalized_email,
            user_created=False,
            must_change_password=bool(existing.must_change_password),
            temporary_password_expires_at=existing.temporary_password_expires_at,
            welcome_email_sent=False,
            result="existing_user_preserved",
        )

    temp_password = temporary_password or generate_temporary_password()
    expires_at = current_time + timedelta(hours=BETA_ACCESS_DEFAULT_EXPIRY_HOURS)
    user = User(
        id=uuid.uuid4(),
        email=normalized_email,
        password_hash=hash_password(temp_password),
        name=name.strip(),
        status="active",
        must_change_password=True,
        temporary_password_expires_at=expires_at,
        access_invitation_source=source,
        access_invitation_created_at=current_time,
        created_at=current_time,
    )
    db.add(user)
    db.flush()

    welcome_sent = False
    sender = email_sender or send_welcome_email
    try:
        welcome_sent = bool(
            sender(
                WelcomeEmail(
                    to_email=normalized_email,
                    name=user.name,
                    login_url=BETA_ACCESS_APP_URL,
                    temporary_password=temp_password,
                    expires_at=expires_at,
                )
            )
        )
        email_result = "created_email_sent" if welcome_sent else "created_email_not_configured"
    except Exception:
        email_result = "created_email_failed"

    if not welcome_sent:
        db.rollback()
        record_beta_access_audit(
            db,
            email=normalized_email,
            user_id=None,
            source=source,
            action="lead_access_created",
            result=email_result,
            metadata=lead_metadata,
        )
        db.commit()
        return BetaLeadAccessResult(
            email=normalized_email,
            user_created=False,
            must_change_password=False,
            temporary_password_expires_at=None,
            welcome_email_sent=False,
            result=email_result,
        )

    record_beta_access_audit(
        db,
        email=normalized_email,
        user_id=str(user.id),
        source=source,
        action="lead_access_created",
        result=email_result,
        metadata={**lead_metadata, "temporary_password_expires_at": expires_at.isoformat()},
    )
    db.commit()

    return BetaLeadAccessResult(
        email=normalized_email,
        user_created=True,
        must_change_password=True,
        temporary_password_expires_at=expires_at,
        welcome_email_sent=welcome_sent,
        result=email_result,
    )


def temporary_password_expired(user: User, now: datetime | None = None) -> bool:
    if not user.must_change_password:
        return False
    if not user.temporary_password_expires_at:
        return False
    current_time = now or datetime.utcnow()
    return user.temporary_password_expires_at.replace(tzinfo=None) <= current_time.replace(
        tzinfo=None
    )
