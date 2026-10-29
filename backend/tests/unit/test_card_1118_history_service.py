"""Card #1118: HistoryService (cobertura, coleta que retoma, versão, limites)."""

from __future__ import annotations

import threading

import pandas as pd
import pytest
from sqlalchemy import text

from app.services.market_history import nyse_calendar as cal
from app.services.market_history import store
from app.services.market_history.equity_provider import (
    BinanceBusinessError,
    BinanceFormatChanged,
    BinanceRateLimited,
    BinanceUnavailable,
)
from app.services.market_history.model import (
    ADJ_ADJUSTED,
    ADJ_RAW,
    crypto_spec,
    equity_spec,
    legacy_spec,
)
from app.services.market_history.rate_limit import CollectionLease, PostgresRateLimiter
from app.services.market_history.service import HistoryService
from market_history_support import (
    FakeCcxt,
    FakeEquityProvider,
    crypto_frame,
    history_schema,
)

NOW = pd.Timestamp("2026-10-23 01:30", tz="UTC")  # sexta, depois do pregão de quinta


@pytest.fixture
def engine(unit_database_url):
    with history_schema(unit_database_url) as eng:
        yield eng


def _service(engine, provider=None, ccxt=None, **kwargs) -> HistoryService:
    return HistoryService(
        engine,
        equity_provider=provider,
        ccxt_client=ccxt,
        clock=lambda: NOW.to_pydatetime(),
        update_ttl_seconds=kwargs.pop("update_ttl_seconds", 0.0),
        lease_wait_seconds=kwargs.pop("lease_wait_seconds", 0.2),
        **kwargs,
    )


def _nvda(timeframe: str, adjustment: str = ADJ_ADJUSTED):
    return equity_spec("binance:equity:EQ_NVDA", "NVDA", "stock", timeframe, adjustment)


def _daily_provider(start="2023-01-02", **kwargs) -> FakeEquityProvider:
    provider = FakeEquityProvider(timeframe="1d", now=NOW, **kwargs)
    provider.build(pd.Timestamp(start, tz="UTC"), NOW)
    return provider


def _five_provider(start="2026-10-12", **kwargs) -> FakeEquityProvider:
    provider = FakeEquityProvider(timeframe="5m", now=NOW, **kwargs)
    provider.build(pd.Timestamp(start, tz="UTC"), NOW)
    return provider


# --- identidade --------------------------------------------------------------


def test_adjusted_and_raw_are_different_series_and_never_mix(engine):
    service = _service(engine, _daily_provider(page_size=300))
    adjusted = service.resolve(_nvda("1d"))
    raw = service.resolve(_nvda("1d", ADJ_RAW))
    assert adjusted.series_id != raw.series_id
    service.ensure(adjusted)
    assert not service.read(raw).candles.shape[0]
    assert service.read(adjusted).candles.shape[0] > 0
    assert service.read(raw).coverage["status"] == "empty"


def test_legacy_provider_candles_do_not_enter_the_binance_series(engine):
    service = _service(engine)
    binance = service.resolve(crypto_spec("BTC/USDT", "1d"))
    legacy = service.resolve(legacy_spec("BTC/USDT", "1d", "yahoo"))
    assert binance.series_id != legacy.series_id and binance.source != legacy.source


# --- coleta de ação/ETF ------------------------------------------------------


def test_daily_history_crosses_pages_without_duplicates_and_reports_coverage(engine):
    provider = _daily_provider(page_size=400)
    service = _service(engine, provider)
    series = service.resolve(_nvda("1d"))
    outcome = service.ensure(series, "2023-01-02")
    assert outcome.status == "ok"
    result = service.read(series, "2023-01-02")
    expected = len(provider.bars)  # todo pregão fechado no período
    # O candle de hoje (ct no futuro) não entra; só candles fechados.
    assert 0 < len(result.candles) <= expected
    assert result.candles.index.is_unique and result.candles.index.is_monotonic_increasing
    cov = result.coverage
    assert cov["status"] == "covered" and cov["gap_count"] == 0 and cov["gaps"] == []
    assert cov["covered"]["start"].startswith("2023-01-03")
    assert cov["requested"]["start"] == "2023-01-02T00:00:00Z"
    assert cov["origin"] == "native" and cov["note"].startswith("Binance Ações")


def test_binance_starting_after_the_request_is_insufficient_not_complete(engine):
    provider = _daily_provider(
        start="2019-01-02", history_start=pd.Timestamp("2024-01-11", tz="UTC")
    )
    service = _service(engine, provider)
    series = service.resolve(_nvda("1d"))
    service.ensure(series, "2019-01-02")
    cov = service.read(series, "2019-01-02").coverage
    assert cov["insufficient"] is True and cov["status"] == "partial"
    assert cov["requested"]["start"].startswith("2019-01-02")
    assert cov["covered"]["start"].startswith("2024-01-1")
    assert cov["history_starts_at"].startswith("2024-01-1")


