from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from types import SimpleNamespace

import httpx
import pytest

import app.services.job_manager as job_manager_service
import app.services.news_localization_service as news_localization_service
import app.services.signal_monitor as signal_monitor_service


@pytest.fixture
def isolated_job_manager(monkeypatch, tmp_path):
    previous = job_manager_service.JobManager._instance
    if previous is not None and hasattr(previous, "engine"):
        previous.engine.dispose()

    monkeypatch.setattr(
        job_manager_service,
        "DB_URL",
        f"sqlite:///{tmp_path / 'optimization-results.sqlite'}",
    )
    monkeypatch.setattr(job_manager_service.JobManager, "DATA_DIR", tmp_path / "jobs")
    job_manager_service.JobManager._instance = None

    manager = job_manager_service.JobManager()
    try:
        yield manager
    finally:
        manager.engine.dispose()
        job_manager_service.JobManager._instance = None


@pytest.fixture(autouse=True)
def reset_news_localization_state():
    news_localization_service._LOCALIZATION_CACHE.clear()
    news_localization_service._LOCALIZATION_CACHE.update(
        {"fingerprint": tuple(), "localized_by_id": {}, "expires_at": 0.0}
    )
    news_localization_service._REFRESH_TASK = None
    yield
    news_localization_service._LOCALIZATION_CACHE.clear()
    news_localization_service._LOCALIZATION_CACHE.update(
        {"fingerprint": tuple(), "localized_by_id": {}, "expires_at": 0.0}
    )
    news_localization_service._REFRESH_TASK = None


def test_job_manager_state_listing_and_result_persistence(monkeypatch, isolated_job_manager):
    manager = isolated_job_manager

    job_id = manager.create_job({"strategy": "ema"})
    state = manager.load_state(job_id)
    assert state is not None
    assert state["status"] == "RUNNING"
    assert (manager.DATA_DIR / f"job_{job_id}.json").exists()

    state["results"] = [
        {"params": {"legacy": 1}, "metrics": {"pnl": 1.0}},
        {"params": {"legacy": 2}, "metrics": {"pnl": 2.0}},
    ]
    manager.save_state(job_id, state)
    (manager.DATA_DIR / "job_broken.json").write_text("{broken", encoding="utf-8")

    jobs = manager.list_jobs()
    assert [job["job_id"] for job in jobs] == [job_id]
    assert jobs[0]["result_count"] == 2
    assert "results" not in jobs[0]

    manager.signal_pause(job_id)
    pausing_state = manager.load_state(job_id)
    assert pausing_state is not None
    assert pausing_state["status"] == "PAUSING"
    assert manager.should_pause(job_id) is True
    assert manager.get_active_job()["job_id"] == job_id

    manager.mark_paused(job_id, pausing_state)
    assert manager.should_pause(job_id) is False
    assert manager.load_state(job_id)["status"] == "PAUSED"

    manager.mark_completed(job_id, {"summary": "done"})
    completed_state = manager.load_state(job_id)
    assert completed_state["status"] == "COMPLETED"
    assert completed_state["final_results"] == {"summary": "done"}

    manager.save_result(job_id, {"params": {"fast": 9}, "metrics": {"pnl": 1.5}}, 0)
    manager.save_result(job_id, {"params": {"fast": 10}, "metrics": {"pnl": 2.5}}, 0)
    manager.save_results_batch(
        job_id,
        [
            {"params": {"fast": 11}, "metrics": {"pnl": 3.5}},
            {"params": {"fast": 12}, "metrics": {"pnl": 4.5}},
        ],
        start_index=1,
    )

    persisted = manager.get_results(job_id, page=1, limit=2)
    assert persisted["pagination"] == {"page": 1, "limit": 2, "total": 3, "pages": 2}
    assert persisted["results"][0]["params"] == {"fast": 10}
    assert persisted["results"][1]["metrics"] == {"pnl": 3.5}

    legacy_state = manager.load_state(job_id)
    legacy_state["results"] = [
        {"params": {"legacy": 10}, "metrics": {"pnl": 10.0}},
        {"params": {"legacy": 20}, "metrics": {"pnl": 20.0}},
    ]
    manager.save_state(job_id, legacy_state)
    monkeypatch.setattr(
        manager,
        "_session_factory",
        lambda: (_ for _ in ()).throw(RuntimeError("database unavailable")),
    )
    fallback = manager.get_results(job_id, page=2, limit=1)
    assert fallback["results"] == [{"params": {"legacy": 20}, "metrics": {"pnl": 20.0}}]
    assert fallback["pagination"] == {"page": 2, "limit": 1, "total": 2, "pages": 2}

    assert manager.load_state("missing-job") is None


