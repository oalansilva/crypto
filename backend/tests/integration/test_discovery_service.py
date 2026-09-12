"""Testes do discovery sweep service (card #469): preflight, criação
idempotente, lifecycle, claims/leases, leaderboard e promoção tier 3."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models_discovery import (
    DiscoveryCombination,
    DiscoveryOutbox,
    DiscoveryResult,
    DiscoverySweep,
)
from app.services.discovery_service import (
    DEFAULT_MAX_TOTAL,
    DiscoveryService,
    build_evidence_fingerprint,
    build_strategy_identity,
)
from database_guard import assert_safe_test_database_url


def _assert_safe_integration_database() -> None:
    assert_safe_test_database_url(
        os.environ["DATABASE_URL"],
        variable_name="DATABASE_URL",
        allow_github_disposable=True,
    )


@pytest.fixture(autouse=True)
def _mock_orchestrator_enqueue(monkeypatch):
    """Evita conexão real com o broker Celery nos testes: o dispatch da outbox
    registra a intenção; o enqueue real é exercitado no runtime worker."""
    from app.tasks import discovery_tasks

    monkeypatch.setattr(
        discovery_tasks, "enqueue_sweep_orchestrator", lambda sweep_id, generation: None
    )


@pytest.fixture(autouse=True)
def _discovery_tables(monkeypatch):
    """Limpa tabelas discovery e evita o seed de templates do list_templates()
    (efeito colateral que contaminaria outros testes de integração que assumem
    catálogo vazio)."""
    from app.services.combo_service import ComboService

    _assert_safe_integration_database()

    def _fake_list_templates(*_a, **_k):
        return {
            "prebuilt": [],
            "examples": [{"name": "multi_ma_crossover", "direction": "long"}],
        }

    def _fake_get_template_metadata(_self, template_name):
        return {
            "name": template_name,
            "direction": "long",
            "indicators": [],
            "optimization_schema": {},
        }

    monkeypatch.setattr(ComboService, "list_templates", _fake_list_templates)
    monkeypatch.setattr(ComboService, "get_template_metadata", _fake_get_template_metadata)

    engine = create_engine(os.environ["DATABASE_URL"])
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "ALTER TABLE discovery_sweeps ADD COLUMN IF NOT EXISTS "
            "insufficient_sample INTEGER NOT NULL DEFAULT 0"
        )
        connection.exec_driver_sql(
            "ALTER TABLE discovery_results ALTER COLUMN eligibility TYPE VARCHAR(32)"
        )
        connection.exec_driver_sql("DELETE FROM discovery_dedup_evidence")
        connection.exec_driver_sql("DELETE FROM discovery_outbox")
        connection.exec_driver_sql("DELETE FROM discovery_results")
        connection.exec_driver_sql("DELETE FROM discovery_combinations")
        connection.exec_driver_sql("DELETE FROM discovery_sweeps")
        connection.exec_driver_sql("DELETE FROM discovery_idempotency")
        # Favoritos criados por promoção de teste não podem contaminar outros
        # testes de integração (ex.: refresh loop que conta favoritos).
        connection.exec_driver_sql("DELETE FROM favorite_strategies")
    yield engine
    engine.dispose()


def _session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_discovery_database_guard_rejects_non_test_database(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg2://root@/crypto_app_dev")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)

    with pytest.raises(RuntimeError, match="non-test database"):
        _assert_safe_integration_database()


def test_discovery_database_guard_allows_disposable_github_database(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres@127.0.0.1/postgres")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    _assert_safe_integration_database()


def _preflight_payload(service: DiscoveryService) -> dict:
    result = service.preflight(
        templates=["multi_ma_crossover"],
        symbols=["BTCUSDT"],
        timeframes=["1d"],
        directions=["long"],
        start_date="2024-01-01",
        end_date="2024-12-31",
        period_type="all",
    )
    assert result["valid_total"] >= 1, result.get("errors")
    return result


class TestPreflight:
    def test_preflight_normalizes_axes_and_reports_total(self, monkeypatch):
        from app.services.combo_service import ComboService

        def fake_list(*_a, **_k):
            return {
                "prebuilt": [],
                "examples": [{"name": "multi_ma_crossover", "direction": "long"}],
            }

        monkeypatch.setattr(ComboService, "list_templates", fake_list)
        service = DiscoveryService()
        service.combo_service = ComboService()
        monkeypatch.setattr(service.combo_service, "list_templates", fake_list)

        result = service.preflight(
            templates=["multi_ma_crossover"],
            symbols=["btcusdt", "BTCUSDT", " ethusdt "],
            timeframes=["1d"],
            directions=["long"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            period_type=None,
        )
        assert result["raw_total"] == 2
        assert result["axes"]["symbols"] == ["BTCUSDT", "ETHUSDT"]
        assert result["snapshot_token"]
        assert result["snapshot_hash"]
        assert result["valid_total"] == 2
        assert result["start_date"] == "2024-01-01"
        assert result["end_date"] == "2024-12-31"
        assert result["period_type"] is None

    def test_preflight_rejects_unsupported_timeframe(self, monkeypatch):
        service = DiscoveryService()
        result = service.preflight(
            templates=["multi_ma_crossover"],
            symbols=["BTCUSDT"],
            timeframes=["15m"],
            directions=["long"],
            start_date=None,
            end_date=None,
            period_type=None,
        )
        assert result["errors"].get("timeframes")


class TestCreateSweepIdempotency:
    def test_create_retry_returns_same_sweep(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["1d"],
            "directions": ["long"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "period_type": "all",
            "snapshot_hash": preflight["snapshot_hash"],
        }
        key = f"k-{uuid.uuid4().hex[:12]}"
        first, status = service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        assert status == 201
        second, status2 = service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        assert status2 == 200
        assert second["sweep_id"] == first["sweep_id"]
        assert second["idempotent_retry"] is True
        db.close()

    def test_create_retry_with_reordered_axes_is_idempotent(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        from app.services.discovery_service import _payload_hash

        left = {
            "templates": ["b", "a"],
            "symbols": ["ethusdt", "BTCUSDT"],
            "timeframes": ["1d", "4h"],
            "directions": ["short", "long"],
        }
        right = {
            "templates": ["a", "b"],
            "symbols": ["BTCUSDT", "ETHUSDT"],
            "timeframes": ["4h", "1d"],
            "directions": ["long", "short"],
        }
        assert _payload_hash(left) == _payload_hash(right)

        preflight = service.preflight(
            templates=["multi_ma_crossover"],
            symbols=["BTCUSDT"],
            timeframes=["4h", "1d"],
            directions=["long"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            period_type="all",
        )
        assert preflight["valid_total"] >= 1, preflight.get("errors")
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["1d", "4h"],
            "directions": ["long"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "period_type": "all",
            "snapshot_hash": preflight["snapshot_hash"],
        }
        key = f"k-{uuid.uuid4().hex[:12]}"
        first, status = service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        assert status == 201
        reordered = dict(payload)
        reordered["timeframes"] = ["4h", "1d"]
        second, status2 = service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight["snapshot_token"],
            payload=reordered,
            db=db,
        )
        assert status2 == 200
        assert second["sweep_id"] == first["sweep_id"]
        assert second["idempotent_retry"] is True
        db.close()

    def test_create_divergent_hash_returns_409(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["1d"],
            "directions": ["long"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "period_type": "all",
            "snapshot_hash": preflight["snapshot_hash"],
        }
        key = f"k-{uuid.uuid4().hex[:12]}"
        service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        divergent = dict(payload)
        divergent["symbols"] = ["ETHUSDT"]
        body, status = service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight["snapshot_token"],
            payload=divergent,
            db=db,
        )
        assert status == 409
        assert "idempotency conflict" in body["error"]
        db.close()

    def test_stale_snapshot_token_rejected(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["1d"],
            "directions": ["long"],
            "period_type": "all",
            "snapshot_hash": "deadbeef",
        }
        body, status = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token="invalid-token",
            payload=payload,
            db=db,
        )
        assert status in (400, 409)
        db.close()


def _start_payload_for(service: DiscoveryService, symbols: list[str]) -> tuple[dict, dict]:
    preflight = service.preflight(
        templates=["multi_ma_crossover"],
        symbols=symbols,
        timeframes=["1d"],
        directions=["long"],
        start_date="2024-01-01",
        end_date="2024-12-31",
        period_type="all",
    )
    assert preflight["valid_total"] >= 1, preflight.get("errors")
    payload = {
        "templates": ["multi_ma_crossover"],
        "symbols": symbols,
        "timeframes": ["1d"],
        "directions": ["long"],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "period_type": "all",
        "snapshot_hash": preflight["snapshot_hash"],
    }
    return payload, preflight


def _terminate_sweep(service: DiscoveryService, db, sweep_id: str) -> None:
    from app.tasks.discovery_tasks import reconcile_sweep

    service.command(sweep_id, "cancel", db)
    summary = reconcile_sweep(sweep_id, db)
    assert summary["state"] == "cancelled", summary


class TestStartAfterTerminal:
    """Iniciar começa a varredura da seleção atual (card #837)."""

    def test_post_terminal_same_selection_same_key_creates_new_sweep(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        payload, preflight = _start_payload_for(service, ["BTCUSDT"])
        key = f"k-{uuid.uuid4().hex[:12]}"
        first, status = service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        assert status == 201
        assert first["idempotency_key"] == key
        _terminate_sweep(service, db, first["sweep_id"])

        payload2, preflight2 = _start_payload_for(service, ["BTCUSDT"])
        second, status2 = service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight2["snapshot_token"],
            payload=payload2,
            db=db,
        )
        assert status2 == 201, second
        assert second["sweep_id"] != first["sweep_id"]
        assert second["idempotency_key"] != key
        dead = db.query(DiscoverySweep).filter(DiscoverySweep.id == first["sweep_id"]).first()
        assert dead.state == "cancelled"
        db.close()

    def test_post_terminal_changed_selection_same_key_creates_new_sweep(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        payload, preflight = _start_payload_for(service, ["BTCUSDT"])
        key = f"k-{uuid.uuid4().hex[:12]}"
        first, status = service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        assert status == 201
        assert first["idempotency_key"] == key
        _terminate_sweep(service, db, first["sweep_id"])

        payload2, preflight2 = _start_payload_for(service, ["ETHUSDT"])
        second, status2 = service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight2["snapshot_token"],
            payload=payload2,
            db=db,
        )
        assert status2 == 201, second
        assert second["sweep_id"] != first["sweep_id"]
        db.close()

    def test_live_other_selection_new_key_blocked_with_guidance(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        payload, preflight = _start_payload_for(service, ["BTCUSDT"])
        first, status = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        assert status == 201

        payload2, preflight2 = _start_payload_for(service, ["ETHUSDT"])
        body, status2 = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight2["snapshot_token"],
            payload=payload2,
            db=db,
        )
        assert status2 == 409, body
        assert "cancele" in body["detail"].lower()
        assert "{" not in body["detail"]
        count = db.query(DiscoverySweep).filter(DiscoverySweep.actor == "admin-1").count()
        assert count == 1
        db.close()

    def test_live_same_selection_new_key_returns_existing(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        payload, preflight = _start_payload_for(service, ["BTCUSDT"])
        first, status = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        assert status == 201

        payload2, preflight2 = _start_payload_for(service, ["BTCUSDT"])
        second, status2 = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight2["snapshot_token"],
            payload=payload2,
            db=db,
        )
        assert status2 == 200, second
        assert second["sweep_id"] == first["sweep_id"]
        assert second["idempotent_retry"] is True
        assert second["idempotency_key"] == first["idempotency_key"]
        count = db.query(DiscoverySweep).filter(DiscoverySweep.actor == "admin-1").count()
        assert count == 1
        db.close()

    def test_commit_integrity_error_resolves_to_live_guidance(self, engine_factory, monkeypatch):
        """IntegrityError no commit cai no caminho de reconciliação (card #837).

        Simula a corrida de unicidade (actor, key): o commit falha, o handler
        reencontra a live com hash divergente e devolve 409 operacional.
        """
        from sqlalchemy.exc import IntegrityError

        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        payload, preflight = _start_payload_for(service, ["BTCUSDT"])
        first, status = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        assert status == 201

        payload2, preflight2 = _start_payload_for(service, ["ETHUSDT"])
        real_commit = db.commit
        calls = {"n": 0}

        def _fail_first_commit():
            calls["n"] += 1
            if calls["n"] == 1:
                raise IntegrityError(
                    "INSERT INTO discovery_sweep", {}, Exception("duplicate key value")
                )
            return real_commit()

        monkeypatch.setattr(db, "commit", _fail_first_commit)
        body, status2 = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight2["snapshot_token"],
            payload=payload2,
            db=db,
        )
        assert status2 == 409, body
        assert body["error"] == "live sweep in progress"
        assert "cancele" in body["detail"].lower()
        count = db.query(DiscoverySweep).filter(DiscoverySweep.actor == "admin-1").count()
        assert count == 1
        db.close()

    def test_commit_unexpected_error_propagates(self, engine_factory, monkeypatch):
        """Erro de commit que não é IntegrityError faz raise (card #837)."""
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()

        def _boom():
            raise RuntimeError("connection lost")

        monkeypatch.setattr(db, "commit", _boom)
        # Actor fresco e único, sem live prévia: o fluxo passa pelos checks
        # (seção crítica estreita não barra) e chega ao insert/commit mockado.
        fresh_actor = f"admin-1-boom-{uuid.uuid4().hex[:12]}"
        payload2, preflight2 = _start_payload_for(service, ["ETHUSDT"])
        with pytest.raises(RuntimeError, match="connection lost"):
            service.create_sweep(
                actor=fresh_actor,
                idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
                snapshot_token=preflight2["snapshot_token"],
                payload=payload2,
                db=db,
            )
        db.close()

    def test_advisory_lock_is_noop_off_postgres(self, engine_factory):
        """O lock por actor não quebra dialetos sem pg_advisory (card #837).

        A chave do lock é única por teste: no CI o banco é PostgreSQL e o
        ramo PG executa de verdade, então reutilizar `admin-1` (chave
        compartilhada com os demais testes) contendia o advisory lock até o
        Timeout. Com actor único ninguém mais detém a chave.
        """
        import time

        from app.services.discovery_service import _acquire_actor_create_lock

        engine = engine_factory()
        db = _session_factory(engine)()
        unique_actor = f"admin-1-lock-{uuid.uuid4().hex[:12]}"
        try:
            dialect = getattr(getattr(db.bind, "dialect", None), "name", "") or ""
            if dialect == "postgresql":
                started = time.monotonic()
                _acquire_actor_create_lock(db, unique_actor)  # não deve levantar
                elapsed = time.monotonic() - started
                # Chave única: a aquisição real retorna rápido; o limite é
                # folgado e só acusa contenção/regressão, nunca o caminho feliz.
                assert elapsed < 10
            else:
                _acquire_actor_create_lock(db, unique_actor)  # no-op: não deve levantar
            db.rollback()
        finally:
            db.close()

    def test_live_same_key_divergent_guides_cancel(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        payload, preflight = _start_payload_for(service, ["BTCUSDT"])
        key = f"k-{uuid.uuid4().hex[:12]}"
        _, status = service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        assert status == 201

        payload2, preflight2 = _start_payload_for(service, ["ETHUSDT"])
        body, status2 = service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight2["snapshot_token"],
            payload=payload2,
            db=db,
        )
        assert status2 == 409
        assert "idempotency conflict" in body["error"]
        assert "cancele" in body["detail"].lower()
        assert "{" not in body["detail"]
        assert "divergente" not in body["detail"].lower()
        db.close()

    def test_invalid_selection_failure_is_operational(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["15m"],
            "directions": ["long"],
            "period_type": "all",
            "snapshot_hash": "deadbeef",
        }
        body, status = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token="tok",
            payload=payload,
            db=db,
        )
        assert status == 400
        assert isinstance(body["detail"], str)
        assert "{" not in body["detail"]
        db.close()


