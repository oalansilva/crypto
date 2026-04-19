from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.workflow_database import WorkflowBase
from app.workflow_models import Project
import app.workflow_database as workflow_database
import app.workers.runtime_worker as runtime_worker


@pytest.fixture(autouse=True)
def clear_workflow_caches(monkeypatch):
    monkeypatch.setattr(workflow_database, "_workflow_engines", {})
    monkeypatch.setattr(workflow_database, "_workflow_sessionmakers", {})


def test_workflow_db_helpers_cover_env_url_and_project_resolution(monkeypatch, tmp_path):
    monkeypatch.setattr(
        workflow_database,
        "get_settings",
        lambda: SimpleNamespace(workflow_db_enabled="1", workflow_database_url=None),
    )
    monkeypatch.setenv("ALLOW_SQLITE_FOR_TESTS", "1")
    monkeypatch.delenv("WORKFLOW_DATABASE_URL", raising=False)

    sqlite_url = workflow_database.get_workflow_db_url()
    assert sqlite_url and sqlite_url.startswith("sqlite:///")
    assert workflow_database._is_postgres_url("postgresql://db")
    assert workflow_database._enabled() is True
    assert workflow_database._allow_sqlite_for_tests() is True
    assert "workflow.db" in workflow_database._default_sqlite_url()

    monkeypatch.setattr(
        workflow_database,
        "get_settings",
        lambda: SimpleNamespace(workflow_db_enabled=None, workflow_database_url=None),
    )
    monkeypatch.setenv("WORKFLOW_DB_ENABLED", "true")
    assert workflow_database._enabled() is True

    monkeypatch.setattr(
        workflow_database,
        "get_settings",
        lambda: SimpleNamespace(workflow_db_enabled="0", workflow_database_url=None),
    )
    assert workflow_database.get_workflow_db_url() is None

    monkeypatch.setattr(
        workflow_database,
        "get_settings",
        lambda: SimpleNamespace(workflow_db_enabled="1", workflow_database_url="sqlite:///bad.db"),
    )
    monkeypatch.delenv("ALLOW_SQLITE_FOR_TESTS", raising=False)
    monkeypatch.setattr(workflow_database.sys, "argv", ["uvicorn"])
    with pytest.raises(RuntimeError, match="must point to PostgreSQL"):
        workflow_database.get_workflow_db_url()

    monkeypatch.setattr(
        workflow_database,
        "get_settings",
        lambda: SimpleNamespace(
            workflow_db_enabled="1", workflow_database_url="postgresql://workflow-db"
        ),
    )
    assert workflow_database.get_workflow_db_url() == "postgresql://workflow-db"

    monkeypatch.setattr(
        workflow_database,
        "get_settings",
        lambda: SimpleNamespace(workflow_db_enabled="1", workflow_database_url=None),
    )
    monkeypatch.delenv("ALLOW_SQLITE_FOR_TESTS", raising=False)
    monkeypatch.delenv("WORKFLOW_DATABASE_URL", raising=False)
    monkeypatch.setattr(workflow_database.sys, "argv", ["uvicorn"])
    with pytest.raises(RuntimeError, match="WORKFLOW_DATABASE_URL is required"):
        workflow_database.get_workflow_db_url()

    monkeypatch.setenv("ALLOW_SQLITE_FOR_TESTS", "1")
    registry_url = f"sqlite:///{tmp_path / 'registry.db'}"
    monkeypatch.setattr(workflow_database, "get_workflow_db_url", lambda: registry_url)
    project = SimpleNamespace(slug="crypto", workflow_database_url="postgresql://project-db")
    assert workflow_database.get_project_workflow_db_url(project) == registry_url

    project.workflow_database_url = None
    assert workflow_database.get_project_workflow_db_url(project) == registry_url

    monkeypatch.setenv("WORKFLOW_ALLOW_SHARED_PROJECT_DB", "0")
    monkeypatch.setattr(workflow_database, "get_workflow_db_url", lambda: "postgresql://registry")
    with pytest.raises(RuntimeError, match="has no workflow_database_url configured"):
        workflow_database.get_project_workflow_db_url(project)


