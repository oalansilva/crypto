#!/usr/bin/env python3
"""Deployment bootstrap for the first administrator (card #689, D9).

Host-only command -- it is **not** an HTTP endpoint and is never reachable from
``POST /api/auth/register`` or the public landing lead endpoint.  It guarantees
that the address already configured in the environment (``ADMIN_EMAILS``)
exists and holds the administrator role:

* account already exists -> only the role is granted (password untouched, no
  extra account);
* account does not exist on a fresh deployment -> it is created as an
  administrator with a credential supplied explicitly by the operator (env or
  stdin).  The credential is never generated, printed, or logged;
* idempotent: running it again yields the same result, creates no second
  administrator, and promotes nothing outside the configured list.

Run it **before** the persistence migration and before the route enforcement
(deploy order contract of D9).
"""

from __future__ import annotations

import argparse
import getpass
import os
import sys
import uuid
from pathlib import Path
from typing import Iterable

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
for _path in (str(ROOT_DIR), str(BACKEND_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from sqlalchemy import func  # noqa: E402
from sqlalchemy.exc import SQLAlchemyError  # noqa: E402

from app.database import SessionLocal, ensure_user_role_column  # noqa: E402
from app.models import User  # noqa: E402
from app.services.beta_access import hash_password  # noqa: E402

ROLE_ADMIN = "admin"
DEFAULT_PASSWORD_ENV = "BOOTSTRAP_ADMIN_PASSWORD"
MIN_PASSWORD_LENGTH = 8


class BootstrapError(RuntimeError):
    """Explicit bootstrap failure; never carries credential material."""


def configured_admin_emails() -> list[str]:
    raw = os.getenv("ADMIN_EMAILS", "") or ""
    ordered = [email.strip().lower() for email in raw.split(",") if email.strip()]
    return list(dict.fromkeys(ordered))


def _display_name(email: str) -> str:
    local_part = email.split("@", 1)[0].strip()
    return local_part or email


def read_operator_password(*, password_env: str, password_stdin: bool) -> str:
    """Read the operator-supplied credential without ever echoing it back."""

    value = str(os.getenv(password_env, "") or "") if password_env else ""
    if value:
        return value

    if password_stdin:
        secret = sys.stdin.readline().rstrip("\r\n")
        if secret:
            return secret
        raise BootstrapError("nenhuma credencial recebida em stdin")

    if sys.stdin is not None and sys.stdin.isatty():
        first = getpass.getpass("Senha do administrador: ")
        second = getpass.getpass("Confirme a senha: ")
        if first != second:
            raise BootstrapError("as senhas informadas não conferem")
        return first

    raise BootstrapError(
        f"nenhuma credencial fornecida; defina {password_env} ou use --password-stdin"
    )


def bootstrap_admin(
    session,
    *,
    emails: Iterable[str],
    password: str | None = None,
) -> dict[str, list[str]]:
    """Make every configured address that exists an admin; create only the first.

    Returns a summary of what changed.  Raises :class:`BootstrapError` instead
    of guessing when the primary address has no account and no credential was
    supplied.
    """

    ordered = [str(email).strip().lower() for email in emails if str(email).strip()]
    ordered = list(dict.fromkeys(ordered))
    if not ordered:
        raise BootstrapError("ADMIN_EMAILS is not configured; nothing to bootstrap")

    created: list[str] = []
    promoted: list[str] = []
    unchanged: list[str] = []
    skipped: list[str] = []

    for index, email in enumerate(ordered):
        user = session.query(User).filter(func.lower(User.email) == email).first()

        if user is None:
            if index != 0:
                # Never create a second administrator.
                skipped.append(email)
                continue
            if not password:
                raise BootstrapError(
                    "a conta configurada não existe; forneça a credencial do operador "
                    "para criar o administrador"
                )
            if len(password) < MIN_PASSWORD_LENGTH:
                raise BootstrapError(
                    f"a credencial do operador precisa ter pelo menos {MIN_PASSWORD_LENGTH} caracteres"
                )
            user = User(
                id=uuid.uuid4(),
                email=email,
                password_hash=hash_password(password),
                name=_display_name(email),
                role=ROLE_ADMIN,
                status="active",
                must_change_password=False,
            )
            session.add(user)
            session.flush()
            created.append(email)
            continue

        if str(user.role or "").strip().lower() != ROLE_ADMIN:
            user.role = ROLE_ADMIN
            session.add(user)
            promoted.append(email)
        else:
            unchanged.append(email)

    session.commit()
    return {
        "created": created,
        "promoted": promoted,
        "unchanged": unchanged,
        "skipped": skipped,
    }


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--password-env",
        default=DEFAULT_PASSWORD_ENV,
        help=(
            "environment variable holding the operator credential used only when the "
            f"configured account does not exist yet (default: {DEFAULT_PASSWORD_ENV})"
        ),
    )
    parser.add_argument(
        "--password-stdin",
        action="store_true",
        help="read the operator credential from stdin instead of prompting",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    emails = configured_admin_emails()

    try:
        if not emails:
            raise BootstrapError("ADMIN_EMAILS is not configured; nothing to bootstrap")

        # D9 runs the bootstrap before the persistence migration.  The narrow
        # schema guard below is idempotent and guarantees the `role` column the
        # command reads, without depending on the rest of the runtime init.
        try:
            ensure_user_role_column()
        except SQLAlchemyError as error:
            raise BootstrapError(
                "users table unavailable; apply the baseline migration before the "
                f"bootstrap: {type(error).__name__}"
            )

        password: str | None = None
        session = SessionLocal()
        try:
            primary_exists = (
                session.query(User).filter(func.lower(User.email) == emails[0]).first() is not None
            )
            if not primary_exists:
                password = read_operator_password(
                    password_env=args.password_env,
                    password_stdin=args.password_stdin,
                )
            summary = bootstrap_admin(session, emails=emails, password=password)
        finally:
            session.close()
    except BootstrapError as error:
        print(f"bootstrap_admin: {error}", file=sys.stderr)
        return 1
    except SQLAlchemyError as error:
        print(
            f"bootstrap_admin: database error ({type(error).__name__}); nothing was changed",
            file=sys.stderr,
        )
        return 1

    for email in summary["created"]:
        print(f"bootstrap_admin: created administrator {email}")
    for email in summary["promoted"]:
        print(f"bootstrap_admin: granted administrator role to {email}")
    for email in summary["unchanged"]:
        print(f"bootstrap_admin: administrator already present {email}")
    for email in summary["skipped"]:
        print(f"bootstrap_admin: skipped address without account {email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
