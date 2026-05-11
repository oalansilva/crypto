from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models import MonitorTelegramAlert, SystemPreference
from app.routes import monitor_telegram_alerts as monitor_alert_route
from app.services.monitor_telegram_alerts import (
    MonitorTelegramAlertSettings,
    build_monitor_alert_candidate,
    load_monitor_telegram_alert_settings,
    run_monitor_telegram_alert_scan,
)


@pytest.fixture
def monitor_alert_db_session():
    engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/postgres")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    db.query(MonitorTelegramAlert).delete()
    db.query(SystemPreference).filter(
        SystemPreference.key == "monitor_telegram_tier_filter"
    ).delete()
    db.commit()
    try:
        yield db
    finally:
        db.query(MonitorTelegramAlert).delete()
        db.query(SystemPreference).filter(
            SystemPreference.key == "monitor_telegram_tier_filter"
        ).delete()
        db.commit()
        db.close()
        engine.dispose()


def _settings(**overrides) -> MonitorTelegramAlertSettings:
    values = {
        "enabled": True,
        "bot_token": None,
        "chat_id": "-1001",
        "allowed_chat_ids": {"-1001"},
        "thread_id": "45",
        "min_repeat_minutes": 360,
        "rate_limit_count": 5,
        "rate_limit_window_minutes": 60,
        "tier_filter": "1,2,3",
    }
    values.update(overrides)
    return MonitorTelegramAlertSettings(**values)


class _FakeOpportunityService:
    def __init__(self, opportunities):
        self.opportunities = opportunities
        self.calls = []

    def get_opportunities(self, *, user_id, tier_filter):
        self.calls.append({"user_id": user_id, "tier_filter": tier_filter})
        return list(self.opportunities)

    def get_catalog_opportunities(self, *, tier_filter, alerts_only=False):
        self.calls.append(
            {"source": "catalog", "tier_filter": tier_filter, "alerts_only": alerts_only}
        )
        return list(self.opportunities)


def _opportunity(status: str = "BUY_SIGNAL") -> dict:
    return {
        "id": 10,
        "symbol": "BTC/USDT",
        "timeframe": "1d",
        "status": status,
        "next_status_label": "entry",
        "distance_to_next_status": 0.2,
    }


def test_build_monitor_alert_candidate_formats_internal_draft():
    candidate = build_monitor_alert_candidate(
        _opportunity("EXIT_SIGNAL"), previous_status="HOLDING"
    )

    assert candidate is not None
    assert candidate.symbol == "BTC/USDT"
    assert candidate.new_status == "EXIT_SIGNAL"
    assert candidate.severity == "Acao necessaria"
    assert "Cripto Farol - rascunho de alerta para beta" in candidate.message
    assert "Texto pronto para Alan encaminhar" in candidate.message
    assert "Isto nao e recomendacao financeira" in candidate.message
    assert candidate.payload_hash


def test_scan_dry_run_records_audit_when_delivery_config_incomplete(monitor_alert_db_session):
    service = _FakeOpportunityService([_opportunity("BUY_SIGNAL")])

    summary = run_monitor_telegram_alert_scan(
        monitor_alert_db_session,
        user_id="user-1",
        settings=_settings(bot_token=None),
        opportunity_service=service,
    )

    assert summary["dry_run"] is True
    assert summary["candidates"] == 1
    assert summary["dry_run_count"] == 1
    assert service.calls == [{"source": "catalog", "tier_filter": "1,2,3", "alerts_only": True}]
    row = monitor_alert_db_session.query(MonitorTelegramAlert).one()
    assert row.result_status == "dry_run"
    assert row.symbol == "BTC/USDT"
    assert row.destination_chat_id == "-1001"
    assert row.destination_thread_id == "45"


def test_scan_deduplicates_same_symbol_timeframe_status(monitor_alert_db_session):
    existing = MonitorTelegramAlert(
        created_at=datetime.utcnow() - timedelta(minutes=5),
        symbol="BTC/USDT",
        timeframe="1d",
        previous_status=None,
        new_status="BUY_SIGNAL",
        severity="Atencao",
        destination_chat_id="-1001",
        result_status="sent",
        payload_hash="old",
        source="monitor",
        payload_json={},
    )
    monitor_alert_db_session.add(existing)
    monitor_alert_db_session.commit()
    service = _FakeOpportunityService([_opportunity("BUY_SIGNAL")])

    summary = run_monitor_telegram_alert_scan(
        monitor_alert_db_session,
        user_id="user-1",
        settings=_settings(bot_token="token"),
        opportunity_service=service,
        sender=lambda *_args, **_kwargs: {"ok": True},
    )

    assert summary["duplicates"] == 1
    assert summary["sent"] == 0
    assert monitor_alert_db_session.query(MonitorTelegramAlert).count() == 1