def test_workflow_db_init_sync_bootstrap_and_dependency(monkeypatch, tmp_path):
    sqlite_url = f"sqlite:///{tmp_path / 'workflow.db'}"
    workflow_database.init_workflow_schema_for_url(sqlite_url)

    engine = workflow_database.get_workflow_engine_for_url(sqlite_url)
    maker = workflow_database.get_workflow_sessionmaker_for_url(sqlite_url)
    monkeypatch.setattr(workflow_database, "get_workflow_db_url", lambda: sqlite_url)
    assert engine is workflow_database.get_workflow_engine_for_url(sqlite_url)
    assert maker is workflow_database.get_workflow_sessionmaker_for_url(sqlite_url)
    assert workflow_database.get_workflow_engine() is engine
    assert workflow_database.get_registry_workflow_sessionmaker() is maker
    assert "wf_changes" in inspect(engine).get_table_names()

    db = maker()
    try:
        project = SimpleNamespace(
            id="proj-1",
            slug="crypto",
            name="Crypto",
            root_directory="/repo",
            database_url="postgresql://app-db",
            frontend_url="http://localhost:5173",
            backend_url="http://localhost:8003",
            workflow_database_url=sqlite_url,
            tech_stack="fastapi,react",
            created_at=datetime.now(timezone.utc),
        )

        workflow_database.sync_project_to_workflow_db(project, db)
        workflow_database.sync_project_to_workflow_db(project, db)
        db.commit()

        saved = db.query(Project).filter(Project.slug == "crypto").first()
        assert saved is not None
        assert saved.workflow_database_url == sqlite_url
    finally:
        db.close()

    bootstrap_project = SimpleNamespace(
        id="proj-2",
        slug="kanban",
        name="Kanban",
        root_directory="/kanban",
        database_url="postgresql://app-db",
        frontend_url="http://localhost:5174",
        backend_url="http://localhost:8004",
        workflow_database_url=sqlite_url,
        tech_stack="fastapi,react",
        created_at=datetime.now(timezone.utc),
    )
    workflow_database.bootstrap_project_workflow_db(bootstrap_project)
    db = maker()
    try:
        assert db.query(Project).filter(Project.slug == "kanban").first() is not None
    finally:
        db.close()

    class FakeSession:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    fake_session = FakeSession()
    monkeypatch.setattr(
        workflow_database, "get_registry_workflow_sessionmaker", lambda: lambda: fake_session
    )

    dependency = workflow_database.get_workflow_db()
    yielded = next(dependency)
    assert yielded is fake_session
    with pytest.raises(StopIteration):
        next(dependency)
    assert fake_session.closed is True

    monkeypatch.setattr(workflow_database, "get_registry_workflow_sessionmaker", lambda: None)
    with pytest.raises(RuntimeError, match="Workflow DB is disabled"):
        next(workflow_database.get_workflow_db())


