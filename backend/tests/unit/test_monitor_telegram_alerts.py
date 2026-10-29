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
import uuid

from app.models import (
    FavoriteStrategy,
    MonitorFavoriteAlertState,
    MonitorObservedStatus,
    MonitorTelegramAlert,
    MonitorPreference,
    SystemPreference,
    User,
    UserExchangeCredential,
)
from app.services.user_exchange_credentials import BINANCE_PROVIDER
from app.routes import monitor_telegram_alerts as monitor_alert_route
from app.services.monitor_telegram_alerts import (
    MonitorTelegramAlertSettings,
    build_monitor_alert_candidate,
    load_monitor_telegram_alert_settings,
    run_monitor_telegram_alert_scan,
    send_telegram_message,
)


@pytest.fixture
def monitor_alert_db_session(postgres_isolation, unit_database_url):
    from app.database import ensure_runtime_schema_migrations

    ensure_runtime_schema_migrations()
    engine = create_engine(unit_database_url)
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
        "min_repeat_minutes": 360,
        "rate_limit_count": 5,
        "rate_limit_window_minutes": 60,
        "tier_filter": "1,2,3",
    }
    values.update(overrides)
    return MonitorTelegramAlertSettings(**values)


def _add_eligible_user(db, *, chat_id: str = "9001") -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"alert-{chat_id}@test.local",
        password_hash="x",
        name="Alert User",
        telegram_chat_id=chat_id,
        telegram_username="alertuser",
        telegram_alerts_enabled=True,
    )
    db.add(user)
    db.commit()
    return user


def _add_binance_credential(db, user: User) -> None:
    db.add(
        UserExchangeCredential(
            user_id=str(user.id),
            provider=BINANCE_PROVIDER,
            api_key="test-key",
            api_secret="test-secret",
        )
    )
    db.commit()


class _FakeOpportunityService:
    def __init__(self, opportunities):
        self.opportunities = opportunities
        self.calls = []

    def get_opportunities(self, *, user_id, tier_filter):
        self.calls.append({"user_id": user_id, "tier_filter": tier_filter})
        return list(self.opportunities)

    def get_alert_opportunities(self, *, now=None):
        self.calls.append({"source": "favorites"})
        return list(self.opportunities)


def _opportunity(status: str = "HOLD") -> dict:
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
        "strategy_display_name": "Combo Alpha",
    }


def test_build_monitor_alert_candidate_formats_short_sell_summary():
    candidate = build_monitor_alert_candidate(_opportunity("EXIT"), previous_status="HOLD")

    assert candidate is not None
    assert candidate.symbol == "BTC/USDT"
    assert candidate.new_status == "EXIT"
    assert candidate.severity == "Acao necessaria"
    assert candidate.message.startswith("Cripto Farol - Alerta Monitor")
    assert "Ativo: BTC/USDT (Cripto · USDT)" in candidate.message
    assert "Este alerta não envia ordem: é só o sinal da estratégia." in candidate.message
    assert "Leitura atual: Venda" in candidate.message
    assert "104.250,50" in candidate.message
    assert candidate.payload["action"] == "Venda"
    assert candidate.payload["entry_price"] == 104250.5
    assert candidate.payload["stop_price"] == 101900.25
    assert candidate.payload_hash


def test_build_monitor_alert_candidate_includes_stop_reason():
    opportunity = _opportunity("EXIT")
    opportunity["stop_breached_now"] = True
    candidate = build_monitor_alert_candidate(opportunity, previous_status="HOLD")

    assert candidate is not None
    assert "Motivo=Stop" in candidate.message
    assert candidate.stop_reason is True


def test_build_monitor_alert_candidate_formats_short_buy_summary():
    candidate = build_monitor_alert_candidate(_opportunity("HOLD"), previous_status=None)

    assert candidate is not None
    assert "Leitura atual: Compra" in candidate.message
    assert "Valor Entrada: 104.250,50 USDT" in candidate.message
    assert "Stop: 101.900,25 USDT" in candidate.message


def _marked_favorite(db, user: User, symbol: str = "BTC/USDT") -> FavoriteStrategy:
    favorite = FavoriteStrategy(
        user_id=str(user.id),
        name=f"Combo Alpha {symbol}",
        symbol=symbol,
        timeframe="1d",
        strategy_name="multi_ma_crossover",
        parameters={"direction": "long"},
        metrics={},
        tier=1,
        notify_telegram=True,
        data_source="ccxt",
        session="24x7",
        adjustment="none",
    )
    db.add(favorite)
    db.commit()
    return favorite


def _seed_state(db, favorite: FavoriteStrategy, status: str) -> None:
    db.add(
        MonitorFavoriteAlertState(
            favorite_id=favorite.id,
            status=status,
            candle_time="2026-05-10T00:00:00+00:00",
            observed_at=datetime.utcnow(),
            payload_json={},
        )
    )
    db.commit()


def _favorite_opportunity(favorite: FavoriteStrategy, status: str) -> dict:
    return {
        **_opportunity(status),
        "id": favorite.id,
        "user_id": favorite.user_id,
        "symbol": favorite.symbol,
        "candle_time": "2026-05-11T00:00:00+00:00",
        "asset_class": "crypto",
        "currency": "USDT",
        "notify_telegram": True,
        "tier": favorite.tier,
        "market_state": {"state": "open", "reason": "24x7"},
    }


