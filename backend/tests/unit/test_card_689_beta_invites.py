"""Card #689 -- single-use beta invite, persisted admin role, bootstrap.

Covers the happy path and the blockers of the invite flow, the two public
doors (register / leads), the deployment bootstrap, the admin issuance surface
and the audit trail.
"""

from __future__ import annotations

import importlib.util
import io
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, func, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models import BetaInvite, BetaAccessAuditLog, User
import app.middleware.authMiddleware as auth_middleware
import app.routes.admin_users as admin_users_routes
import app.routes.auth as auth_routes
import app.routes.beta_invite_public as beta_invite_public
import app.routes.leads as leads_routes
from app.services.beta_access import verify_password
from app.services.beta_invites import (
    STATE_ALREADY_CONSUMED,
    STATE_EMAIL_MISMATCH,
    STATE_EXPIRED,
    STATE_NOT_FOUND,
    STATE_REVOKED,
    InviteConsumptionError,
    build_invite_path,
    consume_invite,
    default_ttl_hours,
    find_invite_by_token,
    hash_invite_token,
    issue_invite,
    validate_invite,
)

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def invite_db_session(postgres_isolation, unit_database_url):
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
                "role VARCHAR(16) NOT NULL DEFAULT 'user'"
            )
        )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture
def public_invite_client(invite_db_session):
    app = FastAPI()
    app.include_router(beta_invite_public.router)
    app.dependency_overrides[get_db] = lambda: invite_db_session
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}@example.com"


def _seed_user(db, *, email: str, role: str = "user", status: str = "active", **kwargs) -> User:
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=kwargs.pop("password_hash", "original-hash"),
        name=kwargs.pop("name", "Seeded"),
        role=role,
        status=status,
        **kwargs,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _issue(db, email: str, **kwargs):
    invite, token = issue_invite(db, email=email, **kwargs)
    db.commit()
    db.refresh(invite)
    return invite, token


def _audits(db, email: str) -> list[BetaAccessAuditLog]:
    return (
        db.query(BetaAccessAuditLog)
        .filter(BetaAccessAuditLog.email == email.lower())
        .order_by(BetaAccessAuditLog.id.asc())
        .all()
    )


def _assert_token_never_recorded(db, token: str, email: str) -> None:
    audits = _audits(db, email)
    assert audits
    for audit in audits:
        assert token not in str(audit.metadata_json)
        assert token not in str(audit.result)
        assert token not in str(audit.action)
    invites = db.query(BetaInvite).all()
    for invite in invites:
        assert token not in str(invite.token_hash)
        assert token not in str(invite.__dict__)


# --- 6.1 happy path ---------------------------------------------------------


def test_invite_happy_path_creates_regular_account_with_chosen_password(invite_db_session):
    db = invite_db_session
    email = _email("happy")
    invite, token = _issue(db, email)

    assert invite.token_hash == hash_invite_token(token)
    assert invite.token_hash != token
    assert invite.consumed_at is None

    consumption = consume_invite(
        db,
        token=token,
        email=f"  {email.upper()}  ",
        password="owner-chosen-pass",
        name="Dono do convite",
    )
    db.commit()

    user = db.query(User).filter(User.email == email).one()
    assert consumption.account_created is True
    assert user.role == "user"
    assert user.must_change_password is False
    assert user.temporary_password_expires_at is None
    assert verify_password("owner-chosen-pass", user.password_hash) is True

    assert consumption.invite.consumed_at is not None
    assert str(consumption.invite.consumed_user_id) == str(user.id)

    results = [audit.result for audit in _audits(db, email)]
    assert "issued" in results
    assert "consumed" in results
    _assert_token_never_recorded(db, token, email)


# --- 6.2 blockers -----------------------------------------------------------


def test_invite_second_consumption_fails_explicitly_and_is_audited(invite_db_session):
    db = invite_db_session
    email = _email("reuse")
    _, token = _issue(db, email)
    consume_invite(db, token=token, email=email, password="first-pass-123")
    db.commit()

    with pytest.raises(InviteConsumptionError) as refusal:
        consume_invite(db, token=token, email=email, password="second-pass-123")

    assert refusal.value.state == STATE_ALREADY_CONSUMED
    assert refusal.value.status_code == 409
    assert "já foi utilizado" in refusal.value.message
    db.rollback()

    user = db.query(User).filter(User.email == email).one()
    assert verify_password("first-pass-123", user.password_hash) is True
    assert verify_password("second-pass-123", user.password_hash) is False
    assert db.query(User).filter(User.email == email).count() == 1
    assert "already_consumed" in [audit.result for audit in _audits(db, email)]
    _assert_token_never_recorded(db, token, email)


