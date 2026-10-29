"""Card #1118: consumidores de cripto leem a autoridade única; amostra estável por execução."""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest
from sqlalchemy import text

from app.services import discovery_inputs as inputs
from app.services import ohlcv_storage
from app.services.discovery_resources import OperationalFailure
from app.services.market_history import facade, snapshots
from app.services.market_history.cache import ParquetReadCache
from app.services.market_history.model import crypto_spec
from app.services.market_history.sample import ExecutionSample
from app.services.market_history.service import HistoryService
from market_history_support import FakeCcxt, crypto_frame, history_schema
from src.data.incremental_loader import IncrementalLoader


def _ohlcv_df(frame: pd.DataFrame) -> pd.DataFrame:
    """DataFrame no formato dos provedores (timestamp_utc como coluna)."""

    out = frame.reset_index().rename(columns={"candle_time": "timestamp_utc"})
    return out


@pytest.fixture
def unified(unit_database_url, tmp_path, monkeypatch):
    """Autoridade única ligada num schema privado, CCXT simulada e cache em tmp."""

    monkeypatch.setenv("MARKET_HISTORY_UNIFIED", "1")
    monkeypatch.setenv("MARKET_HISTORY_SNAPSHOT_DIR", str(tmp_path / "snapshots"))
    with history_schema(unit_database_url) as engine:
        ccxt = FakeCcxt(
            {
                ("BTC/USDT", "1h"): crypto_frame("2026-09-01", 24 * 40, "1h", 30000.0),
                ("BTC/USDT", "4h"): crypto_frame("2026-09-01", 6 * 40, "4h", 30000.0),
                ("BTC/USDT", "1d"): crypto_frame("2025-01-01", 600, "1D", 20000.0),
                ("BTC/USDT", "15m"): crypto_frame("2026-08-01", 96 * 80, "15min", 30000.0),
            }
        )
        service = HistoryService(engine, ccxt_client=ccxt, update_ttl_seconds=0)
        cache = ParquetReadCache(tmp_path / "series")
        facade.set_history_service(service, cache)
        monkeypatch.setattr(ohlcv_storage, "engine", engine)
        import app.database as database_module

        monkeypatch.setattr(database_module, "engine", engine)
        try:
            yield service, engine, ccxt, cache
        finally:
            facade.set_history_service(None, None)
            inputs._SAMPLE_FRAMES.clear()


def _loader(tmp_path) -> IncrementalLoader:
    loader = IncrementalLoader(cache_dir=str(tmp_path / "legacy-parquet"))
    return loader


# --- 4.1 escritor canônico ------------------------------------------------------


def test_canonical_writer_records_into_binance_spot_series(unified):
    service, engine, ccxt, cache = unified
    repo = ohlcv_storage.MarketOhlcvRepository()
    frame = crypto_frame("2026-10-01", 48, "1h")
    written, dup = repo.write_candles(
        "BTC/USDT", "1h", "ccxt", _ohlcv_df(frame), return_metrics=True
    )
    assert (written, dup) == (48, 0)
    again = repo.write_candles("BTC/USDT", "1h", "ccxt", _ohlcv_df(frame), return_metrics=True)
    assert again == (0, 48)  # idempotente: nada duplica
    with engine.connect() as conn:
        series = conn.execute(
            text(
                "SELECT asset_id, source, session, adjustment, timeframe, origin FROM market_series"
            )
        ).all()
        stored = conn.execute(
            text("SELECT count(*), min(source), min(timeframe) FROM market_ohlcv")
        ).one()
    assert [tuple(s) for s in series] == [
        ("binance:spot:BTC/USDT", "binance_spot", "24x7", "na", "1h", "native")
    ]
    assert tuple(stored) == (48, "ccxt", "1h")  # coluna de compatibilidade preservada
    assert repo.get_latest_candle_time("BTC/USDT", "1h") == frame.index[-1].to_pydatetime()
    assert repo.get_earliest_candle_time("BTC/USDT", "1h") == frame.index[0].to_pydatetime()
    rows = repo.read_recent_candles("BTC/USDT", "1h", 10)
    assert [r["timestamp_utc"] for r in rows][-1] == frame.index[-1].isoformat()
    assert len(repo.read_all_candles("BTC/USDT", "1h")) == 48