class _FakeSignalQuery:
    def __init__(self, signals, failure: Exception | None = None):
        self._signals = signals
        self._failure = failure

    def filter(self, *args, **kwargs):
        if self._failure is not None:
            raise self._failure
        return self

    def all(self):
        if self._failure is not None:
            raise self._failure
        return list(self._signals)


class _FakeSignalDB:
    def __init__(self, signals, failure: Exception | None = None):
        self._signals = signals
        self._failure = failure
        self.commit_calls = 0
        self.rollback_calls = 0
        self.close_calls = 0

    def query(self, model):
        return _FakeSignalQuery(self._signals, self._failure)

    def commit(self):
        self.commit_calls += 1

    def rollback(self):
        self.rollback_calls += 1

    def close(self):
        self.close_calls += 1


@pytest.mark.asyncio
async def test_signal_monitor_fetch_price_handles_success_rate_limit_and_errors(monkeypatch):
    class FakeResponse:
        def __init__(self, status_code, payload=None, error=None):
            self.status_code = status_code
            self._payload = payload or {}
            self._error = error

        def raise_for_status(self):
            if self._error is not None:
                raise self._error

        def json(self):
            return self._payload

    responses = [
        FakeResponse(200, {"price": "123.45"}),
        FakeResponse(429, {"price": "0"}),
        FakeResponse(500, error=httpx.HTTPStatusError("boom", request=None, response=None)),
    ]

    class FakeAsyncClient:
        def __init__(self, timeout=None):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params=None):
            return responses.pop(0)

    monkeypatch.setattr(signal_monitor_service.httpx, "AsyncClient", FakeAsyncClient)

    assert await signal_monitor_service._fetch_price("BTCUSDT") == 123.45
    assert await signal_monitor_service._fetch_price("BTCUSDT") is None
    assert await signal_monitor_service._fetch_price("BTCUSDT") is None


def test_signal_monitor_updates_signals_and_handles_failures(monkeypatch):
    now_sp = datetime(2026, 4, 18, 18, 30, tzinfo=timezone.utc)
    signals = [
        SimpleNamespace(
            asset="BTCUSDT",
            type="BUY",
            status="ativo",
            entry_price=100.0,
            target_price=110.0,
            stop_loss=90.0,
            exit_price=None,
            pnl=None,
            updated_at=None,
        ),
        SimpleNamespace(
            asset="ETHUSDT",
            type="BUY",
            status="ativo",
            entry_price=200.0,
            target_price=230.0,
            stop_loss=180.0,
            exit_price=None,
            pnl=None,
            updated_at=None,
        ),
        SimpleNamespace(
            asset="SOLUSDT",
            type="BUY",
            status="ativo",
            entry_price=50.0,
            target_price=55.0,
            stop_loss=45.0,
            exit_price=None,
            pnl=None,
            updated_at=None,
        ),
    ]
    db = _FakeSignalDB(signals)

    async def fake_fetch_price(asset):
        return {"BTCUSDT": 112.0, "ETHUSDT": 175.0, "SOLUSDT": None}[asset]

    monkeypatch.setattr(signal_monitor_service, "SessionLocal", lambda: db)
    monkeypatch.setattr(signal_monitor_service, "_fetch_price", fake_fetch_price)
    monkeypatch.setattr(signal_monitor_service, "sao_paulo_now", lambda: now_sp)
    signal_monitor_service._check_and_update_signals()

    assert db.commit_calls == 1
    assert db.close_calls == 1
    assert signals[0].status == "disparado"
    assert signals[0].exit_price == 110.0
    assert signals[0].pnl == 10.0
    assert signals[0].updated_at == now_sp
    assert signals[1].status == "disparado"
    assert signals[1].exit_price == 180.0
    assert signals[1].pnl == -10.0
    assert signals[2].status == "ativo"

    failing_db = _FakeSignalDB(signals)
    monkeypatch.setattr(signal_monitor_service, "SessionLocal", lambda: failing_db)

    def fail_asyncio_run(coro):
        coro.close()
        raise RuntimeError("network down")

    monkeypatch.setattr(
        signal_monitor_service.asyncio,
        "run",
        fail_asyncio_run,
    )
    signal_monitor_service._check_and_update_signals()
    assert failing_db.commit_calls == 0
    assert failing_db.close_calls == 1

    broken_db = _FakeSignalDB([], failure=RuntimeError("query failed"))
    monkeypatch.setattr(signal_monitor_service, "SessionLocal", lambda: broken_db)
    signal_monitor_service._check_and_update_signals()
    assert broken_db.rollback_calls == 1
    assert broken_db.close_calls == 1