def test_expired_invite_is_refused_with_actionable_message_and_audit(invite_db_session):
    db = invite_db_session
    email = _email("expired")
    start = datetime.utcnow() - timedelta(hours=5)
    _, token = _issue(db, email, ttl_hours=1, now=start)

    with pytest.raises(InviteConsumptionError) as refusal:
        consume_invite(db, token=token, email=email, password="late-pass-123")

    assert refusal.value.state == STATE_EXPIRED
    assert refusal.value.status_code == 410
    assert "expirado" in refusal.value.message
    assert "novo link" in refusal.value.message
    db.rollback()

    assert db.query(User).filter(User.email == email).first() is None
    assert "expired" in [audit.result for audit in _audits(db, email)]
    _assert_token_never_recorded(db, token, email)


def test_invite_address_mismatch_is_refused_and_audited(invite_db_session):
    db = invite_db_session
    invited = _email("bound")
    other = _email("forwarded")
    _, token = _issue(db, invited)

    with pytest.raises(InviteConsumptionError) as refusal:
        consume_invite(db, token=token, email=other, password="other-pass-123")

    assert refusal.value.state == STATE_EMAIL_MISMATCH
    assert refusal.value.status_code == 403
    db.rollback()

    assert db.query(User).filter(User.email.in_([invited, other])).count() == 0
    # The refusal is audited against the address of the attempt.
    assert "email_mismatch" in [audit.result for audit in _audits(db, other)]
    assert [audit.result for audit in _audits(db, invited)] == ["issued"]
    _assert_token_never_recorded(db, token, other)


def test_reissue_supersedes_open_invite_and_keeps_consumed_history(invite_db_session):
    db = invite_db_session
    email = _email("reissue")

    first, first_token = _issue(db, email)
    second, second_token = _issue(db, email)

    db.refresh(first)
    assert first.revoked_at is not None
    assert first.revoked_reason == "superseded"
    assert str(first.superseded_by_id) == str(second.id)
    assert "superseded" in [audit.result for audit in _audits(db, email)]

    with pytest.raises(InviteConsumptionError) as refusal:
        consume_invite(db, token=first_token, email=email, password="old-link-123")
    assert refusal.value.state == STATE_REVOKED
    db.rollback()

    consume_invite(db, token=second_token, email=email, password="new-link-123")
    db.commit()
    assert db.query(User).filter(User.email == email).count() == 1

    # History of consumed invites is left untouched by a later reissue.
    third, _ = _issue(db, email)
    db.refresh(second)
    assert second.consumed_at is not None
    assert second.revoked_at is None
    assert third.revoked_at is None
    _assert_token_never_recorded(db, second_token, email)


def test_reissue_leaves_expired_invites_untouched(invite_db_session):
    db = invite_db_session
    email = _email("reissue-expired")
    start = datetime.utcnow() - timedelta(hours=5)
    expired, expired_token = _issue(db, email, ttl_hours=1, now=start)
    current, current_token = _issue(db, email)

    db.refresh(expired)
    assert expired.revoked_at is None
    assert expired.consumed_at is None
    assert expired.superseded_by_id is None
    assert current.revoked_at is None

    with pytest.raises(InviteConsumptionError) as refusal:
        consume_invite(db, token=expired_token, email=email, password="old-expired-123")
    assert refusal.value.state == STATE_EXPIRED
    db.rollback()

    consume_invite(db, token=current_token, email=email, password="fresh-link-123")
    db.commit()
    assert db.query(User).filter(User.email == email).count() == 1