def test_stooq_candles_never_mix_with_the_binance_series(unified):
    service, engine, ccxt, cache = unified
    repo = ohlcv_storage.MarketOhlcvRepository()
    repo.write_candles("AAPL", "1d", "stooq", _ohlcv_df(crypto_frame("2026-09-01", 10, "1D")))
    repo.write_candles("BTC/USDT", "1d", "ccxt", _ohlcv_df(crypto_frame("2026-09-01", 10, "1D")))
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT asset_id, source FROM market_series ORDER BY asset_id")
        ).all()
    assert [tuple(r) for r in rows] == [
        ("binance:spot:BTC/USDT", "binance_spot"),
        ("legacy:stooq:AAPL", "stooq"),
    ]


# --- 4.2 e 4.4 leitura única e paridade ------------------------------------------


@pytest.mark.parametrize("timeframe", ["1h", "4h"])
def test_chart_and_backtest_get_identical_candles_in_the_same_version(unified, tmp_path, timeframe):
    service, engine, ccxt, cache = unified
    loader = _loader(tmp_path)
    since, until = "2026-09-05", "2026-10-05"
    backtest = loader.fetch_data("BTC/USDT", timeframe, since, until)
    series = service.resolve(crypto_spec("BTC/USDT", timeframe))
    chart = ohlcv_storage.MarketOhlcvRepository().read_all_candles("BTC/USDT", timeframe)
    chart = [
        c
        for c in chart
        if pd.Timestamp(since, tz="UTC")
        <= pd.Timestamp(c["timestamp_utc"])
        <= pd.Timestamp(until, tz="UTC")
    ]
    assert len(backtest) == len(chart) > 100
    assert [pd.Timestamp(c["timestamp_utc"]) for c in chart] == list(backtest.index)
    for column in ("open", "high", "low", "close", "volume"):
        np.testing.assert_array_equal([c[column] for c in chart], backtest[column].to_numpy())
    # mesma versão para os dois
    assert service.read(series).series.data_version == 1


def test_loader_does_not_download_or_keep_its_own_parquet_when_unified(
    unified, tmp_path, monkeypatch
):
    service, engine, ccxt, cache = unified
    loader = _loader(tmp_path)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("o carregador não pode baixar da CCXT por conta própria")

    monkeypatch.setattr(loader.exchange, "fetch_ohlcv", forbidden)
    frame = loader.fetch_data("BTC/USDT", "1h", "2026-09-05", "2026-10-05")
    assert not frame.empty
    assert not list((tmp_path / "legacy-parquet").rglob("*.parquet"))  # sem cópia própria
    assert frame.index.name == "timestamp_utc" and "timestamp" in frame.columns
    # read_only nunca coleta
    calls = len(ccxt.calls)
    loader.fetch_data("BTC/USDT", "1h", "2026-09-06", "2026-09-07", read_only=True)
    assert len(ccxt.calls) == calls


def test_every_analysis_consumer_goes_through_the_history_service(unified, tmp_path, monkeypatch):
    service, engine, ccxt, cache = unified
    seen: list[tuple] = []
    original = facade.loader_frame

    def spy(symbol, timeframe, *args, **kwargs):
        seen.append((symbol, timeframe))
        return original(symbol, timeframe, *args, **kwargs)

    monkeypatch.setattr(facade, "loader_frame", spy)
    from app.services.backtest_service import BacktestService
    from app.services.combo_optimizer import ComboOptimizer, _local_ohlcv_covers
    from app.services.market_data_providers import CcxtMarketDataProvider
    from app.services.sequential_optimizer import SequentialOptimizer

    loader = _loader(tmp_path)
    backtest = BacktestService()
    backtest.loader = loader
    assert not backtest.loader.fetch_data("BTC/USDT", "1d", "2025-06-01", "2025-07-01").empty
    combo = ComboOptimizer(loader=loader)
    assert combo.loader is loader
    assert (
        not CcxtMarketDataProvider(loader)
        .fetch_ohlcv(
            symbol="BTC/USDT", timeframe="1h", since_str="2026-09-05", until_str="2026-09-10"
        )
        .empty
    )
    assert _local_ohlcv_covers(loader, "BTC/USDT", "1h", "2026-09-10")  # cópia local = autoridade
    assert not loader.fetch_intraday_data("BTC/USDT", "15m", "2026-08-10", "2026-08-12").empty
    assert loader.check_intraday_availability("BTC/USDT", "15m")["available"]

    sequential = SequentialOptimizer.__new__(SequentialOptimizer)
    import app.services.sequential_optimizer as seq_module

    monkeypatch.setattr(seq_module, "IncrementalLoader", lambda: loader)
    start, end = sequential.get_full_history_dates("BTC/USDT")
    assert start < end
    assert {tf for _, tf in seen} >= {"1d", "1h", "15m"}


