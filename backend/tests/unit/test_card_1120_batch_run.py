"""Lote multiclasse pelo executor real (card #1120, tarefas 3.1 a 3.6).

BTC/USDT (Binance Spot simulada), NVDA e SPY (Binance Ações simulada) passam pelo mesmo
``BatchRunner``, com o ``ComboOptimizer`` real e um template fixo (``multi_ma_crossover``).
"""

from __future__ import annotations

import pandas as pd
import pytest
from sqlalchemy.orm import sessionmaker

from app.models import FavoriteStrategy
from app.services import batch_backtest_service as service
from app.services.batch_backtest_plan import build_plan
from app.services.batch_backtest_store import get_batch_backtest_store
from app.services.combo_optimizer import ComboOptimizer
from app.services.market_history import facade
from app.services.market_history.cache import ParquetReadCache
from app.services.market_history.model import crypto_spec
from app.services.market_history.service import HistoryService
from market_history_support import FakeCcxt, FakeEquityProvider, crypto_frame, history_schema
from test_card_1118_api_and_catalog import _seed_catalog, public_db  # noqa: F401
from test_card_1118_optimizer_regression import _FakeTemplates, _fixed_ranges, _walk
from test_card_1119_equity_backtest_api import RoutedProvider

pytestmark = pytest.mark.timeout(900)

NOW = pd.Timestamp("2026-10-23 01:30", tz="UTC")
START, END = "2026-02-02", "2026-10-20"
USER = "user-1"


class CountingCcxt(FakeCcxt):
    pass


def _crypto_frames() -> dict[tuple[str, str], pd.DataFrame]:
    daily = pd.date_range("2025-06-01", "2026-10-23", freq="1D", tz="UTC")
    intraday = pd.date_range("2026-01-20", "2026-10-23", freq="15min", tz="UTC")
    five = pd.date_range("2026-09-20", "2026-10-23", freq="5min", tz="UTC")
    return {
        ("BTC/USDT", "1d"): _walk(daily, 21, 60000.0, 0.02),
        ("BTC/USDT", "15m"): _walk(intraday, 22, 60000.0, 0.003),
        ("BTC/USDT", "5m"): _walk(five, 23, 60000.0, 0.001),
    }


@pytest.fixture
def batch_env(public_db, unit_database_url, tmp_path, monkeypatch):  # noqa: F811
    _seed_catalog(public_db)
    monkeypatch.setenv("MARKET_HISTORY_SNAPSHOT_DIR", str(tmp_path / "snapshots"))
    templates = _FakeTemplates()
    monkeypatch.setattr(
        "app.services.combo_service.ComboService.get_template_metadata",
        lambda self, name: templates.metadata,
    )
    with history_schema(unit_database_url) as engine:
        daily = FakeEquityProvider(timeframe="1d", now=NOW, page_size=400)
        daily.build(pd.Timestamp("2025-06-02", tz="UTC"), NOW)
        five = FakeEquityProvider(timeframe="5m", now=NOW, page_size=1000)
        five.build(pd.Timestamp("2026-01-02", tz="UTC"), NOW)
        provider = RoutedProvider({"1d": daily, "5m": five})
        ccxt = CountingCcxt(_crypto_frames())
        history = HistoryService(
            engine,
            equity_provider=provider,
            ccxt_client=ccxt,
            clock=lambda: NOW.to_pydatetime(),
            update_ttl_seconds=0,
            lease_wait_seconds=0.2,
        )
        facade.set_history_service(history, ParquetReadCache(tmp_path / "series"))
        # 15m de BTC/USDT já guardado (a cripto lê o intradiário sem coletar)
        history.ensure(history.resolve(crypto_spec("BTC/USDT", "15m")), "2026-01-20", None)
        get_batch_backtest_store.cache_clear()
        yield {
            "history": history,
            "provider": provider,
            "ccxt": ccxt,
            "db": public_db,
            "Session": sessionmaker(bind=public_db),
        }
        facade.set_history_service(None, None)
        get_batch_backtest_store.cache_clear()


def _optimizer() -> ComboOptimizer:
    optimizer = ComboOptimizer(workers=1)
    optimizer.combo_service = _FakeTemplates()
    return optimizer


def _payload(symbols, timeframe="1d", **extra):
    base = {
        "template_name": "multi_ma_crossover",
        "symbols": symbols,
        "timeframe": timeframe,
        "data_source": None,
        "start_date": START,
        "end_date": END,
        "period_type": None,
        "deep_backtest": True,
        "custom_ranges": _fixed_ranges(),
        "initial_capital": 100,
        "direction": "long",
        "split_train_ratio": None,
        "page": None,
        "user_id": USER,
    }
    base.update(extra)
    return base


