"""Pausa, retomada e encerramento duráveis do lote (card #1120, tarefas 1.1 a 1.3 e 3.4).

O otimizador e a coleta são simulados: o que se prova aqui é o estado no PostgreSQL, a ordem das
etapas e o que a retomada não refaz.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from sqlalchemy.orm import sessionmaker

from app.models import FavoriteStrategy
from app.services import batch_backtest_service as service
from app.services.batch_backtest_plan import build_plan
from app.services.batch_backtest_store import BatchBacktestStore, get_batch_backtest_store
from test_card_1118_api_and_catalog import _seed_catalog, public_db  # noqa: F401

USER = "user-1"
JOB = "7f3c2a91-1111-4000-8000-000000000001"


class Recorder:
    """Chamadas de coleta e de otimização, com ganchos para pedir pausa/encerramento no meio."""

    def __init__(self) -> None:
        self.collected: list[str] = []
        self.optimized: list[str] = []
        self.on_collect: dict[str, callable] = {}
        self.on_optimize: dict[str, callable] = {}


def _result(symbol: str) -> dict:
    return {
        "best_parameters": {"ema_short": 9},
        "best_metrics": {"total_return": 0.1},
        "trades": [],
        "candles": [],
        "indicator_data": {},
        "execution_mode": "deep_15m",
        "snapshot_id": None,
        "asset": {"symbol": symbol, "asset_class": "stock", "currency": "USD"},
        "execution": {
            "precision_requested": "intrabar",
            "precision_effective": "intrabar_15m",
            "window": {"covered": {"candles": 500}},
        },
        "conventions": {"fee": 0.001},
        "data_provenance": {"data_source": "Binance Ações"},
    }


@pytest.fixture
def env(public_db, monkeypatch):  # noqa: F811
    _seed_catalog(public_db)
    get_batch_backtest_store.cache_clear()
    rec = Recorder()

    def fake_prepare(symbol, timeframe, start, end, *, intrabar, service=None, on_progress=None):
        rec.collected.append(symbol)
        if on_progress:
            on_progress("candles", timeframe, 1, 2)
        rec.on_collect.get(symbol, lambda: None)()
        return SimpleNamespace(collection=None)

    class FakeOptimizer:
        def run_optimization(self, **kwargs):
            symbol = kwargs["symbol"]
            rec.optimized.append(symbol)
            rec.on_optimize.get(symbol, lambda: None)()
            return _result(symbol)

    monkeypatch.setattr(service, "prepare_equity_history", fake_prepare)
    monkeypatch.setattr(service, "_collect_crypto_history", lambda *a, **k: None)
    monkeypatch.setattr(service, "minimum_candles", lambda *a, **k: 0)
    rec.factory = FakeOptimizer  # type: ignore[attr-defined]
    rec.Session = sessionmaker(bind=public_db)  # type: ignore[attr-defined]
    yield rec
    get_batch_backtest_store.cache_clear()


def _payload(symbols, **extra):
    return {
        "template_name": "multi_ma_crossover",
        "symbols": symbols,
        "timeframe": "1d",
        "start_date": "2026-02-02",
        "end_date": "2026-10-20",
        "deep_backtest": True,
        "direction": "long",
        "user_id": USER,
        **extra,
    }


def _create(symbols=("NVDA", "SPY", "QQQ"), job_id=JOB, **extra):
    payload = _payload(list(symbols), **extra)
    service.create_batch_job(job_id, user_id=USER, payload=payload, plan=build_plan(payload))
    return job_id


def _go(rec, job_id=JOB):
    store = get_batch_backtest_store()
    assert store.claim(job_id, "task-1")
    service.BatchRunner(job_id, optimizer_factory=rec.factory).run()
    return store.get_job(job_id, include_items=True)


def _favorite_count(env) -> int:
    with env.Session() as db:
        return db.query(FavoriteStrategy).count()


def _states(job):
    return {i["symbol"]: i["state"] for i in job["items"]}


# ------------------------------------------------------------------ 1.1 / 1.2 / 1.3 estado durável


def test_job_and_items_live_in_postgres_and_survive_a_new_store_instance(env):
    _create(("BTC/USDT", "NVDA", "SPY"), timeframe="5m")

    fresh = BatchBacktestStore()  # outro processo: nada em memória
    job = fresh.get_job(JOB, include_items=True)
    assert job["status"] == "queued" and job["user_id"] == USER
    assert job["total"] == 1  # NVDA e SPY ficam fora em 5m: não entram em "N de M"
    assert [(i["symbol"], i["state"], i["asset_class"], i["currency"]) for i in job["items"]] == [
        ("BTC/USDT", "queued", "crypto", "USDT"),
        ("NVDA", "out", "stock", "USD"),
        ("SPY", "out", "etf", "USD"),
    ]
    assert job["totals"] == {"queued": 1, "out": 2}
    assert job["plan"]["totals"]["out"] == 2 and job["payload"]["symbols"][0] == "BTC/USDT"
    assert fresh.get_job("missing") is None


def test_paused_job_has_no_expiry_and_active_job_is_the_latest_non_final(env):
    store = get_batch_backtest_store()
    _create(job_id="aaaaaaaa-0000-4000-8000-000000000001")
    store.request_cancel("aaaaaaaa-0000-4000-8000-000000000001")
    _create(job_id="bbbbbbbb-0000-4000-8000-000000000002")
    assert store.active_job(USER)["job_id"] == "bbbbbbbb-0000-4000-8000-000000000002"
    assert store.active_job("outro-usuario") is None
    assert store.paused_job(USER) is None

    store.request_pause("bbbbbbbb-0000-4000-8000-000000000002")
    paused = store.paused_job(USER)
    assert paused["job_id"] == "bbbbbbbb-0000-4000-8000-000000000002"
    assert store.active_job(USER)["status"] == "paused"  # pausado ainda é o lote ativo, sem prazo
    assert paused["status"] == "paused" and paused["finished_at"] is None


def test_legacy_redis_job_is_still_readable_and_pausable(env):
    from app.services.batch_backtest_store import LegacyBatchStore

    store = get_batch_backtest_store()
    legacy = LegacyBatchStore()
    legacy.init_job("legacy-1", 4)
    job = service.get_batch_progress("legacy-1")
    assert job["status"] == "queued" and job["total"] == 4 and job.get("items") is None
    assert service.request_pause_batch("legacy-1") is True
    assert store.get_job("legacy-1")["status"] == "paused"
    assert store.is_durable("legacy-1") is False
    assert (
        service.request_cancel_batch("legacy-1") is False
    )  # lote antigo pausado é final para o painel antigo


def test_claim_is_exclusive_and_never_takes_a_paused_or_final_job(env):
    store = get_batch_backtest_store()
    job_id = _create()
    assert store.claim(job_id, "task-a") is True
    assert store.claim(job_id, "task-b") is False  # outro worker não assume o lote rodando
    assert store.claim(job_id, "task-a") is True  # mesma tarefa reentregue (worker perdido)

    paused_id = _create(job_id="cccccccc-0000-4000-8000-000000000003")
    store.request_pause(paused_id)
    assert store.claim(paused_id, "task-c") is False
    store.request_cancel(paused_id)
    assert store.claim(paused_id, "task-c") is False


def test_redelivered_task_puts_the_interrupted_step_back_in_the_queue(env):
    store = get_batch_backtest_store()
    _create()
    store.claim(JOB, "task-a")
    store.update_item(JOB, 0, state="optimizing")
    assert store.claim(JOB, "task-a")
    assert store.list_items(JOB)[0]["state"] == "queued"


# ------------------------------------------------------------------ 3.4 pausa, retomada, encerramento


def test_pause_during_collection_stops_after_the_step_and_resume_skips_what_is_done(env):
    store = get_batch_backtest_store()
    job_id = _create()
    env.on_collect["SPY"] = lambda: store.request_pause(job_id)  # pedido no meio da coleta de SPY

    job = _go(env)

    assert job["status"] == "paused" and job["pause_requested"] is False
    assert _states(job) == {"NVDA": "success", "SPY": "queued", "QQQ": "queued"}
    spy = job["items"][1]
    assert spy["progress"] == "histórico coletado; otimiza ao retomar, na mesma amostra."
    assert env.collected == ["NVDA", "SPY"] and env.optimized == [
        "NVDA"
    ]  # a etapa em curso terminou
    assert job["succeeded"] == 1 and job["processed"] == 1 and job["total"] == 3
    assert _favorite_count(env) == 1  # o que terminou fica

    assert store.request_resume(job_id) is True
    job = _go(env)

    assert job["status"] == "completed" and job["processed"] == 3 and job["succeeded"] == 3
    assert env.collected == ["NVDA", "SPY", "QQQ"]  # SPY não foi coletado de novo
    assert env.optimized == ["NVDA", "SPY", "QQQ"]  # NVDA não foi refeito
    assert job["job_id"] == JOB  # o mesmo lote, não um novo
    assert _favorite_count(env) == 3


def test_pause_during_optimization_finishes_that_asset_and_stops_before_the_next(env):
    store = get_batch_backtest_store()
    job_id = _create()
    env.on_optimize["NVDA"] = lambda: store.request_pause(job_id)

    job = _go(env)

    assert job["status"] == "paused"
    assert _states(job) == {"NVDA": "success", "SPY": "queued", "QQQ": "queued"}
    assert env.collected == ["NVDA"]  # o próximo ativo nem começou a coletar
    assert job["items"][1]["progress"] is None


def test_cancel_marks_the_rest_not_run_and_keeps_the_favorites(env):
    store = get_batch_backtest_store()
    job_id = _create()
    env.on_collect["SPY"] = lambda: store.request_cancel(job_id)

    job = _go(env)

    assert job["status"] == "cancelled" and job["finished_at"]
    assert _states(job) == {"NVDA": "success", "SPY": "not_run", "QQQ": "not_run"}
    assert job["items"][1]["reason"] == "lote encerrado antes"
    assert job["succeeded"] == 1 and job["processed"] == 3  # "Não rodou" conta como terminado
    assert env.optimized == ["NVDA"]
    assert _favorite_count(env) == 1
    assert store.active_job(USER) is None


def test_cancel_while_paused_closes_the_batch_at_once(env):
    store = get_batch_backtest_store()
    job_id = _create()
    env.on_collect["SPY"] = lambda: store.request_pause(job_id)
    _go(env)
    assert store.paused_job(USER)["job_id"] == job_id

    assert store.request_cancel(job_id) is True
    job = store.get_job(job_id, include_items=True)
    assert job["status"] == "cancelled" and job["cancel_requested"] is True
    assert _states(job) == {"NVDA": "success", "SPY": "not_run", "QQQ": "not_run"}
    assert store.paused_job(USER) is None
    assert store.request_resume(job_id) is False  # encerrado não volta


def test_pause_on_a_queued_batch_pauses_it_before_it_starts(env):
    store = get_batch_backtest_store()
    job_id = _create()
    assert store.request_pause(job_id) is True
    assert store.get_job(job_id)["status"] == "paused"
    assert (
        store.claim(job_id, "task-1") is False
    )  # a tarefa antiga na fila não roda um lote pausado
    assert store.request_resume(job_id) is True
    job = _go(env)
    assert job["status"] == "completed"


def test_progress_writes_never_clobber_a_pause_requested_in_the_meantime(env):
    store = get_batch_backtest_store()
    job_id = _create()
    stale = store.get_job(job_id)
    store.request_pause(job_id)  # chega pela API depois da leitura do worker
    stale["current_symbol"] = "NVDA"
    store.save_job(stale)  # o worker grava o andamento com a cópia velha
    assert store.get_job(job_id)["status"] == "paused"
    store.update_job(job_id, current_symbol="NVDA", elapsed_sec=3.0)
    again = store.get_job(job_id)
    assert again["pause_requested"] is True and again["current_symbol"] == "NVDA"


def test_batch_completes_with_totals_and_a_replan_at_start(env, monkeypatch):
    job_id = _create(("BTC/USDT", "NVDA"))
    job = _go(env)
    assert job["status"] == "completed" and job["current_symbol"] is None
    assert job["finished_at"] and job["elapsed_sec"] >= 0 and job["estimated_remaining_sec"] is None
    assert job["totals"] == {"success": 2}
    assert job["plan"]["config"]["timeframe"] == "1d"
    assert job_id == job["job_id"]


# ------------------------------------------------------------------ 1.1 migração


def test_migration_creates_the_tables_of_the_models_and_is_idempotent(unit_database_url):
    import importlib.util
    import uuid
    from pathlib import Path

    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from sqlalchemy import create_engine, inspect, text

    from app.models_batch_backtest import BatchBacktestItem, BatchBacktestJob

    path = Path(__file__).parents[2] / "alembic/versions/20261024_0001_batch_backtest_jobs.py"
    spec = importlib.util.spec_from_file_location("migration_1120", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.down_revision == "20261023_0001" and module.revision == "20261024_0001"

    engine = create_engine(unit_database_url)
    schema = "migration_1120_" + uuid.uuid4().hex[:12]
    try:
        with engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA {schema}"))
            conn.execute(text(f"SET LOCAL search_path TO {schema}"))
            context = MigrationContext.configure(conn)
            with Operations.context(context):
                module.upgrade()
                module.upgrade()  # o app também cria as tabelas na subida: idempotente
            inspector = inspect(conn)
            for model in (BatchBacktestJob, BatchBacktestItem):
                created = {
                    c["name"] for c in inspector.get_columns(model.__tablename__, schema=schema)
                }
                assert created == {c.name for c in model.__table__.columns}, model.__tablename__
            with pytest.raises(RuntimeError):
                with Operations.context(context):
                    module.downgrade()  # o estado do lote é do usuário: rollback não apaga
            conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
    finally:
        engine.dispose()