def test_collection_resumes_from_the_cursor_after_a_failure(engine):
    provider = _daily_provider(start="2020-01-02", page_size=300)
    service = _service(engine, provider)
    series = service.resolve(_nvda("1d"))
    provider.fail_with = BinanceRateLimited(429, 30)
    provider.fail_after = 2  # a latest page e mais uma página; a terceira falha
    first = service.ensure(series, "2020-01-02")
    assert first.status == "failed" and first.error_code == "binance_rate_limited"
    partial = service.read(series, "2020-01-02")
    assert (
        partial.coverage["status"] == "failed"
        and partial.coverage["error"]["code"] == "binance_rate_limited"
    )
    kept = len(partial.candles)
    assert kept > 0  # as páginas boas ficaram gravadas
    assert partial.coverage["covered"]["start"] > "2020-01-03"  # nunca "completo"

    with engine.connect() as conn:
        cursor = store.get_fetch(conn, series.series_id)["cursor_end_ms"]
    provider.fail_with = None
    provider.requests.clear()
    second = service.ensure(series, "2020-01-02")
    assert second.status == "ok"
    # A primeira requisição depois da latest page parte do cursor guardado.
    assert provider.requests[1]["end"] == cursor
    final = service.read(series, "2020-01-02")
    assert final.candles.index.is_unique
    assert len(final.candles) > kept and final.coverage["status"] == "covered"
    with engine.connect() as conn:
        assert store.stored_extent(conn, series.series_id)[2] == len(final.candles)


def test_repeating_the_same_query_only_checks_the_latest_page(engine):
    provider = _daily_provider(page_size=300)
    service = _service(engine, provider)
    series = service.resolve(_nvda("1d"))
    service.ensure(series, "2023-01-02")
    provider.requests.clear()
    again = service.ensure(series, "2023-01-02")
    assert again.status == "ok"
    assert len(provider.requests) == 1 and provider.requests[0]["end"] is None


def test_ttl_skips_even_the_latest_page_check(engine):
    provider = _daily_provider(page_size=300)
    service = _service(engine, provider, update_ttl_seconds=3600)
    series = service.resolve(_nvda("1d"))
    service.ensure(series, "2023-01-02")
    provider.requests.clear()
    service.ensure(series, "2023-01-02")
    assert provider.requests == []


def test_new_candle_is_fetched_without_old_pages(engine):
    provider = _daily_provider(page_size=300)
    service = _service(engine, provider)
    series = service.resolve(_nvda("1d"))
    service.ensure(series, "2023-01-02")
    before = len(service.read(series).candles)
    # Passa um pregão: a Binance ganha um candle fechado.
    provider.now = NOW + pd.Timedelta(days=2)
    provider.build(pd.Timestamp("2023-01-02", tz="UTC"), NOW + pd.Timedelta(days=3))
    later = HistoryService(
        engine,
        equity_provider=provider,
        clock=lambda: (NOW + pd.Timedelta(days=3)).to_pydatetime(),
        update_ttl_seconds=0,
    )
    provider.requests.clear()
    later.ensure(series, "2023-01-02")
    assert len(later.read(series).candles) > before
    assert len(provider.requests) == 1  # a página mais recente já alcança o que existia


def test_five_minute_series_keeps_only_regular_session_and_78_per_day(engine):
    provider = _five_provider()
    service = _service(engine, provider)
    series = service.resolve(_nvda("5m"))
    service.ensure(series, "2026-10-12")
    candles = service.read(series, "2026-10-12").candles
    per_day = pd.Series(candles.index.tz_convert(cal.NY).date).value_counts()
    assert set(per_day.values) == {78}
    local = candles.index.tz_convert(cal.NY)
    assert local.min().strftime("%H:%M") == "09:30" and local[-1].strftime("%H:%M") == "15:55"
    assert not ((local.hour == 16) | (local.hour < 9)).any()


def test_partial_candle_in_progress_is_not_stored(engine):
    provider = _five_provider()
    service = HistoryService(
        engine,
        equity_provider=provider,
        clock=lambda: pd.Timestamp("2026-10-22 15:32", tz="UTC").to_pydatetime(),  # 11:32 NY
        update_ttl_seconds=0,
    )
    provider.now = pd.Timestamp("2026-10-22 15:32", tz="UTC")
    series = service.resolve(_nvda("5m"))
    service.ensure(series, "2026-10-21")
    last = service.read(series).candles.index.max()
    assert last == pd.Timestamp("2026-10-22 15:25", tz="UTC")  # o candle das 15:30 ainda abre


