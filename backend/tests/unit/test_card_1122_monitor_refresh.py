"""Card #1122: ação/ETF no Monitor (candle fechado, estado do mercado) e na atualização diária."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import FavoriteStrategy
from app.services import favorite_backtest_refresh_service as refresh_module
from app.services import opportunity_service
from app.services.equity_backtest import EquityPreparation
from app.services.favorite_backtest_refresh_service import (
    REFRESH_STATUS_INSUFFICIENT,
    REFRESH_STATUS_SUCCESS,
    FavoriteBacktestRefreshService,
    last_closed_session_date,
)
from app.services.market_history import nyse_calendar as cal
from app.services.opportunity_service import OpportunityService

BRT = "America/Sao_Paulo"


def _daily_frame(last_day: str, count: int, *, rising_last: bool = True) -> pd.DataFrame:
    sessions = cal.sessions_between(
        pd.Timestamp(last_day) - pd.Timedelta(days=int(count * 1.6) + 20), pd.Timestamp(last_day)
    )[-count:]
    index = pd.DatetimeIndex([cal.ny_midnight_utc(day) for day in sessions], name="timestamp_utc")
    opens = [100.0 + i for i in range(count)]
    closes = [o - 0.5 for o in opens]  # dias de queda (close < open)
    if rising_last:
        closes[-1] = opens[-1] + 2.0  # o último pregão fechado confirma a entrada
    return pd.DataFrame(
        {
            "open": opens,
            "high": [max(o, c) + 1 for o, c in zip(opens, closes)],
            "low": [min(o, c) - 1 for o, c in zip(opens, closes)],
            "close": closes,
            "volume": [1000.0] * count,
        },
        index=index,
    )


class _Provider:
    def __init__(self, frame):
        self.frame = frame
        self.calls = []

    def fetch_ohlcv(self, symbol, timeframe, since_str=None, until_str=None, limit=None, **_):
        self.calls.append({"symbol": symbol, "timeframe": timeframe, "limit": limit})
        return self.frame.copy()


def _service(monkeypatch, frame):
    monkeypatch.setattr(opportunity_service, "_OHLCV_CACHE", {})
    service = OpportunityService(db_path=":memory:")
    provider = _Provider(frame)
    monkeypatch.setattr(opportunity_service, "get_market_data_provider", lambda *_a: provider)
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
    return service, provider


def _favorite(symbol="NVDA", parameters=None, configuration=None):
    params = {"direction": "long", "data_source": "binance_equity"}
    params.update(parameters or {})
    return {
        "id": 21,
        "user_id": "user-1",
        "name": "NVDA teste",
        "symbol": symbol,
        "timeframe": "1d",
        "strategy_name": "teste",
        "parameters": params,
        "tier": 1,
        "notes": None,
        "notify_telegram": True,
        "asset_class": "stock",
        "configuration": configuration,
    }


def test_saturday_reading_uses_friday_closed_candle_without_dropping_it(monkeypatch):
    service, _ = _service(monkeypatch, _daily_frame("2026-10-23", 60))
    rows = service._calculate_opportunities(
        [_favorite()], now=pd.Timestamp("2026-10-24 11:05", tz=BRT)
    )
    assert len(rows) == 1
    row = rows[0]
    # A entrada confirmada no candle de sexta executa na abertura seguinte (seg.): HOLD no sábado.
    assert row["status"] == "HOLD"
    assert row["candle_time"].startswith("2026-10-23")
    assert row["asset_class"] == "stock" and row["currency"] == "USD"
    assert row["configuration"]["label_compact"] == "Binance · NY · split"
    assert row["market_state"]["state"] == "closed"
    assert row["market_state"]["reason"] == "weekend"
    assert row["market_state"]["next_open"].startswith("2026-10-26T13:30")
    assert row["notify_telegram"] is True


def test_tuesday_before_open_reads_monday_and_cuts_the_forming_candle(monkeypatch):
    frame = _daily_frame("2026-10-27", 60)  # inclui terça (em formação às 12:00 NY)
    service, _ = _service(monkeypatch, frame)
    rows = service._calculate_opportunities(
        [_favorite()], now=pd.Timestamp("2026-10-27 12:00", tz="America/New_York")
    )
    assert rows[0]["candle_time"].startswith("2026-10-26")
    assert rows[0]["market_state"]["state"] == "open"
    assert rows[0]["market_state"]["closes_at"].startswith("2026-10-27T20:00")


def test_real_delay_on_tuesday_marks_the_row_stale(monkeypatch):
    service, _ = _service(monkeypatch, _daily_frame("2026-10-23", 60))
    rows = service._calculate_opportunities(
        [_favorite()], now=pd.Timestamp("2026-10-27 08:05", tz=BRT)
    )
    state = rows[0]["market_state"]
    assert state["state"] == "stale"
    assert state["expected_candle"].startswith("2026-10-26")
    assert state["last_candle"].startswith("2026-10-23")
    monday = service._calculate_opportunities(
        [_favorite()], now=pd.Timestamp("2026-10-26 08:05", tz=BRT)
    )
    assert monday[0]["market_state"]["state"] == "closed"
    assert monday[0]["market_state"]["reason"] == "pre_open"


def test_short_history_is_insufficient_without_signal(monkeypatch):
    service, provider = _service(monkeypatch, _daily_frame("2026-10-23", 40))
    rows = service._calculate_opportunities(
        [_favorite(symbol="QQQ", parameters={"sma_long": 200})],
        now=pd.Timestamp("2026-10-24 11:05", tz=BRT),
    )
    row = rows[0]
    assert row["status"] == "EXIT" and row["raw_analysis_status"] == "INSUFFICIENT"
    assert row["market_state"]["state"] == "insufficient"
    assert (row["market_state"]["available"], row["market_state"]["required"]) == (40, 201)
    # A janela de ação/ETF é contada em pregões e cobre o que a estratégia precisa.
    assert provider.calls[0]["limit"] >= 221


def test_stooq_legacy_row_has_its_own_configuration(monkeypatch):
    service, _ = _service(monkeypatch, _daily_frame("2026-10-23", 60))
    legacy = _favorite(parameters={"data_source": "stooq"})
    rows = service._calculate_opportunities([legacy], now=pd.Timestamp("2026-10-24 11:05", tz=BRT))
    assert rows[0]["configuration"]["data_source"] == "stooq"
    assert rows[0]["configuration"]["label_short"] == "Stooq · fonte antiga · diário"


def test_read_failure_counts_as_delay_only_in_the_scan(monkeypatch):
    class Failing:
        def fetch_ohlcv(self, **_):
            raise RuntimeError("binance fora")

    monkeypatch.setattr(opportunity_service, "_OHLCV_CACHE", {})
    service = OpportunityService(db_path=":memory:")
    monkeypatch.setattr(opportunity_service, "get_market_data_provider", lambda *_a: Failing())
    now = pd.Timestamp("2026-10-27 08:05", tz=BRT)
    assert service._calculate_opportunities([_favorite()], now=now) == []
    rows = service._calculate_opportunities([_favorite()], source_label="alert", now=now)
    assert len(rows) == 1
    assert rows[0]["market_state"]["state"] == "stale"
    assert rows[0]["market_state"]["reason"] == "fetch_failed"
    assert rows[0]["user_id"] == "user-1" and rows[0]["status"] is None


# ---------------------------------------------------------------- atualização diária


@pytest.fixture
def refresh_db(postgres_isolation, unit_database_url):
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        yield Session
    finally:
        engine.dispose()


class _Optimizer:
    calls = 0

    def __init__(self):
        self.collection_note = None

    def run_optimization(self, **kwargs):
        type(self).calls += 1
        return {
            "best_metrics": {"total_trades": 1},
            "trades": [],
            "candles": [{"timestamp_utc": "2026-10-23T04:00:00+00:00"}],
        }


def _equity_favorite(Session, **overrides) -> int:
    with Session() as db:
        row = FavoriteStrategy(
            user_id="user-1",
            name="NVDA",
            symbol="NVDA",
            timeframe="1d",
            strategy_name="teste",
            parameters={"direction": "long", "data_source": "binance_equity", "sma": 20},
            metrics=overrides.pop("metrics", {}),
            data_source="binance_equity",
            session="regular_ny",
            adjustment="split",
            **overrides,
        )
        db.add(row)
        db.commit()
        return int(row.id)


def _patch_equity(monkeypatch, frame, now):
    class Provider:
        def __init__(self, *a, **k):
            pass

        def fetch_ohlcv(self, **_):
            return frame.copy()

    import app.services.equity_backtest as equity_backtest
    import app.services.market_data_providers as providers

    monkeypatch.setattr(
        equity_backtest,
        "prepare_equity_history",
        lambda *a, **k: EquityPreparation(asset={"symbol": "NVDA", "asset_class": "stock"}),
    )
    monkeypatch.setattr(providers, "BinanceEquityMarketDataProvider", Provider)
    monkeypatch.setattr(refresh_module, "_utcnow", lambda: now)


def test_sunday_refresh_without_new_candle_keeps_success(refresh_db, monkeypatch):
    fid = _equity_favorite(
        refresh_db,
        auto_refresh_status=REFRESH_STATUS_SUCCESS,
        metrics={"analysis_last_closed_candle": "2026-10-23T04:00:00+00:00"},
    )
    _patch_equity(monkeypatch, _daily_frame("2026-10-23", 60), datetime(2026, 10, 25, 12, 0))
    _Optimizer.calls = 0
    service = FavoriteBacktestRefreshService(db_factory=refresh_db, optimizer_factory=_Optimizer)
    result = service.refresh_favorite(fid)
    assert result["status"] == REFRESH_STATUS_SUCCESS
    assert result["skipped"] == "no_new_closed_candle"
    assert _Optimizer.calls == 0
    with refresh_db() as db:
        assert db.get(FavoriteStrategy, fid).auto_refresh_status == REFRESH_STATUS_SUCCESS


def test_saturday_refresh_runs_and_ends_on_the_last_session(refresh_db, monkeypatch):
    fid = _equity_favorite(
        refresh_db,
        period_type="all",
        metrics={"operational_period_after_walk_forward": True},
    )
    _patch_equity(monkeypatch, _daily_frame("2026-10-23", 60), datetime(2026, 10, 24, 11, 12))
    _Optimizer.calls = 0
    service = FavoriteBacktestRefreshService(db_factory=refresh_db, optimizer_factory=_Optimizer)
    result = service.refresh_favorite(fid)
    assert result["status"] == REFRESH_STATUS_SUCCESS, result
    assert _Optimizer.calls == 1
    with refresh_db() as db:
        row = db.get(FavoriteStrategy, fid)
        assert row.end_date == "2026-10-23"
        assert row.metrics["analysis_last_session"] == "2026-10-23"
    assert last_closed_session_date("1d", datetime(2026, 10, 24, 11, 12)) == "2026-10-23"


def test_short_series_is_insufficient_not_failed(refresh_db, monkeypatch):
    fid = _equity_favorite(refresh_db)
    with refresh_db() as db:
        row = db.get(FavoriteStrategy, fid)
        row.parameters = {"direction": "long", "data_source": "binance_equity", "sma_long": 200}
        db.commit()
    _patch_equity(monkeypatch, _daily_frame("2026-10-23", 40), datetime(2026, 10, 24, 11, 12))
    service = FavoriteBacktestRefreshService(db_factory=refresh_db, optimizer_factory=_Optimizer)
    result = service.refresh_favorite(fid)
    assert result["status"] == REFRESH_STATUS_INSUFFICIENT
    with refresh_db() as db:
        row = db.get(FavoriteStrategy, fid)
        assert row.auto_refresh_status == REFRESH_STATUS_INSUFFICIENT
        assert row.auto_refresh_error == "40 de 201 candles"


def test_real_delay_fails_the_refresh_with_the_reason(refresh_db, monkeypatch):
    fid = _equity_favorite(refresh_db)
    _patch_equity(monkeypatch, _daily_frame("2026-10-23", 60), datetime(2026, 10, 27, 11, 5))
    service = FavoriteBacktestRefreshService(db_factory=refresh_db, optimizer_factory=_Optimizer)
    result = service.refresh_favorite(fid)
    assert result["status"] == "FAILED"
    assert "Dados atrasados" in result["error"]
