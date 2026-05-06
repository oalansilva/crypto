#!/usr/bin/env python3
"""Disable unauthorized users for the closed beta.

Default allowed users:
- o.alan.silva@gmail.com
- o2.alan.silva@gmail.com

The script is intentionally conservative: it bans unauthorized users instead of
deleting rows, preserving historical user-owned data and audit references.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

DEFAULT_ALLOWED_EMAILS = ("o.alan.silva@gmail.com", "o2.alan.silva@gmail.com")


def normalize_email(value: str | None) -> str:
    return str(value or "").strip().lower()


def parse_allowed_emails(raw_values: list[str] | None) -> set[str]:
    if not raw_values:
        return set(DEFAULT_ALLOWED_EMAILS)

    values: set[str] = set()
    for raw in raw_values:
        for part in str(raw or "").split(","):
            email = normalize_email(part)
            if email:
                values.add(email)
    return values


def is_postgres_url(url: str) -> bool:
    normalized = str(url or "").strip().lower()
    return normalized.startswith("postgresql://") or normalized.startswith("postgresql+psycopg2://")


def resolve_database_url() -> str:
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit

    from app.database import resolve_db_url

    return resolve_db_url()


def mask_email(email: str) -> str:
    local, sep, domain = normalize_email(email).partition("@")
    if not sep:
        return "***"
    if len(local) <= 2:
        masked_local = local[:1] + "***"
    else:
        masked_local = f"{local[:2]}***{local[-1:]}"
    return f"{masked_local}@{domain}"


def is_login_blocked(row: dict[str, Any]) -> bool:
    return bool(row.get("is_banned")) or normalize_email(row.get("status")) == "banned"


def build_summary(rows: list[dict[str, Any]], allowed_emails: set[str]) -> dict[str, Any]:
    allowed = []
    allowed_missing = set(allowed_emails)
    unauthorized = []
    unauthorized_active = []

    for row in rows:
        email = normalize_email(row.get("email"))
        item = {
            "id": str(row.get("id")),
            "email_masked": mask_email(email),
            "status": row.get("status"),
            "is_banned": bool(row.get("is_banned")),
            "login_blocked": is_login_blocked(row),
        }
        if email in allowed_emails:
            allowed.append(item)
            allowed_missing.discard(email)
        else:
            unauthorized.append(item)
            if not is_login_blocked(row):
                unauthorized_active.append(item)

    return {
        "total_users": len(rows),
        "allowed_users": len(allowed),
        "allowed_missing": sorted(mask_email(email) for email in allowed_missing),
        "unauthorized_users": len(unauthorized),
        "unauthorized_active": len(unauthorized_active),
        "allowed": allowed,
        "unauthorized_active_masked": [item["email_masked"] for item in unauthorized_active],
    }


def fetch_users(conn) -> list[dict[str, Any]]:
    result = conn.execute(text("""
            SELECT id, email, status, is_banned, notes
            FROM users
            ORDER BY lower(email)
            """))
    return [dict(row._mapping) for row in result]


def apply_cleanup(conn, *, allowed_emails: set[str], reason: str, actor: str) -> int:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    result = conn.execute(
        text("""
            UPDATE users
            SET
                status = 'banned',
                is_banned = TRUE,
                suspension_reason = :reason,
                notes = concat_ws(
                    E'\n',
                    NULLIF(notes, ''),
                    :note
                )
            WHERE lower(email) <> ALL(:allowed_emails)
              AND (status IS DISTINCT FROM 'banned' OR is_banned IS DISTINCT FROM TRUE)
            """),
        {
            "allowed_emails": sorted(allowed_emails),
            "reason": reason,
            "note": f"{now.isoformat()}Z [{actor}] {reason}",
        },
    )
    return int(result.rowcount or 0)


def _safe_db_target(url: str) -> str:
    try:
        from sqlalchemy.engine import make_url

        parsed = make_url(url)
        return f"{parsed.get_backend_name()}://{parsed.host or 'local'}/{parsed.database or ''}"
    except Exception:
        return "postgresql://***"


def run(
    *, db_url: str, allowed_emails: set[str], apply: bool, reason: str, actor: str
) -> dict[str, Any]:
    if not is_postgres_url(db_url):
        raise SystemExit("ERROR: DATABASE_URL must point to PostgreSQL.")

    engine = create_engine(db_url, pool_pre_ping=True)
    with engine.begin() as conn:
        before = build_summary(fetch_users(conn), allowed_emails)
        changed = 0
        if apply:
            changed = apply_cleanup(conn, allowed_emails=allowed_emails, reason=reason, actor=actor)
        after = build_summary(fetch_users(conn), allowed_emails)

    return {
        "mode": "apply" if apply else "dry-run",
        "db_target": _safe_db_target(db_url),
        "allowed_emails_masked": [mask_email(email) for email in sorted(allowed_emails)],
        "changed_users": changed,
        "before": before,
        "after": after,
        "access_hygiene_ok": after["unauthorized_active"] == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Disable unauthorized closed-beta test users.")
    parser.add_argument("--apply", action="store_true", help="Apply cleanup. Default is dry-run.")
    parser.add_argument(
        "--allowed-email",
        action="append",
        default=None,
        help="Allowed email. Can be repeated or comma-separated. Defaults to Alan's two beta accounts.",
    )
    parser.add_argument(
        "--reason",
        default="Closed beta cleanup: unauthorized test user disabled",
    )
    parser.add_argument("--actor", default=os.getenv("USER") or "codex")
    parser.add_argument("--database-url", default=None)
    args = parser.parse_args()

    db_url = args.database_url or resolve_database_url()
    allowed_emails = parse_allowed_emails(args.allowed_email)
    result = run(
        db_url=db_url,
        allowed_emails=allowed_emails,
        apply=args.apply,
        reason=args.reason,
        actor=args.actor,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
