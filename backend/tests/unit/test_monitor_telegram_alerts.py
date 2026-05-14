from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models import MonitorObservedStatus, MonitorTelegramAlert, SystemPreference
from app.routes import monitor_telegram_alerts as monitor_alert_route
from app.services.monitor_telegram_alerts import (
    MonitorTelegramAlertSettings,
    build_monitor_alert_candidate,
    load_monitor_telegram_alert_settings,
    run_monitor_telegram_alert_scan,
    send_telegram_message,
)


@pytest.fixture
def monitor_alert_db_session():
    engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/postgres")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    db.query(MonitorTelegramAlert).delete()
    db.query(MonitorObservedStatus).delete()
    db.query(SystemPreference).filter(
        SystemPreference.key == "monitor_telegram_tier_filter"
    ).delete()
    db.commit()
    try:
        yield db
    finally:
        db.query(MonitorTelegramAlert).delete()
        db.query(MonitorObservedStatus).delete()
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
        "timestamp": "2026-05-11T15:30:00",
        "entry_price": 104250.5,
        "stop_price": 101900.25,
        "next_status_label": "entry",
        "distance_to_next_status": 0.2,
    }


def test_build_monitor_alert_candidate_formats_short_sell_summary():
    candidate = build_monitor_alert_candidate(
        _opportunity("EXIT_SIGNAL"), previous_status="HOLDING"
    )

    assert candidate is not None
    assert candidate.symbol == "BTC/USDT"
    assert candidate.new_status == "EXIT_SIGNAL"
    assert candidate.severity == "Acao necessaria"
    assert candidate.message == (
        "Cripto Farol - Alerta Monitor\n\n"
        "Ativo: BTC/USDT\n"
        "TimeFrame: 1d\n"
        "Acao: Venda\n"
        "Data: 2026-05-11 15:30\n"
        "Valor Entrada: 104.250,50\n"
        "Stop: 101.900,25"
    )
    assert candidate.payload["action"] == "Venda"
    assert candidate.payload["entry_price"] == 104250.5
    assert candidate.payload["stop_price"] == 101900.25
    assert candidate.payload_hash


def test_build_monitor_alert_candidate_formats_short_buy_summary():
    candidate = build_monitor_alert_candidate(_opportunity("BUY_SIGNAL"), previous_status=None)

    assert candidate is not None
    assert "Acao: Compra" in candidate.message
    assert "Valor Entrada: 104.250,50" in candidate.message
    assert "Stop: 101.900,25" in candidate.message


def test_scan_dry_run_records_audit_when_delivery_config_incomplete(monitor_alert_db_session):
    service = _FakeOpportunityService([_opportunity("BUY_SIGNAL")])

    summary = run_monitor_telegram_alert_scan(
        monitor_alert_db_session,
        user_id="user-1",
        settings=_settings(bot_token=None),
        opportunity_service=service,
    )

    assert summary["dry_run"] is True
    assert summary["token_configured"] is False
    assert summary["can_send"] is False
    assert summary["destination_chat_id"] == "-1001"
    assert summary["destination_thread_id"] == "45"
    assert summary["candidates"] == 1
    assert summary["dry_run_count"] == 1
    assert service.calls == [{"source": "catalog", "tier_filter": "1,2,3", "alerts_only": True}]
    row = monitor_alert_db_session.query(MonitorTelegramAlert).one()
    assert row.result_status == "dry_run"
    assert row.symbol == "BTC/USDT"
    assert row.destination_chat_id == "-1001"
    assert row.destination_thread_id == "45"
    observed = monitor_alert_db_session.query(MonitorObservedStatus).one()
    assert observed.symbol == "BTC/USDT"
    assert observed.timeframe == "1d"
    assert observed.status == "BUY_SIGNAL"


def test_scan_skips_unchanged_observed_status(monitor_alert_db_session):
    monitor_alert_db_session.add(
        MonitorObservedStatus(
            symbol="BTC/USDT",
            timeframe="1d",
            status="BUY_SIGNAL",
            payload_json={},
        )
    )
    monitor_alert_db_session.commit()
    service = _FakeOpportunityService([_opportunity("BUY_SIGNAL")])

    summary = run_monitor_telegram_alert_scan(
        monitor_alert_db_session,
        user_id="user-1",
        settings=_settings(bot_token="token"),
        opportunity_service=service,
        sender=lambda *_args, **_kwargs: {"ok": True},
    )

    assert summary["sent"] == 0
    assert summary["skipped"] == 1
    assert summary["results"] == [
        {
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "status": "BUY_SIGNAL",
            "result": "unchanged",
        }
    ]
    assert monitor_alert_db_session.query(MonitorTelegramAlert).count() == 0