def test_regression_backtest_numbers_are_identical_before_and_after_the_switch(
    unified, tmp_path, monkeypatch
):
    """4.5: o histórico existente produz os mesmos números pelo caminho antigo e pelo novo."""

    service, engine, ccxt, cache = unified
    rng = np.random.default_rng(7)
    index = pd.date_range("2025-01-01", periods=420, freq="1D", tz="UTC", name="candle_time")
    close = 20000 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, len(index))))
    frame = pd.DataFrame(
        {
            "open": close * 0.998,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": rng.uniform(100, 1000, len(index)),
        },
        index=index,
    )
    ccxt.frames[("BTC/USDT", "1d")] = frame
    # Cache Parquet antigo com os mesmos candles (o que a análise lia antes).
    legacy_loader = _loader(tmp_path)
    legacy = frame.reset_index().rename(columns={"candle_time": "timestamp_utc"})
    legacy["timestamp"] = pd.DatetimeIndex(legacy["timestamp_utc"]).as_unit("ms").asi8
    legacy.to_parquet(legacy_loader._get_parquet_path("BTC/USDT", "1d"), index=False)

    from app.services.backtest_service import BacktestService

    config = {
        "exchange": "binance",
        "symbol": "BTC/USDT",
        "timeframe": "1d",
        "since": "2025-01-01 00:00:00",
        "until": "2026-02-24 00:00:00",
        "strategies": [
            {"name": "CruzamentoMedias", "media_curta": 5, "media_longa": 30, "media_inter": 15}
        ],
        "cash": 10000,
    }

    def run(unified_flag: str, loader):
        monkeypatch.setenv("MARKET_HISTORY_UNIFIED", unified_flag)
        service_ = BacktestService()
        service_.loader = loader
        return service_.run_backtest(dict(config))

    before = run("0", legacy_loader)
    after = run("1", _loader(tmp_path))
    assert before["results"] and after["results"]
    key = next(iter(before["results"]))
    assert before["results"][key]["metrics"] == after["results"][key]["metrics"]
    assert before["results"][key]["trades"] == after["results"][key]["trades"]
    assert before["benchmark"] == after["benchmark"]
    assert [c["close"] for c in before["candles"]] == [c["close"] for c in after["candles"]]
    # O resultado novo diz de onde vieram os candles e qual amostra usou.
    assert after["snapshot_id"] and "snapshot_id" not in before
    prov = after["data_provenance"]["1d"]
    assert prov["data_source"] == "Binance Spot" and prov["session"] == "24x7"
    assert prov["adjustment"] == "na" and prov["timeframe_origin"] == "native"
    assert prov["data_version"] == 1 and prov["asset_class"] == "crypto"
    assert prov["period_covered"]["candles"] > 300


# --- 5.1 a 5.3 amostra estável ------------------------------------------------------


def _discovery_inputs():
    return dict(
        symbol="BTC/USDT",
        timeframe="1h",
        start_date="2026-09-05",
        end_date="2026-10-05",
    )