def test_issue_invite_locks_open_rows_for_update_before_insert(invite_db_session):
    db = invite_db_session
    email = _email("lock-sql")
    statements: list[str] = []

    def _capture(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    bind = db.get_bind()
    event.listen(bind, "before_cursor_execute", _capture)
    try:
        issue_invite(db, email=email)
        db.commit()
    finally:
        event.remove(bind, "before_cursor_execute", _capture)

    lock_sql = [
        sql for sql in statements if "FOR UPDATE" in sql.upper() and "beta_invites" in sql.lower()
    ]
    assert lock_sql, statements


def test_concurrent_reissue_keeps_a_single_open_invite(invite_db_session):
    db = invite_db_session
    email = _email("race-reissue")
    _issue(db, email)
    db.expire_all()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db.get_bind())

    def _reissue(_):
        session = SessionLocal()
        try:
            invite, _token = issue_invite(session, email=email)
            session.commit()
            return str(invite.id)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(_reissue, range(2)))

    db.expire_all()
    now = datetime.utcnow()
    open_invites = (
        db.query(BetaInvite)
        .filter(
            func.lower(BetaInvite.email) == email,
            BetaInvite.consumed_at.is_(None),
            BetaInvite.revoked_at.is_(None),
            BetaInvite.expires_at > now,
        )
        .all()
    )
    assert len(open_invites) == 1


def test_frontend_ingress_forwards_beta_invite_path_to_backend():
    nginx = (ROOT / "frontend" / "nginx.conf").read_text(encoding="utf-8")
    vite = (ROOT / "frontend" / "vite.config.ts").read_text(encoding="utf-8")

    assert "location /beta-invite/" in nginx
    assert "proxy_pass" in nginx
    assert nginx.index("location /beta-invite/") < nginx.index("try_files")
    assert "'/beta-invite'" in vite
    assert "server:" in vite
    assert "preview:" in vite


def test_invite_for_existing_account_resets_password_only(invite_db_session):
    db = invite_db_session
    email = _email("existing")
    existing = _seed_user(db, email=email, role="user", password_hash="original-hash")
    _, token = _issue(db, email)

    consumption = consume_invite(db, token=token, email=email, password="new-owner-pass")
    db.commit()

    db.refresh(existing)
    assert consumption.account_created is False
    assert db.query(User).filter(User.email == email).count() == 1
    assert existing.role == "user"
    assert verify_password("new-owner-pass", existing.password_hash) is True
    assert existing.password_hash != "original-hash"


def test_invite_never_changes_role_or_rehabilitates_banned_account(invite_db_session):
    db = invite_db_session
    banned_email = _email("banned")
    admin_email = _email("admin-existing")
    banned = _seed_user(db, email=banned_email, role="user", status="banned", is_banned=True)
    admin = _seed_user(db, email=admin_email, role="admin")

    _, banned_token = _issue(db, banned_email)
    consume_invite(db, token=banned_token, email=banned_email, password="banned-pass-123")
    db.commit()

    _, admin_token = _issue(db, admin_email)
    consume_invite(db, token=admin_token, email=admin_email, password="admin-pass-123")
    db.commit()

    db.refresh(banned)
    db.refresh(admin)
    assert banned.status == "banned"
    assert banned.is_banned is True
    assert banned.role == "user"
    assert admin.role == "admin"


# --- 6.3 public doors: register and leads -----------------------------------


def test_register_without_valid_invite_is_neutral_for_privileged_addresses(
    invite_db_session, monkeypatch
):
    db = invite_db_session
    privileged = _email("admin-door")
    visitor = _email("visitor-door")
    monkeypatch.setattr(auth_routes, "ADMIN_EMAILS", {privileged})
    monkeypatch.setattr(auth_routes, "BETA_INVITED_EMAILS", {privileged})
    monkeypatch.setattr(auth_routes, "BETA_PUBLIC_REGISTRATION_ENABLED", False)

    refusals = []
    for address in (privileged, visitor):
        with pytest.raises(HTTPException) as refusal:
            auth_routes.register(
                auth_routes.RegisterRequest(
                    email=address,
                    password="valid-pass-1",
                    name="Visitor",
                ),
                db,
            )
        refusals.append(refusal.value)

    assert {refusal.status_code for refusal in refusals} == {403}
    assert {refusal.detail for refusal in refusals} == {"Closed beta access requires invitation"}
    assert db.query(User).filter(User.email.in_([privileged, visitor])).count() == 0