def test_missing_candle_inside_session_is_a_gap_and_closed_market_is_not(engine):
    gap_time = pd.Timestamp("2026-10-14 14:05", tz="America/New_York").tz_convert("UTC")
    provider = _five_provider(drop={int(gap_time.timestamp() * 1000)})
    service = _service(engine, provider)
    series = service.resolve(_nvda("5m"))
    service.ensure(series, "2026-10-12")
    cov = service.read(series, "2026-10-12").coverage
    assert cov["gap_count"] == 1 and len(cov["gaps"]) == 1
    gap = cov["gaps"][0]
    assert gap["start"] == gap_time.strftime("%Y-%m-%dT%H:%M:%SZ") and gap["count"] == 1
    # O fim de semana de 17-18 out. não virou lacuna.
    assert all(not g["start"].startswith(("2026-10-17", "2026-10-18")) for g in cov["gaps"])


def test_derived_fifteen_minute_shows_the_gap_as_inherited_and_not_counted_twice(engine):
    gap_time = pd.Timestamp("2026-10-14 10:05", tz="America/New_York").tz_convert("UTC")
    provider = _five_provider(drop={int(gap_time.timestamp() * 1000)})
    service = _service(engine, provider)
    five = service.resolve(_nvda("5m"))
    fifteen = service.resolve(_nvda("15m"))
    assert fifteen.is_derived and fifteen.series_id == five.series_id
    service.ensure(five, "2026-10-12")
    result = service.read(fifteen, "2026-10-12")
    cov = result.coverage
    assert cov["origin"] == "derived" and cov["derived_from"] == "5m"
    assert cov["gap_count"] == 0  # não soma de novo no resumo
    assert len(cov["gaps"]) == 1 and cov["gaps"][0]["inherited_from"] == "5m"
    assert cov["gaps"][0]["start"] == pd.Timestamp(
        "2026-10-14 10:00", tz="America/New_York"
    ).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    # O bloco incompleto não virou candle de 15m; os demais sim (26 por pregão).
    per_day = pd.Series(result.candles.index.tz_convert(cal.NY).date).value_counts()
    assert per_day[pd.Timestamp("2026-10-14").date()] == 25
    assert per_day[pd.Timestamp("2026-10-13").date()] == 26
    assert cov["version_label"].endswith("+r1")
    assert service.read(five, "2026-10-12").coverage["gap_count"] == 1


def test_split_in_history_creates_a_new_version_without_a_price_jump(engine):
    before_split = pd.Timestamp("2025-06-09 12:00", tz="UTC")
    clock = {"now": before_split}
    provider = FakeEquityProvider(
        timeframe="1d", now=before_split, page_size=300, price=lambda ts: 1200.0
    )
    provider.build(pd.Timestamp("2024-01-02", tz="UTC"), before_split)
    service = HistoryService(
        engine,
        equity_provider=provider,
        clock=lambda: clock["now"].to_pydatetime(),
        update_ttl_seconds=0,
    )
    series = service.resolve(_nvda("1d"))
    service.ensure(series, "2024-01-02")
    assert service.read(series).series.data_version == 1

    # Split 10:1 em 10 jun. 2025: a Binance passa a devolver o histórico ajustado.
    clock["now"] = NOW
    provider.now = NOW
    provider.price = lambda ts: 120.0
    provider.build(pd.Timestamp("2024-01-02", tz="UTC"), NOW)
    outcome = service.ensure(series, "2024-01-02")
    assert outcome.version_changed
    after = service.read(series, "2024-01-02")
    assert after.series.data_version == 2 and after.coverage["data_version"] == 2
    window = after.candles.loc["2025-06-01":"2025-06-20", "close"]
    assert len(window) > 5 and window.max() / window.min() < 1.01  # sem salto falso
    assert after.candles["close"].max() / after.candles["close"].min() < 1.01
    assert after.candles.index.is_unique
    # Nova consulta, sem mudança na Binance: a versão não anda.
    service.ensure(series, "2024-01-02")
    assert service.read(series).series.data_version == 2


