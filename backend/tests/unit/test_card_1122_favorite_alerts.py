"""Card #1122: alertas por favorito em cripto, ação e ETF (um teste por cenário do design).

Regra de 27/10/2026 (Design d2): alerta = estratégia própria com estrela e alerta ligado; a
carteira não decide. Os cenários novos do d2 estão em ``test_card_1122_d2_alert_rule.py``.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.middleware.authMiddleware import get_current_user
from app.models import (
    FavoriteStrategy,
    MonitorDataHealth,
    MonitorFavoriteAlertState,
    MonitorPreference,
    MonitorSpotOrderRequest,
    MonitorTelegramAlert,
    SystemPreference,
    User,
    UserExchangeCredential,
)
from app.routes import favorites as favorites_route
from app.routes import opportunity_routes
from app.services import market_state
from app.services import monitor_telegram_alerts as alerts
from app.services.market_history import nyse_calendar as cal
from app.services.monitor_telegram_alerts import (
    MonitorTelegramAlertSettings,
    run_monitor_telegram_alert_scan,
    signal_direction,
)
from app.services.user_exchange_credentials import BINANCE_PROVIDER

BRT = "America/Sao_Paulo"
NY = "America/New_York"
BINANCE_CFG = {
    "data_source": "binance_equity",
    "session": "regular_ny",
    "adjustment": "split",
    "label_short": "Binance Ações · NY · split",
    "label_compact": "Binance · NY · split",
    "label_long": "Binance Ações · pregão regular de NY · ajustado por split",
}
STOOQ_CFG = {
    "data_source": "stooq",
    "session": "eod",
    "adjustment": "legacy",
    "label_short": "Stooq · fonte antiga · diário",
    "label_compact": "Stooq · antiga · diário",
    "label_long": "Stooq · fonte antiga · diário",
}
CRYPTO_CFG = {
    "data_source": "ccxt",
    "session": "24x7",
    "adjustment": "none",
    "label_short": "Binance Spot · 24/7",
    "label_compact": "Binance Spot · 24/7",
    "label_long": "Binance Spot · 24/7",
}


@pytest.fixture
def db(postgres_isolation, unit_database_url):
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _settings(**overrides) -> MonitorTelegramAlertSettings:
    values = {
        "enabled": True,
        "bot_token": "token",
        "min_repeat_minutes": 360,
        "rate_limit_count": 5,
        "rate_limit_window_minutes": 60,
        "tier_filter": "all",
    }
    values.update(overrides)
    return MonitorTelegramAlertSettings(**values)


def _user(db, name: str, *, chat: str | None = None, alerts_on: bool = True) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"{name}@test.local",
        password_hash="x",
        name=name,
        telegram_chat_id=chat or f"chat-{name}",
        telegram_username=name,
        telegram_alerts_enabled=alerts_on,
    )
    db.add(user)
    db.commit()
    return user


def _favorite(
    db,
    user: User,
    symbol: str,
    *,
    notify: bool = True,
    strategy: str = "multi_ma_crossover",
    timeframe: str = "1d",
    cfg: dict | None = None,
    tier: int | None = 1,
) -> FavoriteStrategy:
    cfg = cfg or (CRYPTO_CFG if "/" in symbol else BINANCE_CFG)
    row = FavoriteStrategy(
        user_id=str(user.id),
        name=f"{strategy} {symbol}",
        symbol=symbol,
        timeframe=timeframe,
        strategy_name=strategy,
        parameters={"direction": "long", "data_source": cfg["data_source"]},
        metrics={},
        tier=tier,
        notify_telegram=notify,
        data_source=cfg["data_source"],
        session=cfg["session"],
        adjustment=cfg["adjustment"],
    )
    db.add(row)
    db.commit()
    return row


def _portfolio(db, user: User, symbol: str, in_portfolio: bool = True) -> None:
    db.merge(MonitorPreference(user_id=str(user.id), symbol=symbol, in_portfolio=in_portfolio))
    db.commit()


def _opp(
    fav: FavoriteStrategy,
    status: str,
    candle: str,
    *,
    state: str = "closed",
    episode: str | None = None,
    last: str | None = None,
    expected: str | None = None,
) -> dict:
    cfg = {
        "data_source": fav.data_source,
        "session": fav.session,
        "adjustment": fav.adjustment,
        **(
            CRYPTO_CFG
            if fav.data_source == "ccxt"
            else STOOQ_CFG if fav.data_source == "stooq" else BINANCE_CFG
        ),
    }
    crypto = "/" in fav.symbol
    return {
        "id": fav.id,
        "user_id": fav.user_id,
        "symbol": fav.symbol,
        "timeframe": fav.timeframe,
        "status": status,
        "candle_time": candle,
        "timestamp": candle,
        "entry_price": 182.4,
        "stop_price": 173.28,
        "strategy_display_name": f"Estratégia {fav.strategy_name}",
        "asset_class": "crypto" if crypto else "stock",
        "currency": "USDT" if crypto else "USD",
        "configuration": cfg,
        "notify_telegram": bool(fav.notify_telegram),
        "tier": fav.tier,
        "market_state": {
            "state": state,
            "episode_id": episode,
            "stale_since": "2026-10-27T11:05:00" if episode else None,
            "last_candle": last,
            "expected_candle": expected,
        },
    }


class FakeService:
    def __init__(self, rows=None):
        self.rows = list(rows or [])
        self.calls = 0

    def get_alert_opportunities(self, *, now=None):
        self.calls += 1
        return [dict(r) for r in self.rows]


class Sender:
    def __init__(self, fail_for: set[str] | None = None):
        self.messages: list[tuple[str, str]] = []
        self.fail_for = fail_for or set()

    def __call__(self, *, bot_token, chat_id, text, dry_run=False):
        if chat_id in self.fail_for:
            raise RuntimeError("telegram down")
        self.messages.append((chat_id, text))
        return {"ok": True}


def _scan(db, rows, sender, *, now=None, **settings):
    return run_monitor_telegram_alert_scan(
        db,
        user_id="cron",
        settings=_settings(**settings),
        opportunity_service=FakeService(rows),
        sender=sender,
        now=now or datetime(2026, 10, 27, 11, 5),
    )


FRI = "2026-10-23T04:00:00+00:00"
MON = "2026-10-26T04:00:00+00:00"
TUE = "2026-10-27T04:00:00+00:00"
WED = "2026-10-28T04:00:00+00:00"


def _baseline(db, rows, sender):
    _scan(db, rows, sender, now=datetime(2026, 10, 26, 11, 5))


# ---------------------------------------------------------------- origem e identidade


def test_only_the_owner_who_marked_receives(db):
    a = _user(db, "a")
    b = _user(db, "b")
    nvda = _favorite(db, a, "NVDA")
    btc = _favorite(db, a, "BTC/USDT")
    sender = Sender()
    _baseline(db, [_opp(nvda, "EXIT", FRI), _opp(btc, "HOLD", FRI)], sender)
    summary = _scan(db, [_opp(nvda, "HOLD", MON), _opp(btc, "EXIT", MON)], sender)
    chats = [chat for chat, _ in sender.messages]
    # Sem carteira na decisão (d2): a entrada de NVDA e a saída de BTC sem saldo saem para A.
    assert chats == ["chat-a", "chat-a"]
    assert "NVDA (Ação · USD)" in sender.messages[0][1]
    assert "BTC/USDT (Cripto · USDT)" in sender.messages[1][1]
    assert summary["rate_limited"] == 0
    assert "chat-b" not in chats
    assert db.query(MonitorTelegramAlert).filter_by(user_id=str(b.id)).count() == 0


def test_unmarked_favorite_never_alerts_and_first_reading_is_a_baseline(db):
    a = _user(db, "a")
    fav = _favorite(db, a, "NVDA", notify=True)
    unmarked = _favorite(db, a, "SPY", notify=False)
    _portfolio(db, a, "NVDA")
    _portfolio(db, a, "SPY")
    sender = Sender()
    rows = [_opp(fav, "HOLD", MON), {**_opp(unmarked, "HOLD", MON), "notify_telegram": False}]
    summary = _scan(db, rows, sender)
    assert summary["baselines"] == 1 and sender.messages == []
    assert db.get(MonitorFavoriteAlertState, fav.id).status == "HOLD"
    assert db.get(MonitorFavoriteAlertState, unmarked.id) is None


def test_nvda_binance_and_stooq_keep_separate_states(db):
    a = _user(db, "a")
    binance = _favorite(db, a, "NVDA")
    stooq = _favorite(db, a, "NVDA", cfg=STOOQ_CFG)
    _portfolio(db, a, "NVDA")
    sender = Sender()
    _baseline(db, [_opp(binance, "EXIT", FRI), _opp(stooq, "EXIT", FRI)], sender)
    _scan(db, [_opp(binance, "HOLD", MON), _opp(stooq, "EXIT", MON)], sender)
    assert len(sender.messages) == 1
    assert "Binance Ações · pregão regular de NY · ajustado por split" in sender.messages[0][1]
    assert db.get(MonitorFavoriteAlertState, stooq.id).status == "EXIT"
    assert db.get(MonitorFavoriteAlertState, binance.id).status == "HOLD"


def test_two_strategies_changing_together_send_two_alerts(db):
    a = _user(db, "a")
    one = _favorite(db, a, "BTC/USDT", strategy="ema_rsi")
    two = _favorite(db, a, "BTC/USDT", strategy="multi_ma_crossover")
    _portfolio(db, a, "BTC/USDT")
    sender = Sender()
    _baseline(db, [_opp(one, "EXIT", FRI), _opp(two, "EXIT", FRI)], sender)
    _scan(db, [_opp(one, "HOLD", MON), _opp(two, "HOLD", MON)], sender)
    texts = [text for _, text in sender.messages]
    assert len(texts) == 2
    assert any("ema_rsi" in t for t in texts) and any("multi_ma_crossover" in t for t in texts)


# ---------------------------------------------------------------- evento


def test_repeated_scan_sends_once_and_legit_return_alerts_again(db):
    a = _user(db, "a")
    fav = _favorite(db, a, "NVDA")
    _portfolio(db, a, "NVDA")
    sender = Sender()
    _baseline(db, [_opp(fav, "EXIT", FRI)], sender)
    _scan(db, [_opp(fav, "HOLD", MON)], sender)
    second = _scan(db, [_opp(fav, "HOLD", MON)], sender)
    assert len(sender.messages) == 1 and second["sent"] == 0
    _scan(db, [_opp(fav, "EXIT", TUE)], sender, now=datetime(2026, 10, 28, 11, 5))
    _scan(db, [_opp(fav, "HOLD", WED)], sender, now=datetime(2026, 10, 29, 11, 5))
    assert len(sender.messages) == 3


def test_sending_reservation_becomes_unknown_and_is_never_resent(db):
    a = _user(db, "a")
    fav = _favorite(db, a, "NVDA")
    _portfolio(db, a, "NVDA")
    key = alerts.signal_event_key(str(a.id), fav.id, "HOLD", MON)
    db.add(
        MonitorTelegramAlert(
            user_id=str(a.id),
            symbol="NVDA",
            timeframe="1d",
            new_status="HOLD",
            severity="Atencao",
            result_status="sending",
            payload_hash="x",
            source="monitor",
            favorite_id=fav.id,
            event_key=key,
            created_at=datetime(2026, 10, 27, 10, 0),
        )
    )
    db.add(MonitorFavoriteAlertState(favorite_id=fav.id, status="EXIT", observed_at=datetime.now()))
    db.commit()
    sender = Sender()
    summary = _scan(db, [_opp(fav, "HOLD", MON)], sender)
    assert summary["unknown"] == 1 and summary["duplicates"] == 1
    assert sender.messages == []
    assert db.query(MonitorTelegramAlert).filter_by(event_key=key).one().result_status == "unknown"


def test_failed_send_is_retried_while_the_event_is_current(db):
    a = _user(db, "a")
    fav = _favorite(db, a, "NVDA")
    _portfolio(db, a, "NVDA")
    _baseline(db, [_opp(fav, "EXIT", FRI)], Sender())
    failing = Sender(fail_for={"chat-a"})
    first = _scan(db, [_opp(fav, "HOLD", MON)], failing)
    assert first["failed"] == 1
    ok = Sender()
    retry = _scan(db, [_opp(fav, "HOLD", MON)], ok)
    assert retry["sent"] == 1 and len(ok.messages) == 1
    # Reenvio aceito encerra o evento: a linha ``failed`` antiga não o reenfileira.
    again = _scan(db, [_opp(fav, "HOLD", MON)], ok, now=datetime(2026, 10, 27, 12, 5))
    assert again["signal_events"] == 0 and again["duplicates"] == 0
    assert again["candidates"] == 0 and len(ok.messages) == 1


# ---------------------------------------------------------------- sentido (sem carteira)


def test_signal_direction_is_the_same_in_the_three_classes():
    assert signal_direction("EXIT", "HOLD") == "buy"
    assert signal_direction("HOLD", "EXIT") == "sell"
    assert signal_direction("HOLD", "HOLD") is None
    assert signal_direction(None, "HOLD") is None


def test_exit_is_sent_with_or_without_the_asset_in_the_portfolio(db):
    a = _user(db, "a")
    b = _user(db, "b")
    fa = _favorite(db, a, "NVDA")
    fb = _favorite(db, b, "NVDA")
    _portfolio(db, a, "NVDA", True)
    _portfolio(db, b, "NVDA", False)
    sender = Sender()
    _baseline(db, [_opp(fa, "HOLD", FRI), _opp(fb, "HOLD", FRI)], sender)
    _scan(db, [_opp(fa, "EXIT", MON), _opp(fb, "EXIT", MON)], sender)
    assert sorted(chat for chat, _ in sender.messages) == ["chat-a", "chat-b"]
    assert all("Leitura atual: Venda" in text for _, text in sender.messages)


def test_seven_changes_send_seven_messages_without_rate_limit(db):
    a = _user(db, "a")
    favs = []
    for index in range(7):
        symbol = f"T{index}"
        favs.append(_favorite(db, a, symbol))
        _portfolio(db, a, symbol)
    sender = Sender()
    _baseline(db, [_opp(f, "EXIT", FRI) for f in favs], sender)
    summary = _scan(db, [_opp(f, "HOLD", MON) for f in favs], sender, rate_limit_count=5)
    assert len(sender.messages) == 7
    assert summary["rate_limited"] == 0
    assert not any(r.get("result") == "rate_limited" for r in summary["results"])


# ---------------------------------------------------------------- atraso e mercado fechado


def test_delay_notice_once_per_episode_and_recovery_is_silent(db):
    a = _user(db, "a")
    nvda = _favorite(db, a, "NVDA")
    _portfolio(db, a, "NVDA")
    sender = Sender()
    _baseline(db, [_opp(nvda, "EXIT", FRI)], sender)
    stale = _opp(nvda, "HOLD", FRI, state="stale", episode="ep-1", last=FRI, expected=MON)
    first = _scan(db, [stale], sender)
    assert first["delay_notices"] == 1 and first["held_by_delay"] == 1
    assert len(sender.messages) == 1 and "Dados atrasados" in sender.messages[0][1]
    assert "seg., 26 out. 2026" in sender.messages[0][1]
    second = _scan(db, [stale], sender, now=datetime(2026, 10, 28, 11, 5))
    assert len(sender.messages) == 1
    # Aviso repetido do mesmo episódio é ``duplicate`` e não conta como aviso.
    assert second["delay_notices"] == 0 and second["duplicates"] == 1
    # Recuperação: sem mensagem do episódio; a leitura normal decide o sinal com o candle dela.
    _scan(db, [_opp(nvda, "EXIT", TUE)], sender, now=datetime(2026, 10, 29, 11, 5))
    assert len(sender.messages) == 1
    _scan(db, [_opp(nvda, "HOLD", WED)], sender, now=datetime(2026, 10, 30, 11, 5))
    assert len(sender.messages) == 2 and "qua., 28 out. 2026" in sender.messages[1][1]


def test_crypto_delay_notice_goes_to_who_has_it_in_the_monitor_with_the_alert_on(db):
    a = _user(db, "a")
    b = _user(db, "b")
    c = _user(db, "c")
    fa = _favorite(db, a, "BTC/USDT")
    fb = _favorite(db, b, "BTC/USDT")
    fc = _favorite(db, c, "BTC/USDT", notify=False)
    # A carteira não decide: A tem BTC marcado na carteira, B não.
    _portfolio(db, a, "BTC/USDT", True)
    sender = Sender()
    rows = [
        _opp(f, "HOLD", "2026-10-23T00:00:00+00:00", state="stale", episode="ep-btc")
        for f in (fa, fb, fc)
    ]
    summary = _scan(db, rows, sender, now=datetime(2026, 10, 25, 11, 5))
    assert sorted(c for c, _ in sender.messages) == ["chat-a", "chat-b"]
    assert summary["delay_notices"] == 2 and "BTC/USDT (Cripto · USDT)" in sender.messages[0][1]


def test_closed_market_never_sends(db):
    a = _user(db, "a")
    fav = _favorite(db, a, "NVDA")
    _portfolio(db, a, "NVDA")
    sender = Sender()
    _baseline(db, [_opp(fav, "EXIT", FRI)], sender)
    _scan(db, [_opp(fav, "EXIT", FRI, state="closed")], sender, now=datetime(2026, 10, 24, 11, 5))
    assert sender.messages == []


def test_insufficient_data_sends_nothing(db):
    a = _user(db, "a")
    fav = _favorite(db, a, "QQQ")
    _portfolio(db, a, "QQQ")
    sender = Sender()
    summary = _scan(db, [_opp(fav, "EXIT", MON, state="insufficient")], sender)
    assert sender.messages == [] and summary["delay_notices"] == 0
    assert db.get(MonitorFavoriteAlertState, fav.id) is None


def test_calendar_saturday_holiday_and_half_day():
    def brt(text):
        return pd.Timestamp(text, tz=BRT)

    saturday = cal.market_status(brt("2026-10-24 11:05"))
    assert (saturday.state, saturday.reason) == ("closed", "weekend")
    assert saturday.next_open == pd.Timestamp("2026-10-26 09:30", tz=NY).tz_convert("UTC")
    holiday = cal.market_status(pd.Timestamp("2026-11-26 12:00", tz=NY))
    assert (holiday.state, holiday.reason) == ("closed", "holiday")
    assert holiday.next_open == pd.Timestamp("2026-11-27 09:30", tz=NY).tz_convert("UTC")
    half = pd.Timestamp("2026-11-27 13:00", tz=NY)
    assert cal.last_closed_start("1d", half) == cal.ny_midnight_utc(half.date())
    open_status = cal.market_status(brt("2026-10-26 15:00"))
    assert open_status.state == "open"
    assert open_status.closes_at.tz_convert(BRT).strftime("%H:%M") == "17:00"
    assert cal.last_closed_start("1h", pd.Timestamp("2026-10-26 12:10", tz=NY)) == pd.Timestamp(
        "2026-10-26 10:30", tz=NY
    ).tz_convert("UTC")
    # Sábado com o último candle de sexta não é atraso; o feriado também não.
    for now in (brt("2026-10-24 08:05"), brt("2026-10-26 08:05")):
        check = market_state.check_series(
            data_source="binance_equity",
            symbol="NVDA",
            timeframe="1d",
            last_candle=FRI,
            now=now,
        )
        assert not check.stale
    after_holiday = market_state.check_series(
        data_source="binance_equity",
        symbol="SPY",
        timeframe="1d",
        last_candle="2026-11-25T05:00:00+00:00",
        now=brt("2026-11-27 08:05"),
    )
    assert not after_holiday.stale
    tuesday = market_state.check_series(
        data_source="binance_equity",
        symbol="NVDA",
        timeframe="1d",
        last_candle=FRI,
        now=brt("2026-10-27 08:05"),
    )
    assert tuesday.stale and tuesday.expected_candle == pd.Timestamp(MON)
    crypto = market_state.check_series(
        data_source="ccxt",
        symbol="BTC/USDT",
        timeframe="1d",
        last_candle="2026-10-23T00:00:00+00:00",
        now=brt("2026-10-25 08:05"),
    )
    assert crypto.stale


def test_data_health_opens_keeps_and_closes_the_episode(db):
    now = datetime(2026, 10, 27, 11, 5)
    stale = market_state.SeriesCheck(
        "binance_equity", "NVDA", "1d", True, pd.Timestamp(FRI), pd.Timestamp(MON)
    )
    opened = market_state.update_data_health(db, [stale], now=now)[("binance_equity", "NVDA")]
    assert opened.opened and opened.state == "stale"
    kept = market_state.update_data_health(db, [stale], now=now + timedelta(days=1))
    assert kept[("binance_equity", "NVDA")].episode_id == opened.episode_id
    ok = market_state.SeriesCheck(
        "binance_equity", "NVDA", "1d", False, pd.Timestamp(TUE), pd.Timestamp(TUE)
    )
    closed = market_state.update_data_health(db, [ok], now=now + timedelta(days=2))
    assert closed[("binance_equity", "NVDA")].closed
    assert db.get(MonitorDataHealth, ("binance_equity", "NVDA")).state == "ok"


# ---------------------------------------------------------------- transição


def test_transition_notice_only_for_catalog_receivers_and_once(db, monkeypatch):
    receiver = _user(db, "receiver")
    never = _user(db, "never")
    db.add(SystemPreference(key="monitor_telegram_favorite_origin_at", value="2026-10-26T12:00:00"))
    db.add(
        MonitorTelegramAlert(
            user_id=str(receiver.id),
            symbol="BTC/USDT",
            timeframe="1d",
            new_status="HOLD",
            severity="Atencao",
            result_status="sent",
            payload_hash="x",
            source="monitor",
            created_at=datetime(2026, 10, 20, 11, 5),
        )
    )
    db.commit()
    sender = Sender()
    summary = _scan(db, [], sender)
    assert summary["transition_notices"] == 1
    assert [c for c, _ in sender.messages] == ["chat-receiver"]
    assert "Mudança nos alertas" in sender.messages[0][1] and "BTC/USDT" in sender.messages[0][1]
    catalog_reads = []
    original_rows = alerts._catalog_alert_rows

    def _counting_rows(*args, **kwargs):
        catalog_reads.append(args[1])
        return original_rows(*args, **kwargs)

    monkeypatch.setattr(alerts, "_catalog_alert_rows", _counting_rows)
    again = _scan(db, [], sender, now=datetime(2026, 10, 28, 11, 5))
    assert len(sender.messages) == 1
    # Já avisado: não conta de novo nem relê o histórico do catálogo.
    assert again["transition_notices"] == 0 and again["duplicates"] == 0
    assert str(receiver.id) not in catalog_reads
    monkeypatch.undo()
    origin = alerts.alert_origin_for_user(db, str(receiver.id))
    assert origin["show_banner"] and origin["received_catalog_alerts"]
    assert origin["catalog_until"] == "2026-10-26"
    plain = alerts.alert_origin_for_user(db, str(never.id))
    assert plain["show_banner"] and not plain["received_catalog_alerts"]
    assert plain["catalog_until"] is None


# ---------------------------------------------------------------- mensagem e ordens


def test_message_has_class_configuration_candle_and_is_not_an_order(db):
    a = _user(db, "a")
    fav = _favorite(db, a, "NVDA")
    _portfolio(db, a, "NVDA")
    sender = Sender()
    _baseline(db, [_opp(fav, "EXIT", "2026-10-22T04:00:00+00:00")], sender)
    _scan(db, [_opp(fav, "HOLD", FRI)], sender, now=datetime(2026, 10, 24, 11, 5))
    text = sender.messages[0][1]
    for piece in (
        "NVDA (Ação · USD)",
        "Binance Ações · pregão regular de NY · ajustado por split",
        "TimeFrame: 1d",
        "Leitura anterior: Venda",
        "Leitura atual: Compra",
        "sex., 23 out. 2026 (pregão fechou às 17:00 BRT)",
        "182,40 USD",
        "Este alerta não envia ordem: é só o sinal da estratégia.",
    ):
        assert piece in text
    assert "Ordem: nenhuma enviada" not in text
    row = db.query(MonitorTelegramAlert).filter_by(result_status="sent").one()
    assert row.favorite_id == fav.id
    assert row.payload_json["candle_time"] == FRI
    assert row.payload_json["configuration"]["data_source"] == "binance_equity"
    assert db.query(MonitorSpotOrderRequest).count() == 0


# ---------------------------------------------------------------- favoritos (API)


@pytest.fixture
def api(db, monkeypatch):
    class Disabled:
        enabled = False

    monkeypatch.setattr(favorites_route, "_FAVORITE_OHLCV_REPO", Disabled())
    owner = _user(db, "owner")
    other = _user(db, "other")
    state = {"user": str(owner.id)}
    bind = db.get_bind()
    Session = sessionmaker(bind=bind)

    def _db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app = FastAPI()
    app.include_router(favorites_route.router)
    app.include_router(opportunity_routes.router)
    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = lambda: state["user"]
    return TestClient(app), state, owner, other


def _body(symbol="NVDA", source="binance_equity"):
    return {
        "name": f"{symbol} teste",
        "symbol": symbol,
        "timeframe": "1d",
        "strategy_name": "multi_ma_crossover",
        "parameters": {"direction": "long", "data_source": source},
        "metrics": {"total_trades": 1},
    }


def test_same_configuration_is_409_and_other_source_coexists(api, db):
    client, state, owner, _ = api
    _favorite(db, owner, "NVDA", cfg=STOOQ_CFG, notify=False)
    created = client.post("/api/favorites/", json=_body())
    assert created.status_code == 200, created.text
    assert created.json()["configuration"]["session"] == "regular_ny"
    duplicate = client.post("/api/favorites/", json=_body())
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Estratégia já existe nos favoritos com esta configuração"
    exists = client.get(
        "/api/favorites/exists",
        params={"strategy_name": "multi_ma_crossover", "symbol": "NVDA", "timeframe": "1d"},
    )
    assert exists.json() == {"exists": True}
    stooq = client.get(
        "/api/favorites/exists",
        params={
            "strategy_name": "multi_ma_crossover",
            "symbol": "NVDA",
            "timeframe": "1d",
            "data_source": "stooq",
            "session": "eod",
            "adjustment": "legacy",
        },
    )
    assert stooq.json() == {"exists": True}
    listed = client.get("/api/favorites/").json()
    labels = sorted(item["configuration"]["label_short"] for item in listed)
    assert labels == ["Binance Ações · NY · split", "Stooq · fonte antiga · diário"]


def test_owner_marks_alertar_others_get_404_hidden_and_403_on_visible_catalog(api, db, monkeypatch):
    client, state, owner, other = api
    fav = _favorite(db, owner, "SPY", notify=False)
    response = client.patch(f"/api/favorites/{fav.id}", json={"notify_telegram": True})
    assert response.status_code == 200 and response.json()["notify_telegram"] is True
    state["user"] = str(other.id)
    # Favorito que o outro não vê: 404, sem revelar que existe.
    hidden = client.patch(f"/api/favorites/{fav.id}", json={"notify_telegram": False})
    assert hidden.status_code == 404
    # Favorito da vitrine do catálogo (admin): visível, mas "Alertar" é só do dono.
    admin = _user(db, "admin")
    admin.role = "admin"
    db.commit()
    monkeypatch.setattr(favorites_route, "ADMIN_EMAILS", {admin.email})
    catalog = _favorite(db, admin, "QQQ", notify=True)
    refused = client.patch(f"/api/favorites/{catalog.id}", json={"notify_telegram": False})
    assert refused.status_code == 403
    db.expire_all()
    assert db.get(FavoriteStrategy, fav.id).notify_telegram is True
    assert db.get(FavoriteStrategy, catalog.id).notify_telegram is True


def test_alert_origin_endpoint(api, db):
    client, state, owner, _ = api
    body = client.get("/api/opportunities/alert-origin").json()
    assert body["show_banner"] is True and body["received_catalog_alerts"] is False
    _favorite(db, owner, "NVDA", notify=True)
    assert client.get("/api/opportunities/alert-origin").json()["show_banner"] is False


# ---------------------------------------------------------------- signal_monitor


def test_signal_monitor_never_queries_a_ticker(monkeypatch):
    import asyncio

    from app.services import signal_monitor

    assert signal_monitor.is_monitored_asset("BTCUSDT")
    assert not signal_monitor.is_monitored_asset("NVDA")
    assert not signal_monitor.is_monitored_asset("USDT")
    called = []

    class Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, *a, **k):
            called.append(k)
            raise AssertionError("não deveria consultar")

    monkeypatch.setattr(signal_monitor.httpx, "AsyncClient", Client)
    assert asyncio.run(signal_monitor._fetch_price("NVDA")) is None
    assert called == []


# ---------------------------------------------------------------- residuais da revisão (pós-T18)


def _sessions_frame(last_day: str, count: int) -> pd.DataFrame:
    sessions = cal.sessions_between(
        pd.Timestamp(last_day) - pd.Timedelta(days=int(count * 1.6) + 20), pd.Timestamp(last_day)
    )[-count:]
    index = pd.DatetimeIndex([cal.ny_midnight_utc(day) for day in sessions], name="timestamp_utc")
    opens = [100.0 + i for i in range(count)]
    return pd.DataFrame(
        {
            "open": opens,
            "high": [o + 3 for o in opens],
            "low": [o - 3 for o in opens],
            "close": [o + 1 for o in opens],
            "volume": [1000.0] * count,
        },
        index=index,
    )


def test_local_fetch_timeout_is_not_a_delay_and_opens_no_episode(
    db, unit_database_url, monkeypatch
):
    """P1: série que só estourou o orçamento local fica sem leitura; nada de "Dados atrasados"."""

    import time

    from app.services import opportunity_service
    from app.services.opportunity_service import OpportunityService

    a = _user(db, "a")
    for symbol in ("NVDA", "SPY", "QQQ"):
        _favorite(db, a, symbol)
        _portfolio(db, a, symbol)

    class SlowProvider:
        def __init__(self):
            self.calls = []
            self.frame = None

        def fetch_ohlcv(self, symbol, timeframe, since_str=None, limit=None, **_):
            self.calls.append(symbol)
            time.sleep(0.4)
            return self.frame.copy()

    provider = SlowProvider()
    monkeypatch.setattr(opportunity_service, "_OHLCV_CACHE", {})
    monkeypatch.setattr(opportunity_service, "get_market_data_provider", lambda *_a: provider)
    # Um só leitor e orçamento curto: a primeira série termina depois do orçamento e as outras
    # duas nem começam (o caso de dezenas de séries com o cache frio).
    monkeypatch.setattr(opportunity_service, "MARKET_FETCH_WORKERS", 1, raising=False)
    monkeypatch.setenv("OPPORTUNITIES_ALERT_FETCH_TIMEOUT_SECONDS", "0.1")
    monkeypatch.setenv("OPPORTUNITIES_MARKET_FETCH_TIMEOUT_SECONDS", "0.1")
    service = OpportunityService(db_path=unit_database_url)
    monkeypatch.setattr(
        service.combo_service,
        "get_template_metadata",
        lambda name: {
            "indicators": [],
            "entry_logic": "close > open",
            "exit_logic": "close < open",
            "stop_loss": 0.5,
            "display_name": "Teste",
        },
    )
    sender = Sender()
    for day in (27, 28):
        # Dado em dia: o último pregão fechado antes da varredura das 08:05 BRT.
        provider.frame = _sessions_frame(f"2026-10-{day - 1}", 60)
        monkeypatch.setattr(opportunity_service, "_OHLCV_CACHE", {})
        summary = run_monitor_telegram_alert_scan(
            db,
            user_id="cron",
            settings=_settings(),
            opportunity_service=service,
            sender=sender,
            now=datetime(2026, 10, day, 11, 5),
        )
        assert summary["held_by_delay"] == 0 and summary["delay_notices"] == 0
        # A série que terminou depois do orçamento ainda vale nesta passada; as outras não.
        assert summary["favorites_evaluated"] == 1
        db.expire_all()
        assert db.query(MonitorDataHealth).filter_by(state="stale").count() == 0
    assert not [text for _, text in sender.messages if "Dados atrasados" in text]
    assert len(provider.calls) == 2  # uma leitura por passada; as outras ficaram sem leitura
    read = db.query(MonitorDataHealth).all()
    assert 1 <= len(read) <= 2 and all(row.state == "ok" for row in read)


def test_finished_fetch_not_delivered_before_budget_is_not_a_delay(
    db, unit_database_url, monkeypatch
):
    """P1: leitura que terminou mas não saiu do ``as_completed`` no estouro não vira atraso."""

    from concurrent.futures import wait

    from app.services import opportunity_service
    from app.services.opportunity_service import OpportunityService

    a = _user(db, "a")
    for symbol in ("NVDA", "SPY", "QQQ"):
        _favorite(db, a, symbol)
        _portfolio(db, a, symbol)

    class Provider:
        frame = None

        def fetch_ohlcv(self, symbol, timeframe, since_str=None, limit=None, **_):
            return self.frame.copy()

    def as_completed_that_times_out(futures, timeout=None):
        # Todas as leituras já terminaram, mas o orçamento estoura antes de entregar qualquer uma.
        wait(list(futures))
        raise TimeoutError()
        yield  # pragma: no cover - torna a função um gerador

    provider = Provider()
    monkeypatch.setattr(opportunity_service, "get_market_data_provider", lambda *_a: provider)
    monkeypatch.setattr(opportunity_service, "as_completed", as_completed_that_times_out)
    service = OpportunityService(db_path=unit_database_url)
    monkeypatch.setattr(
        service.combo_service,
        "get_template_metadata",
        lambda name: {
            "indicators": [],
            "entry_logic": "close > open",
            "exit_logic": "close < open",
            "stop_loss": 0.5,
            "display_name": "Teste",
        },
    )
    sender = Sender()
    provider.frame = _sessions_frame("2026-10-26", 60)
    monkeypatch.setattr(opportunity_service, "_OHLCV_CACHE", {})
    summary = run_monitor_telegram_alert_scan(
        db,
        user_id="cron",
        settings=_settings(),
        opportunity_service=service,
        sender=sender,
        now=datetime(2026, 10, 27, 11, 5),
    )
    assert summary["held_by_delay"] == 0 and summary["delay_notices"] == 0
    # Na varredura, a leitura terminada é colhida e vale nesta passada.
    assert summary["favorites_evaluated"] == 3
    db.expire_all()
    assert db.query(MonitorDataHealth).filter_by(state="stale").count() == 0
    assert not [text for _, text in sender.messages if "Dados atrasados" in text]


def test_other_timeframe_detail_does_not_decide_the_next_pass(db):
    """P2: 15m atrasado lido uma vez + 1d em dia na passada seguinte: o 1d não fica em espera."""

    now = datetime(2026, 10, 27, 15, 0)
    stale_15m = market_state.SeriesCheck(
        "binance_equity",
        "NVDA",
        "15m",
        True,
        pd.Timestamp("2026-10-27T14:00:00+00:00"),
        pd.Timestamp("2026-10-27T14:30:00+00:00"),
    )
    ok_1d = market_state.SeriesCheck(
        "binance_equity", "NVDA", "1d", False, pd.Timestamp(MON), pd.Timestamp(MON)
    )
    first = market_state.update_data_health(db, [stale_15m], now=now)[("binance_equity", "NVDA")]
    assert first.opened and first.state == "stale"
    # Mesma passada com os dois: o ativo fica em espera, mas a linha 1d guarda os horários dela.
    both = market_state.update_data_health(db, [stale_15m, ok_1d], now=now)
    episode = both[("binance_equity", "NVDA")].as_dict()
    assert episode["episode_id"] == first.episode_id
    held = market_state.build_market_state(
        equity=True, now=pd.Timestamp(now, tz="UTC"), series=ok_1d, episode=episode
    )
    assert held["state"] == "stale"
    assert held["last_candle"].startswith("2026-10-26") and held["stale_timeframe"] == "15m"
    assert held["stale_detail"]["expected_candle"].startswith("2026-10-27T14:30")
    # Passada seguinte só com o 1d em dia: o favorito 1d não fica em espera.
    later = now + timedelta(days=1)
    nxt = market_state.update_data_health(db, [ok_1d], now=later)[("binance_equity", "NVDA")]
    assert nxt.state == "ok" and nxt.episode_id is None and not nxt.opened
    row = market_state.build_market_state(
        equity=True, now=pd.Timestamp(later, tz="UTC"), series=ok_1d, episode=nxt.as_dict()
    )
    assert row["state"] != "stale"
    # O episódio do 15m não reabre (nem avisa de novo) enquanto o 15m não é relido em dia.
    again = market_state.update_data_health(db, [stale_15m], now=later + timedelta(hours=1))
    assert again[("binance_equity", "NVDA")].episode_id == first.episode_id
    assert not again[("binance_equity", "NVDA")].opened


def test_delay_notice_never_labels_other_timeframe_times_as_1d(db):
    """P2: ativo em espera por um 15m atrasado; a DM sai com o rótulo e os horários do 15m."""

    a = _user(db, "a")
    nvda = _favorite(db, a, "NVDA")
    _portfolio(db, a, "NVDA")
    now = datetime(2026, 10, 27, 15, 0)
    stale_15m = market_state.SeriesCheck(
        "binance_equity",
        "NVDA",
        "15m",
        True,
        pd.Timestamp("2026-10-27T14:00:00+00:00"),
        pd.Timestamp("2026-10-27T14:30:00+00:00"),
    )
    ok_1d = market_state.SeriesCheck(
        "binance_equity", "NVDA", "1d", False, pd.Timestamp(MON), pd.Timestamp(MON)
    )
    episode = market_state.update_data_health(db, [stale_15m, ok_1d], now=now)[
        ("binance_equity", "NVDA")
    ].as_dict()
    row = _opp(nvda, "HOLD", MON)
    row["market_state"] = market_state.build_market_state(
        equity=True, now=pd.Timestamp(now, tz="UTC"), series=ok_1d, episode=episode
    )
    sender = Sender()
    summary = _scan(db, [row], sender, now=now)
    assert summary["delay_notices"] == 1 and summary["held_by_delay"] == 1
    text = sender.messages[0][1]
    assert "Último candle recebido: ter., 27 out. 2026, 11:00 BRT (15m)" in text
    assert "Esperado: ter., 27 out. 2026, 11:30 BRT" in text
    assert "(1d)" not in text


def _catalog_receiver_alert(db, user: User) -> None:
    db.add(
        MonitorTelegramAlert(
            user_id=str(user.id),
            symbol="BTC/USDT",
            timeframe="1d",
            new_status="HOLD",
            severity="Atencao",
            result_status="sent",
            payload_hash="x",
            source="monitor",
            created_at=datetime(2026, 10, 20, 11, 5),
        )
    )


def test_transition_notice_only_on_the_first_scan_after_the_switch(db):
    """P3: quem ligou logo após a troca e desligou semanas depois não recebe o aviso."""

    marker = alerts.MONITOR_TELEGRAM_TRANSITION_SCAN_AT_KEY
    receiver = _user(db, "receiver")
    late = _user(db, "late")
    db.add(SystemPreference(key="monitor_telegram_favorite_origin_at", value="2026-10-26T12:00:00"))
    _catalog_receiver_alert(db, receiver)
    _catalog_receiver_alert(db, late)
    db.commit()
    # "late" deu estrela a um favorito (alerta ligado) logo depois da troca: nada para ele.
    fav = _favorite(db, late, "BTC/USDT")
    sender = Sender()
    first = _scan(db, [], sender, now=datetime(2026, 10, 27, 11, 5))
    assert first["transition_notices"] == 1
    assert [c for c, _ in sender.messages] == ["chat-receiver"]
    assert db.get(SystemPreference, marker).value.startswith("2026-10-27T11:05")
    # Depois ele desliga o alerta: nenhuma varredura seguinte manda o aviso.
    fav.notify_telegram = False
    db.commit()
    for now in (datetime(2026, 10, 28, 11, 5), datetime(2026, 11, 16, 11, 5)):
        later = _scan(db, [], sender, now=now)
        assert later["transition_notices"] == 0
    assert len(sender.messages) == 1


def test_transition_notice_is_not_sent_long_after_the_switch(db):
    """P3: primeira varredura semanas depois da troca (timer parado) não manda o aviso."""

    receiver = _user(db, "receiver")
    db.add(SystemPreference(key="monitor_telegram_favorite_origin_at", value="2026-10-26T12:00:00"))
    _catalog_receiver_alert(db, receiver)
    db.commit()
    sender = Sender()
    summary = _scan(db, [], sender, now=datetime(2026, 11, 16, 11, 5))
    assert summary["transition_notices"] == 0 and sender.messages == []


# ---------------------------------------------------------------- regra nova (Design d2, 27/10)
# Alerta = estratégia própria no Monitor (estrela 1–3) com o alerta ligado; a carteira não decide;
# o catálogo não alerta; lote e Descoberta salvam sem estrela.


def _no_wallet(monkeypatch):
    from app.services import monitor_portfolio_status

    def boom(*_a, **_k):
        raise AssertionError("a varredura não lê a carteira Binance")

    monkeypatch.setattr(monitor_portfolio_status, "fetch_user_wallet_holdings", boom)
    monkeypatch.setattr(monitor_portfolio_status, "resolve_portfolio_status_for_user", boom)


def test_d2_unstarred_or_switched_off_favorites_never_alert(db):
    a = _user(db, "a")
    starred = _favorite(db, a, "NVDA", tier=2)
    unstarred = _favorite(db, a, "QQQ", tier=None)
    off = _favorite(db, a, "ETH/USDT", tier=2, notify=False)

    def rows(status, candle):
        return [
            _opp(starred, status, candle),
            _opp(unstarred, status, candle),
            _opp(off, status, candle),
        ]

    sender = Sender()
    _baseline(db, rows("EXIT", FRI), sender)
    summary = _scan(db, rows("HOLD", MON), sender)
    assert summary["favorites_evaluated"] == 1
    assert len(sender.messages) == 1 and "NVDA (Ação · USD)" in sender.messages[0][1]
    # Sem estrela ou desligado: nem estado guardado, nem alerta.
    assert db.get(MonitorFavoriteAlertState, unstarred.id) is None
    assert db.get(MonitorFavoriteAlertState, off.id) is None


def test_d2_catalog_never_alerts_even_with_the_preference_star(db, unit_database_url, monkeypatch):
    from app.models import MonitorStrategyPreference
    from app.services.opportunity_service import OpportunityService

    monkeypatch.setenv("ADMIN_EMAILS", "admin@test.local")
    admin = _user(db, "admin")
    c = _user(db, "c")
    catalog_unstarred = _favorite(db, admin, "ETH/USDT", tier=None)
    catalog_starred = _favorite(db, admin, "BTC/USDT", tier=3)
    db.add(
        MonitorStrategyPreference(
            user_id=str(c.id), favorite_id=catalog_unstarred.id, liked=True, tier=3
        )
    )
    db.commit()
    favorites = OpportunityService(db_path=unit_database_url).get_alert_favorites()
    assert [(f["id"], f["user_id"]) for f in favorites] == [(catalog_starred.id, str(admin.id))]
    # A linha da vitrine que C vê (com a estrela dele) nunca entra na varredura.
    vitrine = {
        **_opp(catalog_unstarred, "HOLD", MON),
        "user_id": str(c.id),
        "tier": 3,
        "is_curated_fallback": True,
    }
    sender = Sender()
    _baseline(db, [{**vitrine, "status": "EXIT"}, _opp(catalog_starred, "EXIT", FRI)], sender)
    _scan(db, [vitrine, _opp(catalog_starred, "HOLD", MON)], sender)
    assert [chat for chat, _ in sender.messages] == ["chat-admin"]


def test_d2_entry_outside_portfolio_exit_and_crypto_without_the_wallet(db, monkeypatch):
    _no_wallet(monkeypatch)
    a = _user(db, "a")
    db.add(
        UserExchangeCredential(
            user_id=str(a.id), provider=BINANCE_PROVIDER, api_key="k", api_secret="s"
        )
    )
    db.commit()
    nvda = _favorite(db, a, "NVDA")  # fora da carteira
    spy = _favorite(db, a, "SPY")
    btc = _favorite(db, a, "BTC/USDT")  # com saldo: a reentrada sai
    sol = _favorite(db, a, "SOL/USDT")  # sem saldo: a saída sai
    _portfolio(db, a, "NVDA", False)
    _portfolio(db, a, "SPY", True)
    sender = Sender()
    _baseline(
        db,
        [
            _opp(nvda, "EXIT", FRI),
            _opp(spy, "HOLD", FRI),
            _opp(btc, "EXIT", FRI),
            _opp(sol, "HOLD", FRI),
        ],
        sender,
    )
    summary = _scan(
        db,
        [
            _opp(nvda, "HOLD", MON),
            _opp(spy, "EXIT", MON),
            _opp(btc, "HOLD", MON),
            _opp(sol, "EXIT", MON),
        ],
        sender,
    )
    texts = [text for _, text in sender.messages]
    assert len(texts) == 4 and summary["sent"] == 4
    assert any("NVDA (Ação" in t and "Leitura atual: Compra" in t for t in texts)
    assert any("SPY (Ação" in t and "Leitura atual: Venda" in t for t in texts)
    assert any("BTC/USDT (Cripto" in t and "Leitura atual: Compra" in t for t in texts)
    assert any("SOL/USDT (Cripto" in t and "Leitura atual: Venda" in t for t in texts)
    assert not any("Aviso operacional" in t for t in texts)
    for gone in ("binance_sync_failed_users", "operational_dms", "suppressed_by_position_matrix"):
        assert gone not in summary
    assert not any(
        str(r.get("result", "")).startswith(("suppressed", "outside_portfolio"))
        for r in summary["results"]
    )


def test_d2_tier_filter_is_ignored_and_recorded(db, monkeypatch):
    monkeypatch.setenv("MONITOR_TELEGRAM_TIER_FILTER", "1")
    a = _user(db, "a")
    one_star = _favorite(db, a, "NVDA", tier=3)
    sender = Sender()
    _baseline(db, [_opp(one_star, "EXIT", FRI)], sender)
    summary = _scan(db, [_opp(one_star, "HOLD", MON)], sender, tier_filter="1")
    assert len(sender.messages) == 1
    assert summary["tier_filter_ignored"] == "1"
    monkeypatch.delenv("MONITOR_TELEGRAM_TIER_FILTER")
    db.add(SystemPreference(key=alerts.MONITOR_TELEGRAM_TIER_FILTER_KEY, value="2"))
    db.commit()
    again = _scan(db, [], Sender(), now=datetime(2026, 10, 28, 11, 5))
    assert again["tier_filter_ignored"] == "2"
    db.query(SystemPreference).filter_by(key=alerts.MONITOR_TELEGRAM_TIER_FILTER_KEY).delete()
    db.commit()
    assert "tier_filter_ignored" not in _scan(db, [], Sender())


def test_d2_signal_and_delay_messages_say_how_to_stop(db):
    a = _user(db, "a")
    nvda = _favorite(db, a, "NVDA")
    sender = Sender()
    _baseline(db, [_opp(nvda, "EXIT", FRI)], sender)
    _scan(db, [_opp(nvda, "HOLD", MON)], sender)
    signal = sender.messages[0][1]
    assert (
        'Para não receber mais desta estratégia: desligue o "Alerta" dela no Monitor '
        "ou tire a estrela em Favoritos." in signal
    )
    assert "carteira" not in signal.lower()
    stale = _opp(nvda, "HOLD", MON, state="stale", episode="ep-9", last=MON, expected=TUE)
    _scan(db, [stale], sender, now=datetime(2026, 10, 28, 11, 5))
    delay = sender.messages[1][1]
    assert "Dados atrasados" in delay
    assert 'Para não receber avisos de NVDA: desligue o "Alerta" das estratégias de NVDA' in delay


def test_d2_delay_notice_without_portfolio_and_not_for_who_switched_off(db):
    a = _user(db, "a")
    b = _user(db, "b")
    fa = _favorite(db, a, "NVDA")  # fora da carteira, alerta ligado
    fb = _favorite(db, b, "NVDA", notify=False)
    sender = Sender()
    rows = [
        _opp(f, "HOLD", FRI, state="stale", episode="ep-n", last=FRI, expected=MON)
        for f in (fa, fb)
    ]
    summary = _scan(db, rows, sender)
    assert [chat for chat, _ in sender.messages] == ["chat-a"]
    assert summary["delay_notices"] == 1


def test_d2_star_switches_the_alert_on_and_resets_the_state(api, db):
    client, _state, owner, _other = api
    qqq = _favorite(db, owner, "QQQ", tier=None, notify=False)
    db.add(MonitorFavoriteAlertState(favorite_id=qqq.id, status="HOLD", observed_at=datetime.now()))
    db.commit()
    # Dar a primeira estrela liga o alerta na mesma gravação e a próxima leitura é só base.
    given = client.patch(f"/api/favorites/{qqq.id}", json={"tier": 3})
    assert given.status_code == 200, given.text
    assert given.json()["tier"] == 3 and given.json()["notify_telegram"] is True
    db.expire_all()
    assert db.get(MonitorFavoriteAlertState, qqq.id) is None
    # Desligar no Monitor; subir de 1 para 2 estrelas não mexe.
    off = client.patch(f"/api/favorites/{qqq.id}", json={"notify_telegram": False})
    assert off.status_code == 200 and off.json()["notify_telegram"] is False
    up = client.patch(f"/api/favorites/{qqq.id}", json={"tier": 2}).json()
    assert up["tier"] == 2 and up["notify_telegram"] is False
    # Tirar as estrelas: sai do Monitor e da varredura (o valor fica guardado).
    removed = client.patch(f"/api/favorites/{qqq.id}", json={"tier": None}).json()
    assert removed["tier"] is None and removed["notify_telegram"] is False
    # Dar a estrela de novo religa o alerta que estava desligado (P3 aceito).
    again = client.patch(f"/api/favorites/{qqq.id}", json={"tier": 1}).json()
    assert again["tier"] == 1 and again["notify_telegram"] is True


def test_d2_new_favorite_starts_without_star_and_with_the_alert_on(api, db):
    client, _state, _owner, _other = api
    created = client.post("/api/favorites/", json={**_body("SPY"), "notify_telegram": False})
    assert created.status_code == 200, created.text
    assert created.json()["tier"] is None and created.json()["notify_telegram"] is True


def test_d2_alert_origin_fields_and_banner_only_for_the_vitrine(api, db, monkeypatch):
    client, state, owner, _other = api
    monkeypatch.setenv("ADMIN_EMAILS", "admin@test.local")
    body = client.get("/api/opportunities/alert-origin").json()
    assert body["show_banner"] is True and body["has_monitored_strategy"] is False
    assert body["alerts_on"] == 0 and "has_marked_favorite" not in body
    # Só favorito sem estrela: o Monitor mostra a vitrine, a faixa fica.
    _favorite(db, owner, "QQQ", tier=None)
    assert client.get("/api/opportunities/alert-origin").json()["show_banner"] is True
    # Estratégia com estrela, mesmo com o alerta desligado: sem faixa.
    _favorite(db, owner, "NVDA", tier=2, notify=False)
    body = client.get("/api/opportunities/alert-origin").json()
    assert body["show_banner"] is False and body["has_monitored_strategy"] is True
    assert body["alerts_on"] == 0
    # O admin nunca vê a vitrine.
    admin = _user(db, "admin")
    state["user"] = str(admin.id)
    assert client.get("/api/opportunities/alert-origin").json()["show_banner"] is False


def test_d2_vitrine_ignores_the_screen_star_filter(db, unit_database_url, monkeypatch):
    from app.services.opportunity_service import OpportunityService

    monkeypatch.setenv("ADMIN_EMAILS", "admin@test.local")
    admin = _user(db, "admin")
    bia = _user(db, "bia")
    _favorite(db, admin, "BTC/USDT", tier=1)
    own = _favorite(db, bia, "NVDA", tier=3)
    service = OpportunityService(db_path=unit_database_url)
    # Bia tem estratégia com estrela: filtrar por 3 estrelas não a joga na vitrine.
    assert service.get_favorites(str(bia.id), tier_filter="1") == []
    listed = service.get_favorites(str(bia.id), tier_filter="1,2,3")
    assert [f["id"] for f in listed] == [own.id]
    assert not listed[0]["is_curated_fallback"]
    # Só favorito sem estrela: a vitrine do catálogo, sem alerta.
    own.tier = None
    db.commit()
    vitrine = service.get_favorites(str(bia.id), tier_filter=None)
    assert vitrine and all(f["is_curated_fallback"] for f in vitrine)
    assert not any(f["notify_telegram"] for f in vitrine)


def _transition_receiver(db, name: str) -> User:
    user = _user(db, name)
    _catalog_receiver_alert(db, user)
    db.commit()
    return user


def test_d2_transition_criterion_text_and_no_mark_in_dry_run(db):
    marker = alerts.MONITOR_TELEGRAM_TRANSITION_SCAN_AT_KEY
    db.add(SystemPreference(key="monitor_telegram_favorite_origin_at", value="2026-10-26T12:00:00"))
    db.commit()
    off = _transition_receiver(db, "off")  # tem estratégia com estrela, mas desligada
    unstarred = _transition_receiver(db, "unstarred")  # só favorito sem estrela
    on = _transition_receiver(db, "on")  # estrela e alerta ligado: não recebe
    _favorite(db, off, "NVDA", tier=1, notify=False)
    _favorite(db, unstarred, "QQQ", tier=None)
    _favorite(db, on, "BTC/USDT", tier=3)
    dry = run_monitor_telegram_alert_scan(
        db,
        user_id="cron",
        settings=_settings(),
        opportunity_service=FakeService([]),
        sender=Sender(),
        force_dry_run=True,
        now=datetime(2026, 10, 27, 11, 5),
    )
    assert dry["transition_notices"] == 2
    # Ensaio: nem a marca nem a reserva da chave ``transition`` são gravadas.
    assert db.get(SystemPreference, marker) is None
    assert db.query(MonitorTelegramAlert).filter_by(source="transition").count() == 0
    sender = Sender()
    real = _scan(db, [], sender, now=datetime(2026, 10, 27, 11, 30))
    assert real["transition_notices"] == 2
    assert sorted(chat for chat, _ in sender.messages) == ["chat-off", "chat-unstarred"]
    text = sender.messages[0][1]
    assert "agora vêm das estratégias que você acompanha no Monitor" in text
    assert "Você recebia: BTC/USDT." in text
    assert "dê pelo menos 1 estrela: o alerta já vem ligado e você desliga no Monitor" in text
    assert "Alertar" not in text
    assert db.get(SystemPreference, marker) is not None


def test_d2_transition_mark_waits_for_a_failed_delivery(db):
    marker = alerts.MONITOR_TELEGRAM_TRANSITION_SCAN_AT_KEY
    db.add(SystemPreference(key="monitor_telegram_favorite_origin_at", value="2026-10-26T12:00:00"))
    db.commit()
    _transition_receiver(db, "ok")
    _transition_receiver(db, "down")
    first = Sender(fail_for={"chat-down"})
    summary = _scan(db, [], first, now=datetime(2026, 10, 27, 11, 5))
    assert summary["failed"] == 1 and [c for c, _ in first.messages] == ["chat-ok"]
    assert db.get(SystemPreference, marker) is None
    retry = Sender()
    again = _scan(db, [], retry, now=datetime(2026, 10, 28, 11, 5))
    # Só quem falhou recebe de novo; a chave impede repetir quem já recebeu.
    assert [c for c, _ in retry.messages] == ["chat-down"] and again["failed"] == 0
    assert db.get(SystemPreference, marker) is not None


def test_d2_discovery_promotion_request_refuses_any_tier(monkeypatch):
    from fastapi import HTTPException

    from app.routes import discovery_routes

    captured = {}

    class FakeDiscovery:
        def promote_result(self, *, result_id, actor, idempotency_key, payload, db):
            captured["payload"] = payload
            if "tier" in payload:
                return {"error": "tier not allowed", "detail": "promoção sem estrela"}, 422
            return {"favorite_id": "1", "result_id": result_id}, 201

    monkeypatch.setattr(discovery_routes, "_service", lambda: FakeDiscovery())
    ok = discovery_routes.promote_discovery_result(
        "RS-1", discovery_routes.PromoteRequest(idempotency_key="promote-1"), "admin", None
    )
    assert ok["favorite_id"] == "1" and captured["payload"] == {"result_id": "RS-1"}
    with pytest.raises(HTTPException) as refused:
        discovery_routes.promote_discovery_result(
            "RS-1",
            discovery_routes.PromoteRequest(idempotency_key="promote-2", tier=3),
            "admin",
            None,
        )
    assert refused.value.status_code == 422
    assert captured["payload"] == {"result_id": "RS-1", "tier": 3}


def test_d2_patch_updates_the_monitor_cache_of_the_owner(api, db, monkeypatch):
    client, _state, owner, _other = api
    fav = _favorite(db, owner, "NVDA", tier=2)
    monkeypatch.setattr(opportunity_routes, "_OPPORTUNITIES_CACHE", {})
    opportunity_routes._write_cached_opportunities(
        str(owner.id), "1,2,3", [{"id": fav.id, "notify_telegram": True, "tier": 2}]
    )
    # Desligar no Monitor: a linha em cache já volta desligada (sem recalcular a lista).
    assert (
        client.patch(f"/api/favorites/{fav.id}", json={"notify_telegram": False}).status_code == 200
    )
    cached = opportunity_routes._read_cached_opportunities(str(owner.id), "1,2,3")
    assert cached == [{"id": fav.id, "notify_telegram": False, "tier": 2}]
    # Mudar a estrela muda quem está na lista: o cache do dono sai.
    assert client.patch(f"/api/favorites/{fav.id}", json={"tier": 3}).status_code == 200
    assert opportunity_routes._read_cached_opportunities(str(owner.id), "1,2,3") is None