def test_register_with_public_flag_enabled_still_requires_invite(invite_db_session, monkeypatch):
    db = invite_db_session
    email = _email("flag-door")
    monkeypatch.setattr(auth_routes, "BETA_PUBLIC_REGISTRATION_ENABLED", True)

    with pytest.raises(HTTPException) as refusal:
        auth_routes.register(
            auth_routes.RegisterRequest(
                email=email,
                password="valid-pass-1",
                name="Flagged",
            ),
            db,
        )

    assert refusal.value.status_code == 403
    assert db.query(User).filter(User.email == email).first() is None


def test_register_with_valid_invite_creates_non_admin_account(invite_db_session, monkeypatch):
    db = invite_db_session
    email = _email("register-ok")
    monkeypatch.setattr(auth_routes, "BETA_PUBLIC_REGISTRATION_ENABLED", False)
    invite, token = _issue(db, email)

    response = auth_routes.register(
        auth_routes.RegisterRequest(
            email=email,
            password="registered-pass",
            name="Registered",
            inviteToken=token,
        ),
        db,
    )

    user = db.query(User).filter(User.email == email).one()
    assert response.email == email
    assert user.role == "user"
    assert verify_password("registered-pass", user.password_hash) is True
    db.refresh(invite)
    assert invite.consumed_at is not None
    assert "consumed" in [audit.result for audit in _audits(db, email)]


def test_register_with_invite_for_existing_account_keeps_400_without_consuming(
    invite_db_session,
):
    db = invite_db_session
    email = _email("register-dup")
    existing = _seed_user(db, email=email, password_hash="untouched-hash")
    invite, token = _issue(db, email)

    with pytest.raises(HTTPException) as refusal:
        auth_routes.register(
            auth_routes.RegisterRequest(
                email=email,
                password="duplicate-pass",
                name="Duplicate",
                inviteToken=token,
            ),
            db,
        )

    assert refusal.value.status_code == 400
    assert refusal.value.detail == "Email already registered"
    db.rollback()
    db.refresh(existing)
    db.refresh(invite)
    assert existing.password_hash == "untouched-hash"
    assert invite.consumed_at is None
    assert invite.revoked_at is None
    assert db.query(User).filter(User.email == email).count() == 1

    # The invite is still open for the owner's password-definition flow (D8).
    consume_invite(db, token=token, email=email, password="recovered-pass")
    db.commit()
    db.refresh(existing)
    assert verify_password("recovered-pass", existing.password_hash) is True


def test_register_with_invite_for_another_address_does_not_consume(invite_db_session):
    db = invite_db_session
    invited = _email("invited-other")
    attacker = _email("attacker")
    invite, token = _issue(db, invited)

    with pytest.raises(HTTPException) as refusal:
        auth_routes.register(
            auth_routes.RegisterRequest(
                email=attacker,
                password="attacker-pass",
                name="Attacker",
                inviteToken=token,
            ),
            db,
        )

    assert refusal.value.status_code == 403
    db.rollback()
    db.refresh(invite)
    assert invite.consumed_at is None
    assert invite.revoked_at is None
    assert db.query(User).filter(User.email.in_([invited, attacker])).count() == 0
    assert "email_mismatch" in [audit.result for audit in _audits(db, attacker)]


def test_leads_without_invite_stays_neutral_and_creates_nothing(invite_db_session):
    db = invite_db_session
    email = _email("lead-no-invite")

    response = leads_routes.create_lead_access(
        leads_routes.LeadAccessRequest(name="Lead", email=email),
        db,
    )

    payload = response.model_dump()
    assert payload["status"] == "accepted"
    assert "userCreated" not in payload
    assert db.query(User).filter(User.email == email).first() is None
    audits = _audits(db, email)
    assert [audit.result for audit in audits] == ["received_without_account"]
    assert audits[0].source == "landing"
    assert "temporary_password" not in str(audits[0].metadata_json)


