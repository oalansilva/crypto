"""Card #1123: cálculo da comparação com referência (função pura, sem banco nem rede)."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from app.services import benchmark_comparison as bench

HOLIDAYS = {(1, 1), (12, 25), (7, 4)}


def crypto_frame(start: str, end: str, base: float = 100.0, step: float = 1.0) -> pd.DataFrame:
    index = pd.date_range(start, end, freq="D", tz="UTC")
    closes = [base + step * i for i in range(len(index))]
    return pd.DataFrame(
        {"open": closes, "high": closes, "low": closes, "close": closes, "volume": 1.0}, index=index
    )


def equity_frame(start: str, end: str, base: float = 50.0, step: float = 0.1) -> pd.DataFrame:
    days = [d for d in pd.bdate_range(start, end) if (d.month, d.day) not in HOLIDAYS]
    index = pd.DatetimeIndex(days).tz_localize("America/New_York").tz_convert("UTC")
    closes = [base + step * i for i in range(len(index))]
    return pd.DataFrame(
        {"open": closes, "high": closes, "low": closes, "close": closes, "volume": 1.0}, index=index
    )


def trade(entry: str, exit_: str, profit: float) -> dict:
    return {
        "entry_time": f"{entry}T00:00:00Z",
        "exit_time": f"{exit_}T00:00:00Z",
        "exit_price": 1.0,
        "profit": profit,
    }


BTC_TRADES = [
    trade("2019-02-01", "2019-06-01", 0.50),
    trade("2019-09-01", "2020-01-10", -0.10),
    trade("2020-03-01", "2020-07-01", 0.80),  # os três primeiros ficam antes de SOL existir
    trade("2020-09-01", "2021-04-01", 1.20),
    trade("2021-10-01", "2022-01-05", -0.05),
    trade("2022-03-01", "2022-08-01", 0.10),
    trade("2023-01-10", "2023-07-01", 0.60),
    trade("2023-10-01", "2024-03-01", 0.90),
    trade("2024-09-01", "2024-12-20", 0.30),
]

BTC = {
    "symbol": "BTC/USDT",
    "asset_class": "crypto",
    "currency": "USDT",
    "asset_id": "binance:spot:BTC/USDT",
    "name": "BTC",
}
SPY = {
    "symbol": "SPY",
    "asset_class": "etf",
    "currency": "USD",
    "asset_id": "binance:equity:SPY",
    "name": "SPDR S&P 500",
}
NVDA = {
    "symbol": "NVDA",
    "asset_class": "stock",
    "currency": "USD",
    "asset_id": "binance:equity:NVDA",
    "name": "NVIDIA",
}


def btc_strategy(trades=BTC_TRADES, direction="long") -> bench.StrategySide:
    return bench.strategy_side(
        symbol="BTC/USDT",
        asset=BTC,
        window={"start": "2019-01-01T00:00:00+00:00", "end": "2024-12-31T00:00:00+00:00"},
        trades=trades,
        direction=direction,
    )


def compound(trades) -> float:
    equity = 1.0
    for t in trades:
        equity *= 1.0 + t["profit"]
    return equity - 1.0


def run(strategy, reference, frame, kind="catalog"):
    closes = bench.daily_closes(frame, reference["asset_class"])
    return bench.compute(strategy, {**reference, "kind": kind}, closes)


def test_btc_against_spy_leaves_out_the_new_york_holiday_with_zero_trades():
    out = run(btc_strategy(), SPY, equity_frame("2003-01-02", "2026-10-27"))
    assert out["status"] == "valid"
    assert out["common_window"] == {"start": "2019-01-02", "end": "2024-12-31", "days": 2190}
    assert out["left_out"] == [
        {"start": "2019-01-01", "end": "2019-01-01", "trades": 0, "note": "no_session"}
    ]
    assert out["strategy"]["trades_out"] == 0
    assert out["strategy"]["return"] == pytest.approx(compound(BTC_TRADES))
    assert out["currency_note"] == "usdt_as_usd"
    assert out["reference"]["return_kind"] == "price_no_dividends"
    assert out["reference"]["long_only"] is True
    ref = out["reference_result"]
    assert ref["first_close"]["date"] == "2019-01-02"
    assert ref["return"] == pytest.approx(
        ref["last_close"]["price"] / ref["first_close"]["price"] - 1
    )
    expected = (1 + out["strategy"]["return"]) ** (365.25 / 2190) - 1
    assert out["strategy"]["cagr"] == pytest.approx(expected)
    assert out["delta"]["cagr_pp"] == pytest.approx((out["strategy"]["cagr"] - ref["cagr"]) * 100)


def test_btc_against_sol_counts_the_three_trades_left_out():
    out = run(
        btc_strategy(),
        {**BTC, "symbol": "SOL/USDT", "asset_id": "binance:spot:SOL/USDT"},
        crypto_frame("2020-08-11", "2026-10-27"),
    )
    assert out["common_window"]["start"] == "2020-08-11"
    assert out["strategy"]["trades_out"] == 3
    assert out["strategy"]["trades_in"] == 6
    assert out["left_out"][0] == {
        "start": "2019-01-01",
        "end": "2020-08-10",
        "trades": 3,
        "note": "no_reference",
    }
    assert out["strategy"]["return"] == pytest.approx(compound(BTC_TRADES[3:]))
    assert out["strategy"]["return"] != pytest.approx(compound(BTC_TRADES))
    assert out["currency_note"] is None
    assert out["reference"]["return_kind"] == "price"


def test_nvda_against_spy_has_no_currency_warning():
    nvda = bench.strategy_side(
        symbol="NVDA",
        asset=NVDA,
        window={"start": "2019-01-02T05:00:00+00:00", "end": "2024-12-31T05:00:00+00:00"},
        trades=[trade("2019-03-01", "2019-09-03", 0.4)],
    )
    out = run(nvda, SPY, equity_frame("2003-01-02", "2026-10-27"))
    assert out["status"] == "valid"
    assert out["currency_note"] is None
    assert out["common_window"]["start"] == "2019-01-02"
    assert out["left_out"] == []


def test_etf_against_its_own_asset_is_price_return_and_covers_the_window():
    spy = bench.strategy_side(
        symbol="SPY",
        asset=SPY,
        window={"start": "2019-01-02T05:00:00+00:00", "end": "2024-12-31T05:00:00+00:00"},
        trades=[trade("2019-03-01", "2019-09-03", 0.1), trade("2020-05-01", "2021-01-04", 0.2)],
    )
    out = run(spy, SPY, equity_frame("2003-01-02", "2026-10-27"), kind="own")
    assert out["reference"]["kind"] == "own"
    assert out["reference"]["return_kind"] == "price_no_dividends"
    assert out["left_out"] == []
    assert out["strategy"]["return"] == pytest.approx(compound(spy.trades))


def test_own_asset_over_the_whole_window_equals_the_total_return():
    out = run(btc_strategy(), BTC, crypto_frame("2017-08-17", "2026-10-27"), kind="own")
    assert out["common_window"] == {"start": "2019-01-01", "end": "2024-12-31", "days": 2191}
    assert out["left_out"] == []
    # Igual ao "Retorno total" da tela: composto dos trades fechados.
    assert out["strategy"]["return"] == compound(BTC_TRADES)


def test_crcl_without_overlap_has_reason_and_no_number():
    crcl = {
        "symbol": "CRCL",
        "asset_class": "stock",
        "currency": "USD",
        "asset_id": "x",
        "name": "Circle",
    }
    out = run(btc_strategy(), crcl, equity_frame("2025-06-05", "2026-10-27"))
    assert out["status"] == "insufficient"
    assert out["reason"]["code"] == "no_overlap"
    assert out["reason"]["text"] == (
        "CRCL tem histórico desde 05/06/2025, depois do fim da estratégia (31/12/2024). Não há período comum."
    )
    assert out["reason"]["short"] == "Sem período comum com CRCL."
    assert out["strategy"]["return"] is None and out["strategy"]["cagr"] is None
    assert out["reference_result"] is None and out["delta"] is None
    assert out["common_window"] is None


def test_short_overlap_below_thirty_days():
    pengu = {**BTC, "symbol": "PENGU/USDT", "asset_id": "binance:spot:PENGU/USDT"}
    out = run(btc_strategy(), pengu, crypto_frame("2024-12-17", "2026-10-27"))
    assert out["status"] == "insufficient"
    assert out["reason"]["code"] == "short_overlap"
    assert out["reason"]["short"] == "Período comum de 14 dias: o mínimo é 30."
    assert out["reason"]["text"] == (
        "Período comum de 14 dias: o mínimo é 30. PENGU/USDT tem histórico desde 17/12/2024 e a "
        "estratégia termina em 31/12/2024."
    )
    assert out["common_window"]["days"] == 14
    assert out["delta"] is None and out["strategy"]["return"] is None


def test_exactly_thirty_days_is_enough():
    pengu = {**BTC, "symbol": "PENGU/USDT"}
    out = run(btc_strategy(trades=[]), pengu, crypto_frame("2024-12-01", "2026-10-27"))
    assert out["common_window"]["days"] == 30
    assert out["status"] == "valid"
    assert (
        out["strategy"]["return"] == 0.0
    )  # sem trades no período: retorno 0 é dado, não "sem comparação"


def test_no_history_after_collection():
    out = run(btc_strategy(), SPY, pd.DataFrame())
    assert out["reason"]["code"] == "no_history"
    assert out["status"] == "insufficient"


def test_short_strategy_keeps_a_long_only_reference():
    out = run(
        btc_strategy(direction="short"), BTC, crypto_frame("2017-08-17", "2026-10-27"), kind="own"
    )
    assert out["strategy"]["direction"] == "short"
    assert out["reference"]["long_only"] is True
    assert out["reference_result"]["return"] > 0  # comprada, mesmo com a estratégia vendida


def test_window_without_record_is_deduced_from_requested_period():
    side = bench.strategy_side(
        symbol="BTC/USDT",
        asset=None,
        window=None,
        requested={"start": "2023-01-01", "end": "2025-10-31"},
        trades=[],
    )
    assert side.window_state == "deduzido"
    assert side.window_start == date(2023, 1, 1)
    assert side.asset_class == "crypto" and side.currency == "USDT"


def test_trade_crossing_the_common_start_is_left_out():
    trades = [trade("2020-08-01", "2020-09-01", 0.5), trade("2020-10-01", "2020-11-01", 0.2)]
    out = run(
        btc_strategy(trades=trades),
        {**BTC, "symbol": "SOL/USDT"},
        crypto_frame("2020-08-11", "2026-10-27"),
    )
    assert out["strategy"]["trades_out"] == 1
    assert out["strategy"]["return"] == pytest.approx(0.2)


def test_currency_note_only_when_currencies_differ():
    assert bench.currency_note_of("USDT", "USD") == "usdt_as_usd"
    assert bench.currency_note_of("USD", "USDT") == "usdt_as_usd"
    assert bench.currency_note_of("USD", "USD") is None


def test_expired_candidate_sample_has_no_number():
    payload = bench.expired_sample_payload(
        btc_strategy(), {**SPY, "kind": "catalog"}, "2026-09-30T00:00:00Z"
    )
    assert payload["status"] == "insufficient"
    assert payload["reason"]["code"] == bench.SAMPLE_EXPIRED
    assert payload["reason"]["short"] == "Amostra do candidato vencida em 30/09/2026."
    assert payload["delta"] is None


def test_contract_refuses_numbers_in_an_insufficient_comparison():
    from app.schemas.benchmark import BenchmarkComparisonContract

    crcl = {
        "symbol": "CRCL",
        "asset_class": "stock",
        "currency": "USD",
        "asset_id": "x",
        "name": "C",
    }
    out = run(btc_strategy(), crcl, equity_frame("2025-06-05", "2026-10-27"))
    body = {
        **out,
        "id": "c1",
        "created_at": "2026-10-27T12:00:00Z",
        "trigger": "choice",
        "owner": {"kind": "result"},
    }
    BenchmarkComparisonContract.check(body)
    with pytest.raises(ValueError):
        BenchmarkComparisonContract.check({**body, "delta": {"cagr_pp": 0.0}})
    valid = run(btc_strategy(), SPY, equity_frame("2003-01-02", "2026-10-27"))
    BenchmarkComparisonContract.check({**body, **valid})
