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

    def test_create_retry_normalizes_axis_order(self, engine_factory):
        engine = engine_factory()
        db = _session_factory(engine)()
        service = DiscoveryService()
        preflight = service.preflight(
            templates=["multi_ma_crossover"],
            symbols=["BTCUSDT"],
            timeframes=["4h", "1d"],
            directions=["long"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            period_type="all",
        )
        payload = {
            "templates": ["multi_ma_crossover"],
            "symbols": ["BTCUSDT"],
            "timeframes": ["4h", "1d"],
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
        reordered = {**payload, "timeframes": ["1d", "4h"]}
        second, retry_status = service.create_sweep(
            actor="admin-1",
            idempotency_key=key,
            snapshot_token=preflight["snapshot_token"],
            payload=reordered,
            db=db,
        )

        assert status == 201
        assert retry_status == 200
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
        for i, (rid, symbol, timeframe, direction, calmar, trades, elig, dedup) in enumerate(specs):
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