def test_scan_applies_rate_limit_before_send(monitor_alert_db_session):
    for idx in range(2):
        monitor_alert_db_session.add(
            MonitorTelegramAlert(
                created_at=datetime.utcnow() - timedelta(minutes=idx),
                symbol=f"ETH{idx}/USDT",
                timeframe="1d",
                previous_status=None,
                new_status="BUY_SIGNAL",
                severity="Atencao",
                destination_chat_id="-1001",
                result_status="sent",
                payload_hash=f"hash-{idx}",
                source="monitor",
                payload_json={},
            )
        )
    monitor_alert_db_session.commit()
    service = _FakeOpportunityService([_opportunity("EXIT_SIGNAL")])

    summary = run_monitor_telegram_alert_scan(
        monitor_alert_db_session,
        user_id="user-1",
        settings=_settings(bot_token="token", rate_limit_count=2),
        opportunity_service=service,
        sender=lambda *_args, **_kwargs: {"ok": True},
    )

    assert summary["rate_limited"] == 1
    assert summary["sent"] == 0


def test_scan_records_failure_and_continues(monitor_alert_db_session):
    service = _FakeOpportunityService([_opportunity("EXIT_SIGNAL")])

    def failing_sender(*_args, **_kwargs):
        raise RuntimeError("telegram down")

    summary = run_monitor_telegram_alert_scan(
        monitor_alert_db_session,
        user_id="user-1",
        settings=_settings(bot_token="token"),
        opportunity_service=service,
        sender=failing_sender,
    )

    assert summary["failed"] == 1
    row = monitor_alert_db_session.query(MonitorTelegramAlert).one()
    assert row.result_status == "failed"
    assert "telegram down" in row.error_text


def test_settings_require_allowlisted_destination(monkeypatch, monitor_alert_db_session):
    monkeypatch.setenv("MONITOR_TELEGRAM_ALERTS_ENABLED", "1")
    monkeypatch.setenv("MONITOR_TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("MONITOR_TELEGRAM_CHAT_ID", "-1002")
    monkeypatch.setenv("MONITOR_TELEGRAM_ALLOWED_CHAT_IDS", "-1001")

    settings = load_monitor_telegram_alert_settings(monitor_alert_db_session)

    assert settings.enabled is True
    assert settings.destination_allowed is False
    assert settings.can_send is False


def test_settings_default_to_all_tiers(monkeypatch, monitor_alert_db_session):
    monkeypatch.delenv("MONITOR_TELEGRAM_TIER_FILTER", raising=False)

    settings = load_monitor_telegram_alert_settings(monitor_alert_db_session)

    assert settings.tier_filter == "all"


def test_admin_route_runs_scan_with_mocked_service(monitor_alert_db_session, monkeypatch):
    app = FastAPI()
    app.include_router(monitor_alert_route.router)

    def override_db():
        yield monitor_alert_db_session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[monitor_alert_route.get_current_admin] = lambda: "admin-1"

    monkeypatch.setattr(
        monitor_alert_route,
        "load_monitor_telegram_alert_settings",
        lambda db: _settings(bot_token=None),
    )
    monkeypatch.setattr(
        monitor_alert_route,
        "run_monitor_telegram_alert_scan",
        lambda db, **kwargs: {
            "enabled": True,
            "dry_run": True,
            "candidates": 1,
            "sent": 0,
            "dry_run_count": 1,
            "duplicates": 0,
            "rate_limited": 0,
            "skipped": 0,
            "failed": 0,
            "destination_allowed": True,
            "results": [{"result": "dry_run"}],
            "kwargs": kwargs,
        },
    )

    client = TestClient(app)
    response = client.post("/api/admin/monitor-telegram-alerts/run", json={"dry_run": True})

    assert response.status_code == 200
    payload = response.json()
    assert payload["candidates"] == 1
    assert payload["dry_run_count"] == 1