def test_reader_in_transaction_sees_one_whole_version(engine):
    provider = _daily_provider(page_size=300)
    service = _service(engine, provider)
    series = service.resolve(_nvda("1d"))
    service.ensure(series, "2023-01-02")
    with engine.connect() as reader:
        reader.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        before = store.read_frame(reader, series.series_id)
        provider.price = lambda ts: 5.0
        provider.build(pd.Timestamp("2023-01-02", tz="UTC"), NOW)
        service.ensure(series, "2023-01-02")  # troca a versão em outra transação
        during = store.read_frame(reader, series.series_id)
    assert before.equals(during)  # o leitor não vê a troca no meio
    assert service.read(series).candles["close"].iloc[0] != before["close"].iloc[0]


def test_failure_modes_surface_as_coverage_not_as_empty_lists(engine):
    for error, code in (
        (BinanceBusinessError("488006"), "binance_business_error"),
        (BinanceUnavailable("HTTP 503"), "binance_unavailable"),
        (BinanceFormatChanged("campo c ausente"), "binance_format_changed"),
    ):
        provider = _daily_provider(page_size=300)
        service = _service(engine, provider)
        series = service.resolve(_nvda("1d"))
        provider.fail_with = error
        outcome = service.ensure(series, "2023-01-02")
        cov = service.read(series, "2023-01-02").coverage
        assert outcome.status == "failed" and outcome.error_code == code
        assert cov["status"] == "failed" and cov["error"]["code"] == code
        assert cov["covered"]["start"] is None and cov["covered"]["candles"] == 0
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM market_series_fetch"))
            conn.execute(text("DELETE FROM market_series_coverage"))
            conn.execute(text("DELETE FROM market_series"))


def test_invalid_page_writes_nothing(engine):
    provider = _daily_provider(page_size=300)
    provider.fail_with = BinanceFormatChanged("OHLC incoerente")
    service = _service(engine, provider)
    series = service.resolve(_nvda("1d"))
    service.ensure(series, "2023-01-02")
    with engine.connect() as conn:
        assert store.stored_extent(conn, series.series_id)[2] == 0


def test_timeframes_outside_the_equity_set_are_refused(engine):
    from app.services.market_history.model import SeriesNotSupported

    service = _service(engine)
    # 1h e 4h entraram no #1119 (montados do 5m); 30m e 1m seguem fora para ação/ETF.
    for refused in ("1m", "30m"):
        with pytest.raises(SeriesNotSupported):
            service.resolve(_nvda(refused))
    assert service.resolve(_nvda("1h")).is_derived


# --- travas e limitador ------------------------------------------------------


def test_second_worker_for_the_same_series_waits_and_does_not_collect(engine):
    service = _service(engine, _daily_provider(page_size=300), lease_wait_seconds=0.3)
    series = service.resolve(_nvda("1d"))
    with CollectionLease(engine, series.series_id, wait_seconds=0.1) as holder:
        assert holder.acquired
        outcome = service.ensure(series, "2023-01-02")
        assert outcome.status == "waiting"
        # Quem espera lê o que já está gravado e recebe a cobertura atual.
        assert service.read(series).coverage["status"] == "empty"
    again = service.ensure(series, "2023-01-02")
    assert again.status == "ok"


def test_at_most_two_series_collect_at_once(engine):
    held = [CollectionLease(engine, 100 + n, wait_seconds=0.1) for n in range(2)]
    for lease in held:
        lease.__enter__()
        assert lease.acquired
    third = CollectionLease(engine, 102, wait_seconds=0.2)
    with third:
        assert not third.acquired
    held[0].__exit__(None, None, None)
    fourth = CollectionLease(engine, 102, wait_seconds=0.2)
    with fourth:
        assert fourth.acquired
    held[1].__exit__(None, None, None)