def test_leads_with_valid_invite_does_not_consume_and_keeps_it_open(invite_db_session):
    db = invite_db_session
    email = _email("lead-with-invite")
    invite, token = _issue(db, email)

    response = leads_routes.create_lead_access(
        leads_routes.LeadAccessRequest(
            name="Lead",
            email=email,
            inviteToken=token,
            utm_source="linkedin",
        ),
        db,
    )

    payload = response.model_dump()
    assert payload["status"] == "accepted"
    db.refresh(invite)
    assert invite.consumed_at is None
    assert invite.revoked_at is None
    assert db.query(User).filter(User.email == email).first() is None
    audits = _audits(db, email)
    assert "invite_validated_not_consumed" in [audit.result for audit in audits]
    assert "issued" in [audit.result for audit in audits]
    _assert_token_never_recorded(db, token, email)

    # The invite is still consumable on the invite link's own POST.
    consume_invite(db, token=token, email=email, password="from-link-pass")
    db.commit()
    assert db.query(User).filter(User.email == email).count() == 1


def test_leads_with_expired_invite_stays_neutral_and_creates_nothing(invite_db_session):
    db = invite_db_session
    email = _email("lead-expired")
    _, token = _issue(db, email, ttl_hours=1, now=datetime.utcnow() - timedelta(hours=3))

    response = leads_routes.create_lead_access(
        leads_routes.LeadAccessRequest(name="Lead", email=email, inviteToken=token),
        db,
    )

    assert response.status == "accepted"
    assert db.query(User).filter(User.email == email).first() is None
    audits = _audits(db, email)
    states = [audit.metadata_json.get("invite_state") for audit in audits]
    assert "expired" in states
    assert "issued" in [audit.result for audit in audits]


def test_validate_invite_reports_unknown_token_without_state_change(invite_db_session):
    db = invite_db_session
    decision = validate_invite(db, token="not-a-real-token", email=_email("unknown"))
    assert decision.state == STATE_NOT_FOUND
    assert decision.invite is None
    assert find_invite_by_token(db, "") is None
    assert find_invite_by_token(db, None) is None


# --- 6.4 bootstrap ----------------------------------------------------------

_bootstrap_spec = importlib.util.spec_from_file_location(
    "card_689_bootstrap_admin", ROOT / "ops" / "bootstrap_admin.py"
)
assert _bootstrap_spec and _bootstrap_spec.loader
bootstrap_admin = importlib.util.module_from_spec(_bootstrap_spec)
_bootstrap_spec.loader.exec_module(bootstrap_admin)


def test_bootstrap_creates_only_the_configured_admin_and_is_idempotent(
    invite_db_session, monkeypatch
):
    db = invite_db_session
    primary = _email("bootstrap-primary")
    secondary = _email("bootstrap-secondary")
    unrelated = _seed_user(db, email=_email("bootstrap-unrelated"))

    first = bootstrap_admin.bootstrap_admin(
        db, emails=[primary, secondary], password="operator-secret-1"
    )
    assert first["created"] == [primary]
    assert first["skipped"] == [secondary]

    admin = db.query(User).filter(User.email == primary).one()
    assert admin.role == "admin"
    assert verify_password("operator-secret-1", admin.password_hash) is True
    assert db.query(User).filter(User.role == "admin").count() == 1
    assert db.query(User).filter(User.email == secondary).first() is None

    second = bootstrap_admin.bootstrap_admin(
        db, emails=[primary, secondary], password="operator-secret-1"
    )
    assert second["unchanged"] == [primary]
    assert db.query(User).filter(User.role == "admin").count() == 1

    db.refresh(unrelated)
    assert unrelated.role == "user"


def test_bootstrap_promotes_existing_account_without_touching_password(invite_db_session):
    db = invite_db_session
    email = _email("bootstrap-existing")
    existing = _seed_user(db, email=email, password_hash="keep-this-hash")

    summary = bootstrap_admin.bootstrap_admin(db, emails=[email], password="ignored-secret")

    assert summary["promoted"] == [email]
    db.refresh(existing)
    assert existing.role == "admin"
    assert existing.password_hash == "keep-this-hash"


def test_bootstrap_requires_operator_credential_when_account_is_missing(invite_db_session):
    db = invite_db_session
    email = _email("bootstrap-missing")

    with pytest.raises(bootstrap_admin.BootstrapError):
        bootstrap_admin.bootstrap_admin(db, emails=[email], password=None)
    with pytest.raises(bootstrap_admin.BootstrapError):
        bootstrap_admin.bootstrap_admin(db, emails=[], password="operator-secret-1")


