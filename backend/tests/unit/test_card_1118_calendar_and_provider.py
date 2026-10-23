"""Card #1118: calendário da NYSE, 15m derivado e adaptador Binance de ações."""

from __future__ import annotations

import collections

import httpx
import pandas as pd
import pytest

from app.services.market_history import nyse_calendar as cal
from app.services.market_history.equity_provider import (
    BinanceBusinessError,
    BinanceCircuitOpen,
    BinanceEquityProvider,
    BinanceFormatChanged,
    BinanceRateLimited,
    BinanceUnavailable,
    UnsupportedTimeframe,
    parse_page,
)


def _utc(text: str) -> pd.Timestamp:
    return pd.Timestamp(text, tz="UTC")


def _per_day(index: pd.DatetimeIndex) -> dict:
    return collections.Counter(ts.tz_convert(cal.NY).date() for ts in index)


# --- calendário --------------------------------------------------------------


def test_each_regular_session_has_78_five_minute_candles_across_both_dst_changes():
    # Virada de março (8 mar. 2026) e de novembro (1 nov. 2026).
    march = _per_day(cal.expected_5m(_utc("2026-03-04"), _utc("2026-03-13")))
    november = _per_day(cal.expected_5m(_utc("2026-10-28"), _utc("2026-11-06")))
    counts = list(march.values()) + list(november.values())
    assert counts and set(counts) == {78}
    assert len(march) == 7 and len(november) == 7  # só dias úteis


def test_half_day_and_holidays_are_not_gaps():
    days = _per_day(cal.expected_5m(_utc("2026-11-24"), _utc("2026-11-30")))
    # 26 nov. (Ação de Graças) fechado; 27 nov. fecha às 13:00 (42 candles).
    assert {d.isoformat() for d in days} == {"2026-11-24", "2026-11-25", "2026-11-27"}
    assert days[pd.Timestamp("2026-11-27").date()] == 42
    one_day = cal.expected_1d(_utc("2026-11-20"), _utc("2026-11-30"))
    stamps = {ts.tz_convert(cal.NY).date().isoformat() for ts in one_day}
    assert "2026-11-26" not in stamps and "2026-11-28" not in stamps and "2026-11-29" not in stamps


def test_regular_mask_drops_pre_post_overnight_and_closed_days():
    times = pd.DatetimeIndex(
        [
            _utc("2026-10-22 08:00"),  # pré (04:00 NY)
            _utc("2026-10-22 13:25"),  # 09:25 NY, antes da abertura
            _utc("2026-10-22 13:30"),  # 09:30 NY, abre
            _utc("2026-10-22 19:55"),  # 15:55 NY, último candle
            _utc("2026-10-22 20:00"),  # 16:00 NY, pós
            _utc("2026-10-24 15:00"),  # sábado
        ]
    )
    assert cal.regular_5m_mask(times).tolist() == [False, False, True, True, False, False]


def test_summer_and_winter_sessions_open_at_0930_new_york():
    summer = cal.session_window(pd.Timestamp("2026-07-01").date())
    winter = cal.session_window(pd.Timestamp("2026-01-05").date())
    assert summer.open_utc == _utc("2026-07-01 13:30") and winter.open_utc == _utc(
        "2026-01-05 14:30"
    )


def _five(start: str, minutes: list[int], price: float = 10.0) -> pd.DataFrame:
    base = _utc(start)
    idx = pd.DatetimeIndex([base + pd.Timedelta(minutes=m) for m in minutes], name="candle_time")
    frame = pd.DataFrame(
        {
            "open": [price + i for i in range(len(idx))],
            "high": [price + i + 2 for i in range(len(idx))],
            "low": [price + i - 2 for i in range(len(idx))],
            "close": [price + i + 1 for i in range(len(idx))],
            "volume": [1.0] * len(idx),
        },
        index=idx,
    )
    return frame


def test_fifteen_minute_candle_is_assembled_from_three_five_minute_candles():
    frame = _five("2026-10-22 13:30", [0, 5, 10])
    derived = cal.derive_15m(frame)
    assert len(derived.candles) == 1 and not derived.incomplete
    row = derived.candles.iloc[0]
    assert derived.candles.index[0] == _utc("2026-10-22 13:30")
    assert row["open"] == frame["open"].iloc[0]
    assert row["close"] == frame["close"].iloc[2]
    assert row["high"] == frame["high"].max() and row["low"] == frame["low"].min()
    assert row["volume"] == 3.0