class TestLifecycle:
    def test_transition_matrix_and_cancelling_prevails(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["1d"],
            "directions": ["long"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "period_type": "all",
            "snapshot_hash": preflight["snapshot_hash"],
        }
        body, _ = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        sweep_id = body["sweep_id"]
        sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == sweep_id).first()
        sweep.state = "running"  # dispatcher iniciou (pending -> running)
        db.commit()
        service.command(sweep_id, "pause", db)
        db.refresh(sweep)
        assert sweep.state == "paused"
        service.command(sweep_id, "resume", db)
        db.refresh(sweep)
        assert sweep.state == "running"
        # Com voo em curso o cancel permanece `cancelling` (Q1): o inline
        # reconcile não força `running` a `skipped` (card #853).
        claimed = service.claim_combinations(sweep_id, owner="w1", db=db)
        assert len(claimed) == 1
        body_c, status_c = service.command(sweep_id, "cancel", db)
        assert status_c == 200
        assert body_c["state"] == "cancelling"
        db.refresh(sweep)
        assert sweep.state == "cancelling"
        db.refresh(claimed[0])
        assert claimed[0].state == "running"
        # Repeat-cancel passa pelo ensure sem duplicar o finalizador em aberto.
        outstanding_before = (
            db.query(DiscoveryOutbox)
            .filter(
                DiscoveryOutbox.sweep_id == sweep_id,
                DiscoveryOutbox.state.in_(("pending", "delivered")),
            )
            .count()
        )
        assert outstanding_before == 1
        body_r, status_r = service.command(sweep_id, "cancel", db)
        assert status_r == 200
        assert body_r["state"] == "cancelling"
        outstanding_after = (
            db.query(DiscoveryOutbox)
            .filter(
                DiscoveryOutbox.sweep_id == sweep_id,
                DiscoveryOutbox.state.in_(("pending", "delivered")),
            )
            .count()
        )
        assert outstanding_after == 1
        body2, status = service.command(sweep_id, "pause", db)
        assert status == 409
        assert "cancelling prevails" in body2["error"]
        db.close()

    def test_terminal_state_rejects_commands(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["1d"],
            "directions": ["long"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "period_type": "all",
            "snapshot_hash": preflight["snapshot_hash"],
        }
        body, _ = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        sweep_id = body["sweep_id"]
        # Com voo em curso o cancel fica `cancelling` (sem voo fecharia inline
        # a `cancelled` — card #853); resume segue rejeitado e o estado fica.
        claimed = service.claim_combinations(sweep_id, owner="w1", db=db)
        assert len(claimed) == 1
        body_c, status_c = service.command(sweep_id, "cancel", db)
        assert status_c == 200
        assert body_c["state"] == "cancelling"
        body_r, status_r = service.command(sweep_id, "resume", db)
        assert status_r == 409
        db.refresh(db.query(DiscoverySweep).filter(DiscoverySweep.id == sweep_id).first())
        sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == sweep_id).first()
        assert sweep.state == "cancelling"  # resume rejeitado, permanece cancelling
        # Settle do voo + reconcile fecha a `cancelled`; comando em terminal
        # é no-op idempotente (rascunho libera via estado terminal).
        for combo in claimed:
            db.refresh(combo)
            combo.state = "succeeded"
            combo.result_id = "RS-TERM-1"
        db.commit()
        from app.tasks.discovery_tasks import reconcile_sweep as _reconcile

        summary = _reconcile(sweep_id, db)
        assert summary["state"] == "cancelled"
        body_t, status_t = service.command(sweep_id, "resume", db)
        assert status_t == 200
        assert body_t["state"] == "cancelled"
        db.close()


