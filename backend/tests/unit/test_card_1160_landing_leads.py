"""Card #1160 -- landing lead saved at step 1, enriched at step 2, Telegram notice.

Covers D1 (``landing_leads`` upsert by normalized e-mail, ``step`` 1/2/absent),
D3 (notice to admins with a linked Telegram after the commit, failure only
logged without personal data) and the #689 guarantees that stay (neutral 202,
audit, no account, invite never consumed).
"""

from __future__ import annotations

import importlib.util
import logging
import uuid
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

import app.services.monitor_telegram_alerts as telegram_module
import app.routes.leads as leads_routes
from app.database import Base, get_db
from app.models import BetaAccessAuditLog, BetaInvite, LandingLead, User
from app.services.beta_invites import issue_invite

ADMIN_CHAT = "900100200"
BLOCK_PROD_BOT = "CRYPTO_TELEGRAM_ALERT_SCAN_BLOCK_PROD_BOT"
MIGRATION = Path(__file__).parents[2] / "alembic/versions/20261030_0001_landing_leads.py"


@pytest.fixture
def leads_db(postgres_isolation, unit_database_url):
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
def sent(monkeypatch):
    """Capture every Telegram send (token configured, no network)."""

    calls: list[dict] = []

    def fake_send(*, bot_token, chat_id, text, dry_run=False):
        calls.append({"chat_id": chat_id, "text": text})
        return {"ok": True}

    monkeypatch.setenv("MONITOR_TELEGRAM_BOT_TOKEN", "test-token-not-real")
    monkeypatch.delenv(BLOCK_PROD_BOT, raising=False)
    monkeypatch.setattr(telegram_module, "send_telegram_message", fake_send)
    return calls


@pytest.fixture
def client(leads_db):
    app = FastAPI()
    app.include_router(leads_routes.router)
    app.dependency_overrides[get_db] = lambda: leads_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}@example.com"


def _seed_user(db, *, email: str, role: str = "user", telegram_chat_id: str | None = None) -> User:
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash="original-hash",
        name="Seeded",
        role=role,
        status="active",
        telegram_chat_id=telegram_chat_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _seed_admin(db) -> User:
    return _seed_user(db, email=_email("admin"), role="admin", telegram_chat_id=ADMIN_CHAT)


def _leads(db, email: str) -> list[LandingLead]:
    db.expire_all()
    return db.query(LandingLead).filter(LandingLead.email == email.lower()).all()


def _step1(client, email: str, name: str = "Ana Lead", **extra):
    return client.post(
        "/api/leads",
        json={"step": 1, "name": name, "email": email, "origin": "landing", **extra},
    )


def _step2(client, email: str, **fields):
    return client.post("/api/leads", json={"step": 2, "email": email, **fields})


def test_step1_saves_lead_without_step2(client, leads_db, sent):
    _seed_admin(leads_db)
    email = _email("step1")

    response = _step1(client, email, utm_source="whatsapp", utm_campaign="beta")

    assert response.status_code == 202
    [lead] = _leads(leads_db, email)
    assert lead.name == "Ana Lead"
    assert lead.whatsapp is None and lead.profile is None and lead.pain is None
    assert lead.step_reached == 1
    assert lead.origin == "landing"
    assert lead.attribution_json["utm_source"] == "whatsapp"
    assert [call["chat_id"] for call in sent] == [ADMIN_CHAT]
    assert sent[0]["text"].startswith("Cripto Farol - Novo lead na landing")
    assert "Ana Lead" in sent[0]["text"] and email in sent[0]["text"]
    assert "whatsapp / beta" in sent[0]["text"]


def test_step2_enriches_same_lead_without_duplicate(client, leads_db, sent):
    _seed_admin(leads_db)
    email = _email("step2")
    _step1(client, email)

    response = _step2(
        client,
        email,
        whatsapp="51999990000",
        profile="Iniciante",
        pain="timing de saída",
        lead_ref="ignored-by-backend",
    )

    assert response.status_code == 202
    [lead] = _leads(leads_db, email)
    assert lead.name == "Ana Lead"
    assert (lead.whatsapp, lead.profile, lead.pain) == (
        "51999990000",
        "Iniciante",
        "timing de saída",
    )
    assert lead.step_reached == 2
    assert [call["text"].splitlines()[0] for call in sent] == [
        "Cripto Farol - Novo lead na landing",
        "Cripto Farol - Lead completou o cadastro",
    ]
    assert "51999990000" in sent[1]["text"] and "Iniciante" in sent[1]["text"]


def test_empty_step2_is_accepted_and_keeps_step1(client, leads_db, sent):
    _seed_admin(leads_db)
    email = _email("empty2")
    _step1(client, email)

    response = _step2(client, email, whatsapp="", profile="", pain="  ")

    assert response.status_code == 202
    [lead] = _leads(leads_db, email)
    assert lead.name == "Ana Lead"
    assert lead.whatsapp is None and lead.profile is None and lead.pain is None
    # Nothing enriched: only the "new lead" notice from step 1.
    assert len(sent) == 1