def test_incomplete_block_is_a_gap_inherited_from_the_five_minute_series():
    # Falta o candle das 10:05 de Nova York (14:05 UTC no horário de verão).
    frame = _five("2026-10-22 13:30", [m for m in range(0, 60, 5) if m != 35])
    derived = cal.derive_15m(frame)
    assert [ts.tz_convert(cal.NY).strftime("%H:%M") for ts in derived.candles.index] == [
        "09:30",
        "09:45",
        "10:15",
    ]
    assert [(a.tz_convert(cal.NY).strftime("%H:%M"), n) for a, _, n in derived.incomplete] == [
        ("10:00", 1)
    ]


def test_fifteen_minute_blocks_do_not_cross_the_early_close():
    # Meio-pregão de 27 nov. 2026: 09:30-13:00 = 14 blocos; o 5m das 13:00 não existe.
    day = pd.Timestamp("2026-11-27").date()
    candles = cal.session_candles_5m(day)
    frame = pd.DataFrame(
        {"open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5, "volume": 1.0},
        index=pd.DatetimeIndex(candles, name="candle_time"),
    )
    derived = cal.derive_15m(frame)
    assert len(derived.candles) == 14 and not derived.incomplete
    assert derived.candles.index[-1].tz_convert(cal.NY).strftime("%H:%M") == "12:45"


def test_dst_days_keep_26_blocks_per_session():
    for day in ("2026-03-09", "2026-11-02", "2026-03-06"):
        frame = pd.DataFrame(
            {"open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5, "volume": 1.0},
            index=pd.DatetimeIndex(
                cal.session_candles_5m(pd.Timestamp(day).date()), name="candle_time"
            ),
        )
        assert len(cal.derive_15m(frame).candles) == 26


# --- validação da página -----------------------------------------------------


def _bar(t: int, *, dur: int = 300_000, o="10", h="11", l="9", c="10.5", v=100, **extra) -> dict:
    out = {"t": t, "ct": t + dur - 1, "o": o, "h": h, "l": l, "c": c, "v": v, "vw": "10.1", "n": 3}
    out.update(extra)
    return out


def _payload(bars: list[dict], code: str = "000000") -> dict:
    return {"code": code, "data": {"symbol": "NVDA", "timeframe": "5T", "bars": bars}}


def test_valid_page_is_parsed_in_order():
    bars = parse_page(_payload([_bar(0), _bar(300_000)]), timeframe="5m", end_time=None)
    assert [b.t for b in bars] == [0, 300_000]


def test_business_error_in_http_200_is_not_an_empty_page():
    with pytest.raises(BinanceBusinessError) as caught:
        parse_page({"code": "488006", "data": None}, timeframe="5m", end_time=1)
    assert caught.value.business_code == "488006"
    assert "488006" in str(caught.value)  # o texto do produto não mostra o código cru (ver API)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda b: b.pop("c"),
        lambda b: b.update(c=None),
        lambda b: b.update(c="abc"),
        lambda b: b.update(t="x"),
        lambda b: b.update(ct=b["t"] + 1),
        lambda b: b.update(o="-1"),
        lambda b: b.update(v=-5),
        lambda b: b.update(h="9.5"),  # máxima abaixo do fechamento
        lambda b: b.update(l="10.9"),  # mínima acima da abertura
    ],
)
def test_format_changes_never_become_data(mutation):
    bar = _bar(0)
    mutation(bar)
    with pytest.raises(BinanceFormatChanged):
        parse_page(_payload([bar]), timeframe="5m", end_time=None)


def test_unordered_duplicate_or_late_bars_are_rejected():
    with pytest.raises(BinanceFormatChanged):
        parse_page(_payload([_bar(300_000), _bar(0)]), timeframe="5m", end_time=None)
    with pytest.raises(BinanceFormatChanged):
        parse_page(_payload([_bar(0), _bar(0)]), timeframe="5m", end_time=None)
    with pytest.raises(BinanceFormatChanged):
        parse_page(_payload([_bar(600_000)]), timeframe="5m", end_time=300_000)


