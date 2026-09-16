"""Card #948: órfãos após DELETE de favorito — reclassificar e reler na hora."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import FavoriteStrategy
from app.models_discovery import DiscoveryDedupEvidence, DiscoveryResult
from app.services.discovery_service import DiscoveryService
from database_guard import assert_safe_test_database_url


def _session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def engine():
    assert_safe_test_database_url(
        os.environ["DATABASE_URL"],
        variable_name="DATABASE_URL",
        allow_github_disposable=True,
    )
    engine = create_engine(os.environ["DATABASE_URL"])
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.exec_driver_sql("DELETE FROM discovery_dedup_evidence")
        connection.exec_driver_sql("DELETE FROM discovery_results")
        connection.exec_driver_sql("DELETE FROM favorite_strategies")
    yield engine
    engine.dispose()


_combination_seq = 948_000


def _discovery_row(
    *,
    result_id: str,
    dedup_state: str,
    dedup_reference: str | None,
    identity: str,
) -> DiscoveryResult:
    global _combination_seq
    _combination_seq += 1
    now = datetime.now(timezone.utc)
    return DiscoveryResult(
        id=result_id,
        sweep_id="sw-948",
        combination_id=_combination_seq,
        template_id="multi_ma_crossover",
        symbol="BTCUSDT",
        timeframe="1d",
        direction="long",
        parameters={"ema_short": 8},
        start_at=now,
        end_at=now + timedelta(days=30),
        metrics={},
        trades_count=45,
        calmar_ratio=2.0,
        strategy_identity_key=identity,
        evidence_fingerprint=f"fp-{result_id}",
        eligibility="eligible",
        dedup_state=dedup_state,
        dedup_reference=dedup_reference,
    )


class TestDeletedFavoriteReconciliation:
    def test_delete_reclassifies_duplicate_and_promoted_rows(self, engine):
        db = _session_factory(engine)()
        service = DiscoveryService()
        db.add(
            _discovery_row(
                result_id="RS-DUP-948",
                dedup_state="duplicate_favorite",
                dedup_reference="42",
                identity="id-dup-948",
            )
        )
        db.add(
            _discovery_row(
                result_id="RS-PRO-948",
                dedup_state="already_promoted",
                dedup_reference="42",
                identity="id-pro-948",
            )
        )
        db.commit()
        count = service.reclassify_discovery_results_for_deleted_favorite(42, db)
        assert count == 2
        db.commit()
        dup = db.query(DiscoveryResult).filter(DiscoveryResult.id == "RS-DUP-948").one()
        pro = db.query(DiscoveryResult).filter(DiscoveryResult.id == "RS-PRO-948").one()
        assert dup.dedup_state == "unique"
        assert dup.dedup_reference is None
        assert pro.dedup_state == "unique"
        evidence = (
            db.query(DiscoveryDedupEvidence)
            .filter(DiscoveryDedupEvidence.classification == "unique")
            .all()
        )
        assert len(evidence) == 2
        db.close()

    def test_reclassify_points_at_live_equivalent_not_unique(self, engine):
        db = _session_factory(engine)()
        service = DiscoveryService()
        now = datetime.now(timezone.utc)
        live = FavoriteStrategy(
            user_id="admin-948",
            name="equivalent live",
            symbol="BTCUSDT",
            timeframe="1d",
            strategy_name="multi_ma_crossover",
            parameters={"ema_short": 8, "direction": "long"},
            tier=3,
            start_date=now.date().isoformat(),
            end_date=(now + timedelta(days=30)).date().isoformat(),
            period_type="all",
            metrics={"strategy_identity_key": "id-equiv-948"},
        )
        doomed = FavoriteStrategy(
            user_id="admin-948",
            name="to delete",
            symbol="BTCUSDT",
            timeframe="1d",
            strategy_name="multi_ma_crossover",
            parameters={"ema_short": 8, "direction": "long"},
            tier=3,
            start_date=now.date().isoformat(),
            end_date=(now + timedelta(days=30)).date().isoformat(),
            period_type="all",
            metrics={"strategy_identity_key": "id-equiv-948"},
        )
        db.add(live)
        db.add(doomed)
        db.flush()
        live_id = live.id
        doomed_id = doomed.id
        db.add(
            _discovery_row(
                result_id="RS-EQUIV-948",
                dedup_state="duplicate_favorite",
                dedup_reference=str(doomed_id),
                identity="id-equiv-948",
            )
        )
        db.commit()
        count = service.reclassify_discovery_results_for_deleted_favorite(doomed_id, db)
        assert count == 1
        db.delete(doomed)
        db.commit()
        stored = db.query(DiscoveryResult).filter(DiscoveryResult.id == "RS-EQUIV-948").one()
        assert stored.dedup_state == "duplicate_favorite"
        assert stored.dedup_reference == str(live_id)
        rows, _, _ = service.leaderboard("sw-948", db=db)
        grid = next(r for r in rows if r["result_id"] == "RS-EQUIV-948")
        assert grid["dedup_state"] == "duplicate_favorite"
        assert grid["dedup_reference"] == str(live_id)
        body, status = service.promote_result(
            result_id="RS-EQUIV-948",
            actor="admin-948",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            payload={"tier": 3, "result_id": "RS-EQUIV-948"},
            db=db,
        )
        assert status == 409
        assert body["error"] == "duplicate"
        assert body["reference"] == str(live_id)
        db.close()

    def test_leaderboard_resolves_missing_reference_without_reclassify_hook(self, engine):
        db = _session_factory(engine)()
        service = DiscoveryService()
        db.add(
            _discovery_row(
                result_id="RS-ORPHAN-948",
                dedup_state="duplicate_favorite",
                dedup_reference="99",
                identity="id-orphan-948",
            )
        )
        db.commit()
        rows, _, _ = service.leaderboard("sw-948", db=db)
        row = next(r for r in rows if r["result_id"] == "RS-ORPHAN-948")
        assert row["dedup_state"] == "unique"
        assert row["dedup_reference"] is None
        db.close()

    def test_promote_orphan_creates_new_favorite(self, engine):
        db = _session_factory(engine)()
        service = DiscoveryService()
        db.add(
            _discovery_row(
                result_id="RS-PROM-948",
                dedup_state="already_promoted",
                dedup_reference="77",
                identity="id-prom-orphan-948",
            )
        )
        db.commit()
        body, status = service.promote_result(
            result_id="RS-PROM-948",
            actor="admin-948",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            payload={"tier": 3, "result_id": "RS-PROM-948"},
            db=db,
        )
        assert status == 201
        new_id = int(body["favorite_id"])
        assert new_id != 77
        favorite = db.query(FavoriteStrategy).filter(FavoriteStrategy.id == new_id).one()
        assert favorite.tier == 3
        refreshed = db.query(DiscoveryResult).filter(DiscoveryResult.id == "RS-PROM-948").one()
        assert refreshed.dedup_state == "already_promoted"
        assert refreshed.dedup_reference == str(new_id)
        db.close()

    def test_promote_still_blocks_live_duplicate(self, engine):
        db = _session_factory(engine)()
        service = DiscoveryService()
        now = datetime.now(timezone.utc)
        live = FavoriteStrategy(
            user_id="admin-948",
            name="live",
            symbol="BTCUSDT",
            timeframe="1d",
            strategy_name="multi_ma_crossover",
            parameters={"ema_short": 8, "direction": "long"},
            tier=3,
            start_date=now.date().isoformat(),
            end_date=(now + timedelta(days=30)).date().isoformat(),
            period_type="all",
            metrics={"strategy_identity_key": "id-live-948"},
        )
        db.add(live)
        db.flush()
        db.add(
            _discovery_row(
                result_id="RS-LIVE-948",
                dedup_state="duplicate_favorite",
                dedup_reference=str(live.id),
                identity="id-live-948",
            )
        )
        db.commit()
        body, status = service.promote_result(
            result_id="RS-LIVE-948",
            actor="admin-948",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            payload={"tier": 3, "result_id": "RS-LIVE-948"},
            db=db,
        )
        assert status == 409
        assert body["error"] == "duplicate"
        db.close()

    def test_discard_orphan_already_promoted_allowed(self, engine):
        db = _session_factory(engine)()
        service = DiscoveryService()
        db.add(
            _discovery_row(
                result_id="RS-DSC-ORPHAN",
                dedup_state="already_promoted",
                dedup_reference="55",
                identity="id-dsc-orphan",
            )
        )
        db.commit()
        body, status = service.discard_result(result_id="RS-DSC-ORPHAN", db=db)
        assert status == 200
        assert body["dedup_state"] == "discarded"
        fav_count = db.query(FavoriteStrategy).count()
        assert fav_count == 0
        db.close()

    def test_discard_live_promoted_still_rejected(self, engine):
        db = _session_factory(engine)()
        service = DiscoveryService()
        now = datetime.now(timezone.utc)
        live = FavoriteStrategy(
            user_id="admin-948",
            name="live discard",
            symbol="ETHUSDT",
            timeframe="1d",
            strategy_name="multi_ma_crossover",
            parameters={"direction": "long"},
            tier=3,
            start_date=now.date().isoformat(),
            end_date=(now + timedelta(days=30)).date().isoformat(),
            period_type="all",
            metrics={},
        )
        db.add(live)
        db.flush()
        db.add(
            _discovery_row(
                result_id="RS-DSC-LIVE",
                dedup_state="already_promoted",
                dedup_reference=str(live.id),
                identity="id-dsc-live",
            )
        )
        db.commit()
        body, status = service.discard_result(result_id="RS-DSC-LIVE", db=db)
        assert status == 409
        assert body["error"] == "already_promoted"
        db.close()