def test_bootstrap_main_never_prints_the_credential(invite_db_session, monkeypatch):
    db = invite_db_session
    email = _email("bootstrap-print")
    monkeypatch.setenv("ADMIN_EMAILS", email)
    monkeypatch.setenv("BOOTSTRAP_ADMIN_PASSWORD", "super-secret-operator")
    monkeypatch.setattr(bootstrap_admin, "SessionLocal", lambda: db)
    schema_calls = []
    monkeypatch.setattr(
        bootstrap_admin,
        "ensure_user_role_column",
        lambda: schema_calls.append(True),
    )

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = bootstrap_admin.main([])

    output = buffer.getvalue()
    assert exit_code == 0
    # D9: the bootstrap runs before the persistence migration, so it guarantees
    # the schema it reads through the runtime schema init.
    assert schema_calls == [True]
    assert email in output
    assert "super-secret-operator" not in output
    assert db.query(User).filter(User.email == email).one().role == "admin"


# --- 6.5 admin issuance surface and non-admin refusal -----------------------


def test_admin_issues_invite_and_returns_the_link_once(invite_db_session, monkeypatch):
    db = invite_db_session
    monkeypatch.setenv("BETA_INVITE_BASE_URL", "https://dev.criptofarol.com.br/")
    admin = _seed_user(db, email=_email("issuer"), role="admin")
    target = _email("invited-by-admin")

    response = admin_users_routes.create_beta_invite(
        admin_users_routes.BetaInviteCreateRequest(email=target.upper(), ttlHours=24),
        _admin_user_id=str(admin.id),
        db=db,
    )

    assert response.email == target
    token = response.invitePath.removeprefix("/beta-invite/")
    assert token
    assert response.invitePath == build_invite_path(token)
    assert response.inviteUrl == f"https://dev.criptofarol.com.br/beta-invite/{token}"

    invite = db.query(BetaInvite).one()
    assert invite.token_hash == hash_invite_token(token)
    assert token not in str(invite.__dict__)
    ttl = invite.expires_at - invite.created_at
    assert timedelta(hours=23) < ttl <= timedelta(hours=24)

    audits = _audits(db, target)
    assert audits[0].action == "beta_invite_issued"
    assert audits[0].result == "issued"
    assert audits[0].source == "admin_invite"
    _assert_token_never_recorded(db, token, target)


def test_admin_invite_validation_is_explicit_without_revealing_privilege(invite_db_session):
    db = invite_db_session
    admin = _seed_user(db, email=_email("issuer-validation"), role="admin")

    with pytest.raises(HTTPException) as bad_email:
        admin_users_routes.create_beta_invite(
            admin_users_routes.BetaInviteCreateRequest(email="not-an-email"),
            _admin_user_id=str(admin.id),
            db=db,
        )
    assert bad_email.value.status_code == 400

    with pytest.raises(HTTPException) as bad_ttl:
        admin_users_routes.create_beta_invite(
            admin_users_routes.BetaInviteCreateRequest(email=_email("ttl"), ttlHours=5000),
            _admin_user_id=str(admin.id),
            db=db,
        )
    assert bad_ttl.value.status_code == 400
    assert db.query(BetaInvite).count() == 0


@pytest.mark.asyncio
async def test_non_admin_cannot_issue_invite(invite_db_session):
    db = invite_db_session
    regular = _seed_user(db, email=_email("regular"), role="user")

    with pytest.raises(HTTPException) as refusal:
        await auth_middleware.get_current_admin(str(regular.id), db)

    assert refusal.value.status_code == 403
    assert db.query(BetaInvite).count() == 0


@pytest.mark.asyncio
async def test_admin_authorization_reads_persisted_role_not_the_env(invite_db_session, monkeypatch):
    db = invite_db_session
    monkeypatch.setattr(auth_middleware, "ADMIN_EMAILS", {"env-admin@example.com"})
    env_only = _seed_user(db, email="env-admin@example.com", role="user")
    persisted = _seed_user(db, email=_email("persisted-admin"), role="admin")

    assert auth_middleware.is_admin_email(db, "env-admin@example.com") is False
    assert auth_middleware.is_admin_email(db, persisted.email) is True
    with pytest.raises(HTTPException):
        await auth_middleware.get_current_admin(str(env_only.id), db)
    assert await auth_middleware.get_current_admin(str(persisted.id), db) == str(persisted.id)

    serialized = admin_users_routes._serialize_user(persisted)
    assert serialized["role"] == "admin"
    assert serialized["isAdmin"] is True


