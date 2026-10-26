"""Card #1122: alertas por favorito em cripto, ação e ETF (um teste por cenário do design)."""

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
    should_send_position_aware_alert,
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

    def get_alert_opportunities(self, *, tier_filter, now=None):
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
    _portfolio(db, a, "NVDA")
    _portfolio(db, a, "BTC/USDT")
    sender = Sender()
    _baseline(db, [_opp(nvda, "EXIT", FRI), _opp(btc, "HOLD", FRI)], sender)
    summary = _scan(db, [_opp(nvda, "HOLD", MON), _opp(btc, "EXIT", MON)], sender)
    chats = [chat for chat, _ in sender.messages]
    # BTC flat sem credencial: matriz de hoje (só a entrada); NVDA entrada.
    assert chats == ["chat-a"]
    assert "NVDA (Ação · USD)" in sender.messages[0][1]
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


# ---------------------------------------------------------------- matriz


def test_equity_in_portfolio_gets_entry_and_exit_and_outside_gets_nothing():
    assert should_send_position_aware_alert(
        previous_status="HOLD",
        new_status="EXIT",
        has_spot_position=False,
        in_portfolio=True,
        asset_class="stock",
    ) == (True, "sell")
    assert should_send_position_aware_alert(
        previous_status="EXIT",
        new_status="HOLD",
        has_spot_position=False,
        in_portfolio=True,
        asset_class="etf",
    ) == (True, "buy")
    assert should_send_position_aware_alert(
        previous_status="EXIT",
        new_status="HOLD",
        has_spot_position=False,
        in_portfolio=False,
        asset_class="stock",
    ) == (False, "outside_portfolio_scope")
    # Cripto como hoje: flat suprime a saída.
    assert should_send_position_aware_alert(
        previous_status="HOLD",
        new_status="EXIT",
        has_spot_position=False,
        in_portfolio=True,
        asset_class="crypto",
    ) == (False, "suppressed_flat_exit")


def test_nvda_exit_in_portfolio_is_sent_and_outside_portfolio_is_not(db):
    a = _user(db, "a")
    b = _user(db, "b")
    fa = _favorite(db, a, "NVDA")
    fb = _favorite(db, b, "NVDA")
    _portfolio(db, a, "NVDA", True)
    _portfolio(db, b, "NVDA", False)
    sender = Sender()
    _baseline(db, [_opp(fa, "HOLD", FRI), _opp(fb, "HOLD", FRI)], sender)
    _scan(db, [_opp(fa, "EXIT", MON), _opp(fb, "EXIT", MON)], sender)
    assert [chat for chat, _ in sender.messages] == ["chat-a"]
    assert "Leitura atual: Venda" in sender.messages[0][1]


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


def test_wallet_failure_pauses_crypto_only_and_the_notice_is_rate_limited(db, monkeypatch):
    a = _user(db, "a")
    db.add(
        UserExchangeCredential(
            user_id=str(a.id), provider=BINANCE_PROVIDER, api_key="k", api_secret="s"
        )
    )
    db.commit()
    nvda = _favorite(db, a, "NVDA")
    btc = _favorite(db, a, "BTC/USDT")
    _portfolio(db, a, "NVDA")
    monkeypatch.setattr(alerts, "fetch_user_wallet_holdings", lambda *a, **k: ({}, False))
    sender = Sender()
    _baseline(db, [_opp(nvda, "EXIT", FRI), _opp(btc, "EXIT", FRI)], sender)
    sender.messages.clear()
    summary = _scan(db, [_opp(nvda, "HOLD", MON), _opp(btc, "HOLD", MON)], sender)
    texts = [t for _, t in sender.messages]
    assert any("NVDA (Ação · USD)" in t for t in texts)
    assert not any("BTC/USDT (Cripto" in t for t in texts)
    notice = next(t for t in texts if "Aviso operacional" in t)
    assert "ações e ETFs seguem" in notice
    assert summary["binance_sync_failed_users"] == 1
    again = _scan(
        db,
        [_opp(nvda, "HOLD", MON), _opp(btc, "EXIT", TUE)],
        Sender(),
        now=datetime(2026, 10, 27, 11, 30),
    )
    assert again["operational_dms"] == 0 and again["operational_rate_limited"] == 1


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


def test_crypto_delay_notice_needs_the_asset_in_portfolio(db):
    a = _user(db, "a")
    b = _user(db, "b")
    fa = _favorite(db, a, "BTC/USDT")
    fb = _favorite(db, b, "BTC/USDT")
    _portfolio(db, a, "BTC/USDT", True)
    sender = Sender()
    rows = [
        _opp(f, "HOLD", "2026-10-23T00:00:00+00:00", state="stale", episode="ep-btc")
        for f in (fa, fb)
    ]
    summary = _scan(db, rows, sender, now=datetime(2026, 10, 25, 11, 5))
    assert [c for c, _ in sender.messages] == ["chat-a"]
    assert summary["delay_notices"] == 1 and "BTC/USDT (Cripto · USDT)" in sender.messages[0][1]


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


def test_owner_marks_alertar_and_other_user_gets_403(api, db, monkeypatch):
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