def _start(payload, job_id="7f3c2a91-0000-4000-8000-000000000001"):
    plan = build_plan(payload)
    service.create_batch_job(job_id, user_id=USER, payload=payload, plan=plan)
    return job_id


def _run(job_id, runner_factory=None):
    runner = service.BatchRunner(job_id, optimizer_factory=runner_factory or _optimizer)
    store = get_batch_backtest_store()
    assert store.claim(job_id, "task-test")
    runner.run()
    return store.get_job(job_id, include_items=True)


def _favorites(env):
    with env["Session"]() as db:
        return db.query(FavoriteStrategy).order_by(FavoriteStrategy.id).all()


def _items(job):
    return {i["symbol"]: i for i in job["items"]}


# ------------------------------------------------------------------ 3.6 lote misto em 1d


def test_mixed_1d_batch_saves_three_favorites_with_precision_and_window(batch_env, monkeypatch):
    reads: list[str] = []
    original_sample = ComboOptimizer._begin_sample

    def sample_spy(self, selected_source, symbol, timeframe, start, end, df):
        reads.append(symbol)  # 3.3: o provedor é lido uma vez por ativo
        frozen = original_sample(self, selected_source, symbol, timeframe, start, end, df)
        reads.append(f"sample:{symbol}:{self._sample_id}")
        return frozen

    monkeypatch.setattr(ComboOptimizer, "_begin_sample", sample_spy)
    store = get_batch_backtest_store()
    progress: list[str] = []
    original_update = store.update_item

    def update_spy(job_id, position, **changes):
        if changes.get("progress"):
            progress.append(changes["progress"])  # 3.2: série e página no item
        return original_update(job_id, position, **changes)

    monkeypatch.setattr(store, "update_item", update_spy)
    job = _run(_start(_payload(["BTC/USDT", "NVDA", "SPY"])))

    assert job["status"] == "completed" and job["total"] == 3 and job["processed"] == 3
    items = _items(job)
    assert {s: i["state"] for s, i in items.items()} == {
        "BTC/USDT": "success",
        "NVDA": "success",
        "SPY": "success",
    }
    favorites = {f.symbol: f for f in _favorites(batch_env)}
    assert set(favorites) == {"BTC/USDT", "NVDA", "SPY"}
    for symbol, favorite in favorites.items():
        assert items[symbol]["favorite_id"] == favorite.id
        metrics = favorite.metrics
        assert favorite.notes == "gerado em lote (7f3c2a91)"
        assert metrics["batch_id"] == job["job_id"]
        execution = metrics["analysis_execution"]
        assert execution["precision_requested"] == "intrabar"
        assert execution["precision_effective"] == "intrabar_15m"
        assert execution["window"]["covered"]["candles"] > 100
        assert metrics["analysis_conventions"]["fee"] > 0
        assert metrics["data_provenance"]["snapshot_id"] == items[symbol]["snapshot_id"]
        assert favorite.snapshot_id == items[symbol]["snapshot_id"]
        assert favorite.parameters["data_source"] in ("ccxt", "binance_equity")
    assert favorites["NVDA"].metrics["analysis_asset"]["asset_class"] == "stock"
    assert favorites["NVDA"].metrics["analysis_asset"]["currency"] == "USD"
    assert favorites["SPY"].metrics["analysis_asset"]["asset_class"] == "etf"
    assert favorites["BTC/USDT"].metrics["analysis_asset"]["currency"] == "USDT"
    # cripto mantém o nível de estrela do lote; ação/ETF sem nível até o #1122
    assert favorites["BTC/USDT"].tier == 3
    # Card #1122 (decisão 12 e decisão 2 de Alan): 1 estrela em qualquer classe e sem "Alertar".
    assert favorites["NVDA"].tier == 3 and favorites["SPY"].tier == 3
    assert not any(f.notify_telegram for f in favorites.values())
    assert (favorites["NVDA"].data_source, favorites["NVDA"].session) == (
        "binance_equity",
        "regular_ny",
    )
    assert favorites["BTC/USDT"].data_source == "ccxt"
    assert favorites["NVDA"].parameters["data_source"] == "binance_equity"

    # 3.3 mesma amostra: cada ativo foi lido uma vez e a amostra vai para o item e para o favorito
    assert [r for r in reads if not r.startswith("sample:")] == ["BTC/USDT", "NVDA", "SPY"]
    for symbol in ("BTC/USDT", "NVDA", "SPY"):
        assert f"sample:{symbol}:{items[symbol]['snapshot_id']}" in reads
    assert len({i["snapshot_id"] for i in items.values()}) == 3
    # a cripto congelou a amostra mesmo sem MARKET_HISTORY_UNIFIED no ambiente
    assert favorites["BTC/USDT"].metrics["data_provenance"]["snapshot_id"]
    # 3.2 progresso por página: "série · página N" (de M quando o total é conhecido)
    assert any(t.startswith("1d · página 1") for t in progress), progress
    assert any(t.startswith("5m do intrabar · página") for t in progress), progress


