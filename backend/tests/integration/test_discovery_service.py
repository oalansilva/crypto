"""Testes do discovery sweep service (card #469): preflight, criação
idempotente, lifecycle, claims/leases, leaderboard e promoção tier 3."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

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

    def _fake_list_templates(*_a, **_k):
        return {"prebuilt": [], "examples": [{"name": "multi_ma_crossover", "direction": "long"}]}

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
        service.command(sweep_id, "cancel", db)
        db.refresh(sweep)
        assert sweep.state == "cancelling"
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
        service.command(sweep_id, "cancel", db)
        service.command(sweep_id, "resume", db)
        db.refresh(db.query(DiscoverySweep).filter(DiscoverySweep.id == sweep_id).first())
        sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == sweep_id).first()
        assert sweep.state == "cancelling"  # resume rejeitado, permanece cancelling
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
            discovery_tasks, "enqueue_sweep_orchestrator", lambda s, g: calls.append((s, g))
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
            result_id="RS-PRO-1", actor="admin-1", idempotency_key=key, payload=payload, db=db
        )
        assert status == 201
        favorite_id = body["favorite_id"]
        favorite = (
            db.query(FavoriteStrategy).filter(FavoriteStrategy.id == int(favorite_id)).first()
        )
        assert favorite is not None
        assert favorite.tier == 3

        retry, status2 = service.promote_result(
            result_id="RS-PRO-1", actor="admin-1", idempotency_key=key, payload=payload, db=db
        )
        assert status2 == 200
        assert retry["favorite_id"] == favorite_id
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


class TestCoverageCalendar:
    def test_expected_candles_for_window(self):
        from app.tasks.discovery_tasks import _expected_candles_for_window

        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = start + timedelta(days=365)
        assert _expected_candles_for_window("1d", start, end) == 365
        assert _expected_candles_for_window("4h", start, end) == 365 * 6
        assert _expected_candles_for_window("1d", end, end) == 0