def test_runtime_worker_env_database_init_and_signal_handlers(monkeypatch):
    assert runtime_worker._env_enabled("MISSING_ENABLED", default="1") is True
    monkeypatch.setenv("RUN_SIGNAL_MONITOR", "0")
    assert runtime_worker._env_enabled("RUN_SIGNAL_MONITOR") is False

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, _stmt):
            return 1

    monkeypatch.setattr(runtime_worker, "engine", SimpleNamespace(connect=lambda: FakeConnection()))
    runtime_worker._wait_for_database(max_attempts=1, delay_seconds=0)

    monkeypatch.setattr(
        runtime_worker,
        "engine",
        SimpleNamespace(connect=lambda: (_ for _ in ()).throw(RuntimeError("db down"))),
    )
    monkeypatch.setitem(
        __import__("sys").modules, "time", SimpleNamespace(sleep=lambda _seconds: None)
    )
    with pytest.raises(RuntimeError, match="Unable to connect"):
        runtime_worker._wait_for_database(max_attempts=1, delay_seconds=0)

    calls = []
    monkeypatch.setattr(
        runtime_worker, "_wait_for_database", lambda **_kwargs: calls.append("wait")
    )
    monkeypatch.setattr(
        runtime_worker.Base.metadata, "create_all", lambda bind: calls.append(("create_all", bind))
    )
    monkeypatch.setattr(
        runtime_worker, "sync_postgres_identity_sequences", lambda: calls.append("sync")
    )
    monkeypatch.setattr(
        runtime_worker, "ensure_runtime_schema_migrations", lambda: calls.append("migrate")
    )
    runtime_worker._initialize_runtime_state()
    assert calls[0] == "wait"
    assert "sync" in calls and "migrate" in calls

    stop_event = asyncio.Event()
    recorded = []

    class FakeLoop:
        def add_signal_handler(self, signum, callback):
            recorded.append(signum)
            callback()

    monkeypatch.setattr(runtime_worker.asyncio, "get_running_loop", lambda: FakeLoop())
    runtime_worker._install_signal_handlers(stop_event, [runtime_worker.signal.SIGINT])
    assert stop_event.is_set() is True
    assert recorded == [runtime_worker.signal.SIGINT]

    stop_event = asyncio.Event()

    class FallbackLoop:
        def add_signal_handler(self, signum, callback):
            raise NotImplementedError

    fallback_calls = []
    monkeypatch.setattr(runtime_worker.asyncio, "get_running_loop", lambda: FallbackLoop())
    monkeypatch.setattr(
        runtime_worker.signal,
        "signal",
        lambda signum, callback: (fallback_calls.append(signum), callback()),
    )
    runtime_worker._install_signal_handlers(stop_event, [runtime_worker.signal.SIGTERM])
    assert stop_event.is_set() is True
    assert fallback_calls == [runtime_worker.signal.SIGTERM]


@pytest.mark.asyncio
async def test_runtime_worker_run_and_main_cover_enabled_and_disabled_paths(monkeypatch):
    stop_event = asyncio.Event()

    monkeypatch.setattr(runtime_worker, "_env_enabled", lambda name, default="1": False)
    await runtime_worker._run(stop_event)

    tracker: list[str] = []
    stop_event = asyncio.Event()
    stop_event.set()

    monkeypatch.setattr(
        runtime_worker,
        "_env_enabled",
        lambda name, default="1": name in {"RUN_SIGNAL_MONITOR", "RUN_SIGNAL_FEED_SNAPSHOT_WORKER"},
    )
    monkeypatch.setattr(runtime_worker, "_initialize_runtime_state", lambda: tracker.append("init"))
    monkeypatch.setattr(
        runtime_worker.signal_monitor, "start", lambda: tracker.append("monitor-start")
    )
    monkeypatch.setattr(
        runtime_worker.signal_monitor, "stop", lambda: tracker.append("monitor-stop")
    )

    async def _start_feed():
        tracker.append("feed-start")

    async def _stop_feed():
        tracker.append("feed-stop")

    monkeypatch.setattr(runtime_worker, "start_signal_feed_snapshot_worker", _start_feed)
    monkeypatch.setattr(runtime_worker, "stop_signal_feed_snapshot_worker", _stop_feed)

    await runtime_worker._run(stop_event)
    assert tracker == ["init", "monitor-start", "feed-start", "feed-stop", "monitor-stop"]

    main_calls: list[str] = []

    async def _fake_run(event):
        main_calls.append("run")
        assert isinstance(event, asyncio.Event)

    monkeypatch.setattr(
        runtime_worker,
        "_install_signal_handlers",
        lambda event, signals: main_calls.append("signals"),
    )
    monkeypatch.setattr(runtime_worker, "_run", _fake_run)
    await runtime_worker.main()
    assert main_calls == ["signals", "run"]