def test_cache_rebuilt_or_history_corrected_during_a_run_does_not_change_the_sample(
    unified, tmp_path, monkeypatch
):
    service, engine, ccxt, cache = unified
    manifest = inputs.prepare(_discovery_inputs())
    assert manifest["snapshot_id"] and set(manifest["files"]) == {"candles", "intraday"}
    assert not (tmp_path / "snapshots" / "inputs-x").exists()  # nada de spool inputs-*
    inputs.activate(manifest)
    try:
        before = inputs.read("candles")
        before_15m = inputs.read("intraday")
        # O cache Parquet é apagado e a Binance corrige um candle no meio da varredura.
        shutil.rmtree(cache.root, ignore_errors=True)
        inputs._SAMPLE_FRAMES.clear()
        corrected = ccxt.frames[("BTC/USDT", "1h")].copy()
        corrected.loc["2026-09-20 12:00", "close"] += 50  # dentro da janela da varredura
        ccxt.frames[("BTC/USDT", "1h")] = corrected
        service.ensure(service.resolve(crypto_spec("BTC/USDT", "1h")), force_update=True)
        live = _loader(tmp_path).fetch_data("BTC/USDT", "1h", "2026-09-05", "2026-10-05")
        assert live["close"].sum() != before["close"].sum()  # a consulta seguinte usa a versão nova
        pd.testing.assert_frame_equal(inputs.read("candles"), before, check_exact=True)
        pd.testing.assert_frame_equal(inputs.read("intraday"), before_15m, check_exact=True)
        assert inputs.FrozenProvider().fetch_ohlcv().equals(before)
        # Nova tentativa: o mesmo manifesto, sem pedir nada a provedor.
        monkeypatch.setattr(
            "app.services.market_data_providers.CcxtMarketDataProvider.fetch_ohlcv",
            lambda *a, **k: (_ for _ in ()).throw(AssertionError("retry não pergunta ao provedor")),
        )
        assert inputs.prepare({"candle_manifest": manifest}) == manifest
    finally:
        os.environ.pop(inputs.SNAPSHOT_ID_ENV, None)
        os.environ.pop(inputs.SNAPSHOT_SEGMENTS_ENV, None)


def test_tampered_segment_is_detected_by_sha256(unified, tmp_path):
    manifest = inputs.prepare(_discovery_inputs())
    segment = manifest["files"]["candles"]["segments"][0]["sha256"]
    path = snapshots.segment_path(snapshots.snapshot_root(), segment)
    path.write_bytes(b"corrompido")
    with pytest.raises(OperationalFailure, match="frozen_input_corrupt"):
        inputs.prepare({"candle_manifest": manifest})
    path.unlink()
    with pytest.raises(OperationalFailure, match="frozen_input_invalid"):
        inputs.prepare({"candle_manifest": manifest})


def test_discard_releases_the_reference_without_deleting_bytes(unified, tmp_path):
    service, engine, ccxt, cache = unified
    manifest = inputs.prepare(_discovery_inputs())
    files_before = sorted(p.name for p in (tmp_path / "snapshots" / "segments").rglob("*.parquet"))
    inputs.discard(manifest)
    assert (
        sorted(p.name for p in (tmp_path / "snapshots" / "segments").rglob("*.parquet"))
        == files_before
    )
    row = snapshots.get_manifest(engine, manifest["snapshot_id"])
    assert row["finished_at"] is not None
    assert row["retain_until"] - row["finished_at"] >= timedelta(days=29, hours=23)


def test_segments_are_stored_once_and_shared_between_executions(unified, tmp_path):
    service, engine, ccxt, cache = unified
    first = inputs.prepare(_discovery_inputs())
    second = inputs.prepare(_discovery_inputs())
    assert first["snapshot_id"] != second["snapshot_id"]
    shas_a = [s["sha256"] for s in first["files"]["candles"]["segments"]]
    shas_b = [s["sha256"] for s in second["files"]["candles"]["segments"]]
    assert shas_a == shas_b  # mesmos bytes -> mesmo SHA-256
    files = list((tmp_path / "snapshots" / "segments").rglob("*.parquet"))
    assert len(files) == len({f.stem for f in files})
    candles = {s["sha256"] for s in first["files"]["candles"]["segments"]}
    intraday = {s["sha256"] for s in first["files"]["intraday"]["segments"]}
    assert len(files) == len(candles | intraday)  # nada gravado em duplicidade
    # Mês corrente muda; meses fechados seguem iguais depois de mais um candle.
    ccxt = unified[2]
    ccxt.frames[("BTC/USDT", "1h")] = crypto_frame("2026-09-01", 24 * 40 + 6, "1h", 30000.0)
    service.ensure(service.resolve(crypto_spec("BTC/USDT", "1h")), force_update=True)
    third = inputs.prepare(_discovery_inputs())
    shas_c = [s["sha256"] for s in third["files"]["candles"]["segments"]]
    assert shas_c[0] == shas_a[0]  # setembro já fechado


def test_sample_provenance_comes_from_the_series(unified):
    manifest = inputs.prepare(_discovery_inputs())
    assert manifest["provenance"] == {
        "data_source": "Binance Spot",
        "asset_class": "crypto",
        "session": "24x7",
        "adjustment": "na",
        "timeframe_origin": "native",
        "period_requested": {"start": "2026-09-05T00:00:00Z", "end": "2026-10-05T00:00:00Z"},
        "period_covered": manifest["provenance"]["period_covered"],
        "data_version": 1,
        "version_label": "1",
        "snapshot_id": manifest["snapshot_id"],
        "content_sha256": manifest["files"]["candles"]["sha256"],
    }
    assert manifest["provenance"]["period_covered"]["candles"] > 600