class _Clock:
    def __init__(self, t=1000.0):
        self.t = t
        self.sleeps = []

    def now(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s


def test_token_bucket_spaces_requests_to_two_per_second_across_instances(engine):
    clock = _Clock()
    a = PostgresRateLimiter(engine, clock=clock.now, sleep=clock.sleep)
    b = PostgresRateLimiter(engine, clock=clock.now, sleep=clock.sleep)  # outro worker
    stamps = []
    for limiter in (a, b, a, b, a, b):
        limiter.acquire()
        stamps.append(clock.t)
    gaps = [round(y - x, 3) for x, y in zip(stamps, stamps[1:])]
    assert all(g >= 0.5 for g in gaps), gaps
    assert (stamps[-1] - stamps[0]) / (len(stamps) - 1) <= 0.6


def test_retry_after_blocks_every_worker_for_the_stated_time(engine):
    clock = _Clock()
    a = PostgresRateLimiter(engine, clock=clock.now, sleep=clock.sleep)
    b = PostgresRateLimiter(engine, clock=clock.now, sleep=clock.sleep)
    a.acquire()
    a.throttled(30, 429)
    with pytest.raises(BinanceRateLimited) as caught:
        b.acquire()
    assert 29 <= caught.value.retry_after <= 30
    clock.t += 31
    b.acquire()  # passou o tempo: sai


def test_three_failures_in_a_row_open_the_circuit_for_five_minutes(engine):
    from app.services.market_history.equity_provider import BinanceCircuitOpen

    clock = _Clock()
    limiter = PostgresRateLimiter(engine, clock=clock.now, sleep=clock.sleep)
    limiter.failure("http_503")
    limiter.failure("http_500")
    limiter.acquire()  # ainda fechado com 2 falhas
    limiter.failure("network")
    with pytest.raises(BinanceCircuitOpen) as caught:
        limiter.acquire()
    assert 299 <= caught.value.until_epoch - clock.t <= 300
    clock.t += 301
    limiter.acquire()
    limiter.success()


def test_success_resets_the_failure_count(engine):
    clock = _Clock()
    limiter = PostgresRateLimiter(engine, clock=clock.now, sleep=clock.sleep)
    limiter.failure("http_503")
    limiter.failure("http_503")
    limiter.success()
    limiter.failure("http_503")
    limiter.failure("http_503")
    limiter.acquire()  # 2 falhas depois do reset: circuito continua fechado


# --- cripto ------------------------------------------------------------------


def test_crypto_series_collects_tail_head_and_counts_gaps(engine):
    frame = crypto_frame("2026-10-01", 24 * 20, "1h")
    frame = frame.drop(frame.index[100:103])  # buraco de 3 candles
    ccxt = FakeCcxt({("BTC/USDT", "1h"): frame})
    service = _service(engine, ccxt=ccxt)
    series = service.resolve(crypto_spec("BTC/USDT", "1h"))
    service.ensure(series, "2026-10-05", full_history_if_empty=False)
    first = service.read(series)
    assert first.coverage["covered"]["start"].startswith("2026-10-05")
    # A cauda é puxada de novo e a cabeça antes do início guardado.
    service.ensure(series, "2026-10-02")
    result = service.read(series, "2026-10-02")
    assert result.coverage["covered"]["start"].startswith("2026-10-02")
    assert result.coverage["gap_count"] == 1 and result.coverage["gaps"][0]["count"] == 3
    assert result.candles.index.is_unique
    assert result.coverage["note"] == "Binance Spot · 24/7 · ajuste não se aplica"


def test_crypto_failure_is_reported_and_keeps_stored_candles(engine):
    ccxt = FakeCcxt({("ETH/USDT", "1d"): crypto_frame("2026-01-01", 200, "1D")})
    service = _service(engine, ccxt=ccxt)
    series = service.resolve(crypto_spec("ETH/USDT", "1d"))
    service.ensure(series, "2026-01-01")
    stored = len(service.read(series).candles)
    ccxt.fail = True
    outcome = service.ensure(series, "2026-01-01", force_update=True)
    assert outcome.status == "failed" and outcome.error_code == "binance_unavailable"
    cov = service.read(series).coverage
    assert cov["status"] == "failed" and len(service.read(series).candles) == stored


def test_crypto_correction_of_an_old_candle_creates_a_new_version(engine):
    frame = crypto_frame("2026-10-01", 24 * 10, "1h")
    ccxt = FakeCcxt({("BTC/USDT", "1h"): frame})
    service = _service(engine, ccxt=ccxt)
    series = service.resolve(crypto_spec("BTC/USDT", "1h"))
    service.ensure(series, "2026-10-01")
    assert service.read(series).series.data_version == 1
    corrected = frame.copy()
    corrected.iloc[-2, corrected.columns.get_loc("close")] += 5  # penúltimo candle corrigido
    ccxt.frames[("BTC/USDT", "1h")] = corrected
    service.ensure(series, "2026-10-01", force_update=True)
    assert service.read(series).series.data_version == 2


def test_crypto_last_candle_refresh_is_not_a_new_version(engine):
    frame = crypto_frame("2026-10-01", 24 * 10, "1h")
    ccxt = FakeCcxt({("BTC/USDT", "1h"): frame})
    service = _service(engine, ccxt=ccxt)
    series = service.resolve(crypto_spec("BTC/USDT", "1h"))
    service.ensure(series, "2026-10-01")
    final = frame.copy()
    final.iloc[-1, final.columns.get_loc("close")] += 1  # candle em andamento fechou
    ccxt.frames[("BTC/USDT", "1h")] = final
    service.ensure(series, "2026-10-01", force_update=True)
    assert service.read(series).series.data_version == 1
    assert service.read(series).candles["close"].iloc[-1] == pytest.approx(final["close"].iloc[-1])