class TestClaimsAndOutbox:
    def test_claim_respects_sweep_state(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", lambda *a, **k: None)
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["1d"],
            "directions": ["long"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "period_type": "all",
            "snapshot_hash": preflight["snapshot_hash"],
        }
        body, _ = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        sweep_id = body["sweep_id"]
        # O dispatcher já iniciou (pending -> running) no create.
        assert body["state"] == "running"
        claimed = service.claim_combinations(sweep_id, owner="w1", db=db)
        assert len(claimed) >= 1
        # Segunda claim não reclama a mesma combinação (lease ativa).
        claimed2 = service.claim_combinations(sweep_id, owner="w2", db=db)
        assert claimed2 == []
        db.close()

    def test_lease_expiry_recovers_pending(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["1d"],
            "directions": ["long"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "period_type": "all",
            "snapshot_hash": preflight["snapshot_hash"],
        }
        body, _ = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        sweep_id = body["sweep_id"]
        service.command(sweep_id, "resume", db)
        claimed = service.claim_combinations(sweep_id, owner="w1", db=db)
        combo = claimed[0]
        combo.lease_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
        recovered = service.release_expired_leases(db=db)
        assert recovered >= 1
        db.refresh(combo)
        assert combo.state == "pending"
        db.close()

    def test_outbox_dispatches_within_limits(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks

        calls = []
        monkeypatch.setattr(
            discovery_tasks,
            "enqueue_sweep_orchestrator",
            lambda s, g: calls.append((s, g)),
        )
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["1d"],
            "directions": ["long"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "period_type": "all",
            "snapshot_hash": preflight["snapshot_hash"],
        }
        body, _ = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        sweep_id = body["sweep_id"]
        # O dispatcher entregou o wake-up do orquestrador no create.
        assert any(s == sweep_id for s, _ in calls), calls
        intent = db.query(DiscoveryOutbox).filter(DiscoveryOutbox.sweep_id == sweep_id).first()
        assert intent is not None
        assert intent.state == "delivered"
        assert service.ack_outbox(sweep_id, intent.generation, db=db) == 1
        db.refresh(intent)
        assert intent.state == "acked"
        assert intent.acked_at is not None
        db.close()

    def test_outbox_stays_pending_when_broker_publish_fails(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks

        def _broker_down(*_args, **_kwargs):
            raise ConnectionError("broker unavailable")

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", _broker_down)
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["1d"],
            "directions": ["long"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "period_type": "all",
            "snapshot_hash": preflight["snapshot_hash"],
        }

        body, status = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )

        assert status == 201
        intent = db.query(DiscoveryOutbox).filter_by(sweep_id=body["sweep_id"]).one()
        assert intent.state == "pending"
        assert intent.attempts == 1
        db.close()


class TestIdentityAndLeaderboard:
    def test_identity_key_excludes_window(self):
        identity_a = build_strategy_identity(
            template_id="t1",
            parameters={"fast": 7, "slow": 25},
            symbol="BTCUSDT",
            timeframe="1d",
            direction="long",
        )
        identity_b = build_strategy_identity(
            template_id="t1",
            parameters={"fast": 7, "slow": 25},
            symbol="BTCUSDT",
            timeframe="1d",
            direction="long",
        )
        assert identity_a == identity_b

    def test_identity_key_differs_on_direction(self):
        identity_a = build_strategy_identity(
            template_id="t1",
            parameters={"fast": 7},
            symbol="BTCUSDT",
            timeframe="1d",
            direction="long",
        )
        identity_b = build_strategy_identity(
            template_id="t1",
            parameters={"fast": 7},
            symbol="BTCUSDT",
            timeframe="1d",
            direction="short",
        )
        assert identity_a != identity_b

    def test_evidence_fingerprint_differs_on_window(self):
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        fp_a = build_evidence_fingerprint(
            start_at=start,
            end_at=start + timedelta(days=365),
            candle_source="ccxt",
            candle_version="v1",
            expected_candles=365,
            observed_valid_candles=365,
            coverage=1.0,
            fees_slippage={"fees": 0.001},
            metrics={"sharpe": 1.0},
        )
        fp_b = build_evidence_fingerprint(
            start_at=start,
            end_at=start + timedelta(days=180),
            candle_source="ccxt",
            candle_version="v1",
            expected_candles=180,
            observed_valid_candles=180,
            coverage=1.0,
            fees_slippage={"fees": 0.001},
            metrics={"sharpe": 1.0},
        )
        assert fp_a != fp_b

    def test_rank_eligible_deterministic(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        sweep_id = f"sw-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        rows = [(f"RS-{i:04d}", 2.84, 44 + (i % 2), now) for i in range(1048, 1050)]
        for result_id, calmar, trades, created in rows:
            db.add(
                DiscoveryResult(
                    id=result_id,
                    sweep_id=sweep_id,
                    combination_id=int(result_id[3:]),
                    template_id="t1",
                    symbol="BTCUSDT",
                    timeframe="1d",
                    direction="long",
                    parameters={},
                    start_at=now,
                    end_at=now + timedelta(days=1),
                    metrics={},
                    trades_count=trades,
                    calmar_ratio=calmar,
                    strategy_identity_key=f"id-{result_id}",
                    evidence_fingerprint=f"fp-{result_id}",
                    eligibility="eligible",
                    dedup_state="unique",
                )
            )
        db.commit()
        ranked = service.rank_eligible(sweep_id, metric="calmar_ratio", db=db)
        # RS-1049 (45 trades) antes de RS-1048 (44 trades) apesar do ID maior.
        assert [r["result_id"] for r in ranked] == ["RS-1049", "RS-1048"]
        assert ranked[0]["rank"] == 1
        db.close()

    def test_rank_eligible_go_class_precedes_nogo_and_exposes_verdict(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        sweep_id = f"sw-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        specs = [
            (
                "RS-B109ED2C80",
                "ALPHA/USDT",
                22.0,
                30,
                {"oos_verdict": {"status": "NO-GO", "reasons": ["Sharpe IS 0,31"]}},
            ),
            (
                "RS-896-01",
                "BTC/USDT",
                1.20,
                42,
                {"oos_verdict": {"status": "GO", "reasons": ["ok"]}},
            ),
            (
                "RS-896-02",
                "ETH/USDT",
                0.94,
                44,
                {"oos_verdict": {"status": "GO"}},
            ),
            (
                "RS-896-NA",
                "ARPA/USDT",
                1.195e27,
                31,
                {"oos_verdict": {"status": "NO-GO"}},
            ),
            (
                "RS-896-MISS",
                "SOL/USDT",
                50.0,
                40,
                {},
            ),
        ]
        for i, (rid, symbol, calmar, trades, metrics) in enumerate(specs):
            db.add(
                DiscoveryResult(
                    id=rid,
                    sweep_id=sweep_id,
                    combination_id=896000 + i,
                    template_id="t1",
                    symbol=symbol,
                    timeframe="1d",
                    direction="long",
                    parameters={},
                    start_at=now,
                    end_at=now + timedelta(days=1),
                    metrics=metrics,
                    trades_count=trades,
                    calmar_ratio=calmar,
                    strategy_identity_key=f"id-{rid}",
                    evidence_fingerprint=f"fp-{rid}",
                    eligibility="eligible",
                    dedup_state="unique",
                )
            )
        db.commit()
        ranked = service.rank_eligible(sweep_id, metric="calmar_ratio", db=db)
        ids = [r["result_id"] for r in ranked]
        assert ids[:2] == ["RS-896-01", "RS-896-02"]
        assert ids.index("RS-B109ED2C80") > ids.index("RS-896-01")
        assert ids.index("RS-B109ED2C80") > ids.index("RS-896-02")
        assert ids.index("RS-896-MISS") > ids.index("RS-896-02")
        assert ids[-1] == "RS-896-NA"
        assert ranked[0]["rank"] == 1
        assert ranked[0]["oos_verdict"]["status"] == "GO"
        assert ranked[0]["calmar_ratio"] == pytest.approx(1.20)
        alpha = next(r for r in ranked if r["result_id"] == "RS-B109ED2C80")
        assert alpha["oos_verdict"]["status"] == "NO-GO"
        assert alpha["rank"] > 2
        missing = next(r for r in ranked if r["result_id"] == "RS-896-MISS")
        assert missing["oos_verdict"] is None
        na = next(r for r in ranked if r["result_id"] == "RS-896-NA")
        assert na["rank"] == 5
        db.close()

    def test_two_nogos_keep_calmar_then_trades_then_id(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        sweep_id = f"sw-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        for i, (rid, calmar, trades) in enumerate(
            (("RS-N2", 3.0, 30), ("RS-N1", 3.0, 45), ("RS-N0", 8.0, 30))
        ):
            db.add(
                DiscoveryResult(
                    id=rid,
                    sweep_id=sweep_id,
                    combination_id=896100 + i,
                    template_id="t1",
                    symbol="BTCUSDT",
                    timeframe="1d",
                    direction="long",
                    parameters={},
                    start_at=now,
                    end_at=now + timedelta(days=1),
                    metrics={"oos_verdict": {"status": "NO-GO"}},
                    trades_count=trades,
                    calmar_ratio=calmar,
                    strategy_identity_key=f"id-{rid}",
                    evidence_fingerprint=f"fp-{rid}",
                    eligibility="eligible",
                    dedup_state="unique",
                )
            )
        db.commit()
        ranked = service.rank_eligible(sweep_id, metric="calmar_ratio", db=db)
        assert [r["result_id"] for r in ranked] == ["RS-N0", "RS-N1", "RS-N2"]
        db.close()

    def test_leaderboard_filters_pagination_and_ineligible(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        sweep_id = f"sw-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        specs = [
            ("RS-A", "BTCUSDT", "1d", "long", 3.0, 45, "eligible", "unique"),
            ("RS-B", "BTCUSDT", "4h", "long", 2.5, 40, "eligible", "unique"),
            ("RS-C", "ETHUSDT", "1d", "short", 1.8, 33, "eligible", "unique"),
            ("RS-D", "SOLUSDT", "4h", "long", 1.2, 18, "low_sample", "unique"),
        ]
        for i, (
            rid,
            symbol,
            timeframe,
            direction,
            calmar,
            trades,
            elig,
            dedup,
        ) in enumerate(specs):
            db.add(
                DiscoveryResult(
                    id=rid,
                    sweep_id=sweep_id,
                    combination_id=950000 + i,
                    template_id="t1",
                    symbol=symbol,
                    timeframe=timeframe,
                    direction=direction,
                    parameters={},
                    start_at=now,
                    end_at=now + timedelta(days=1),
                    metrics={},
                    trades_count=trades,
                    calmar_ratio=calmar,
                    strategy_identity_key=f"id-{rid}",
                    evidence_fingerprint=f"fp-{rid}",
                    eligibility=elig,
                    dedup_state=dedup,
                )
            )
        db.commit()

        # Ranking global: elegíveis ranqueados (RS-A > RS-B > RS-C); ineligible
        # aparece por último com rank None (não re-numera posições).
        rows, total, unfiltered_total = service.leaderboard(sweep_id, metric="calmar_ratio", db=db)
        assert total == 4
        assert unfiltered_total == 4
        assert [r["result_id"] for r in rows] == ["RS-A", "RS-B", "RS-C", "RS-D"]
        assert [r["rank"] for r in rows] == [1, 2, 3, None]

        # Filtro por símbolo (aceita "BTC/USDT" e "BTCUSDT").
        rows, total, unfiltered_total = service.leaderboard(
            sweep_id, metric="calmar_ratio", symbol="BTC/USDT", db=db
        )
        assert total == 2
        assert unfiltered_total == 4
        assert [r["result_id"] for r in rows] == ["RS-A", "RS-B"]

        # Filtro por timeframe + direção.
        rows, total, unfiltered_total = service.leaderboard(
            sweep_id, metric="calmar_ratio", timeframe="1d", direction="short", db=db
        )
        assert total == 1
        assert unfiltered_total == 4
        assert rows[0]["result_id"] == "RS-C"

        rows, total, unfiltered_total = service.leaderboard(
            sweep_id, metric="calmar_ratio", eligibility="low_sample", db=db
        )
        assert total == 1
        assert unfiltered_total == 4
        assert rows[0]["result_id"] == "RS-D"
        assert rows[0]["rank"] is None

        # Paginação preserva rank global e total do recorte filtrado.
        rows, total, unfiltered_total = service.leaderboard(
            sweep_id, metric="calmar_ratio", offset=1, limit=2, db=db
        )
        assert total == 4
        assert unfiltered_total == 4
        assert [r["result_id"] for r in rows] == ["RS-B", "RS-C"]
        assert [r["rank"] for r in rows] == [2, 3]
        db.close()

    def test_insufficient_sample_on_decidir_and_excluded_from_partials(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        sweep_id = f"sw-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        specs = [
            ("RS-E", "BTCUSDT", 3.0, 45, "eligible"),
            ("RS-L", "ADAUSDT", 3.2, 18, "low_sample"),
            ("RS-I", "BLZUSDT", None, None, "insufficient_sample"),
        ]
        for i, (rid, symbol, calmar, trades, elig) in enumerate(specs):
            db.add(
                DiscoveryResult(
                    id=rid,
                    sweep_id=sweep_id,
                    combination_id=960000 + i,
                    template_id="t1",
                    symbol=symbol,
                    timeframe="1d",
                    direction="long",
                    parameters={},
                    start_at=now,
                    end_at=now + timedelta(days=1),
                    metrics={},
                    trades_count=trades,
                    calmar_ratio=calmar,
                    max_drawdown=None if elig == "insufficient_sample" else 0.15,
                    coverage=None if elig == "insufficient_sample" else 0.97,
                    strategy_identity_key=f"id-{rid}",
                    evidence_fingerprint=f"fp-{rid}",
                    eligibility=elig,
                    dedup_state="unique",
                )
            )
        db.commit()
        rows, total, unfiltered_total = service.leaderboard(sweep_id, metric="calmar_ratio", db=db)
        by_id = {r["result_id"]: r for r in rows}
        assert total == 3
        assert unfiltered_total == 3
        assert by_id["RS-I"]["rank"] is None
        assert by_id["RS-I"]["eligibility"] == "insufficient_sample"
        assert by_id["RS-I"]["calmar_ratio"] is None
        assert by_id["RS-I"]["trades_count"] is None
        assert by_id["RS-E"]["rank"] == 1
        assert by_id["RS-L"]["rank"] is None

        partials, ptotal, _ = service.leaderboard(
            sweep_id,
            metric="calmar_ratio",
            exclude_eligibility="insufficient_sample",
            limit=5,
            db=db,
        )
        assert all(r["eligibility"] != "insufficient_sample" for r in partials)
        assert [r["result_id"] for r in partials] == ["RS-E", "RS-L"]
        assert ptotal == 2
        db.close()

    def test_result_row_exposes_strategy_identity_fields(self):
        from app.services.strategy_descriptions import resolve_strategy_identity

        service = DiscoveryService()
        now = datetime.now(timezone.utc)
        identity_map = {
            "multi_ma_crossover": resolve_strategy_identity("multi_ma_crossover"),
            "card549_unknown_template": resolve_strategy_identity("card549_unknown_template"),
        }
        mapped_row = DiscoveryResult(
            id="RS-MAP",
            sweep_id="sw-identity",
            combination_id=960001,
            template_id="multi_ma_crossover",
            symbol="BTCUSDT",
            timeframe="1d",
            direction="long",
            parameters={},
            start_at=now,
            end_at=now + timedelta(days=1),
            metrics={},
            trades_count=45,
            calmar_ratio=3.0,
            strategy_identity_key="id-map",
            evidence_fingerprint="fp-map",
            eligibility="eligible",
            dedup_state="unique",
        )
        raw_row = DiscoveryResult(
            id="RS-RAW",
            sweep_id="sw-identity",
            combination_id=960002,
            template_id="card549_unknown_template",
            symbol="BTCUSDT",
            timeframe="1d",
            direction="long",
            parameters={},
            start_at=now,
            end_at=now + timedelta(days=1),
            metrics={},
            trades_count=40,
            calmar_ratio=2.0,
            strategy_identity_key="id-raw",
            evidence_fingerprint="fp-raw",
            eligibility="eligible",
            dedup_state="unique",
        )

        mapped = service._result_row(mapped_row, 1, identity_map=identity_map)
        raw = service._result_row(raw_row, 2, identity_map=identity_map)

        assert mapped["display_name"] == "Médias Móveis: Tendência em Virada"
        assert mapped["description"]
        assert "média curta" in mapped["description"].lower()
        assert mapped["template_id"] == "multi_ma_crossover"
        assert mapped["rank"] == 1

        assert raw["display_name"] == "card549_unknown_template"
        assert raw["description"]
        assert raw["display_name"] != "Estratégia Cripto Farol"
        assert raw["rank"] == 2

    def test_leaderboard_omits_discarded_results(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        now = datetime.now(timezone.utc)
        sweep_id = "sw-discard-lb"
        db.add(
            DiscoverySweep(
                id=sweep_id,
                actor="admin-1",
                state="completed",
                idempotency_key="disc-lb-1",
                payload_hash="a" * 64,
                snapshot_token="tok",
                snapshot_hash="b" * 64,
                snapshot={},
                total=2,
                succeeded=2,
            )
        )
        for rid, state, calmar, cid in (
            ("RS-KEEP", "unique", 2.0, 700001),
            ("RS-DROP", "discarded", 9.0, 700002),
        ):
            db.add(
                DiscoveryResult(
                    id=rid,
                    sweep_id=sweep_id,
                    combination_id=cid,
                    template_id="t1",
                    symbol="BTCUSDT",
                    timeframe="1d",
                    direction="long",
                    parameters={},
                    start_at=now,
                    end_at=now + timedelta(days=1),
                    metrics={},
                    trades_count=40,
                    calmar_ratio=calmar,
                    strategy_identity_key=f"id-{rid}",
                    evidence_fingerprint=f"fp-{rid}",
                    eligibility="eligible",
                    dedup_state=state,
                )
            )
        db.commit()
        rows, total, unfiltered = service.leaderboard(sweep_id, db=db)
        assert [r["result_id"] for r in rows] == ["RS-KEEP"]
        assert total == 1
        assert unfiltered == 1
        assert rows[0]["rank"] == 1
        db.close()


@pytest.fixture
def engine_factory():
    def _factory():
        engine = create_engine(os.environ["DATABASE_URL"])
        Base.metadata.create_all(bind=engine)
        return engine

    return _factory


class TestPromotion:
    def test_promote_creates_tier3_favorite_and_is_idempotent(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        now = datetime.now(timezone.utc)
        result = DiscoveryResult(
            id="RS-PRO-1",
            sweep_id="sw-promo",
            combination_id=999001,
            template_id="multi_ma_crossover",
            symbol="BTCUSDT",
            timeframe="1d",
            direction="long",
            parameters={"fast": 7},
            start_at=now,
            end_at=now + timedelta(days=30),
            metrics={"sharpe": 1.2},
            trades_count=45,
            calmar_ratio=2.5,
            strategy_identity_key="id-promo-1",
            evidence_fingerprint="fp-promo-1",
            eligibility="eligible",
            dedup_state="unique",
        )
        db.add(result)
        db.commit()

        from app.models import FavoriteStrategy

        payload = {"tier": 3, "result_id": "RS-PRO-1"}
        key = f"p-{uuid.uuid4().hex[:12]}"
        body, status = service.promote_result(
            result_id="RS-PRO-1",
            actor="admin-1",
            idempotency_key=key,
            payload=payload,
            db=db,
        )
        assert status == 201
        favorite_id = body["favorite_id"]
        favorite = (
            db.query(FavoriteStrategy).filter(FavoriteStrategy.id == int(favorite_id)).first()
        )
        assert favorite is not None
        assert favorite.tier == 3

        retry, status2 = service.promote_result(
            result_id="RS-PRO-1",
            actor="admin-1",
            idempotency_key=key,
            payload=payload,
            db=db,
        )
        assert status2 == 200
        assert retry["favorite_id"] == favorite_id
        db.close()

    def test_promote_copies_snapshot_onto_grid_keys(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        now = datetime.now(timezone.utc)
        snapshot = {
            "sharpe_ratio": 0.31,
            "win_rate": 0.467,
            "total_return": 169.51,
            "total_return_pct": 16951,
            "max_drawdown": 0.165,
            "total_trades": 30,
            "profit_factor": 1.42,
        }
        result = DiscoveryResult(
            id="RS-B109ED2C80",
            sweep_id="sw-promo-193",
            combination_id=999193,
            template_id="bollinger_breakout",
            symbol="ALPHA/USDT",
            timeframe="1d",
            direction="long",
            parameters={"window": 20},
            start_at=datetime(2020, 10, 10, tzinfo=timezone.utc),
            end_at=datetime(2024, 2, 1, tzinfo=timezone.utc),
            metrics=snapshot,
            trades_count=30,
            win_rate=0.467,
            sharpe_ratio=0.31,
            profit_factor=1.42,
            max_drawdown=0.165,
            strategy_identity_key="id-promo-193",
            evidence_fingerprint="fp-promo-193",
            eligibility="eligible",
            dedup_state="unique",
        )
        db.add(result)
        db.commit()

        from app.models import FavoriteStrategy

        body, status = service.promote_result(
            result_id="RS-B109ED2C80",
            actor="admin-1",
            idempotency_key=f"p-{uuid.uuid4().hex[:12]}",
            payload={"tier": 3, "result_id": "RS-B109ED2C80"},
            db=db,
        )
        assert status == 201
        favorite = (
            db.query(FavoriteStrategy)
            .filter(FavoriteStrategy.id == int(body["favorite_id"]))
            .first()
        )
        metrics = favorite.metrics
        assert metrics["origin_type"] == "discovery_sweep"
        assert metrics["sweep_id"] == "sw-promo-193"
        assert metrics["result_id"] == "RS-B109ED2C80"
        assert metrics["strategy_identity_key"] == "id-promo-193"
        assert metrics["metrics_snapshot"]["sharpe_ratio"] == 0.31
        assert metrics["sharpe_ratio"] == 0.31
        assert metrics["total_trades"] == 30
        assert metrics["win_rate"] == 0.467
        assert metrics["total_return_pct"] == 16951
        assert metrics["max_drawdown"] == 0.165
        assert metrics["profit_factor"] == 1.42
        db.close()

    def test_promote_rejects_other_tier(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        now = datetime.now(timezone.utc)
        db.add(
            DiscoveryResult(
                id="RS-PRO-2",
                sweep_id="sw-promo2",
                combination_id=999002,
                template_id="t1",
                symbol="BTCUSDT",
                timeframe="1d",
                direction="long",
                parameters={},
                start_at=now,
                end_at=now + timedelta(days=30),
                metrics={},
                trades_count=40,
                strategy_identity_key="id-promo-2",
                evidence_fingerprint="fp-promo-2",
                eligibility="eligible",
                dedup_state="unique",
            )
        )
        db.commit()
        body, status = service.promote_result(
            result_id="RS-PRO-2",
            actor="admin-1",
            idempotency_key=f"p-{uuid.uuid4().hex[:12]}",
            payload={"tier": 2, "result_id": "RS-PRO-2"},
            db=db,
        )
        assert status == 422
        assert "tier must be 3" in body["error"]
        db.close()

    def test_promote_low_sample_rejected(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        now = datetime.now(timezone.utc)
        db.add(
            DiscoveryResult(
                id="RS-PRO-3",
                sweep_id="sw-promo3",
                combination_id=999003,
                template_id="t1",
                symbol="BTCUSDT",
                timeframe="1d",
                direction="long",
                parameters={},
                start_at=now,
                end_at=now + timedelta(days=30),
                metrics={},
                trades_count=10,
                strategy_identity_key="id-promo-3",
                evidence_fingerprint="fp-promo-3",
                eligibility="low_sample",
                eligibility_reason="trades 10 < mínimo 30",
                dedup_state="unique",
            )
        )
        db.commit()
        body, status = service.promote_result(
            result_id="RS-PRO-3",
            actor="admin-1",
            idempotency_key=f"p-{uuid.uuid4().hex[:12]}",
            payload={"tier": 3, "result_id": "RS-PRO-3"},
            db=db,
        )
        assert status == 422
        assert "ineligible" in body["error"]
        db.close()

    def test_discard_persists_and_blocks_promote(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        now = datetime.now(timezone.utc)
        db.add(
            DiscoveryResult(
                id="RS-DSC-1",
                sweep_id="sw-dsc",
                combination_id=888001,
                template_id="t1",
                symbol="BTCUSDT",
                timeframe="1d",
                direction="long",
                parameters={},
                start_at=now,
                end_at=now + timedelta(days=30),
                metrics={},
                trades_count=40,
                calmar_ratio=1.5,
                strategy_identity_key="id-dsc-1",
                evidence_fingerprint="fp-dsc-1",
                eligibility="eligible",
                dedup_state="unique",
            )
        )
        db.commit()
        body, status = service.discard_result(result_id="RS-DSC-1", db=db)
        assert status == 200
        assert body["dedup_state"] == "discarded"
        again, status2 = service.discard_result(result_id="RS-DSC-1", db=db)
        assert status2 == 200
        promo, pstatus = service.promote_result(
            result_id="RS-DSC-1",
            actor="admin-1",
            idempotency_key=f"p-{uuid.uuid4().hex[:12]}",
            payload={"tier": 3, "result_id": "RS-DSC-1"},
            db=db,
        )
        assert pstatus == 422
        assert promo["error"] == "discarded"
        db.close()

    def test_discard_rejects_already_promoted(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        now = datetime.now(timezone.utc)
        db.add(
            DiscoveryResult(
                id="RS-DSC-2",
                sweep_id="sw-dsc",
                combination_id=888002,
                template_id="t1",
                symbol="ETHUSDT",
                timeframe="1d",
                direction="long",
                parameters={},
                start_at=now,
                end_at=now + timedelta(days=30),
                metrics={},
                trades_count=40,
                calmar_ratio=1.2,
                strategy_identity_key="id-dsc-2",
                evidence_fingerprint="fp-dsc-2",
                eligibility="eligible",
                dedup_state="already_promoted",
                dedup_reference="fav-1",
            )
        )
        db.commit()
        body, status = service.discard_result(result_id="RS-DSC-2", db=db)
        assert status == 409
        assert body["error"] == "already_promoted"
        db.close()


class TestReconcileTerminal:
    def test_cancel_skips_pending_and_processed_equals_total(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks
        from app.tasks.discovery_tasks import reconcile_sweep

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", lambda s, g: None)
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["1d"],
            "directions": ["long"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "period_type": "all",
            "snapshot_hash": preflight["snapshot_hash"],
        }
        body, _ = service.create_sweep(
            actor="admin-1",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            snapshot_token=preflight["snapshot_token"],
            payload=payload,
            db=db,
        )
        sweep_id = body["sweep_id"]
        service.command(sweep_id, "cancel", db)
        summary = reconcile_sweep(sweep_id, db)
        assert summary["state"] == "cancelled"
        assert summary["processed"] == summary["total"]
        assert summary["skipped"] == summary["total"]
        db.close()


class TestCancelReconcile:
    """Cancelamento auto-finaliza (card #853): regressão do caso PROD,
    finalizador único, guards anti-corrida e re-finalização terminal."""

    @staticmethod
    def _seed(db, sweep_id, *, sweep_state, combos, outbox, processed=0, total=None):
        """Semeia um sweep com combinações e intents.

        combos: lista de estados ("pending"/"running"/"succeeded"/"skipped").
        outbox: lista de (generation, state). `running` ganha lease válido,
        salvo sufixo ":expired".
        """
        now = datetime.now(timezone.utc)
        states = [c.split(":")[0] for c in combos]
        # A chave única (sweep, template, symbol, timeframe, direction) exige
        # eixos distintos por combinação: roda símbolos por índice.
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT"]
        db.add(
            DiscoverySweep(
                id=sweep_id,
                actor="admin-1",
                state=sweep_state,
                idempotency_key=f"k-{sweep_id}",
                payload_hash="h" * 64,
                snapshot_token="tok",
                snapshot_hash="y" * 64,
                snapshot={},
                total=total if total is not None else len(states),
                processed=processed,
                completed_at=now if sweep_state == "cancelled" else None,
                created_at=now,
            )
        )
        for index, raw in enumerate(combos):
            state, _, modifier = raw.partition(":")
            kwargs = {
                "sweep_id": sweep_id,
                "template_id": "multi_ma_crossover",
                "symbol": symbols[index % len(symbols)],
                "timeframe": "1d",
                "direction": "long",
                "state": state,
            }
            if state == "running":
                kwargs["lease_owner"] = "w1"
                delta = timedelta(seconds=-10) if modifier == "expired" else timedelta(seconds=300)
                kwargs["lease_expires_at"] = now + delta
            if state == "succeeded":
                kwargs["result_id"] = f"RS-{sweep_id}"
            db.add(DiscoveryCombination(**kwargs))
        for generation, ostate in outbox:
            db.add(DiscoveryOutbox(sweep_id=sweep_id, generation=generation, state=ostate))
        db.commit()

    @staticmethod
    def _outstanding(db, sweep_id):
        return (
            db.query(DiscoveryOutbox)
            .filter(
                DiscoveryOutbox.sweep_id == sweep_id,
                DiscoveryOutbox.state.in_(("pending", "delivered")),
            )
            .all()
        )

    def test_41_prod_stuck_cancelling_heals_on_dispatch(self, engine_factory):
        """4.1: `cancelling` + outbox `acked` + `pending > 0` + `running == 0`
        vira `cancelled` com `processed = total` no próximo dispatch, sem
        reprocessar ignoradas."""
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed(
            db,
            "sw-prod-41",
            sweep_state="cancelling",
            combos=["pending", "pending", "pending", "succeeded"],
            outbox=[(1, "acked")],
        )
        published = service.dispatch_outbox(db=db)
        assert published == 0
        sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == "sw-prod-41").first()
        assert sweep.state == "cancelled"
        assert sweep.processed == sweep.total == 4
        assert sweep.skipped == 3
        assert (
            db.query(DiscoveryCombination)
            .filter(
                DiscoveryCombination.sweep_id == "sw-prod-41",
                DiscoveryCombination.state.notin_(("skipped", "succeeded")),
            )
            .count()
            == 0
        )
        assert (
            db.query(DiscoveryResult).filter(DiscoveryResult.sweep_id == "sw-prod-41").count() == 0
        )
        db.close()

    def test_41_repeat_cancel_command_closes_stuck_sweep(self, engine_factory):
        """4.1 (comando): repeat-cancel sobre `cancelling` órfão fecha inline."""
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed(
            db,
            "sw-prod-41b",
            sweep_state="cancelling",
            combos=["pending", "pending", "succeeded"],
            outbox=[(1, "acked")],
        )
        body, status = service.command("sw-prod-41b", "cancel", db)
        assert status == 200
        assert body["state"] == "cancelled"
        snap = service.get_sweep("sw-prod-41b", db)
        assert snap["processed"] == snap["total"] == 3
        db.close()

    def test_42_cancel_with_flight_waits_single_finalizer_then_closes(self, engine_factory):
        """4.2: com `running` em voo permanece `cancelling` (sem forçar
        `skipped`), repeat-cancel não duplica o finalizador e o settle fecha
        a `cancelled`."""
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed(
            db,
            "sw-flight-42",
            sweep_state="running",
            combos=["running", "pending"],
            outbox=[(1, "delivered")],
        )
        body, status = service.command("sw-flight-42", "cancel", db)
        assert status == 200
        assert body["state"] == "cancelling"
        states = {
            c.state
            for c in db.query(DiscoveryCombination)
            .filter(DiscoveryCombination.sweep_id == "sw-flight-42")
            .all()
        }
        assert states == {"running", "skipped"}
        assert len(self._outstanding(db, "sw-flight-42")) == 1
        # Repetido sob `cancelling` passa pelo ensure com dedup: não duplica.
        body_r, status_r = service.command("sw-flight-42", "cancel", db)
        assert (status_r, body_r["state"]) == (200, "cancelling")
        assert len(self._outstanding(db, "sw-flight-42")) == 1
        # Repetido sob `cancelled` é no-op sem wake-up (após o settle).
        combo = (
            db.query(DiscoveryCombination)
            .filter(
                DiscoveryCombination.sweep_id == "sw-flight-42",
                DiscoveryCombination.state == "running",
            )
            .first()
        )
        combo.state = "succeeded"
        combo.result_id = "RS-sw-flight-42"
        db.commit()
        body_s, _ = service.command("sw-flight-42", "cancel", db)
        assert body_s["state"] == "cancelled"
        snap = service.get_sweep("sw-flight-42", db)
        assert snap["processed"] == snap["total"] == 2
        outbox_rows = db.query(DiscoveryOutbox).filter_by(sweep_id="sw-flight-42").count()
        assert outbox_rows == 1
        db.close()

    def test_43_cancel_without_flight_closes_inline(self, engine_factory):
        """4.3: cancel sem voo fecha na hora no próprio comando."""
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed(
            db,
            "sw-inline-43",
            sweep_state="running",
            combos=["pending", "pending"],
            outbox=[(1, "acked")],
        )
        body, status = service.command("sw-inline-43", "cancel", db)
        assert status == 200
        assert body["state"] == "cancelled"
        snap = service.get_sweep("sw-inline-43", db)
        assert snap["processed"] == snap["total"] == 2
        assert snap["skipped"] == 2
        assert snap["completed_at"] is not None
        assert db.query(DiscoveryOutbox).filter_by(sweep_id="sw-inline-43").count() == 1
        db.close()

    def test_44_pause_resume_rejected_while_cancelling(self, engine_factory):
        """4.4: `pause`/`resume` em `cancelling` continuam rejeitados."""
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed(
            db,
            "sw-prevail-44",
            sweep_state="cancelling",
            combos=["running"],
            outbox=[(1, "delivered")],
        )
        body_p, status_p = service.command("sw-prevail-44", "pause", db)
        assert status_p == 409
        assert "cancelling prevails" in body_p["error"]
        body_r, status_r = service.command("sw-prevail-44", "resume", db)
        assert status_r == 409
        sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == "sw-prevail-44").first()
        assert sweep.state == "cancelling"
        db.close()

    def test_45_repair_with_running_schedules_single_finalizer(self, engine_factory):
        """4.5: `cancelling` com `running > 0` e sem intent em aberto gera
        exatamente um finalizador (repair repetido não duplica); após o
        settle vira `cancelled`."""
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed(
            db,
            "sw-repair-45",
            sweep_state="cancelling",
            combos=["running"],
            outbox=[(1, "acked")],
        )
        service.dispatch_outbox(db=db)
        intents = (
            db.query(DiscoveryOutbox)
            .filter_by(sweep_id="sw-repair-45")
            .order_by(DiscoveryOutbox.generation)
            .all()
        )
        assert [(i.generation, i.state) for i in intents] == [(1, "acked"), (2, "delivered")]
        sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == "sw-repair-45").first()
        assert sweep.state == "cancelling"
        service.dispatch_outbox(db=db)
        assert db.query(DiscoveryOutbox).filter_by(sweep_id="sw-repair-45").count() == 2
        assert len(self._outstanding(db, "sw-repair-45")) == 1
        combo = (
            db.query(DiscoveryCombination)
            .filter(DiscoveryCombination.sweep_id == "sw-repair-45")
            .first()
        )
        combo.state = "succeeded"
        combo.result_id = "RS-sw-repair-45"
        db.commit()
        service.dispatch_outbox(db=db)
        db.refresh(sweep)
        assert sweep.state == "cancelled"
        assert sweep.processed == sweep.total == 1
        db.close()

    def test_46_stale_redelivery_and_double_finalizer_idempotent(self, engine_factory, monkeypatch):
        """4.6: redelivery (`delivered` stale → `pending`) não gera segundo
        finalizador; orquestrador 2× para o mesmo (`sweep_id`, `generation`)
        não reexecuta combinação com resultado e dá `ack` uma vez."""
        from app.tasks import discovery_celery_tasks

        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed(
            db,
            "sw-redel-46",
            sweep_state="cancelling",
            combos=["pending", "succeeded"],
            outbox=[(1, "delivered")],
        )
        # Envelhece o intent para o TTL de redelivery cobri-lo.
        intent = db.query(DiscoveryOutbox).filter_by(sweep_id="sw-redel-46").first()
        intent.updated_at = datetime.now(timezone.utc) - timedelta(hours=2)
        db.commit()
        # Resultado commitado da combinação `succeeded` (idempotência).
        combo_ok = (
            db.query(DiscoveryCombination)
            .filter(
                DiscoveryCombination.sweep_id == "sw-redel-46",
                DiscoveryCombination.state == "succeeded",
            )
            .first()
        )
        now = datetime.now(timezone.utc)
        db.add(
            DiscoveryResult(
                id="RS-sw-redel-46",
                sweep_id="sw-redel-46",
                combination_id=combo_ok.id,
                template_id="multi_ma_crossover",
                symbol="BTCUSDT",
                timeframe="1d",
                direction="long",
                parameters={},
                start_at=now,
                end_at=now + timedelta(days=30),
                metrics={},
                strategy_identity_key="id-46",
                evidence_fingerprint="fp-46",
                eligibility="eligible",
                dedup_state="unique",
            )
        )
        db.commit()
        monkeypatch.setattr(discovery_celery_tasks, "SessionLocal", _session_factory(engine))
        first = discovery_celery_tasks.run_sweep_orchestrator("sw-redel-46", 1)
        assert first["state"] == "cancelled"
        assert first["processed"] == first["total"] == 2
        second = discovery_celery_tasks.run_sweep_orchestrator("sw-redel-46", 1)
        assert second["state"] == "cancelled"
        assert db.query(DiscoveryOutbox).filter_by(sweep_id="sw-redel-46").count() == 1
        assert db.query(DiscoveryResult).filter_by(sweep_id="sw-redel-46").count() == 1
        assert service.get_sweep("sw-redel-46", db)["processed"] == 2
        db.close()

    def test_47_run_precheck_returns_pending_under_cancelling_skipped_under_terminal(
        self, engine_factory
    ):
        """4.7: combinação reclamada antes do cancel, cujo `run_combination`
        roda já sob `cancelling`, volta a `pending` (reconcile marca
        `skipped`); sob `cancelled` vai direto a `skipped`."""
        from app.tasks.discovery_tasks import reconcile_sweep, run_combination

        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed(
            db,
            "sw-race-47",
            sweep_state="running",
            combos=["pending"],
            outbox=[(1, "delivered")],
        )
        claimed = service.claim_combinations("sw-race-47", owner="w1", db=db)
        assert len(claimed) == 1
        db.query(DiscoverySweep).filter(DiscoverySweep.id == "sw-race-47").update(
            {DiscoverySweep.state: "cancelling"}, synchronize_session=False
        )
        db.commit()
        run_combination(db, claimed[0], owner="w1")
        db.refresh(claimed[0])
        assert claimed[0].state == "pending"
        summary = reconcile_sweep("sw-race-47", db)
        assert summary["state"] == "cancelled"
        db.refresh(claimed[0])
        assert claimed[0].state == "skipped"
        # Sob terminal não se cria `pending`: direto a `skipped`.
        self._seed(
            db,
            "sw-term-47",
            sweep_state="cancelled",
            combos=["running"],
            outbox=[(1, "acked")],
            processed=0,
        )
        combo = (
            db.query(DiscoveryCombination)
            .filter(DiscoveryCombination.sweep_id == "sw-term-47")
            .first()
        )
        run_combination(db, combo, owner="w1")
        db.refresh(combo)
        assert combo.state == "skipped"
        assert (
            db.query(DiscoveryCombination)
            .filter(
                DiscoveryCombination.sweep_id == "sw-term-47",
                DiscoveryCombination.state == "pending",
            )
            .count()
            == 0
        )
        db.close()

    def test_48_concurrent_claim_after_inline_close_claims_nothing(self, engine_factory):
        """4.8: com o cancel já commitado a `cancelled`, `claim_combinations`
        concorrente observa o terminal sob lock e devolve `[]` sem tocar em
        linha alguma."""
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed(
            db,
            "sw-claim-48",
            sweep_state="running",
            combos=["pending"],
            outbox=[(1, "acked")],
        )
        body, _ = service.command("sw-claim-48", "cancel", db)
        assert body["state"] == "cancelled"
        before = {
            (c.id, c.state, c.attempts)
            for c in db.query(DiscoveryCombination)
            .filter(DiscoveryCombination.sweep_id == "sw-claim-48")
            .all()
        }
        assert service.claim_combinations("sw-claim-48", owner="late", db=db) == []
        after = {
            (c.id, c.state, c.attempts)
            for c in db.query(DiscoveryCombination)
            .filter(DiscoveryCombination.sweep_id == "sw-claim-48")
            .all()
        }
        assert before == after
        sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == "sw-claim-48").first()
        assert sweep.state == "cancelled"
        assert sweep.processed == sweep.total == 1
        db.close()

    def test_49_reconcile_under_cancelled_refinalizes_without_rewriting_terminal(
        self, engine_factory
    ):
        """4.9: `reconcile`/`repair` sob `cancelled` com resíduo converte
        `pending → skipped` + recount (inclusive `running` expirado via
        release escopado no mesmo commit), mantém `state`/`completed_at` e
        restaura `processed = total` sem wake-up novo."""
        from app.tasks.discovery_tasks import reconcile_sweep

        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed(
            db,
            "sw-resid-49",
            sweep_state="cancelled",
            combos=["succeeded", "succeeded", "pending"],
            outbox=[(1, "acked")],
            processed=2,
        )
        sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == "sw-resid-49").first()
        completed_at = sweep.completed_at
        assert completed_at is not None
        summary = reconcile_sweep("sw-resid-49", db)
        assert summary["state"] == "cancelled"
        db.refresh(sweep)
        assert sweep.state == "cancelled"
        assert sweep.completed_at == completed_at
        assert sweep.processed == sweep.total == 3
        assert db.query(DiscoveryOutbox).filter_by(sweep_id="sw-resid-49").count() == 1
        # `running` de lease expirado sob `cancelled` converge no repair do
        # próximo dispatch (release escopado + `skipped` no mesmo commit).
        self._seed(
            db,
            "sw-exp-49",
            sweep_state="cancelled",
            combos=["running:expired"],
            outbox=[(1, "acked")],
            processed=1,
        )
        service.dispatch_outbox(db=db)
        sweep2 = db.query(DiscoverySweep).filter(DiscoverySweep.id == "sw-exp-49").first()
        assert sweep2.state == "cancelled"
        assert sweep2.processed == sweep2.total == 1
        combo2 = (
            db.query(DiscoveryCombination)
            .filter(DiscoveryCombination.sweep_id == "sw-exp-49")
            .first()
        )
        assert combo2.state == "skipped"
        assert db.query(DiscoveryOutbox).filter_by(sweep_id="sw-exp-49").count() == 1
        db.close()


class TestCoverageCalendar:
    def test_expected_candles_for_window(self):
        from app.tasks.discovery_tasks import _expected_candles_for_window

        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = start + timedelta(days=365)
        assert _expected_candles_for_window("1d", start, end) == 365
        assert _expected_candles_for_window("4h", start, end) == 365 * 6
        assert _expected_candles_for_window("1d", end, end) == 0


class TestDiscoveryRoutes:
    def _build_app(self, engine=None):
        from fastapi import FastAPI

        from app.database import get_db
        from app.routes import discovery_routes

        test_app = FastAPI()
        test_app.include_router(discovery_routes.router)
        test_app.dependency_overrides[discovery_routes.get_current_admin] = lambda: "admin-1"
        if engine is not None:
            session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

            def _override_db():
                db = session_factory()
                try:
                    yield db
                finally:
                    db.close()

            test_app.dependency_overrides[get_db] = _override_db
        return test_app, discovery_routes

    async def test_preflight_endpoint_requires_admin(self, monkeypatch):
        from fastapi import FastAPI

        from app.routes import discovery_routes

        app = FastAPI()
        app.include_router(discovery_routes.router)
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(
                "/api/combos/discovery/sweeps/preflight",
                json={
                    "templates": ["t1"],
                    "symbols": ["BTCUSDT"],
                    "timeframes": ["1d"],
                    "directions": ["long"],
                },
            )
        assert res.status_code == 401

    async def test_preflight_endpoint_ok(self, monkeypatch):
        app, routes = self._build_app()
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(
                "/api/combos/discovery/sweeps/preflight",
                json={
                    "templates": ["multi_ma_crossover"],
                    "symbols": ["BTCUSDT"],
                    "timeframes": ["1d"],
                    "directions": ["long"],
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                },
            )
        assert res.status_code == 200
        body = res.json()
        assert body["snapshot_token"]
        assert body["snapshot_hash"]

    async def test_create_and_get_sweep_endpoints(self, engine_factory):
        engine = engine_factory()
        app, routes = self._build_app(engine=engine)
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            create_res = await client.post(
                "/api/combos/discovery/sweeps",
                json={
                    "templates": ["multi_ma_crossover"],
                    "symbols": ["BTCUSDT"],
                    "timeframes": ["1d"],
                    "directions": ["long"],
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "period_type": "all",
                    "snapshot_token": preflight["snapshot_token"],
                    "snapshot_hash": preflight["snapshot_hash"],
                    "idempotency_key": "route-key-0001",
                },
            )
            assert create_res.status_code == 201, create_res.text
            sweep_id = create_res.json()["sweep_id"]
            get_res = await client.get(f"/api/combos/discovery/sweeps/{sweep_id}")
            assert get_res.status_code == 200
            assert get_res.json()["state"] in ("pending", "running")

    async def test_leaderboard_and_promote_endpoints(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", lambda *a, **k: None)
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        db.add(
            DiscoverySweep(
                id="sw-routes",
                actor="admin-1",
                state="completed",
                idempotency_key="lb-key-0001",
                payload_hash="x" * 64,
                snapshot_token="tok",
                snapshot_hash="y" * 64,
                snapshot={},
                total=1,
                succeeded=1,
            )
        )
        now = datetime.now(timezone.utc)
        db.add(
            DiscoveryResult(
                id="RS-RTE-1",
                sweep_id="sw-routes",
                combination_id=900001,
                template_id="t1",
                symbol="BTCUSDT",
                timeframe="1d",
                direction="long",
                parameters={},
                start_at=now,
                end_at=now + timedelta(days=30),
                metrics={},
                trades_count=40,
                calmar_ratio=2.0,
                strategy_identity_key="id-rte-1",
                evidence_fingerprint="fp-rte-1",
                eligibility="eligible",
                dedup_state="unique",
            )
        )
        db.commit()
        db.close()

        app, routes = self._build_app(engine=engine_factory())
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            lb = await client.get("/api/combos/discovery/sweeps/sw-routes/leaderboard")
            assert lb.status_code == 200
            assert lb.json()["results"][0]["result_id"] == "RS-RTE-1"
            bad_metric = await client.get(
                "/api/combos/discovery/sweeps/sw-routes/leaderboard?metric=sharpe"
            )
            assert bad_metric.status_code == 400
            missing = await client.get("/api/combos/discovery/sweeps/sw-missing")
            assert missing.status_code == 404
            promote = await client.post(
                "/api/combos/discovery/results/RS-RTE-1/promote",
                json={"tier": 3, "idempotency_key": "promote-rte-1"},
            )
            assert promote.status_code == 201
            promote2 = await client.post(
                "/api/combos/discovery/results/RS-RTE-1/promote",
                json={"tier": 3, "idempotency_key": "promote-rte-1"},
            )
            assert promote2.status_code == 200
            discarded = await client.post("/api/combos/discovery/results/RS-RTE-1/discard")
            assert discarded.status_code == 409

    async def test_command_endpoints(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", lambda *a, **k: None)
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        body, _ = service.create_sweep(
            actor="admin-1",
            idempotency_key="cmd-key-0001",
            snapshot_token=preflight["snapshot_token"],
            payload={
                "templates": ["multi_ma_crossover"],
                "symbols": ["BTCUSDT"],
                "timeframes": ["1d"],
                "directions": ["long"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "period_type": "all",
                "snapshot_hash": preflight["snapshot_hash"],
            },
            db=db,
        )
        db.close()
        app, routes = self._build_app(engine=engine_factory())
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            cancel = await client.post(f"/api/combos/discovery/sweeps/{body['sweep_id']}/cancel")
            assert cancel.status_code == 200
            pause = await client.post(f"/api/combos/discovery/sweeps/{body['sweep_id']}/pause")
            assert pause.status_code in (200, 409)
            unknown = await client.post("/api/combos/discovery/sweeps/nope/cancel")
            assert unknown.status_code == 404

    async def test_history_endpoint(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        service.create_sweep(
            actor="admin-1",
            idempotency_key="hist-key-0001",
            snapshot_token=preflight["snapshot_token"],
            payload={
                "templates": ["multi_ma_crossover"],
                "symbols": ["BTCUSDT"],
                "timeframes": ["1d"],
                "directions": ["long"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "period_type": "all",
                "snapshot_hash": preflight["snapshot_hash"],
            },
            db=db,
        )
        db.close()
        app, routes = self._build_app(engine=engine_factory())
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/combos/discovery/sweeps/history")
            assert res.status_code == 200
            assert len(res.json()["sweeps"]) >= 1


class TestOrchestratorTasks:
    def test_reconcile_completed_and_count_claimable(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks
        from app.tasks.discovery_tasks import reconcile_sweep

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", lambda *a, **k: None)
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        body, _ = service.create_sweep(
            actor="admin-1",
            idempotency_key="rec-key-0001",
            snapshot_token=preflight["snapshot_token"],
            payload={
                "templates": ["multi_ma_crossover"],
                "symbols": ["BTCUSDT"],
                "timeframes": ["1d"],
                "directions": ["long"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "period_type": "all",
                "snapshot_hash": preflight["snapshot_hash"],
            },
            db=db,
        )
        sweep_id = body["sweep_id"]
        combo = (
            db.query(DiscoveryCombination).filter(DiscoveryCombination.sweep_id == sweep_id).first()
        )
        combo.state = "succeeded"
        combo.result_id = "RS-REC-1"
        db.commit()
        summary = reconcile_sweep(sweep_id, db)
        assert summary["state"] == "completed"
        assert summary["processed"] == summary["total"] == 1
        assert service.count_claimable(sweep_id, db=db) == 0
        db.close()

    def test_serialize_exposes_fourth_counter_default_zero(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = _preflight_payload(service)
        body, _ = service.create_sweep(
            actor="admin-1",
            idempotency_key="ins-key-0001",
            snapshot_token=preflight["snapshot_token"],
            payload={
                "templates": ["multi_ma_crossover"],
                "symbols": ["BTCUSDT"],
                "timeframes": ["1d"],
                "directions": ["long"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "period_type": "all",
                "snapshot_hash": preflight["snapshot_hash"],
            },
            db=db,
        )
        snap = service.get_sweep(body["sweep_id"], db)
        assert snap["insufficient_sample"] == 0
        assert (
            snap["processed"]
            == snap["succeeded"] + snap["failed"] + snap["skipped"] + snap["insufficient_sample"]
        )
        db.close()

    def test_orchestrator_enqueue_and_run_with_missing_sweep(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks
        from app.tasks.discovery_tasks import run_combination

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", lambda *a, **k: None)
        engine = engine_factory()
        db = _session_factory(engine)()
        combo = DiscoveryCombination(
            sweep_id="sw-nonexistent",
            template_id="t1",
            symbol="BTCUSDT",
            timeframe="1d",
            direction="long",
            state="running",
            lease_owner="w1",
        )
        db.add(combo)
        db.commit()
        run_combination(db, combo, owner="w1")
        db.refresh(combo)
        assert combo.state == "skipped"
        db.close()

    def test_expected_candles_and_coverage_in_runner(self):
        from app.tasks.discovery_tasks import _expected_candles_for_window

        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = start + timedelta(days=10)
        assert _expected_candles_for_window("1d", start, end) == 10
        assert _expected_candles_for_window("4h", start, end) == 60


class TestRestoreAndWakeup:
    def test_active_lists_non_terminal_for_actor_only(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        now = datetime.now(timezone.utc)
        db.add(
            DiscoverySweep(
                id="sw-other",
                actor="admin-2",
                state="running",
                idempotency_key="k-other",
                payload_hash="h" * 64,
                snapshot_token="tok",
                snapshot_hash="y" * 64,
                snapshot={
                    "axes": {
                        "templates": ["t"],
                        "symbols": ["BTCUSDT"],
                        "timeframes": ["1d"],
                        "directions": ["long"],
                    }
                },
                total=1,
                created_at=now,
            )
        )
        db.add(
            DiscoverySweep(
                id="sw-done",
                actor="admin-1",
                state="completed",
                idempotency_key="k-done",
                payload_hash="h" * 64,
                snapshot_token="tok",
                snapshot_hash="y" * 64,
                snapshot={},
                total=1,
                created_at=now,
            )
        )
        db.add(
            DiscoverySweep(
                id="sw-old",
                actor="admin-1",
                state="paused",
                idempotency_key="k-old",
                payload_hash="h" * 64,
                snapshot_token="tok",
                snapshot_hash="y" * 64,
                snapshot={
                    "axes": {
                        "templates": ["t"],
                        "symbols": ["BTCUSDT"],
                        "timeframes": ["1d"],
                        "directions": ["long"],
                    }
                },
                total=2,
                created_at=now - timedelta(hours=1),
            )
        )
        db.add(
            DiscoverySweep(
                id="sw-new",
                actor="admin-1",
                state="running",
                idempotency_key="k-new",
                payload_hash="h" * 64,
                snapshot_token="tok",
                snapshot_hash="y" * 64,
                snapshot={
                    "axes": {
                        "templates": ["t"],
                        "symbols": ["BTCUSDT"],
                        "timeframes": ["1d"],
                        "directions": ["long"],
                    }
                },
                total=3,
                created_at=now,
            )
        )
        db.add(
            DiscoverySweep(
                id="sw-pend",
                actor="admin-1",
                state="pending",
                idempotency_key="k-pend",
                payload_hash="h" * 64,
                snapshot_token="tok",
                snapshot_hash="y" * 64,
                snapshot={
                    "axes": {
                        "templates": ["t"],
                        "symbols": ["BTCUSDT"],
                        "timeframes": ["1d"],
                        "directions": ["long"],
                    }
                },
                total=1,
                created_at=now - timedelta(minutes=30),
            )
        )
        db.add(
            DiscoverySweep(
                id="sw-can",
                actor="admin-1",
                state="cancelling",
                idempotency_key="k-can",
                payload_hash="h" * 64,
                snapshot_token="tok",
                snapshot_hash="y" * 64,
                snapshot={
                    "axes": {
                        "templates": ["t"],
                        "symbols": ["BTCUSDT"],
                        "timeframes": ["1d"],
                        "directions": ["long"],
                    }
                },
                total=1,
                created_at=now - timedelta(minutes=10),
            )
        )
        db.commit()
        active = service.list_active_sweeps("admin-1", db)
        assert [row["sweep_id"] for row in active] == ["sw-new", "sw-can", "sw-pend", "sw-old"]
        assert {row["state"] for row in active} == {"running", "paused", "pending", "cancelling"}
        assert active[0]["draft_key"] == "k-new"
        assert service.get_sweep("sw-other", db, actor="admin-1") is None
        db.close()

    async def test_active_and_cross_actor_routes(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        now = datetime.now(timezone.utc)
        db.add(
            DiscoverySweep(
                id="sw-other",
                actor="admin-2",
                state="running",
                idempotency_key="k-other-r",
                payload_hash="h" * 64,
                snapshot_token="tok",
                snapshot_hash="y" * 64,
                snapshot={},
                total=1,
                created_at=now,
            )
        )
        db.add(
            DiscoverySweep(
                id="sw-mine",
                actor="admin-1",
                state="paused",
                idempotency_key="k-mine-r",
                payload_hash="h" * 64,
                snapshot_token="tok",
                snapshot_hash="y" * 64,
                snapshot={},
                total=1,
                created_at=now,
            )
        )
        db.commit()
        db.close()
        app, _ = TestDiscoveryRoutes()._build_app(engine=engine)
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            active_res = await client.get("/api/combos/discovery/sweeps/active")
            other_res = await client.get("/api/combos/discovery/sweeps/sw-other")
            pause = await client.post("/api/combos/discovery/sweeps/sw-other/pause")
        assert active_res.status_code == 200
        assert [s["sweep_id"] for s in active_res.json()["sweeps"]] == ["sw-mine"]
        assert other_res.status_code == 404
        assert pause.status_code == 404

    def _seed_paused_sweep(
        self, db, *, sweep_id: str, outbox_state: str, sweep_state: str = "paused"
    ):
        now = datetime.now(timezone.utc)
        db.add(
            DiscoverySweep(
                id=sweep_id,
                actor="admin-1",
                state=sweep_state,
                idempotency_key=f"k-{sweep_id}",
                payload_hash="h" * 64,
                snapshot_token="tok",
                snapshot_hash="y" * 64,
                snapshot={
                    "axes": {
                        "templates": ["multi_ma_crossover"],
                        "symbols": ["BTCUSDT"],
                        "timeframes": ["1d"],
                        "directions": ["long"],
                    }
                },
                total=1,
                created_at=now,
            )
        )
        db.add(
            DiscoveryCombination(
                sweep_id=sweep_id,
                template_id="multi_ma_crossover",
                symbol="BTCUSDT",
                timeframe="1d",
                direction="long",
                state="pending",
            )
        )
        db.add(DiscoveryOutbox(sweep_id=sweep_id, generation=1, state=outbox_state))
        db.commit()

    def test_resume_creates_next_generation_after_acked(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", lambda *a, **k: None)
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed_paused_sweep(db, sweep_id="sw-resume-ack", outbox_state="acked")
        payload, status = service.command("sw-resume-ack", "resume", db, actor="admin-1")
        assert status == 200
        assert payload["state"] == "running"
        intents = (
            db.query(DiscoveryOutbox)
            .filter_by(sweep_id="sw-resume-ack")
            .order_by(DiscoveryOutbox.generation)
            .all()
        )
        assert intents[-1].generation == 2
        assert intents[-1].state in ("pending", "delivered")
        db.close()

    def test_resume_does_not_duplicate_delivered_wakeup(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", lambda *a, **k: None)
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed_paused_sweep(db, sweep_id="sw-resume-del", outbox_state="delivered")
        service.command("sw-resume-del", "resume", db)
        gens = [
            row.generation
            for row in db.query(DiscoveryOutbox).filter_by(sweep_id="sw-resume-del").all()
        ]
        assert gens == [1]
        db.close()

    def test_resume_deferred_when_broker_down(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks

        def _boom(*_a, **_k):
            raise RuntimeError("broker down")

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", _boom)
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed_paused_sweep(db, sweep_id="sw-resume-def", outbox_state="acked")
        payload, status = service.command("sw-resume-def", "resume", db)
        assert status == 200
        assert payload["state"] == "running"
        assert payload["wake_up_state"] == "pending"
        assert payload["dispatch_status"] == "deferred"
        db.close()

    def test_dispatcher_repairs_running_without_claimable_wakeup(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", lambda *a, **k: None)
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed_paused_sweep(
            db, sweep_id="sw-repair", outbox_state="acked", sweep_state="running"
        )
        published = service.dispatch_outbox(db=db)
        assert published >= 1
        newest = (
            db.query(DiscoveryOutbox)
            .filter_by(sweep_id="sw-repair")
            .order_by(DiscoveryOutbox.generation.desc())
            .first()
        )
        assert newest.generation == 2
        assert newest.state == "delivered"
        db.close()

    def test_pause_does_not_create_wakeup(self, engine_factory, monkeypatch):
        from app.tasks import discovery_tasks

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", lambda *a, **k: None)
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed_paused_sweep(db, sweep_id="sw-pause-wu", outbox_state="acked")
        before = db.query(DiscoveryOutbox).filter_by(sweep_id="sw-pause-wu").count()
        service.ensure_sweep_wakeup(db, "sw-pause-wu")
        db.commit()
        assert db.query(DiscoveryOutbox).filter_by(sweep_id="sw-pause-wu").count() == before
        db.close()

    def test_rotate_from_creates_next_generation_while_current_delivered(
        self, engine_factory, monkeypatch
    ):
        from app.tasks import discovery_tasks

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", lambda *a, **k: None)
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        self._seed_paused_sweep(
            db, sweep_id="sw-rotate", outbox_state="delivered", sweep_state="running"
        )
        result = service.ensure_sweep_wakeup(db, "sw-rotate", rotate_from=1)
        db.commit()
        assert result["created"] is True
        assert result["generation"] == 2
        states = {
            row.generation: row.state
            for row in db.query(DiscoveryOutbox).filter_by(sweep_id="sw-rotate").all()
        }
        assert states[1] == "delivered"
        assert states[2] == "pending"
        skipped = service.ensure_sweep_wakeup(db, "sw-rotate", rotate_from=1)
        db.commit()
        assert skipped["created"] is False
        assert skipped["generation"] == 2
        db.close()

    def test_concurrent_ensure_creates_single_next_generation(self, engine_factory, monkeypatch):
        from concurrent.futures import ThreadPoolExecutor

        from app.tasks import discovery_tasks

        monkeypatch.setattr(discovery_tasks, "enqueue_sweep_orchestrator", lambda *a, **k: None)
        engine = engine_factory()
        service = DiscoveryService()
        db = _session_factory(engine)()
        self._seed_paused_sweep(db, sweep_id="sw-race", outbox_state="acked", sweep_state="running")
        db.close()

        def _once():
            session = _session_factory(engine)()
            try:
                service.ensure_sweep_wakeup(session, "sw-race")
                session.commit()
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda _: _once(), range(4)))
        check = _session_factory(engine)()
        gens = [
            row.generation
            for row in check.query(DiscoveryOutbox).filter_by(sweep_id="sw-race").all()
        ]
        pending_or_delivered = (
            check.query(DiscoveryOutbox)
            .filter(
                DiscoveryOutbox.sweep_id == "sw-race",
                DiscoveryOutbox.state.in_(("pending", "delivered")),
            )
            .count()
        )
        check.close()
        assert 2 in gens
        assert pending_or_delivered >= 1
