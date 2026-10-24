"""Gap no stop (card #1119, tarefas 2.1 a 2.4): uma regra, todos os caminhos de saída."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

import support_card_1119 as sup
from app.metrics.backtest_execution_costs import (
    EQUITY_FEE,
    TRADING_FEE,
    fee_for_class,
    fee_for_symbol,
    long_trade_profit_frac,
    short_trade_profit_frac,
)
from app.services import deep_backtest as deep
from app.services.combo_optimizer import (
    _fast_extract_trades_from_signals,
    _legacy_extract_trades_from_signals,
)

DAILY = [
    pytest.param(_legacy_extract_trades_from_signals, id="legacy"),
    pytest.param(_fast_extract_trades_from_signals, id="fast"),
]
DEEP = [
    pytest.param(deep._legacy_simulate_execution_with_15m, id="legacy"),
    pytest.param(deep._fast_simulate_execution_with_15m, id="fast"),
    pytest.param(deep._compiled_simulate_execution_with_15m, id="compiled"),
]


def _daily(rows, signals, start="2026-01-05", freq="D"):
    idx = pd.date_range(start, periods=len(rows), freq=freq, tz="UTC")
    frame = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)
    frame["volume"] = 1.0
    frame["signal"] = signals
    return frame


# ---------------------------------------------------------------- 2.1 / 2.3 diário


@pytest.mark.parametrize("extract", DAILY)
def test_gap_long_exits_at_open_not_at_stop(extract):
    # entrada a 100, stop 5% = 95; o candle seguinte abre em 90
    df = _daily(
        [(100, 101, 99, 100), (90, 92, 88, 91), (91, 92, 90, 91)],
        [1, 0, 0],
    )
    trades = extract(df, 0.05, "long", 0.0)
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_price"] == 90.0
    assert t["exit_reason"] == "stop_loss_gap"
    assert t["signal_type"] == "Stop com gap"
    assert t["stop_price"] == pytest.approx(95.0)
    assert t["gap_pct"] == pytest.approx(5 / 95)
    assert t["profit"] == pytest.approx(long_trade_profit_frac(100, 90))


@pytest.mark.parametrize("extract", DAILY)
def test_gap_short_exits_at_open_not_at_stop(extract):
    # entrada a 100, stop 5% = 105; o candle seguinte abre em 110
    df = _daily(
        [(100, 101, 99, 100), (110, 112, 109, 111), (111, 112, 110, 111)],
        [1, 0, 0],
    )
    trades = extract(df, 0.05, "short", 0.0)
    assert len(trades) == 1
    t = trades[0]
    assert t["type"] == "short"
    assert t["exit_price"] == 110.0
    assert t["exit_reason"] == "stop_loss_gap"
    assert t["stop_price"] == pytest.approx(105.0)
    assert t["profit"] == pytest.approx(short_trade_profit_frac(100, 110))


@pytest.mark.parametrize("extract", DAILY)
def test_touch_without_gap_is_as_before(extract):
    # abre em 97 (acima do stop 95) e a mínima 94 toca o stop
    df = _daily([(100, 101, 99, 100), (97, 98, 94, 96), (96, 97, 95, 96)], [1, 0, 0])
    t = extract(df, 0.05, "long", 0.0)[0]
    assert t["exit_price"] == pytest.approx(95.0)
    assert t["exit_reason"] == "stop_loss"
    assert t["signal_type"] == "Stop"
    assert "stop_price" not in t and "gap_pct" not in t


@pytest.mark.parametrize("extract", DAILY)
def test_open_exactly_at_stop_is_a_gap_exit_at_that_price(extract):
    df = _daily([(100, 101, 99, 100), (95, 96, 94, 95), (95, 96, 94, 95)], [1, 0, 0])
    t = extract(df, 0.05, "long", 0.0)[0]
    assert t["exit_price"] == pytest.approx(95.0)
    assert t["exit_reason"] == "stop_loss_gap"


@pytest.mark.parametrize("extract", DAILY)
def test_resumption_after_weekend_uses_the_open_of_the_first_session(extract):
    # sexta 2026-01-09 fecha acima do stop; segunda 2026-01-12 abre abaixo dele
    idx = pd.DatetimeIndex(["2026-01-08", "2026-01-09", "2026-01-12", "2026-01-13"], tz="UTC")
    df = pd.DataFrame(
        {
            "open": [100.0, 99.0, 90.0, 91.0],
            "high": [101.0, 100.0, 92.0, 92.0],
            "low": [99.0, 98.0, 88.0, 90.0],
            "close": [100.0, 99.0, 91.0, 91.0],
            "volume": 1.0,
            "signal": [1, 0, 0, 0],
        },
        index=idx,
    )
    t = extract(df, 0.05, "long", 0.0)[0]
    assert t["exit_time"].startswith("2026-01-12")
    assert t["exit_price"] == 90.0
    assert t["exit_reason"] == "stop_loss_gap"


@pytest.mark.parametrize("extract", DAILY)
def test_gap_exit_pays_fee_and_slippage(extract):
    df = _daily([(100, 101, 99, 100), (90, 92, 88, 91), (91, 92, 90, 91)], [1, 0, 0])
    slip = 0.0003
    t = extract(df, 0.05, "long", slip)[0]
    assert t["profit"] == pytest.approx(long_trade_profit_frac(100, 90, slippage=slip))
    assert t["profit"] < long_trade_profit_frac(100, 95, slippage=slip)


@pytest.mark.parametrize("extract", DAILY)
def test_switch_off_restores_exit_at_stop_price(extract, monkeypatch):
    monkeypatch.setenv("STOP_GAP_EXIT", "0")
    df = _daily([(100, 101, 99, 100), (90, 92, 88, 91), (91, 92, 90, 91)], [1, 0, 0])
    t = extract(df, 0.05, "long", 0.0)[0]
    assert t["exit_price"] == pytest.approx(95.0)
    assert t["exit_reason"] == "stop_loss"


# ---------------------------------------------------------------- custo por classe (tarefa 1.1 / 5.4)


def test_fee_by_class_is_confirmed_and_applied_per_symbol():
    assert fee_for_class("crypto") == (TRADING_FEE, True)
    assert fee_for_class("stock") == (EQUITY_FEE, True)
    assert fee_for_class("etf") == (EQUITY_FEE, True)
    assert EQUITY_FEE == pytest.approx(0.001) and TRADING_FEE == pytest.approx(0.00075)
    assert fee_for_symbol("BTC/USDT") == TRADING_FEE
    assert fee_for_symbol("NVDA") == EQUITY_FEE


@pytest.mark.parametrize("extract", DAILY)
def test_equity_fee_reaches_the_daily_exit_and_crypto_default_is_unchanged(extract):
    df = _daily([(100, 101, 99, 100), (90, 92, 88, 91), (91, 92, 90, 91)], [1, 0, 0])
    default = extract(df, 0.05, "long", 0.0)[0]["profit"]
    equity = extract(df, 0.05, "long", 0.0, EQUITY_FEE)[0]["profit"]
    assert default == pytest.approx(long_trade_profit_frac(100, 90))
    assert equity == pytest.approx(long_trade_profit_frac(100, 90, fee=EQUITY_FEE))
    assert equity < default


# ---------------------------------------------------------------- 2.2 / 2.3 15m


def _intraday(day, rows):
    idx = pd.date_range(f"{day} 00:00", periods=len(rows), freq="15min", tz="UTC")
    frame = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)
    frame["volume"] = 1.0
    return frame


@pytest.mark.parametrize("simulate", DEEP)
def test_gap_inside_a_15m_candle_long(simulate):
    daily = _daily([(100, 101, 90, 91), (91, 92, 90, 91), (91, 92, 90, 91)], [1, 0, 0])
    intra = _intraday(
        "2026-01-05",
        [(100, 100.5, 99.5, 100), (100, 100.2, 96, 97), (97, 97.5, 96.5, 97), (92, 93, 90, 91)],
    )
    # stop 95: o 15m das 00:45 abre em 92 (já abaixo) e a mínima anterior (96) não tocou
    trades = simulate(daily, intra, 0.05, "long", 0.0)
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_price"] == 92.0
    assert t["exit_reason"] == "stop_loss_gap"
    assert t["signal_type"] == "Stop com gap"
    assert t["stop_price"] == pytest.approx(95.0)
    assert t["exit_time"].startswith("2026-01-05T00:45")
    assert t["profit"] == pytest.approx(long_trade_profit_frac(100, 92))


@pytest.mark.parametrize("simulate", DEEP)
def test_equity_fee_reaches_the_15m_exit(simulate):
    daily = _daily([(100, 101, 90, 91), (91, 92, 90, 91), (91, 92, 90, 91)], [1, 0, 0])
    intra = _intraday(
        "2026-01-05",
        [(100, 100.5, 99.5, 100), (100, 100.2, 96, 97), (97, 97.5, 96.5, 97), (92, 93, 90, 91)],
    )
    trade = simulate(daily, intra, 0.05, "long", 0.0, EQUITY_FEE)[0]
    assert trade["profit"] == pytest.approx(long_trade_profit_frac(100, 92, fee=EQUITY_FEE))


@pytest.mark.parametrize("simulate", DEEP)
def test_gap_inside_a_15m_candle_short(simulate):
    daily = _daily([(100, 112, 99, 111), (111, 112, 110, 111), (111, 112, 110, 111)], [1, 0, 0])
    intra = _intraday(
        "2026-01-05",
        [(100, 100.5, 99.5, 100), (100, 104, 99.8, 103), (108, 110, 107, 109)],
    )
    t = simulate(daily, intra, 0.05, "short", 0.0)[0]
    assert t["exit_price"] == 108.0
    assert t["exit_reason"] == "stop_loss_gap"
    assert t["stop_price"] == pytest.approx(105.0)


@pytest.mark.parametrize("simulate", DEEP)
def test_15m_touch_without_gap_exits_at_stop(simulate):
    daily = _daily([(100, 101, 94, 96), (96, 97, 95, 96), (96, 97, 95, 96)], [1, 0, 0])
    intra = _intraday(
        "2026-01-05",
        [(100, 100.5, 99.5, 100), (99.5, 99.8, 94.5, 96), (96, 97, 95.5, 96)],
    )
    t = simulate(daily, intra, 0.05, "long", 0.0)[0]
    assert t["exit_price"] == pytest.approx(95.0)
    assert t["exit_reason"] == "stop_loss_15m"
    assert t["signal_type"] == "Stop"
    assert "stop_price" not in t


@pytest.mark.parametrize("simulate", DEEP)
def test_15m_resumption_after_closed_market(simulate):
    # posição de sexta sai na primeira barra de segunda (sem barras no fim de semana)
    d_idx = pd.DatetimeIndex(["2026-01-09", "2026-01-12", "2026-01-13"], tz="UTC")
    daily = pd.DataFrame(
        {
            "open": [100.0, 90.0, 90.0],
            "high": [101.0, 91.0, 91.0],
            "low": [99.0, 88.0, 89.0],
            "close": [100.0, 89.0, 90.0],
            "volume": 1.0,
            "signal": [1, 0, 0],
        },
        index=d_idx,
    )
    fri = _intraday("2026-01-09", [(100, 100.5, 99.5, 100), (100, 100.5, 99.5, 99.5)])
    mon = _intraday("2026-01-12", [(90, 91, 88, 89), (89, 90, 88.5, 89)])
    intra = pd.concat([fri, mon])
    t = simulate(daily, intra, 0.05, "long", 0.0)[0]
    assert t["exit_price"] == 90.0
    assert t["exit_time"].startswith("2026-01-12T00:00")
    assert t["exit_reason"] == "stop_loss_gap"


def test_15m_variants_agree_with_gap():
    daily = _daily([(100, 101, 90, 91), (91, 92, 90, 91), (91, 92, 90, 91)], [1, 0, 0])
    intra = _intraday(
        "2026-01-05",
        [(100, 100.5, 99.5, 100), (100, 100.2, 96, 97), (92, 93, 90, 91)],
    )
    results = [
        fn(daily, intra, 0.05, "long", 0.0003)
        for fn in (
            deep._legacy_simulate_execution_with_15m,
            deep._fast_simulate_execution_with_15m,
            deep._compiled_simulate_execution_with_15m,
        )
    ]
    assert results[0] == results[1] == results[2]


# ---------------------------------------------------------------- 2.4 regressão cripto


def _is_gap(trade: dict) -> bool:
    return trade.get("exit_reason") == "stop_loss_gap"


@pytest.fixture(scope="module")
def before():
    return json.loads(sup.GOLDEN_BEFORE.read_text())


@pytest.mark.parametrize("case", sup.all_cases(), ids=lambda c: "|".join(map(str, c)))
def test_switch_off_reproduces_the_routine_recorded_before_the_card(case, before, monkeypatch):
    monkeypatch.setenv("STOP_GAP_EXIT", "0")
    got = sup.jsonable(
        sup.run_case(
            case, _fast_extract_trades_from_signals, deep._fast_simulate_execution_with_15m
        )
    )
    assert got == before[sup.case_id(*case)]


@pytest.mark.parametrize("case", sup.all_cases(), ids=lambda c: "|".join(map(str, c)))
def test_crypto_regression_only_gap_trades_differ(case, before):
    got = sup.jsonable(
        sup.run_case(
            case, _fast_extract_trades_from_signals, deep._fast_simulate_execution_with_15m
        )
    )
    old = before[sup.case_id(*case)]
    assert len(got) == len(old)
    for new_trade, old_trade in zip(got, old):
        if _is_gap(new_trade):
            assert new_trade["entry_time"] == old_trade["entry_time"]
            continue
        assert new_trade == old_trade  # sem gap, idêntico campo a campo


@pytest.mark.parametrize("kind", ["daily", "deep"])
def test_crypto_regression_all_implementations_agree(kind):
    case = (kind, "4h", 0.015, "long")
    legacy = sup.run_case(
        case, _legacy_extract_trades_from_signals, deep._legacy_simulate_execution_with_15m
    )
    fast = sup.run_case(
        case, _fast_extract_trades_from_signals, deep._fast_simulate_execution_with_15m
    )
    compiled = sup.run_case(
        case, _fast_extract_trades_from_signals, deep._compiled_simulate_execution_with_15m
    )
    assert sup.jsonable(legacy) == sup.jsonable(fast) == sup.jsonable(compiled)


def test_injected_gap_changes_only_that_trade(before):
    """Abertura rebaixada num candle de stop: a diferença é exatamente um trade, com gap."""

    case = ("daily", "1d", 0.03, "long")
    old = before[sup.case_id(*case)]
    stops = [t for t in old if t["exit_reason"] == "stop_loss"]
    assert stops, "a amostra precisa ter ao menos um stop para o teste"
    target = stops[0]
    df = sup.with_signals(sup.load("1d"), "long")
    when = pd.Timestamp(target["exit_time"])
    stop_price = target["exit_price"]
    df.loc[when, "open"] = stop_price * 0.97
    df.loc[when, "low"] = min(df.loc[when, "low"], df.loc[when, "open"])
    df.loc[when, "high"] = max(df.loc[when, "high"], df.loc[when, "open"])
    new = sup.jsonable(_fast_extract_trades_from_signals(df, 0.03, "long", sup.SLIPPAGE["1d"]))
    diffs = [(n, o) for n, o in zip(new, old) if n != o]
    assert len(new) >= 1 and len(diffs) >= 1
    first_new, first_old = diffs[0]
    assert first_new["exit_reason"] == "stop_loss_gap"
    assert first_new["exit_price"] == pytest.approx(stop_price * 0.97)
    assert first_new["profit"] < first_old["profit"]