def test_data_without_bars_list_is_a_format_change():
    with pytest.raises(BinanceFormatChanged):
        parse_page({"code": "000000", "data": {"bars": None}}, timeframe="5m", end_time=None)
    with pytest.raises(BinanceFormatChanged):
        parse_page({"code": "000000"}, timeframe="5m", end_time=None)


def test_daily_candle_must_last_exactly_24_hours():
    day = 86_400_000
    ok = parse_page(_payload([_bar(0, dur=day)]), timeframe="1d", end_time=None)
    assert len(ok) == 1
    with pytest.raises(BinanceFormatChanged):
        parse_page(_payload([_bar(0, dur=day - 3_600_000)]), timeframe="1d", end_time=None)


def test_unsupported_timeframes_are_refused_before_any_request():
    with pytest.raises(UnsupportedTimeframe):
        parse_page(_payload([]), timeframe="1h", end_time=None)
    provider = BinanceEquityProvider(
        client=httpx.Client(transport=httpx.MockTransport(lambda r: 1 / 0))
    )
    with pytest.raises(UnsupportedTimeframe):
        provider.fetch_page("NVDA", "4h")


# --- HTTP, paginação, vazia confirmada e limitador ---------------------------


class _Limiter:
    def __init__(self):
        self.events: list[tuple] = []

    def acquire(self):
        self.events.append(("acquire",))

    def success(self):
        self.events.append(("success",))

    def throttled(self, retry_after, status):
        self.events.append(("throttled", retry_after, status))

    def failure(self, reason):
        self.events.append(("failure", reason))


def _provider(handler, limiter=None):
    return BinanceEquityProvider(
        limiter=limiter or _Limiter(), client=httpx.Client(transport=httpx.MockTransport(handler))
    )


def test_request_uses_the_chart_route_with_retroactive_cursor():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(dict(request.url.params))
        return httpx.Response(200, json=_payload([_bar(0), _bar(300_000)]))

    page = _provider(handler).fetch_page("nvda", "5m", end_time=999_999)
    assert page.min_t == 0 and page.max_t == 300_000
    assert seen == [
        {
            "symbol": "NVDA",
            "timeframe": "5T",
            "limit": "1000",
            "adjustmentMode": "ADJUSTED",
            "sessionMode": "REGULAR_MARKET",
            "endTime": "999999",
        }
    ]
    assert "startTime" not in seen[0]


def test_only_the_intraday_request_asks_for_the_regular_session():
    """O 1D recusa ``sessionMode`` (488009) e já é o pregão regular; o 5m pede só o regular."""

    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(dict(request.url.params))
        return httpx.Response(200, json=_payload([_bar(0, dur=86_400_000)]))

    _provider(handler).fetch_page("NVDA", "1d")
    assert "sessionMode" not in seen[0] and seen[0]["timeframe"] == "1D"


def test_empty_page_is_asked_twice_before_it_is_the_start_of_history():
    calls = []

    def handler(request):
        calls.append(1)
        return httpx.Response(200, json=_payload([]))

    page = _provider(handler).fetch_page("NVDA", "5m", end_time=1)
    assert len(calls) == 2 and page.confirmed_empty and page.requests == 2


def test_empty_then_data_is_not_the_start_of_history():
    answers = iter([_payload([]), _payload([_bar(0)])])

    def handler(request):
        return httpx.Response(200, json=next(answers))

    page = _provider(handler).fetch_page("NVDA", "5m", end_time=300_000)
    assert page.bars and not page.confirmed_empty


def test_business_error_with_http_200_raises_and_reports_to_the_limiter():
    limiter = _Limiter()
    provider = _provider(lambda r: httpx.Response(200, json={"code": "488006"}), limiter)
    with pytest.raises(BinanceBusinessError):
        provider.fetch_page("NVDA", "5m")
    assert limiter.events == [
        ("acquire",),
        ("success",),
    ]  # a Binance respondeu: não é falha de rede


def test_429_with_retry_after_is_reported_to_the_shared_limiter():
    limiter = _Limiter()
    provider = _provider(lambda r: httpx.Response(429, headers={"Retry-After": "30"}), limiter)
    with pytest.raises(BinanceRateLimited) as caught:
        provider.fetch_page("NVDA", "5m")
    assert caught.value.retry_after == 30.0
    assert ("throttled", 30.0, 429) in limiter.events


