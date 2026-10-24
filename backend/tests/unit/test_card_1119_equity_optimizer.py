"""Otimização de 1 ação pelo otimizador real (card #1119, tarefas 3.3, 5.3 e 5.6).

Ação/ETF lê o 15m montado do 5m pelo ``HistoryService`` (sem CCXT), congela a amostra da execução e devolve
identidade, precisão efetiva e convenções.
"""

from __future__ import annotations

import pandas as pd
import pytest

from app.metrics.backtest_execution_costs import long_trade_profit_frac
from app.services.combo_optimizer import ComboOptimizer
from app.services.equity_backtest import prepare_equity_history
from app.services.market_data_providers import BinanceEquityMarketDataProvider
from app.services.market_history import facade
from app.services.market_history.cache import ParquetReadCache
from app.services.market_history.service import HistoryService
from market_history_support import FakeEquityProvider, history_schema
from oracles._build_card_945 import load_templates, metadata_from_export
from test_card_1118_api_and_catalog import _seed_catalog, public_db  # noqa: F401
from test_card_1118_optimizer_regression import _FakeTemplates, _fixed_ranges
from test_card_1119_equity_backtest_api import RoutedProvider

pytestmark = pytest.mark.timeout(600)

NOW = pd.Timestamp("2026-10-23 01:30", tz="UTC")


@pytest.fixture
def equity_env(public_db, unit_database_url, tmp_path, monkeypatch):  # noqa: F811
    _seed_catalog(public_db)
    monkeypatch.setenv("MARKET_HISTORY_SNAPSHOT_DIR", str(tmp_path / "snapshots"))
    with history_schema(unit_database_url) as engine:
        daily = FakeEquityProvider(timeframe="1d", now=NOW, page_size=400)
        daily.build(pd.Timestamp("2025-06-02", tz="UTC"), NOW)
        five = FakeEquityProvider(timeframe="5m", now=NOW, page_size=1000)
        five.build(pd.Timestamp("2026-01-02", tz="UTC"), NOW)
        provider = RoutedProvider({"1d": daily, "5m": five})
        service = HistoryService(
            engine,
            equity_provider=provider,
            clock=lambda: NOW.to_pydatetime(),
            update_ttl_seconds=0,
            lease_wait_seconds=0.2,
        )
        facade.set_history_service(service, ParquetReadCache(tmp_path / "series"))
        yield service, provider
        facade.set_history_service(None, None)


def _optimize(symbol, start, end, timeframe="1d", deep=True):
    prep = prepare_equity_history(symbol, timeframe, start, end, intrabar=deep)
    optimizer = ComboOptimizer(workers=1)
    optimizer.combo_service = _FakeTemplates()
    optimizer._provider = BinanceEquityMarketDataProvider(ensure=False)
    optimizer.collection_note = prep.collection
    result = optimizer.run_optimization(
        template_name="multi_ma_crossover",
        symbol=symbol,
        timeframe=timeframe,
        data_source="binance_equity",
        start_date=start,
        end_date=end,
        custom_ranges=_fixed_ranges(),
        deep_backtest=deep,
    )
    return result


def test_nvda_optimization_with_5m_covering_the_window_runs_intrabar(equity_env):
    result = _optimize("NVDA", "2026-02-02", "2026-10-20")
    assert result["asset"]["asset_class"] == "stock" and result["asset"]["currency"] == "USD"
    execution = result["execution"]
    assert execution["precision_requested"] == "intrabar"
    assert execution["precision_effective"] == "intrabar_15m", execution
    assert execution["intraday_missing"] == [] and execution["intraday_reason"] is None
    assert result["execution_mode"] == "deep_15m"
    prov = result["data_provenance"]
    assert prov["data_source"] == "Binance Ações" and prov["session"] == "rth"
    assert prov["adjustment"] == "adjusted" and prov["snapshot_id"] == result["snapshot_id"]
    assert prov["kept_until"] > prov["period_covered"]["end"]
    conv = result["conventions"]
    assert conv["fee"] == pytest.approx(0.001) and conv["fee_confirmed"] is True
    assert "periods_per_year" not in conv
    assert conv["fraction"]["confirms_account"] is False
    assert execution["window"]["covered"]["candles"] > 100
    # cada saída com gap carrega o stop e a abertura
    for trade in result["trades"]:
        if trade["exit_reason"] == "stop_loss_gap":
            assert trade["signal_type"] == "Stop com gap" and trade["stop_price"] > 0
    assert execution["gap_stops"] == sum(
        1 for t in result["trades"] if t["exit_reason"] == "stop_loss_gap"
    )
    # a taxa de ação/ETF (0,10% por lado) é a que entra no lucro de cada trade da otimização
    longs = [t for t in result["trades"] if t.get("type", "long") == "long"]
    assert longs
    for trade in longs:
        expected = long_trade_profit_frac(
            trade["entry_price"], trade["exit_price"], fee=0.001, slippage=conv["slippage"]
        )
        assert trade["profit"] == pytest.approx(expected)


def test_nvda_all_history_falls_back_to_daily_precision_with_the_missing_stretch(equity_env):
    # o 15m (5m) só existe desde 2 jan. 2026; a janela começa em out. 2025
    result = _optimize("NVDA", "2025-10-01", "2026-10-20")
    execution = result["execution"]
    assert execution["precision_requested"] == "intrabar"
    assert execution["precision_effective"] == "candle"
    assert execution["intraday_reason"] == "coverage"
    stretch = execution["intraday_missing"][0]
    assert stretch["from"] == "2025-10-01" and stretch["to"] <= "2026-01-02"
    assert result["execution_mode"] == "fast_1d"
    assert execution["timeframe"] == "1d"


def test_spy_1h_optimization_reads_the_derived_candles_inside_the_session(equity_env):
    result = _optimize("SPY", "2026-09-01", "2026-10-20", timeframe="1h")
    assert result["asset"]["asset_class"] == "etf"
    assert "periods_per_year" not in result["conventions"]
    assert result["conventions"]["slippage"] == pytest.approx(0.0003)
    candles = pd.DatetimeIndex([c["timestamp_utc"] for c in result["candles"]])
    local = candles.tz_convert("America/New_York") if candles.tz is not None else candles
    assert local.hour.min() == 9 and local.minute[local.hour == 9].min() == 30
    assert local.hour.max() <= 15  # o último 1h do pregão começa às 15:30
    assert result["execution"]["precision_effective"] == "intrabar_15m"
