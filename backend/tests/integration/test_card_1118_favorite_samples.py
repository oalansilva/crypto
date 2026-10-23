"""Card #1118: amostra do favorito, refresh diário, prazo de 30 dias, coleta de lixo e reprodução."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import AutoBacktestRun, FavoriteStrategy
from app.models_discovery import DiscoveryResult
from app.routes import favorites as favorites_routes
from app.services import discovery_inputs
from app.services.discovery_service import DiscoveryService
from app.services.favorite_backtest_refresh_service import (
    REFRESH_STATUS_FAILED,
    REFRESH_STATUS_SUCCESS,
    FavoriteBacktestRefreshService,
)
from app.services.market_history import reproduction, snapshots
from app.services.market_history.model import SeriesRef
from app.services.market_history.sample import ExecutionSample
from app.services.market_history.schema import ADD_COLUMNS_SQL, execute_all, side_table_statements


@pytest.fixture
def engine(tmp_path, monkeypatch):
    monkeypatch.setenv("MARKET_HISTORY_SNAPSHOT_DIR", str(tmp_path / "snapshots"))
    eng = create_engine(os.environ["DATABASE_URL"])
    Base.metadata.create_all(bind=eng)
    with eng.begin() as conn:
        execute_all(conn, side_table_statements())
        execute_all(conn, ADD_COLUMNS_SQL)
        for table in (
            "execution_data_snapshots",
            "auto_backtest_runs",
            "discovery_results",
            "favorite_strategies",
        ):
            conn.execute(text(f"DELETE FROM {table}"))
    yield eng
    with eng.begin() as conn:
        for table in (
            "execution_data_snapshots",
            "auto_backtest_runs",
            "discovery_results",
            "favorite_strategies",
        ):
            conn.execute(text(f"DELETE FROM {table}"))
    eng.dispose()
    discovery_inputs._SAMPLE_FRAMES.clear()


def _series() -> SeriesRef:
    return SeriesRef(
        series_id=7,
        asset_id="binance:spot:BTC/USDT",
        symbol="BTC/USDT",
        asset_class="crypto",
        source="binance_spot",
        session="24x7",
        adjustment="na",
        timeframe="1d",
        origin="native",
        data_version=3,
        physical_timeframe="1d",
    )


def _frame(start: str, periods: int, base: float = 100.0) -> pd.DataFrame:
    index = pd.date_range(start, periods=periods, freq="1D", tz="UTC", name="candle_time")
    close = pd.Series([base + i for i in range(periods)], index=index)
    return pd.DataFrame(
        {"open": close - 1, "high": close + 1, "low": close - 2, "close": close, "volume": 5.0}
    )


def _snapshot(engine, *, start="2026-08-01", periods=60, base=100.0, kind="optimization") -> str:
    sample = ExecutionSample(kind, engine=engine)
    sample.freeze("candles", _series(), start, "2026-10-01", _frame(start, periods, base))
    sample.freeze("intraday", _series(), start, "2026-10-01", _frame(start, periods, base))
    sample.finish()
    return sample.snapshot_id


def _row(engine, snapshot_id):
    return snapshots.get_manifest(engine, snapshot_id)


def _favorite(db, snapshot_id=None, **extra) -> FavoriteStrategy:
    favorite = FavoriteStrategy(
        user_id="user-1118",
        name="BTC",
        symbol="BTC/USDT",
        timeframe="1d",
        strategy_name="multi_ma_crossover",
        parameters={"ema_short": 8, "direction": "long"},
        tier=3,
        metrics={"total_return_pct": 4.0},
        snapshot_id=snapshot_id,
        **extra,
    )
    db.add(favorite)
    db.commit()
    return favorite


# --- prazo de 30 dias, favorito fixado e desfavoritar ------------------------------


def test_unfavorite_on_22_oct_keeps_the_sample_until_21_nov(engine):
    sid = _snapshot(engine)
    with engine.begin() as conn:
        snapshots.pin(conn, sid)
    assert _row(engine, sid)["pinned"] is True
    with engine.begin() as conn:
        # A varredura terminou em 1 set.; o favorito a segurou por muito mais tempo que isso.
        conn.execute(
            text(
                "UPDATE execution_data_snapshots SET finished_at = '2026-09-01T00:00:00Z', "
                "retain_until = '2026-10-01T00:00:00Z' WHERE snapshot_id = :i"
            ),
            {"i": sid},
        )
        snapshots.release(conn, sid, datetime(2026, 10, 22, 12, 0, tzinfo=timezone.utc))
    row = _row(engine, sid)
    assert row["pinned"] is False
    assert row["retain_until"] == datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
    # Soltar de novo mais tarde nunca encurta o prazo já dado.
    with engine.begin() as conn:
        snapshots.release(conn, sid, datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc))
    assert _row(engine, sid)["retain_until"] == datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)


def test_non_favorite_sample_stays_30_days_from_the_end_of_the_execution(engine):
    sid = _snapshot(engine)
    row = _row(engine, sid)
    assert row["pinned"] is False
    assert (
        timedelta(days=29, hours=23)
        <= row["retain_until"] - row["finished_at"]
        <= timedelta(days=30, hours=1)
    )
    assert snapshots.sample_state(row)["state"] == "kept"
    later = datetime.now(timezone.utc) + timedelta(days=31)
    assert snapshots.sample_state(row, later)["state"] == "expired"
    assert snapshots.states_for(engine, ["inexistente"])["inexistente"]["state"] == "expired"


def test_unfavoriting_releases_the_pinned_sample_for_30_days(engine):
    sid = _snapshot(engine)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        favorite = _favorite(db, sid)
        with engine.begin() as conn:
            snapshots.pin(conn, sid)
        favorite_id = favorite.id
        favorites_routes.delete_favorite(favorite_id, current_user_id="user-1118", db=db)
    row = _row(engine, sid)
    assert row["pinned"] is False
    assert (
        timedelta(days=29, hours=23)
        <= row["retain_until"] - datetime.now(timezone.utc)
        <= timedelta(days=30, hours=1)
    )


def test_promotion_gives_the_favorite_the_sample_of_the_promoted_result(engine):
    sid = _snapshot(engine, kind="discovery")
    Session = sessionmaker(bind=engine)
    now = datetime.now(timezone.utc)
    with Session() as db:
        db.add(
            DiscoveryResult(
                id="RS-1118",
                sweep_id="sw-1118",
                combination_id=1118001,
                template_id="multi_ma_crossover",
                symbol="BTC/USDT",
                timeframe="1d",
                direction="long",
                parameters={"ema_short": 8},
                start_at=now - timedelta(days=60),
                end_at=now,
                metrics={},
                trades_count=45,
                calmar_ratio=2.0,
                strategy_identity_key="id-1118",
                evidence_fingerprint="fp-1118",
                eligibility="eligible",
                dedup_state="unique",
                snapshot_id=sid,
                data_source="Binance Spot",
                asset_class="crypto",
                session="24x7",
                adjustment="na",
                timeframe_origin="native",
                data_version=3,
            )
        )
        db.commit()
        body, status = DiscoveryService().promote_result(
            result_id="RS-1118",
            actor="admin-1118",
            idempotency_key=f"k-{uuid.uuid4().hex[:12]}",
            payload={"tier": 3, "result_id": "RS-1118"},
            db=db,
        )
        assert status == 201
        favorite = db.query(FavoriteStrategy).filter_by(id=int(body["favorite_id"])).one()
        assert favorite.snapshot_id == sid
    row = _row(engine, sid)
    assert row["pinned"] is True  # vale até o primeiro refresh
    assert snapshots.sample_state(row)["state"] == "pinned"


# --- refresh diário: troca da amostra no mesmo commit ---------------------------------


class _RefreshOptimizer:
    """Devolve um resultado válido com a amostra desta tentativa."""

    created: list[str] = []
    fail_after_optimizer = False

    def run_optimization(self, **kwargs):
        sid = _snapshot(self.engine, start="2026-09-01", periods=45, base=200.0 + len(self.created))
        self.created.append(sid)
        now = datetime.utcnow()
        candles = [{"timestamp_utc": now.isoformat(), "close": 100.0}]
        if self.fail_after_optimizer:
            candles = [{"timestamp_utc": (now - timedelta(days=60)).isoformat(), "close": 100.0}]
        return {
            "best_metrics": {"total_return_pct": 8.5, "total_trades": 1},
            "trades": [{"entry_time": (now - timedelta(days=1)).isoformat(), "profit": 0.085}],
            "candles": candles,
            "indicator_data": {},
            "execution_mode": "favorite_auto_refresh",
            "snapshot_id": sid,
        }


def _service(engine, fail=False):
    Session = sessionmaker(bind=engine)

    class Optimizer(_RefreshOptimizer):
        pass

    Optimizer.engine = engine
    Optimizer.created = []
    Optimizer.fail_after_optimizer = fail
    service = FavoriteBacktestRefreshService(
        db_factory=Session,
        optimizer_factory=Optimizer,
        market_data_provider_factory=lambda _source: None,
    )
    service._prepare_market_data = lambda *a, **k: None
    return service, Session, Optimizer


def test_refresh_swaps_the_sample_in_the_same_commit_that_writes_the_number(engine):
    old = _snapshot(engine, base=50.0)
    service, Session, Optimizer = _service(engine)
    with Session() as db:
        favorite = _favorite(db, old)
        with engine.begin() as conn:
            snapshots.pin(conn, old)
        favorite_id = favorite.id
    result = service.refresh_favorite(favorite_id)
    assert result["status"] == REFRESH_STATUS_SUCCESS
    new = Optimizer.created[-1]
    with Session() as db:
        favorite = db.query(FavoriteStrategy).filter_by(id=favorite_id).one()
        run = db.query(AutoBacktestRun).filter_by(run_id=result["run_id"]).one()
        assert favorite.snapshot_id == new and run.snapshot_id == new
        assert favorite.metrics["total_return_pct"] == 8.5  # o número de /favorites
    assert _row(engine, new)["pinned"] is True
    previous = _row(engine, old)
    assert previous["pinned"] is False
    assert (
        timedelta(days=29, hours=23)
        <= previous["retain_until"] - datetime.now(timezone.utc)
        <= timedelta(days=30, hours=1)
    )


def test_old_favorite_gets_a_sample_on_the_first_refresh_and_promises_nothing_before(engine):
    service, Session, Optimizer = _service(engine)
    with Session() as db:
        favorite = _favorite(db, None)
        favorite_id = favorite.id
        before = reproduction.sample_status(engine, favorite.snapshot_id)
    assert before["state"] == "none" and before["reproducible"] is False
    assert "não é prometida" in before["message"]
    assert service.refresh_favorite(favorite_id)["status"] == REFRESH_STATUS_SUCCESS
    with Session() as db:
        favorite = db.query(FavoriteStrategy).filter_by(id=favorite_id).one()
        assert favorite.snapshot_id == Optimizer.created[-1]
        assert reproduction.sample_status(engine, favorite.snapshot_id)["state"] == "pinned"


def test_failed_refresh_changes_neither_the_sample_nor_the_number(engine):
    old = _snapshot(engine, base=50.0)
    service, Session, Optimizer = _service(engine, fail=True)
    with Session() as db:
        favorite = _favorite(db, old)
        with engine.begin() as conn:
            snapshots.pin(conn, old)
        favorite_id = favorite.id
    result = service.refresh_favorite(favorite_id)
    assert result["status"] == REFRESH_STATUS_FAILED
    with Session() as db:
        favorite = db.query(FavoriteStrategy).filter_by(id=favorite_id).one()
        assert favorite.snapshot_id == old
        assert favorite.metrics == {"total_return_pct": 4.0}
        assert favorite.auto_refresh_status == REFRESH_STATUS_FAILED
    assert _row(engine, old)["pinned"] is True  # amostra e número anteriores seguem coerentes
    attempt = _row(engine, Optimizer.created[-1])
    assert attempt["pinned"] is False
    assert attempt["retain_until"] <= datetime.now(timezone.utc)  # o GC leva
    assert snapshots.sample_state(attempt)["state"] == "expired"


# --- coleta de lixo -------------------------------------------------------------------


def test_garbage_collection_respects_pins_references_and_the_grace_window(engine, tmp_path):
    root = snapshots.snapshot_root()
    keep = _snapshot(engine, start="2026-08-01", periods=60, base=100.0)
    expired = _snapshot(engine, start="2025-01-01", periods=60, base=900.0)
    pinned = _snapshot(engine, start="2024-01-01", periods=40, base=700.0)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        _favorite(db, pinned)
    past = datetime.now(timezone.utc) - timedelta(days=1)
    with engine.begin() as conn:
        snapshots.pin(conn, pinned)
        conn.execute(
            text(
                "UPDATE execution_data_snapshots SET retain_until = :t WHERE snapshot_id = ANY(:ids)"
            ),
            {"t": past, "ids": [expired, pinned]},
        )

    def shas(sid):
        return {s["sha256"] for e in _row(engine, sid)["series"] for s in e["segments"]}

    expired_shas, pinned_shas, keep_shas = shas(expired), shas(pinned), shas(keep)
    # Dentro da carência, nenhum arquivo sai (podem ser de um manifesto ainda em gravação).
    first = snapshots.collect_garbage(engine, root)
    assert first["manifests_deleted"] == 1 and first["segments_deleted"] == 0
    assert snapshots.get_manifest(engine, expired) is None
    assert (
        snapshots.get_manifest(engine, pinned) is not None
        and snapshots.get_manifest(engine, keep) is not None
    )
    # Depois da carência, só segmento sem referência vai embora.
    second = snapshots.collect_garbage(
        engine, root, now=datetime.now(timezone.utc) + timedelta(hours=2)
    )
    assert second["segments_deleted"] > 0
    on_disk = {p.stem for p in (root / "segments").rglob("*.parquet")}
    assert pinned_shas <= on_disk and keep_shas <= on_disk
    assert not ((expired_shas - pinned_shas - keep_shas) & on_disk)


def test_reused_orphan_segment_survives_gc_until_the_new_manifest_exists(engine):
    root = snapshots.snapshot_root()
    frame = _frame("2026-08-01", 20, 100.0)
    [orphan] = snapshots.freeze_frame(root, frame)
    path = snapshots.segment_path(root, orphan["sha256"])
    old = (datetime.now(timezone.utc) - timedelta(days=3)).timestamp()
    os.utime(path, (old, old))  # órfão antigo, sem manifesto, já fora da carência
    # Nova execução reaproveita os mesmos bytes e ainda não gravou o manifesto.
    [reused] = snapshots.freeze_frame(root, frame)
    assert reused["sha256"] == orphan["sha256"]
    summary = snapshots.collect_garbage(engine, root)
    assert summary["segments_deleted"] == 0 and path.exists()
    # Sem nova execução, o órfão volta a ser coletado depois da carência.
    later = datetime.now(timezone.utc) + timedelta(hours=2)
    assert snapshots.collect_garbage(engine, root, now=later)["segments_deleted"] == 1
    assert not path.exists()


# --- reprodução ------------------------------------------------------------------------


class _Reproducer:
    """Otimizador que lê só a amostra congelada, como a execução refeita."""

    seen: list = []

    def run_optimization(self, **kwargs):
        candles = discovery_inputs.FrozenProvider().fetch_ohlcv()
        intraday = discovery_inputs.read("intraday")
        _Reproducer.seen.append((len(candles), len(intraday), kwargs["end_date"]))
        return {
            "best_metrics": {
                "total_return_pct": float(candles["close"].sum()) / 1000.0,
                "total_trades": 1,
            }
        }


def test_favorite_is_reproduced_from_its_sample_after_a_refresh(engine):
    sid = _snapshot(engine, base=300.0)
    expected = float(_frame("2026-08-01", 60, 300.0)["close"].sum()) / 1000.0
    Session = sessionmaker(bind=engine)
    with Session() as db:
        favorite = _favorite(db, sid)
        favorite.metrics = {"total_return_pct": expected, "total_trades": 1}
        with engine.begin() as conn:
            snapshots.pin(conn, sid)
        db.commit()
        outcome = reproduction.reproduce_favorite(
            favorite, engine=engine, optimizer_factory=_Reproducer
        )
    assert outcome["reproduced"] and outcome["metrics_match"] is True and outcome["deltas"] == {}
    assert _Reproducer.seen[-1] == (60, 60, "2026-10-01")
    assert outcome["candles"] == 60 and outcome["status"]["state"] == "pinned"
    # Depois do refresh seguinte o número muda e a amostra também: a nova reproduz o novo número.
    with Session() as db:
        favorite = db.query(FavoriteStrategy).filter_by(user_id="user-1118").one()
        favorite.metrics = {"total_return_pct": expected + 1, "total_trades": 1}
        db.commit()
        diverged = reproduction.reproduce_favorite(
            favorite, engine=engine, optimizer_factory=_Reproducer
        )
    assert diverged["metrics_match"] is False and "total_return_pct" in diverged["deltas"]


def test_expired_or_missing_sample_answers_not_reproducible_exactly(engine):
    sid = _snapshot(engine)
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE execution_data_snapshots SET retain_until = now() - interval '1 day'"),
        )
    Session = sessionmaker(bind=engine)
    with Session() as db:
        favorite = _favorite(db, sid)
        outcome = reproduction.reproduce_favorite(
            favorite, engine=engine, optimizer_factory=_Reproducer
        )
        old_favorite = _favorite(db, None)
        old_outcome = reproduction.reproduce_favorite(
            old_favorite, engine=engine, optimizer_factory=_Reproducer
        )
    assert outcome["reproduced"] is False
    assert "não reproduzível exatamente" in outcome["status"]["message"]
    assert old_outcome["reproduced"] is False and old_outcome["status"]["state"] == "none"


def test_reproduce_endpoint_reports_a_tampered_sample_without_running(engine):
    sid = _snapshot(engine)
    entry = _row(engine, sid)["series"][0]
    snapshots.segment_path(snapshots.snapshot_root(), entry["segments"][0]["sha256"]).write_bytes(
        b"x"
    )
    Session = sessionmaker(bind=engine)
    with Session() as db:
        favorite = _favorite(db, sid)
        with engine.begin() as conn:
            snapshots.pin(conn, sid)
        with pytest.raises(HTTPException) as caught:
            favorites_routes.reproduce_favorite_endpoint(
                favorite.id, current_user_id="user-1118", db=db
            )
    assert caught.value.status_code == 409
    assert caught.value.detail["code"] == "frozen_input_corrupt"
    with Session() as db:
        status = favorites_routes.get_favorite_sample(
            db.query(FavoriteStrategy).one().id, current_user_id="user-1118", db=db
        )
    assert status["state"] == "pinned"