def test_equity_in_the_batch_equals_the_single_asset_backtest(batch_env):
    from app.services.equity_backtest import prepare_equity_history
    from app.services.market_data_providers import BinanceEquityMarketDataProvider

    prep = prepare_equity_history("NVDA", "1d", START, END, intrabar=True)
    single = _optimizer()
    single._provider = BinanceEquityMarketDataProvider(ensure=False)
    single.collection_note = prep.collection
    alone = single.run_optimization(
        template_name="multi_ma_crossover",
        symbol="NVDA",
        timeframe="1d",
        data_source="binance_equity",
        start_date=START,
        end_date=END,
        custom_ranges=_fixed_ranges(),
        deep_backtest=True,
    )

    _run(_start(_payload(["NVDA"]), "00000000-0000-4000-8000-000000000002"))
    favorite = _favorites(batch_env)[0]
    assert favorite.metrics["total_return"] == pytest.approx(alone["best_metrics"]["total_return"])
    assert len(favorite.metrics["trades"]) == len(alone["trades"])
    assert favorite.metrics["analysis_execution"]["precision_effective"] == (
        alone["execution"]["precision_effective"]
    )


# ------------------------------------------------------------------ 3.6 5m: ação e ETF ficam fora


def test_5m_batch_runs_only_the_crypto_and_marks_equity_out(batch_env):
    payload = _payload(
        ["BTC/USDT", "NVDA", "SPY"],
        timeframe="5m",
        deep_backtest=False,
        start_date="2026-10-01",
        end_date="2026-10-20",
    )
    job_id = _start(payload)
    created = get_batch_backtest_store().get_job(job_id, include_items=True)
    assert {s: i["state"] for s, i in _items(created).items()} == {
        "BTC/USDT": "queued",
        "NVDA": "out",
        "SPY": "out",
    }
    assert created["total"] == 1  # "N de M ativos" não conta os que ficam fora

    job = _run(job_id)
    items = _items(job)
    assert items["NVDA"]["state"] == "out" and "não rodam em 5m" in items["NVDA"]["reason"]
    assert items["SPY"]["state"] == "out"
    assert items["BTC/USDT"]["state"] == "success"
    assert job["status"] == "completed" and job["processed"] == 1
    assert {f.symbol for f in _favorites(batch_env)} == {"BTC/USDT"}
    assert batch_env["provider"].requests == []  # ação/ETF fora: nada coletado


# ------------------------------------------------------------------ 3.3 regressão cripto


def test_crypto_only_batch_matches_the_same_optimization_on_the_frozen_sample(batch_env):
    """Regressão do lote só cripto: o número do favorito é o da otimização direta, mesma amostra."""

    with_unified = _optimizer()
    from app.services.market_history import force_unified

    with force_unified():
        direct = with_unified.run_optimization(
            template_name="multi_ma_crossover",
            symbol="BTC/USDT",
            timeframe="1d",
            data_source="ccxt",
            start_date=START,
            end_date=END,
            custom_ranges=_fixed_ranges(),
            deep_backtest=True,
        )
    job = _run(_start(_payload(["BTC/USDT"]), "00000000-0000-4000-8000-000000000003"))
    assert job["items"][0]["state"] == "success"
    favorite = _favorites(batch_env)[0]
    assert favorite.metrics["total_return"] == pytest.approx(direct["best_metrics"]["total_return"])
    assert len(favorite.metrics["trades"]) == len(direct["trades"])


# ------------------------------------------------------------------ 3.6 problemas não param o lote