def test_signal_monitor_loop_and_lifecycle(monkeypatch):
    signal_monitor_service.SignalMonitor._instance = None
    monitor = signal_monitor_service.SignalMonitor()

    loop_calls: list[str] = []

    class LoopEvent:
        def __init__(self):
            self._set = False
            self.wait_calls = 0

        def is_set(self):
            return self._set

        def wait(self, timeout):
            self.wait_calls += 1
            self._set = True

        def set(self):
            self._set = True

        def clear(self):
            self._set = False

    monitor._stop_event = LoopEvent()
    monkeypatch.setattr(
        signal_monitor_service, "_check_and_update_signals", lambda: loop_calls.append("tick")
    )
    monitor._run_loop()
    assert loop_calls == ["tick"]
    assert monitor._stop_event.wait_calls == 1

    created_threads: list[SimpleNamespace] = []

    class FakeThread:
        def __init__(self, target=None, daemon=None):
            self.target = target
            self.daemon = daemon
            self.started = False
            self.join_calls = 0
            self._alive = False
            created_threads.append(self)

        def start(self):
            self.started = True
            self._alive = True

        def is_alive(self):
            return self._alive

        def join(self, timeout=None):
            self.join_calls += 1
            self._alive = False

    monkeypatch.setattr(signal_monitor_service.threading, "Thread", FakeThread)
    monitor._stop_event = LoopEvent()
    monitor._thread = None
    monitor.start()
    assert len(created_threads) == 1
    assert created_threads[0].daemon is True
    monitor.start()
    assert len(created_threads) == 1
    monitor.stop()
    assert created_threads[0].join_calls == 1
    assert monitor._thread is None
    monitor.stop()


