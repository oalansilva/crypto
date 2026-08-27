from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import MonitorPreference, User
from app.services.monitor_portfolio_status import resolve_portfolio_status_for_user
from app.services.monitor_telegram_alerts import should_send_position_aware_alert
from app.services.user_telegram_service import create_link_token, normalize_telegram_username, process_link_command


@pytest.fixture
def db_session(postgres_isolation, unit_database_url):
    from app.database import ensure_runtime_schema_migrations

    ensure_runtime_schema_migrations()
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


pytestmark = pytest.mark.postgres


def test_normalize_telegram_username():
    assert normalize_telegram_username("@Alan_Test") == "alan_test"


def test_should_send_position_aware_matrix():
    assert should_send_position_aware_alert(
        previous_status="HOLD", new_status="EXIT", has_spot_position=True, in_portfolio=True
    ) == (True, "sell")
    assert should_send_position_aware_alert(
        previous_status="EXIT", new_status="HOLD", has_spot_position=False, in_portfolio=True
    ) == (True, "buy")
    assert should_send_position_aware_alert(
        previous_status="HOLD", new_status="EXIT", has_spot_position=False, in_portfolio=True
    ) == (False, "suppressed_flat_exit")
    assert should_send_position_aware_alert(
        previous_status="EXIT", new_status="HOLD", has_spot_position=True, in_portfolio=True
    ) == (False, "suppressed_reentry")


def test_link_token_and_process(db_session):
    user = User(
        id=uuid.uuid4(),
        email="tg@test.local",
        password_hash="x",
        name="TG User",
        telegram_username="declared_user",
    )
    db_session.add(user)
    db_session.commit()

    token_payload = create_link_token(db_session, user)
    ok, _ = process_link_command(
        db_session,
        token=token_payload["token"],
        chat_id="12345",
        from_username="other_user",
    )
    assert ok is True
    db_session.refresh(user)
    assert user.telegram_chat_id == "12345"
    assert user.telegram_username_mismatch is True


def test_link_token_expired(db_session):
    user = User(
        id=uuid.uuid4(),
        email="expired@test.local",
        password_hash="x",
        name="Expired",
        telegram_username="declared_user",
        telegram_link_token="expired-token",
        telegram_link_expires_at=datetime.utcnow() - timedelta(minutes=1),
    )
    db_session.add(user)
    db_session.commit()

    ok, reply = process_link_command(
        db_session,
        token="expired-token",
        chat_id="99999",
        from_username="declared_user",
    )
    assert ok is False
    assert "expir" in reply.lower()


def test_resolve_portfolio_manual_when_no_binance(db_session):
    user = User(
        id=uuid.uuid4(),
        email="manual@test.local",
        password_hash="x",
        name="Manual",
    )
    db_session.add(user)
    db_session.add(
        MonitorPreference(
            user_id=str(user.id),
            symbol="BTC/USDT",
            in_portfolio=True,
        )
    )
    db_session.commit()

    result = resolve_portfolio_status_for_user(
        db_session,
        str(user.id),
        ["BTC/USDT"],
        wallet_holdings={},
        binance_sync_ok=True,
    )
    assert result["BTC/USDT"].in_portfolio is True
    assert result["BTC/USDT"].derived_active is False