def test_insufficient_and_failed_do_not_save_and_do_not_stop_the_batch(batch_env):
    class Flaky(ComboOptimizer):
        def run_optimization(self, **kwargs):
            if kwargs["symbol"] == "SPY":
                raise RuntimeError("falha simulada do otimizador")
            return super().run_optimization(**kwargs)

    def factory():
        optimizer = Flaky(workers=1)
        optimizer.combo_service = _FakeTemplates()
        return optimizer

    # janela curta: menos candles do que o maior período (50) + 1
    payload = _payload(["NVDA", "SPY", "AAPL", "BTC/USDT"], start_date="2026-10-12")
    job = _run(_start(payload, "00000000-0000-4000-8000-000000000004"), factory)

    items = _items(job)
    assert items["SPY"]["state"] == "failed" and "Nenhum favorito gravado" in items["SPY"]["reason"]
    assert job["status"] == "completed" and job["processed"] == 4
    assert _favorites(batch_env) == []  # nenhum resultado inválido virou favorito
    assert job["failed"] == 1 and {e["symbol"] for e in job["errors"]} == {"SPY"}
    assert items["NVDA"]["state"] == "insufficient" and "pelo menos 51" in items["NVDA"]["reason"]
    assert items["AAPL"]["state"] == "insufficient"
    assert items["BTC/USDT"]["state"] == "insufficient"  # o último ativo rodou depois dos problemas
    assert "pelo menos 51" in items["BTC/USDT"]["reason"]


def test_walk_forward_no_go_is_rejected_without_a_favorite(batch_env):
    class NoGo(ComboOptimizer):
        def run_optimization(self, **kwargs):
            result = super().run_optimization(**kwargs)
            result["oos_verdict"] = {"status": "NO-GO", "reasons": ["retorno do holdout −8,2%"]}
            return result

    def factory():
        optimizer = NoGo(workers=1)
        optimizer.combo_service = _FakeTemplates()
        return optimizer

    # BTC/USDT (1d, cripto) é o ativo mais barato de otimizar; o NO-GO vale para qualquer classe
    job = _run(_start(_payload(["BTC/USDT"]), "00000000-0000-4000-8000-000000000005"), factory)
    item = job["items"][0]
    assert item["state"] == "rejected" and "NO-GO" in item["reason"]
    assert _favorites(batch_env) == []
    assert job["skipped"] == 1 and job["skipped_reasons"][0]["symbol"] == "BTC/USDT"


def test_existing_favorite_is_skipped_and_failed_collection_says_why(batch_env):
    with batch_env["Session"]() as db:
        db.add(
            FavoriteStrategy(
                user_id=USER,
                name="multi_ma_crossover - SPY 1d",
                symbol="SPY",
                timeframe="1d",
                strategy_name="multi_ma_crossover",
                # Card #1122: a duplicata compara a configuração (Binance Ações; Stooq coexiste).
                parameters={"direction": "long", "data_source": "binance_equity"},
                data_source="binance_equity",
                session="regular_ny",
                adjustment="split",
                metrics={},
                start_date=START,
                end_date=END,
            )
        )
        db.commit()
    again = _run(_start(_payload(["SPY"]), "00000000-0000-4000-8000-000000000007"))
    assert again["items"][0]["state"] == "skipped"
    assert "Já está nos favoritos" in again["items"][0]["reason"]
    assert len(_favorites(batch_env)) == 1
    assert batch_env["provider"].requests == []  # pulado antes de coletar

    from app.services.market_history.equity_provider import BinanceRateLimited

    batch_env["provider"].by_tf["1d"].fail_with = BinanceRateLimited("limite", retry_after=1)
    failed = _run(_start(_payload(["AAPL"]), "00000000-0000-4000-8000-000000000008"))
    item = failed["items"][0]
    assert item["state"] == "failed"
    assert "Histórico de AAPL indisponível" in item["reason"]
    assert "limite de requisições da Binance" in item["reason"]


# ------------------------------------------------------------------ 3.2 HistoryService


def test_history_service_reports_progress_page_by_page(batch_env):
    history = batch_env["history"]
    series = history.resolve(facade.spec_for_request(symbol="AAPL", timeframe="5m"))
    pages: list[tuple[int, int | None]] = []
    history.ensure(
        series,
        pd.Timestamp("2026-09-01", tz="UTC"),
        None,
        on_progress=lambda s, page, total: pages.append((page, total)),
    )
    assert [p for p, _ in pages] == list(range(1, len(pages) + 1)) and len(pages) >= 2
    assert all(total is None or total >= page for page, total in pages)
    last = pages[-1]
    assert last[1] is None or last[1] >= last[0]

    # um erro no retorno de progresso nunca derruba a coleta
    other = history.resolve(facade.spec_for_request(symbol="SPY", timeframe="5m"))
    outcome = history.ensure(
        other,
        pd.Timestamp("2026-09-20", tz="UTC"),
        None,
        on_progress=lambda *_a: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    assert outcome.status == "ok"