def test_backtest_run_reads_only_its_frozen_sample(unified, tmp_path):
    service, engine, ccxt, cache = unified
    from app.services.backtest_service import BacktestService

    backtest = BacktestService()
    backtest.loader = _loader(tmp_path)
    sample = ExecutionSample("backtest")
    token = BacktestService._SAMPLE.set(sample)
    try:
        first = backtest._fetch("BTC/USDT", "1h", "2026-09-05", "2026-10-05")
        shutil.rmtree(cache.root, ignore_errors=True)
        corrected = ccxt.frames[("BTC/USDT", "1h")].copy()
        corrected.loc["2026-09-21 12:00", "close"] += 77
        ccxt.frames[("BTC/USDT", "1h")] = corrected
        service.ensure(service.resolve(crypto_spec("BTC/USDT", "1h")), force_update=True)
        second = backtest._fetch("BTC/USDT", "1h", "2026-09-05", "2026-10-05")
        pd.testing.assert_frame_equal(first, second, check_exact=True)
    finally:
        BacktestService._SAMPLE.reset(token)
    fresh = backtest._fetch("BTC/USDT", "1h", "2026-09-05", "2026-10-05")
    assert fresh["close"].sum() != first["close"].sum()


def test_optimizer_freezes_candles_and_intraday_at_the_start(unified, tmp_path, monkeypatch):
    service, engine, ccxt, cache = unified
    from app.services.combo_optimizer import ACTIVE_SAMPLE_ID, ComboOptimizer

    loader = _loader(tmp_path)
    optimizer = ComboOptimizer(loader=loader)
    optimizer._sample = None
    df = loader.fetch_data("BTC/USDT", "1h", "2026-09-05", "2026-10-05")
    frozen = optimizer._begin_sample("ccxt", "BTC/USDT", "1h", "2026-09-05", "2026-10-05", df)
    assert optimizer._sample is not None and optimizer._sample.snapshot_id
    pd.testing.assert_frame_equal(frozen, df, check_exact=True)
    loader.fetch_intraday_data("BTC/USDT", "15m", "2026-08-10", "2026-08-20")  # etapa de preparo
    optimizer._freeze_intraday("BTC/USDT", "2026-08-10", "2026-08-20")
    sample = optimizer._sample
    assert sample.has("candles") and sample.has("intraday")
    assert ACTIVE_SAMPLE_ID.get() == sample.snapshot_id
    # Os workers recebem o id e leem só do manifesto.
    from app.services.combo_optimizer import _worker_get_15m_cache

    worker_frame = _worker_get_15m_cache(
        "BTC/USDT", "2026-08-10", "2026-08-20", None, sample.snapshot_id
    )
    pd.testing.assert_frame_equal(worker_frame, sample.frame("intraday"), check_exact=True)
    assert optimizer._batch_worker().keywords["sample_id"] == sample.snapshot_id
    ACTIVE_SAMPLE_ID.set(None)


def test_multi_strategy_optimization_freezes_the_period_the_path_asks_for(
    unified, tmp_path, monkeypatch
):
    """Com a flag ligada, o wrapper não congela outro período que o multi-estratégia pede.

    A referência é o pedido cru ao carregador (o que a flag desligada devolve), sem rede.
    """

    from app.services.backtest_service import BacktestService

    config = {
        "exchange": "binance",
        "symbol": "BTC/USDT",
        "timeframe": "1d",
        "since": "2025-06-01",
        "full_period": True,
        "mode": "optimize",
        "strategies": ["CruzamentoMedias", "EmaRsiVolume"],
    }
    requested = _loader(tmp_path).fetch_data("BTC/USDT", "1d", "2025-06-01", None)
    service_ = BacktestService()
    service_.loader = _loader(tmp_path)
    monkeypatch.setattr(
        service_, "_run_single_strategy_optimization", lambda *a, **k: {"error": "stub"}
    )
    result = service_.run_backtest(dict(config))
    assert len(requested) > 0
    assert result["dataset"]["candle_count"] == len(requested)
    assert result["dataset"]["since"] == "2025-06-01"