def test_news_localization_helpers_and_cache(monkeypatch):
    class FakeSession:
        def close(self):
            self.closed = True

    monkeypatch.setattr(news_localization_service, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(
        news_localization_service, "get_system_preference_value", lambda db, key: "stored-key"
    )
    assert news_localization_service._get_minimax_api_key() == "stored-key"

    monkeypatch.setattr(
        news_localization_service, "get_system_preference_value", lambda db, key: ""
    )
    monkeypatch.setenv("MINIMAX_API_KEY", "env-key")
    assert news_localization_service._get_minimax_api_key() == "env-key"

    assert news_localization_service._fallback_summary("", "") == "Resumo indisponível no momento."
    assert (
        news_localization_service._fallback_summary("Alta do BTC", "CoinDesk")
        == "Resumo automático indisponível. Fonte original: CoinDesk."
    )
    assert (
        news_localization_service._extract_json_object('```json\n{"title_pt":"Oi"}\n```')
        == '{"title_pt":"Oi"}'
    )
    assert news_localization_service._parse_localized_content(
        '{"title_pt":"Titulo","summary_pt":"Resumo"}'
    ) == (
        "Titulo",
        "Resumo",
    )
    assert news_localization_service._parse_localized_content(
        "TITLE_PT: Titulo\nSUMMARY_PT: Resumo"
    ) == ("Titulo", "Resumo")
    assert news_localization_service._parse_localized_content("Titulo\nResumo 1\nResumo 2") == (
        "Titulo",
        "Resumo 1 Resumo 2",
    )
    assert news_localization_service._build_fingerprint(
        [{"id": 1, "title": "BTC"}, "skip", {"id": 2, "title": "ETH"}]
    ) == (("1", "BTC"), ("2", "ETH"))

    items = [{"id": "1", "title": "BTC sobe"}]

    async def fake_localize_news_items(news_items):
        return [{"id": "1", "title_pt": "BTC sobe", "summary_pt": "Resumo PT"}]

    monkeypatch.setattr(news_localization_service, "localize_news_items", fake_localize_news_items)
    asyncio.run(news_localization_service._refresh_localized_news_cache(items))
    localized, is_fresh = news_localization_service.get_cached_localized_news(items)
    assert is_fresh is True
    assert localized == {"1": {"title_pt": "BTC sobe", "summary_pt": "Resumo PT"}}


def test_news_localization_scheduler_branches(monkeypatch):
    items = [{"id": "1", "title": "BTC sobe"}]
    created: list[object] = []

    class FakeTask:
        def __init__(self, done_state):
            self._done_state = done_state

        def done(self):
            return self._done_state

    def fake_create_task(coro):
        created.append(coro)
        coro.close()
        return FakeTask(done_state=False)

    monkeypatch.setattr(news_localization_service.asyncio, "create_task", fake_create_task)
    news_localization_service.schedule_news_localization_refresh(items)
    assert len(created) == 1

    news_localization_service._LOCALIZATION_CACHE["fingerprint"] = (
        news_localization_service._build_fingerprint(items)
    )
    news_localization_service._LOCALIZATION_CACHE["localized_by_id"] = {
        "1": {"title_pt": "BTC", "summary_pt": "Resumo"}
    }
    news_localization_service._LOCALIZATION_CACHE["expires_at"] = time.time() + 60
    created.clear()
    news_localization_service.schedule_news_localization_refresh(items)
    assert created == []

    news_localization_service._LOCALIZATION_CACHE["expires_at"] = 0
    news_localization_service._REFRESH_TASK = FakeTask(done_state=False)
    news_localization_service.schedule_news_localization_refresh(items)
    assert created == []

    news_localization_service._REFRESH_TASK = None
    news_localization_service._LOCALIZATION_CACHE["fingerprint"] = tuple()

    def fail_create_task(coro):
        coro.close()
        raise RuntimeError("no running loop")

    monkeypatch.setattr(
        news_localization_service.asyncio,
        "create_task",
        fail_create_task,
    )
    news_localization_service.schedule_news_localization_refresh(items)
    news_localization_service.schedule_news_localization_refresh([])


@pytest.mark.asyncio
async def test_localize_news_items_handles_empty_fallback_retry_and_failure(monkeypatch):
    assert await news_localization_service.localize_news_items([]) == []

    items = [
        {"id": "1", "title": "BTC up", "source": "CoinDesk"},
        {"id": "2", "title": "ETH down", "source": "The Block"},
        {"id": "3", "title": "SOL flat", "source": "Decrypt"},
    ]

    monkeypatch.setattr(news_localization_service, "_get_minimax_api_key", lambda: "")
    fallback = await news_localization_service.localize_news_items(items)
    assert fallback[0]["title_pt"] == "BTC up"
    assert fallback[0]["summary_pt"].startswith("Resumo automático indisponível")

    monkeypatch.setattr(news_localization_service, "_get_minimax_api_key", lambda: "minimax-key")

    class FakeResponse:
        def __init__(self, content):
            self._content = content

        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": self._content}}]}

    attempts: dict[str, int] = {}

    class FakeAsyncClient:
        def __init__(self, timeout=None):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, headers=None, json=None):
            payload = json_module.loads(json["messages"][1]["content"])
            item_id = payload["id"]
            attempts[item_id] = attempts.get(item_id, 0) + 1
            if item_id == "1":
                return FakeResponse("TITLE_PT: BTC sobe\nSUMMARY_PT: Resumo BTC")
            if item_id == "2" and attempts[item_id] == 1:
                return FakeResponse("TITLE_PT: ETH cai")
            if item_id == "2":
                return FakeResponse("TITLE_PT: ETH cai\nSUMMARY_PT: Resumo ETH")
            raise RuntimeError("provider unavailable")

    json_module = json
    monkeypatch.setattr(news_localization_service.httpx, "AsyncClient", FakeAsyncClient)
    localized = await news_localization_service.localize_news_items(items)

    assert localized[0] == {"id": "1", "title_pt": "BTC sobe", "summary_pt": "Resumo BTC"}
    assert localized[1] == {"id": "2", "title_pt": "ETH cai", "summary_pt": "Resumo ETH"}
    assert localized[2]["title_pt"] == "SOL flat"
    assert localized[2]["summary_pt"].startswith("Resumo automático indisponível")