# --- invite link surface (3.7) ---------------------------------------------


def test_invite_link_get_serves_locked_form_for_valid_token(
    invite_db_session, public_invite_client
):
    db = invite_db_session
    email = _email("link-get")
    _, token = _issue(db, email)

    response = public_invite_client.get(f"/beta-invite/{token}")

    assert response.status_code == 200
    assert email in response.text
    assert "readonly" in response.text
    assert "/monitor" not in response.text
    assert "/favorites" not in response.text
    # A valid GET only renders the form: nothing is consumed or audited.
    assert [audit.result for audit in _audits(db, email)] == ["issued"]


def test_invite_link_get_refuses_expired_token_with_actionable_message(
    invite_db_session, public_invite_client
):
    db = invite_db_session
    email = _email("link-expired")
    _, token = _issue(db, email, ttl_hours=1, now=datetime.utcnow() - timedelta(hours=2))

    response = public_invite_client.get(f"/beta-invite/{token}")

    assert response.status_code == 410
    assert "expirado" in response.text
    assert "novo link" in response.text
    assert "expired" in [audit.result for audit in _audits(db, email)]
    _assert_token_never_recorded(db, token, email)


def test_invite_link_get_refuses_unknown_token(public_invite_client):
    response = public_invite_client.get("/beta-invite/definitely-not-a-token")
    assert response.status_code == 404
    assert "Convite não encontrado" in response.text


def test_invite_link_post_consumes_once_and_defines_the_password(
    invite_db_session, public_invite_client
):
    db = invite_db_session
    email = _email("link-post")
    invite, token = _issue(db, email)

    response = public_invite_client.post(
        f"/beta-invite/{token}",
        data={
            "email": email,
            "password": "link-chosen-pass",
            "passwordConfirm": "link-chosen-pass",
            "name": "Dono Link",
        },
    )

    assert response.status_code == 200
    assert "Acesso liberado" in response.text
    user = db.query(User).filter(User.email == email).one()
    assert user.role == "user"
    assert user.name == "Dono Link"
    assert verify_password("link-chosen-pass", user.password_hash) is True
    db.refresh(invite)
    assert invite.consumed_at is not None

    reuse = public_invite_client.post(
        f"/beta-invite/{token}",
        data={
            "email": email,
            "password": "other-pass-123",
            "passwordConfirm": "other-pass-123",
        },
    )
    assert reuse.status_code == 409
    assert "já foi utilizado" in reuse.text
    db.refresh(user)
    assert verify_password("link-chosen-pass", user.password_hash) is True
    _assert_token_never_recorded(db, token, email)


def test_invite_link_post_refuses_another_address_and_short_password(
    invite_db_session, public_invite_client
):
    db = invite_db_session
    invited = _email("link-bound")
    other = _email("link-other")
    invite, token = _issue(db, invited)

    mismatch = public_invite_client.post(
        f"/beta-invite/{token}",
        data={"email": other, "password": "valid-pass-1", "passwordConfirm": "valid-pass-1"},
    )
    assert mismatch.status_code == 403
    assert db.query(User).filter(User.email.in_([invited, other])).count() == 0

    short = public_invite_client.post(
        f"/beta-invite/{token}",
        data={"email": invited, "password": "short", "passwordConfirm": "short"},
    )
    assert short.status_code == 200
    assert "pelo menos" in short.text

    db.refresh(invite)
    assert invite.consumed_at is None
    assert "email_mismatch" in [audit.result for audit in _audits(db, other)]


def test_invite_ttl_defaults_and_environment_override(invite_db_session, monkeypatch):
    monkeypatch.setenv("BETA_INVITE_TTL_HOURS", "12")
    assert default_ttl_hours() == 12

    db = invite_db_session
    email = _email("ttl-default")
    invite, _ = issue_invite(db, email=email, now=datetime(2026, 1, 1, 12, 0, 0))
    assert invite.expires_at - invite.created_at == timedelta(hours=12)

    monkeypatch.setenv("BETA_INVITE_TTL_HOURS", "99999")
    assert default_ttl_hours() == 720
    monkeypatch.setenv("BETA_INVITE_TTL_HOURS", "not-a-number")
    assert default_ttl_hours() == 72