def test_scan_reports_no_opportunities_reason(monitor_alert_db_session):
    service = _FakeOpportunityService([])

    summary = run_monitor_telegram_alert_scan(
        monitor_alert_db_session,
        user_id="user-1",
        settings=_settings(bot_token="token"),
        opportunity_service=service,
        sender=lambda *_args, **_kwargs: {"ok": True},
    )

    assert summary["skipped"] == 1
    assert summary["results"] == [{"result": "no_opportunities"}]
    assert summary["token_configured"] is True
    assert summary["can_send"] is True


def test_scan_reports_not_sendable_reason(monitor_alert_db_session):
    service = _FakeOpportunityService([_opportunity("WAITING")])

    summary = run_monitor_telegram_alert_scan(
        monitor_alert_db_session,
        user_id="user-1",
        settings=_settings(bot_token="token"),
        opportunity_service=service,
        sender=lambda *_args, **_kwargs: {"ok": True},
    )

    assert summary["sent"] == 0
    assert summary["skipped"] == 1
    assert summary["results"] == [
        {
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "status": "WAITING",
            "result": "not_sendable",
        }
    ]
    assert monitor_alert_db_session.query(MonitorTelegramAlert).count() == 0


def test_scan_alerts_when_silent_observed_status_becomes_sendable(monitor_alert_db_session):
    monitor_alert_db_session.add(
        MonitorObservedStatus(
            symbol="BTC/USDT",
            timeframe="1d",
            status="WAITING",
            payload_json={},
        )
    )
    monitor_alert_db_session.commit()
    service = _FakeOpportunityService([_opportunity("BUY_SIGNAL")])
    sent_messages = []

    summary = run_monitor_telegram_alert_scan(
        monitor_alert_db_session,
        user_id="user-1",
        settings=_settings(bot_token="token"),
        opportunity_service=service,
        sender=lambda _settings, text: sent_messages.append(text) or {"ok": True},
    )

    assert summary["sent"] == 1
    assert "Acao: Compra" in sent_messages[0]
    row = monitor_alert_db_session.query(MonitorTelegramAlert).one()
    assert row.previous_status == "WAITING"
    observed = monitor_alert_db_session.query(MonitorObservedStatus).one()
    assert observed.status == "BUY_SIGNAL"


def test_scan_updates_observed_status_for_non_sendable_status(monitor_alert_db_session):
    service = _FakeOpportunityService([_opportunity("WAITING")])

    summary = run_monitor_telegram_alert_scan(
        monitor_alert_db_session,
        user_id="user-1",
        settings=_settings(bot_token="token"),
        opportunity_service=service,
        sender=lambda *_args, **_kwargs: {"ok": True},
    )

    assert summary["sent"] == 0
    assert summary["skipped"] == 1
    assert summary["results"][0]["result"] == "not_sendable"
    assert monitor_alert_db_session.query(MonitorTelegramAlert).count() == 0
    observed = monitor_alert_db_session.query(MonitorObservedStatus).one()
    assert observed.symbol == "BTC/USDT"
    assert observed.timeframe == "1d"
    assert observed.status == "WAITING"


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


def test_send_telegram_message_uses_configured_thread(monkeypatch):
    requests_payloads = []

    class _Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"ok": True}

    def fake_post(url, *, json, timeout):
        requests_payloads.append({"url": url, "json": json, "timeout": timeout})
        return _Response()

    monkeypatch.setattr("app.services.monitor_telegram_alerts.requests.post", fake_post)

    response = send_telegram_message(
        _settings(
            bot_token="token",
            chat_id="-1003891182144",
            allowed_chat_ids={"-1003891182144"},
            thread_id="5",
        ),
        "mensagem",
    )

    assert response == {"ok": True}
    assert requests_payloads == [
        {
            "url": "https://api.telegram.org/bottoken/sendMessage",
            "json": {
                "chat_id": "-1003891182144",
                "text": "mensagem",
                "disable_web_page_preview": True,
                "message_thread_id": "5",
            },
            "timeout": 10,
        }
    ]


def test_cron_wrapper_loads_monitor_token_from_runtime_secret(tmp_path, monkeypatch):
    module_path = Path(__file__).resolve().parents[3] / "ops" / "run_monitor_telegram_alert_scan.py"
    spec = importlib.util.spec_from_file_location(
        "run_monitor_telegram_alert_scan_test", module_path
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    secret_path = tmp_path / "runtime-secrets.json"
    secret_path.write_text(
        json.dumps({"env": {"MONITOR_TELEGRAM_BOT_TOKEN": "monitor-token"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "SECRETS_PATH", secret_path)
    monkeypatch.delenv("MONITOR_TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    assert module._load_telegram_token() == "monitor-token"


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