def test_step2_without_previous_lead_creates_it(client, leads_db, sent):
    email = _email("orphan2")

    response = _step2(client, email, whatsapp="51988887777")

    assert response.status_code == 202
    [lead] = _leads(leads_db, email)
    assert lead.whatsapp == "51988887777"
    assert lead.step_reached == 2


def test_repeated_step1_preserves_step2_and_sends_nothing(client, leads_db, sent):
    _seed_admin(leads_db)
    email = _email("again")
    _step1(client, email)
    _step2(client, email, whatsapp="51977776666", profile="Trader", pain="risco")
    sent.clear()

    response = _step1(client, email.upper(), name="Ana Nova")

    assert response.status_code == 202
    [lead] = _leads(leads_db, email)
    assert lead.name == "Ana Nova"
    assert (lead.whatsapp, lead.profile, lead.pain) == ("51977776666", "Trader", "risco")
    assert lead.step_reached == 2
    assert sent == []


def test_response_is_identical_for_email_with_account(client, leads_db, sent):
    existing = _seed_user(leads_db, email=_email("has-account"))
    new_email = _email("no-account")

    for_account = _step1(client, existing.email)
    for_new = _step1(client, new_email)

    assert for_account.status_code == for_new.status_code == 202
    assert for_account.json() == for_new.json()
    leads_db.expire_all()
    user = leads_db.query(User).filter(User.email == existing.email).one()
    assert user.password_hash == "original-hash"
    assert leads_db.query(User).filter(User.email == new_email).first() is None


def test_no_account_and_invite_not_consumed(client, leads_db, sent):
    email = _email("invited")
    invite, token = issue_invite(leads_db, email=email)
    leads_db.commit()

    response = _step1(client, email, inviteToken=token)

    assert response.status_code == 202
    leads_db.expire_all()
    stored = leads_db.query(BetaInvite).filter(BetaInvite.id == invite.id).one()
    assert stored.consumed_at is None and stored.revoked_at is None
    assert leads_db.query(User).filter(User.email == email).first() is None
    audits = (
        leads_db.query(BetaAccessAuditLog)
        .filter(
            BetaAccessAuditLog.email == email,
            BetaAccessAuditLog.action == "lead_access_requested",
        )
        .all()
    )
    assert [audit.result for audit in audits] == ["invite_validated_not_consumed"]
    assert audits[0].metadata_json["step"] == 1
    assert token not in str(audits[0].metadata_json)


def test_audit_is_recorded_for_each_step(client, leads_db, sent):
    email = _email("audit")
    _step1(client, email)
    _step2(client, email, whatsapp="51911112222")

    leads_db.expire_all()
    audits = (
        leads_db.query(BetaAccessAuditLog)
        .filter(BetaAccessAuditLog.email == email)
        .order_by(BetaAccessAuditLog.id.asc())
        .all()
    )
    assert [audit.metadata_json.get("step") for audit in audits] == [1, 2]
    assert audits[1].metadata_json["has_whatsapp"] is True


def test_telegram_failure_does_not_fail_submission(client, leads_db, monkeypatch, caplog):
    _seed_admin(leads_db)
    email = _email("tg-down")

    def broken_send(**kwargs):
        raise ConnectionError("telegram unreachable")

    monkeypatch.setenv("MONITOR_TELEGRAM_BOT_TOKEN", "test-token-not-real")
    monkeypatch.delenv(BLOCK_PROD_BOT, raising=False)
    monkeypatch.setattr(telegram_module, "send_telegram_message", broken_send)

    with caplog.at_level(logging.WARNING, logger="app.services.landing_leads"):
        response = _step1(client, email, name="Pessoa Sigilosa")

    assert response.status_code == 202
    assert len(_leads(leads_db, email)) == 1
    messages = " ".join(record.getMessage() for record in caplog.records)
    assert "landing lead notice failed" in messages
    assert email not in messages and "Pessoa Sigilosa" not in messages


def test_no_admin_with_telegram_is_logged_without_personal_data(client, leads_db, sent, caplog):
    _seed_user(leads_db, email=_email("admin-no-tg"), role="admin")
    _seed_user(leads_db, email=_email("user-with-tg"), telegram_chat_id="123")
    email = _email("nobody")

    with caplog.at_level(logging.WARNING, logger="app.services.landing_leads"):
        response = _step1(client, email)

    assert response.status_code == 202
    assert len(_leads(leads_db, email)) == 1
    assert sent == []
    messages = " ".join(record.getMessage() for record in caplog.records)
    assert "sem destino" in messages
    assert email not in messages