def test_418_and_5xx_and_network_errors_are_failures_that_count_toward_the_circuit():
    limiter = _Limiter()
    provider = _provider(lambda r: httpx.Response(418), limiter)
    with pytest.raises(BinanceRateLimited):
        provider.fetch_page("NVDA", "5m")
    provider = _provider(lambda r: httpx.Response(503), limiter)
    with pytest.raises(BinanceUnavailable):
        provider.fetch_page("NVDA", "5m")

    def boom(request):
        raise httpx.ConnectError("sem rede")

    with pytest.raises(BinanceUnavailable):
        _provider(boom, limiter).fetch_page("NVDA", "5m")
    assert [e for e in limiter.events if e[0] in {"throttled", "failure"}] == [
        ("throttled", None, 418),
        ("failure", "http_503"),
        ("failure", "network"),
    ]


def test_non_json_body_is_a_format_change_not_an_empty_list():
    provider = _provider(lambda r: httpx.Response(200, content=b"<html>"))
    with pytest.raises(BinanceFormatChanged):
        provider.fetch_page("NVDA", "5m")


def test_invalid_ticker_is_refused_without_a_request():
    provider = _provider(lambda r: 1 / 0)
    with pytest.raises(BinanceFormatChanged):
        provider.fetch_page("NV DA&x=1", "5m")


# --- fábrica de provedores (tarefa 2.5) -----------------------------------------------


def test_factory_registers_the_equity_adapter_without_retiring_legacy_providers():
    from app.services import market_data_providers as providers

    equity = providers.get_market_data_provider("binance_equity")
    assert isinstance(equity, providers.BinanceEquityMarketDataProvider)
    assert providers.get_market_data_provider("binance_equity") is equity  # instância única
    assert isinstance(providers.get_market_data_provider("ccxt"), providers.CcxtMarketDataProvider)
    assert isinstance(providers.get_market_data_provider("stooq"), providers.StooqEodProvider)
    # Yahoo e Alpha Vantage seguem no código (a retirada é do #1126).
    assert providers.YahooMarketDataProvider.source == "yahoo"
    assert providers.AlphaVantageMarketDataProvider.source == "alphavantage"
    # A fonte nova não vira valor aceito pelas rotas de análise antes do #1119.
    with pytest.raises(ValueError):
        providers.normalize_data_source("binance_equity")


def test_equity_market_data_provider_reads_through_the_history_service(monkeypatch):
    from app.services import market_data_providers as providers
    from app.services.market_history import facade
    from app.services.market_history.model import SeriesRef, equity_spec

    series = SeriesRef(
        series_id=1,
        asset_id="binance:equity:EQ_NVDA",
        symbol="NVDA",
        asset_class="stock",
        source="binance_equity",
        session="rth",
        adjustment="adjusted",
        timeframe="1d",
        origin="native",
        data_version=1,
        physical_timeframe="1d",
    )

    class _Service:
        def resolve(self, spec):
            assert (spec.symbol, spec.timeframe, spec.adjustment) == ("NVDA", "1d", "adjusted")
            return series

        def history(self, ref, since, until, limit=None):
            index = pd.DatetimeIndex(["2026-10-21", "2026-10-22"], tz="UTC", name="candle_time")
            frame = pd.DataFrame(
                {
                    "open": [1.0, 2.0],
                    "high": [2.0, 3.0],
                    "low": [0.5, 1.5],
                    "close": [1.5, 2.5],
                    "volume": [9.0, 8.0],
                },
                index=index,
            )

            class _Result:
                candles = frame
                coverage = {"status": "covered"}

            return _Result()

    monkeypatch.setattr(
        facade,
        "spec_for_request",
        lambda **kw: equity_spec(
            "binance:equity:EQ_NVDA", "NVDA", "stock", kw["timeframe"], kw["adjustment"]
        ),
    )
    frame = providers.BinanceEquityMarketDataProvider(service=_Service()).fetch_ohlcv("NVDA", "1d")
    assert list(frame.columns) == ["timestamp", "open", "high", "low", "close", "volume"]
    assert frame.index.name == "timestamp_utc" and len(frame) == 2