def test_scan_dry_run_records_audit_when_delivery_config_incomplete(
    monitor_alert_db_session,
):
    db = monitor_alert_db_session
    user = _add_eligible_user(db)
    db.add(MonitorPreference(user_id=str(user.id), symbol="BTC/USDT", in_portfolio=True))
    db.commit()
    favorite = _marked_favorite(db, user)
    _seed_state(db, favorite, "EXIT")
    sent = []

    summary = run_monitor_telegram_alert_scan(
        db,
        user_id="ignored",
        settings=_settings(bot_token=None),
        opportunity_service=_FakeOpportunityService([_favorite_opportunity(favorite, "HOLD")]),
        sender=lambda **kwargs: sent.append(kwargs) or {"ok": True},
    )

    assert summary["dry_run"] is True
    assert summary["dry_run_count"] == 1
    assert sent == []
    row = db.query(MonitorTelegramAlert).one()
    assert row.result_status == "dry_run"
    assert row.favorite_id == favorite.id and row.event_key
    assert db.get(MonitorFavoriteAlertState, favorite.id).status == "HOLD"


def test_scan_skips_unchanged_favorite_state(monitor_alert_db_session):
    db = monitor_alert_db_session
    user = _add_eligible_user(db)
    favorite = _marked_favorite(db, user)
    _seed_state(db, favorite, "HOLD")

    summary = run_monitor_telegram_alert_scan(
        db,
        user_id="ignored",
        settings=_settings(),
        opportunity_service=_FakeOpportunityService([_favorite_opportunity(favorite, "HOLD")]),
        sender=lambda **kwargs: {"ok": True},
    )

    assert summary["candidates"] == 0
    assert db.query(MonitorTelegramAlert).count() == 0


def test_scan_reports_not_sendable_status_without_alert(monitor_alert_db_session):
    db = monitor_alert_db_session
    user = _add_eligible_user(db)
    favorite = _marked_favorite(db, user)
    _seed_state(db, favorite, "EXIT")

    summary = run_monitor_telegram_alert_scan(
        db,
        user_id="ignored",
        settings=_settings(),
        opportunity_service=_FakeOpportunityService([_favorite_opportunity(favorite, "NEUTRAL")]),
        sender=lambda **kwargs: {"ok": True},
    )

    assert summary["candidates"] == 0
    assert db.query(MonitorTelegramAlert).count() == 0


def test_scan_records_failure_and_continues(monitor_alert_db_session):
    db = monitor_alert_db_session
    user = _add_eligible_user(db)
    db.add(MonitorPreference(user_id=str(user.id), symbol="BTC/USDT", in_portfolio=True))
    db.commit()
    favorite = _marked_favorite(db, user)
    _seed_state(db, favorite, "EXIT")

    def failing_sender(**_kwargs):
        raise RuntimeError("telegram down")

    summary = run_monitor_telegram_alert_scan(
        db,
        user_id="ignored",
        settings=_settings(bot_token="token"),
        opportunity_service=_FakeOpportunityService([_favorite_opportunity(favorite, "HOLD")]),
        sender=failing_sender,
    )

    assert summary["failed"] == 1
    row = db.query(MonitorTelegramAlert).one()
    assert row.result_status == "failed"
    assert "telegram down" in row.error_text


def test_scan_two_users_different_positions_both_receive(monitor_alert_db_session, monkeypatch):
    """Card #1122 (d2): a carteira não decide; com e sem saldo, a saída sai para os dois."""
    db = monitor_alert_db_session
    user_a = _add_eligible_user(db, chat_id="9001")
    user_b = _add_eligible_user(db, chat_id="9002")
    _add_binance_credential(db, user_a)
    for user in (user_a, user_b):
        db.add(MonitorPreference(user_id=str(user.id), symbol="BTC/USDT", in_portfolio=True))
    db.commit()
    fav_a = _marked_favorite(db, user_a)
    fav_b = _marked_favorite(db, user_b)
    _seed_state(db, fav_a, "HOLD")
    _seed_state(db, fav_b, "HOLD")

    def wallet_must_not_be_read(*_args, **_kwargs):
        raise AssertionError("a varredura não lê a carteira Binance")

    monkeypatch.setattr(
        "app.services.monitor_portfolio_status.fetch_user_wallet_holdings",
        wallet_must_not_be_read,
    )
    sent_chat_ids: list[str] = []

    summary = run_monitor_telegram_alert_scan(
        db,
        user_id="ignored",
        settings=_settings(bot_token="token"),
        opportunity_service=_FakeOpportunityService(
            [_favorite_opportunity(fav_a, "EXIT"), _favorite_opportunity(fav_b, "EXIT")]
        ),
        sender=lambda **kwargs: sent_chat_ids.append(str(kwargs.get("chat_id"))) or {"ok": True},
    )

    assert summary["eligible_users"] == 2
    assert summary["sent"] == 2
    assert "suppressed_by_position_matrix" not in summary
    assert sorted(sent_chat_ids) == ["9001", "9002"]
    rows = db.query(MonitorTelegramAlert).all()
    assert {row.user_id for row in rows} == {str(user_a.id), str(user_b.id)}


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

    response = send_telegram_message(bot_token="token", chat_id="-1003891182144", text="mensagem")

    assert response == {"ok": True}
    assert requests_payloads == [
        {
            "url": "https://api.telegram.org/bottoken/sendMessage",
            "json": {
                "chat_id": "-1003891182144",
                "text": "mensagem",
                "disable_web_page_preview": True,
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
    module.SECRETS_CANDIDATES = (secret_path,)
    monkeypatch.delenv("MONITOR_TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("MONITOR_TELEGRAM_SECRETS_FILE", raising=False)

    assert module._load_telegram_token() == "monitor-token"


def test_settings_can_send_requires_bot_token(monkeypatch, monitor_alert_db_session):
    monkeypatch.setenv("MONITOR_TELEGRAM_ALERTS_ENABLED", "1")
    monkeypatch.delenv("MONITOR_TELEGRAM_BOT_TOKEN", raising=False)

    settings = load_monitor_telegram_alert_settings(monitor_alert_db_session)

    assert settings.enabled is True
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