@pytest.mark.parametrize("flag", ["1", " 1 "])
def test_blocked_prod_bot_saves_lead_and_sends_nothing(
    client, leads_db, sent, monkeypatch, caplog, flag
):
    _seed_admin(leads_db)
    email = _email("blocked")
    monkeypatch.setenv(BLOCK_PROD_BOT, flag)

    with caplog.at_level(logging.WARNING, logger="app.services.landing_leads"):
        step1 = _step1(client, email, name="Pessoa Sigilosa")
        step2 = _step2(client, email, whatsapp="51933332222", pain="segredo do lead")

    assert step1.status_code == step2.status_code == 202
    [lead] = _leads(leads_db, email)
    assert lead.name == "Pessoa Sigilosa"
    assert lead.whatsapp == "51933332222"
    assert lead.step_reached == 2
    assert sent == []
    messages = " ".join(record.getMessage() for record in caplog.records)
    assert "PROD bot blocked" in messages
    for personal in (email, "Pessoa Sigilosa", "51933332222", "segredo do lead"):
        assert personal not in messages


@pytest.mark.parametrize("flag", ["0", "", "true"])
def test_block_flag_needs_exactly_one_to_block(client, leads_db, sent, monkeypatch, flag):
    """Same rule as the alert scanner: only ``1`` blocks."""

    _seed_admin(leads_db)
    monkeypatch.setenv(BLOCK_PROD_BOT, flag)

    assert _step1(client, _email("not-blocked")).status_code == 202
    assert [call["chat_id"] for call in sent] == [ADMIN_CHAT]


@pytest.mark.parametrize("whatsapp", ["51955554444", None])
def test_payload_without_step_is_step1_plus_step2(client, leads_db, sent, whatsapp):
    """The v4 page (via Node until F4) and the landing commit-base send no ``step``."""

    _seed_admin(leads_db)
    email = _email("v4")
    payload = {
        "name": "Lead V4",
        "email": email,
        "profile": "Intermediário",
        "pain": "excesso de informação",
        "origin": "landing-v4",
        "utm_source": "instagram",
        "landing_path": "/?utm_source=instagram&email=x@y.z",
    }
    if whatsapp:
        payload["whatsapp"] = whatsapp

    response = client.post("/api/leads", json=payload)

    assert response.status_code == 202
    [lead] = _leads(leads_db, email)
    assert lead.name == "Lead V4"
    assert lead.whatsapp == whatsapp
    assert (lead.profile, lead.pain) == ("Intermediário", "excesso de informação")
    assert lead.origin == "landing-v4"
    assert lead.step_reached == 2
    assert lead.attribution_json["landing_path"] == "/?utm_source=instagram"
    assert len(sent) == 1
    assert sent[0]["text"].startswith("Cripto Farol - Novo lead na landing")
    assert "Intermediário" in sent[0]["text"]


def test_step1_requires_name(client, leads_db, sent):
    email = _email("noname")

    assert client.post("/api/leads", json={"step": 1, "email": email}).status_code == 422
    assert client.post("/api/leads", json={"email": email, "name": "  "}).status_code == 422
    assert (
        client.post("/api/leads", json={"step": 3, "name": "X", "email": email}).status_code == 422
    )
    assert _leads(leads_db, email) == []


# Task 1.5: GET /api/leads/stats e BETA_TOTAL_SPOTS ficam neste PR (cobertos por
# test_database_and_auth.py::test_leads_stats_counts_active_users_and_remaining_spots) e saem
# no PR-2 (card-1160-landing-remocoes) junto com aquele teste; por isso não há asserção deles aqui.


def _load_migration():
    spec = importlib.util.spec_from_file_location("migration_1160", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(conn, fn) -> None:
    context = MigrationContext.configure(conn)
    with Operations.context(context):
        fn()


def test_migration_creates_table_idempotently_and_downgrade_drops_it(unit_database_url):
    module = _load_migration()
    assert module.down_revision == "20261028_0002"
    engine = create_engine(unit_database_url)
    schema = "migration_1160_" + uuid.uuid4().hex[:12]
    try:
        with engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA {schema}"))
            conn.execute(text(f"SET LOCAL search_path TO {schema}"))
            for _ in range(2):  # idempotente: o app também cria a tabela na subida
                _run(conn, module.upgrade)
            insp = inspect(conn)
            assert "landing_leads" in insp.get_table_names(schema=schema)
            columns = {c["name"] for c in insp.get_columns("landing_leads", schema=schema)}
            assert {
                "email",
                "name",
                "whatsapp",
                "profile",
                "pain",
                "origin",
                "attribution_json",
                "step_reached",
                "created_at",
                "updated_at",
            } <= columns
            conn.execute(
                text(
                    "INSERT INTO landing_leads (email, created_at, updated_at) "
                    "VALUES ('a@b.c', now(), now())"
                )
            )
            assert conn.execute(text("SELECT step_reached FROM landing_leads")).scalar() == 1
            try:
                with conn.begin_nested():
                    conn.execute(
                        text(
                            "INSERT INTO landing_leads (email, created_at, updated_at) "
                            "VALUES ('a@b.c', now(), now())"
                        )
                    )
                raise AssertionError("dois leads com o mesmo e-mail")
            except Exception as exc:
                assert "uq_landing_leads_email" in str(exc)
            _run(conn, module.downgrade)
            assert "landing_leads" not in inspect(conn).get_table_names(schema=schema)
    finally:
        with engine.begin() as conn:
            conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        engine.dispose()
