"""1h e 4h de ação/ETF montados do 5m no pregão (card #1119, tarefas 4.1 a 4.3)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import support_card_1119 as sup
from app.services.combo_optimizer import _fast_extract_trades_from_signals
from app.services.market_history import nyse_calendar as cal
from app.services.market_history.model import ADJ_ADJUSTED, equity_spec
from app.services.market_history.service import HistoryService
from market_history_support import FakeEquityProvider, history_schema

NY = cal.NY


def _five(days: list[str], *, drop: set[str] | None = None) -> pd.DataFrame:
    """5m sintético de cada pregão (09:30 a 16:00, ou 13:00 em meio-pregão)."""

    rows = []
    for day in days:
        d = pd.Timestamp(day).date()
        for t in cal.session_candles_5m(d):
            if drop and t.strftime("%Y-%m-%dT%H:%M") in drop:
                continue
            p = 100.0 + (t.value // 10**9 % 997) / 100.0
            rows.append((t, p, p + 0.5, p - 0.5, p + 0.1, 10.0))
    frame = pd.DataFrame(rows, columns=["candle_time", "open", "high", "low", "close", "volume"])
    return frame.set_index(pd.DatetimeIndex(frame.pop("candle_time"), name="candle_time"))


def _ny(ts: pd.Timestamp) -> str:
    return ts.tz_convert(NY).strftime("%H:%M")


def _local(candles: pd.DataFrame, day: str) -> list[str]:
    idx = candles.index.tz_convert(NY)
    return [t.strftime("%H:%M") for t in idx if t.strftime("%Y-%m-%d") == day]


def test_full_session_has_seven_1h_candles_and_two_4h_candles():
    five = _five(["2026-10-21"])
    one = cal.derive_blocks(five, 60)
    four = cal.derive_blocks(five, 240)
    assert _local(one.candles, "2026-10-21") == [
        "09:30",
        "10:30",
        "11:30",
        "12:30",
        "13:30",
        "14:30",
        "15:30",
    ]
    assert _local(four.candles, "2026-10-21") == ["09:30", "13:30"]
    assert one.incomplete == [] and four.incomplete == []
    # o último 1h termina no fechamento (6 candles de 5m), o último 4h tem 30 (13:30 a 16:00)
    last_hour = five[five.index >= one.candles.index[-1]]
    assert len(last_hour) == 6
    assert len(five[five.index >= four.candles.index[-1]]) == 30


def test_1h_and_4h_aggregate_ohlcv_correctly():
    five = _five(["2026-10-21"])
    first_hour = five.iloc[:12]
    candle = cal.derive_blocks(five, 60).candles.iloc[0]
    assert candle["open"] == first_hour["open"].iloc[0]
    assert candle["close"] == first_hour["close"].iloc[-1]
    assert candle["high"] == first_hour["high"].max()
    assert candle["low"] == first_hour["low"].min()
    assert candle["volume"] == first_hour["volume"].sum()


def test_half_session_of_27_nov_2026_closes_at_13h():
    five = _five(["2026-11-27"])
    one = cal.derive_blocks(five, 60)
    four = cal.derive_blocks(five, 240)
    assert _local(one.candles, "2026-11-27") == ["09:30", "10:30", "11:30", "12:30"]
    assert _local(four.candles, "2026-11-27") == ["09:30"]
    last = five[five.index >= one.candles.index[-1]]
    assert _ny(last.index[0]) == "12:30" and _ny(last.index[-1]) == "12:55"
    assert len(five[five.index >= four.candles.index[-1]]) == 42  # 09:30 a 13:00
    assert one.incomplete == [] and four.incomplete == []


@pytest.mark.parametrize(
    "days",
    [
        ["2026-03-06", "2026-03-09"],  # virada para o horário de verão (8 mar. 2026)
        ["2026-10-30", "2026-11-02"],  # volta ao horário padrão (1 nov. 2026)
    ],
)
def test_daylight_saving_change_keeps_the_0930_anchor_without_holes(days):
    five = _five(days)
    for minutes, expected in ((60, 7), (240, 2), (15, 26)):
        derived = cal.derive_blocks(five, minutes)
        for day in days:
            local = _local(derived.candles, day)
            assert local[0] == "09:30"
            assert len(local) == expected
        assert derived.incomplete == []
    # em UTC a abertura muda uma hora, em Nova York não
    starts = [
        t.strftime("%H:%M") for t in cal.derive_blocks(five, 60).candles.index if _ny(t) == "09:30"
    ]
    assert starts[0] != starts[1]


def test_weekend_and_holiday_produce_no_candle():
    five = _five(["2026-11-25", "2026-11-27"])
    # candles soltos em feriado (Ação de Graças, 26 nov.) e fim de semana não viram nada
    stray = pd.DatetimeIndex(["2026-11-26 15:00", "2026-11-28 15:00", "2026-11-29 15:00"], tz="UTC")
    extra = pd.DataFrame(
        {"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1.0}, index=stray
    )
    extra.index.name = "candle_time"
    for minutes in (60, 240):
        derived = cal.derive_blocks(pd.concat([five, extra]), minutes)
        days = {t.tz_convert(NY).strftime("%Y-%m-%d") for t in derived.candles.index}
        assert days == {"2026-11-25", "2026-11-27"}


def test_missing_5m_inside_an_hour_is_an_inherited_gap_not_a_candle():
    five = _five(["2026-10-21"], drop={"2026-10-21T14:05"})  # 10:05 em Nova York (EDT)
    one = cal.derive_blocks(five, 60)
    four = cal.derive_blocks(five, 240)
    assert "09:30" not in _local(one.candles, "2026-10-21")
    assert len(_local(one.candles, "2026-10-21")) == 6
    assert _local(four.candles, "2026-10-21") == ["13:30"]  # o 4h da manhã também fica sem candle
    assert [(_ny(a), _ny(b)) for a, b, _ in one.incomplete] == [("09:30", "10:30")]
    assert [(_ny(a), _ny(b)) for a, b, _ in four.incomplete] == [("09:30", "13:30")]


def test_fifteen_minute_derivation_is_unchanged():
    five = _five(["2026-10-21"])
    assert len(cal.derive_blocks(five, 15).candles) == 26
    assert cal.derive_15m(five).candles.equals(cal.derive_blocks(five, 15).candles)


def test_block_size_must_be_a_multiple_of_five():
    with pytest.raises(ValueError):
        cal.derive_blocks(_five(["2026-10-21"]), 7)


# ---------------------------------------------------------------- split do NVDA (4.3)


def test_nvda_split_of_june_2024_has_no_price_jump_and_no_false_long_stop():
    frame = pd.read_csv(sup.FIXTURES / "nvda_1d_split_2024.csv", index_col=0, parse_dates=True)
    window = frame.loc["2024-06-03":"2024-06-14"]
    gaps = (window["open"] / window["close"].shift(1) - 1).abs().dropna()
    assert gaps.max() < 0.06, "série ajustada: a abertura de 10 jun. não salta 10:1"
    closes = window["close"].pct_change().abs().dropna()
    assert closes.max() < 0.06
    # posição long aberta em 6 jun. atravessa o split sem stop falso (stop 5%)
    df = frame.loc["2024-06-03":"2024-06-14"].copy()
    df["signal"] = 0
    df.iloc[1, df.columns.get_loc("signal")] = 1
    df.iloc[-1, df.columns.get_loc("signal")] = -1
    trades = _fast_extract_trades_from_signals(df, 0.05, "long", 0.0)
    assert len(trades) == 1 and trades[0]["exit_reason"] == "signal"
    split_day = df.index[df.index.strftime("%Y-%m-%d") == "2024-06-10"][0]
    assert pd.Timestamp(trades[0]["exit_time"]) > split_day


# ---------------------------------------------------------------- serviço (DB)


@pytest.fixture
def engine(unit_database_url):
    with history_schema(unit_database_url) as eng:
        yield eng


NOW = pd.Timestamp("2026-10-22 22:00", tz="UTC")


def _nvda(timeframe: str):
    return equity_spec("binance:equity:EQ_NVDA", "NVDA", "stock", timeframe, ADJ_ADJUSTED)


def _service(engine, provider) -> HistoryService:
    return HistoryService(
        engine,
        equity_provider=provider,
        clock=lambda: NOW.to_pydatetime(),
        update_ttl_seconds=0.0,
        lease_wait_seconds=0.2,
    )


def test_history_service_serves_1h_and_4h_from_the_5m_and_lists_them_as_derived(engine):
    provider = FakeEquityProvider(timeframe="5m", now=NOW)
    provider.build(pd.Timestamp("2026-10-12", tz="UTC"), NOW)
    service = _service(engine, provider)
    five = service.resolve(_nvda("5m"))
    one = service.resolve(_nvda("1h"))
    four = service.resolve(_nvda("4h"))
    assert one.is_derived and four.is_derived
    assert one.series_id == four.series_id == five.series_id
    service.ensure(one, "2026-10-12")  # coleta o 5m físico
    read_1h = service.read(one, "2026-10-13", "2026-10-13 23:59")
    read_4h = service.read(four, "2026-10-13", "2026-10-13 23:59")
    assert len(read_1h.candles) == 7 and len(read_4h.candles) == 2
    assert read_1h.coverage["origin"] == "derived" and read_1h.coverage["derived_from"] == "5m"
    assert read_4h.coverage["version_label"].endswith("+r1")
    assert read_4h.coverage["covered"]["start"] == service.read(five).coverage["covered"]["start"]
    # 1h e 4h não são gravados como série nativa
    with engine.connect() as conn:
        from sqlalchemy import text

        tfs = {r[0] for r in conn.execute(text("SELECT DISTINCT timeframe FROM market_series"))}
    assert tfs <= {"5m", "1d"}
