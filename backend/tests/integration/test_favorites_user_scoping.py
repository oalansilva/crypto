from __future__ import annotations

import asyncio
from pathlib import Path
import uuid

from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import MonitorStrategyPreference, User
from app.routes import favorites
from app.services.opportunity_service import OpportunityService


def _session_factory(tmp_path: Path):
    db_file = tmp_path / "favorites_test.db"
    engine = create_engine(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE monitor_strategy_preferences ADD COLUMN IF NOT EXISTS tier INTEGER NULL"
            )
        )
        connection.execute(
            text("DELETE FROM monitor_strategy_preferences WHERE user_id IN ('user-a', 'user-b')")
        )
        connection.execute(
            text("DELETE FROM favorite_strategies WHERE user_id IN ('user-a', 'user-b')")
        )
    return TestingSessionLocal


def _favorite_payload(name: str, symbol: str = "BTC/USDT") -> favorites.FavoriteStrategyCreate:
    return favorites.FavoriteStrategyCreate(
        name=name,
        symbol=symbol,
        timeframe="1d",
        strategy_name="multi_ma_crossover",
        parameters={"ema_short": 9, "sma_medium": 21, "sma_long": 50, "direction": "long"},
        metrics={"total_return_pct": 12.3},
        period_type="2y",
    )


def test_favorites_list_only_returns_current_user_rows(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        favorites.create_favorite(_favorite_payload("A favorite"), current_user_id="user-a", db=db)
        favorites.create_favorite(
            _favorite_payload("B favorite", symbol="ETH/USDT"), current_user_id="user-b", db=db
        )
        listed_b = favorites.list_favorites(current_user_id="user-b", db=db)
        listed_a = favorites.list_favorites(current_user_id="user-a", db=db)

    assert [item.name for item in listed_b] == ["B favorite"]
    assert [item.name for item in listed_a] == ["A favorite"]
    assert listed_a[0].strategy_name == "Estratégia protegida"
    assert listed_a[0].parameters == {}
    assert listed_a[0].is_strategy_protected is True


def test_favorites_list_keeps_strategy_details_for_admin(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    monkeypatch.setattr(favorites, "can_view_strategy_secrets", lambda *_args, **_kwargs: True)

    with SessionLocal() as db:
        favorites.create_favorite(
            _favorite_payload("A favorite"), current_user_id="admin-user", db=db
        )
        listed = favorites.list_favorites(current_user_id="admin-user", db=db)

    assert listed[0].strategy_name == "multi_ma_crossover"
    assert listed[0].parameters == {
        "ema_short": 9,
        "sma_medium": 21,
        "sma_long": 50,
        "direction": "long",
    }
    assert listed[0].is_strategy_protected is False


def test_favorites_exists_and_mutations_are_scoped_per_user(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        created = favorites.create_favorite(
            _favorite_payload("Scoped favorite"), current_user_id="user-a", db=db
        )

        exists_a = favorites.favorite_exists(
            strategy_name="multi_ma_crossover",
            symbol="BTC/USDT",
            timeframe="1d",
            period_type="2y",
            direction="long",
            current_user_id="user-a",
            db=db,
        )
        exists_b = favorites.favorite_exists(
            strategy_name="multi_ma_crossover",
            symbol="BTC/USDT",
            timeframe="1d",
            period_type="2y",
            direction="long",
            current_user_id="user-b",
            db=db,
        )

        try:
            favorites.update_favorite(
                created.id,
                favorites.FavoriteStrategyUpdate(tier=1),
                current_user_id="user-b",
                db=db,
            )
            raise AssertionError("user-b should not update user-a favorite")
        except HTTPException as exc:
            assert exc.status_code == 404

        try:
            favorites.delete_favorite(created.id, current_user_id="user-b", db=db)
            raise AssertionError("user-b should not delete user-a favorite")
        except HTTPException as exc:
            assert exc.status_code == 404

        updated = favorites.update_favorite(
            created.id,
            favorites.FavoriteStrategyUpdate(tier=2),
            current_user_id="user-a",
            db=db,
        )
        final_a = favorites.list_favorites(current_user_id="user-a", db=db)

    assert exists_a.exists is True
    assert exists_b.exists is False
    assert updated.tier == 2
    assert final_a[0].tier == 2


def test_common_user_lists_admin_catalog_and_saves_own_star_tier(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    admin_id = str(uuid.uuid4())
    common_id = str(uuid.uuid4())
    admin_email = f"admin-{uuid.uuid4()}@example.com"
    common_email = f"common-{uuid.uuid4()}@example.com"
    monkeypatch.setattr(favorites, "ADMIN_EMAILS", {admin_email})
    monkeypatch.setattr(
        favorites, "is_admin_email", lambda email: str(email).lower() == admin_email
    )

    with SessionLocal() as db:
        db.add(
            User(
                id=admin_id,
                email=admin_email,
                password_hash="x",
                name="Alan Admin",
            )
        )
        db.add(
            User(
                id=common_id,
                email=common_email,
                password_hash="x",
                name="Alan Common",
            )
        )
        db.commit()

        admin_favorite = favorites.create_favorite(
            _favorite_payload("Admin generated", symbol="BTC/USDT"),
            current_user_id=admin_id,
            db=db,
        )

        common_list = favorites.list_favorites(current_user_id=common_id, db=db)
        updated = favorites.update_favorite(
            admin_favorite.id,
            favorites.FavoriteStrategyUpdate(tier=1),
            current_user_id=common_id,
            db=db,
        )
        common_list_after = favorites.list_favorites(current_user_id=common_id, db=db)

        admin_row = db.query(favorites.FavoriteStrategy).filter_by(id=admin_favorite.id).one()
        common_pref = (
            db.query(MonitorStrategyPreference)
            .filter_by(user_id=common_id, favorite_id=admin_favorite.id)
            .one()
        )

    assert [item.id for item in common_list] == [admin_favorite.id]
    assert common_list[0].tier is None
    assert common_list[0].strategy_name == "Estratégia protegida"
    assert updated.tier == 1
    assert common_list_after[0].tier == 1
    assert admin_row.tier is None
    assert common_pref.tier == 1
    assert common_pref.liked is True


def test_common_user_monitor_favorites_use_own_star_tier(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    admin_id = str(uuid.uuid4())
    common_id = str(uuid.uuid4())
    admin_email = f"admin-{uuid.uuid4()}@example.com"
    common_email = f"common-{uuid.uuid4()}@example.com"

    from app.services import opportunity_service

    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    monkeypatch.setattr(favorites, "ADMIN_EMAILS", {admin_email})
    monkeypatch.setattr(
        favorites, "is_admin_email", lambda email: str(email).lower() == admin_email
    )
    monkeypatch.setattr(opportunity_service, "ADMIN_EMAILS", {admin_email})

    with SessionLocal() as db:
        db.add(
            User(
                id=admin_id,
                email=admin_email,
                password_hash="x",
                name="Alan Admin",
            )
        )
        db.add(
            User(
                id=common_id,
                email=common_email,
                password_hash="x",
                name="Alan Common",
            )
        )
        db.commit()

        admin_favorite = favorites.create_favorite(
            _favorite_payload("Admin generated", symbol="BTC/USDT"),
            current_user_id=admin_id,
            db=db,
        )
        db.add(
            MonitorStrategyPreference(
                user_id=common_id,
                favorite_id=admin_favorite.id,
                liked=True,
                tier=2,
            )
        )
        db.commit()

    service = OpportunityService()
    selected = service.get_favorites(user_id=common_id, tier_filter="1,2,3")
    unselected = service.get_favorites(user_id=common_id, tier_filter="1")

    assert [item["id"] for item in selected] == [admin_favorite.id]
    assert selected[0]["tier"] == 2
    assert unselected == []


def test_favorite_trades_returns_saved_trades_without_regeneration(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    monkeypatch.setattr(favorites, "can_view_strategy_secrets", lambda *_args, **_kwargs: True)

    with SessionLocal() as db:
        created = favorites.create_favorite(
            favorites.FavoriteStrategyCreate(
                **{
                    **_favorite_payload("Saved trades").model_dump(),
                    "metrics": {
                        "total_trades": 1,
                        "trades": [{"entry_time": "2026-01-01T00:00:00Z", "profit": 0.01}],
                        "analysis_candles": [
                            {"timestamp_utc": "2026-01-01T00:00:00Z", "close": 100}
                        ],
                    },
                }
            ),
            current_user_id="user-a",
            db=db,
        )

        response = asyncio.run(
            favorites.get_favorite_trades(created.id, current_user_id="user-a", db=db)
        )

    assert response.regenerated is False
    assert response.metrics_match is True
    assert response.trades == [{"entry_time": "2026-01-01T00:00:00Z", "profit": 0.01}]


def test_favorite_trades_backfills_legacy_saved_trades_without_chart_context(
    tmp_path: Path, monkeypatch
):
    SessionLocal = _session_factory(tmp_path)
    monkeypatch.setattr(favorites, "can_view_strategy_secrets", lambda *_args, **_kwargs: True)
    calls = {"count": 0}

    async def fake_run_favorite_optimization(_favorite):
        calls["count"] += 1
        return {
            "best_metrics": {
                "total_trades": 1,
                "win_rate": 1,
                "total_return": 0.01,
                "total_return_pct": 1,
                "max_drawdown": 0,
                "profit_factor": 999,
            },
            "trades": [{"entry_time": "2026-01-01T00:00:00Z", "profit": 0.01}],
            "candles": [{"timestamp_utc": "2026-01-01T00:00:00Z", "close": 100}],
            "indicator_data": {"sma_medium": [99]},
            "execution_mode": "fast_1d",
        }

    monkeypatch.setattr(favorites, "_run_favorite_optimization", fake_run_favorite_optimization)

    with SessionLocal() as db:
        created = favorites.create_favorite(
            favorites.FavoriteStrategyCreate(
                **{
                    **_favorite_payload("Legacy saved trades").model_dump(),
                    "metrics": {
                        "total_trades": 1,
                        "win_rate": 1,
                        "total_return": 0.01,
                        "total_return_pct": 1,
                        "max_drawdown": 0,
                        "profit_factor": 999,
                        "trades": [{"entry_time": "2026-01-01T00:00:00Z", "profit": 0.01}],
                    },
                }
            ),
            current_user_id="user-a",
            db=db,
        )

        response = asyncio.run(
            favorites.get_favorite_trades(created.id, current_user_id="user-a", db=db)
        )
        cached_response = asyncio.run(
            favorites.get_favorite_trades(created.id, current_user_id="user-a", db=db)
        )
        stored = db.query(favorites.FavoriteStrategy).filter_by(id=created.id).one().metrics

    assert response.regenerated is True
    assert cached_response.regenerated is False
    assert calls["count"] == 1
    assert response.candles == [{"timestamp_utc": "2026-01-01T00:00:00Z", "close": 100}]
    assert cached_response.candles == response.candles
    assert stored["analysis_candles"] == response.candles


def test_favorite_trades_regenerates_and_persists_missing_trades(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    monkeypatch.setattr(favorites, "can_view_strategy_secrets", lambda *_args, **_kwargs: True)

    async def fake_run_favorite_optimization(favorite):
        assert favorite.strategy_name == "multi_ma_crossover"
        assert favorite.symbol == "BTC/USDT"
        assert favorite.timeframe == "1d"
        return {
            "best_metrics": {
                "total_trades": 1,
                "win_rate": 1,
                "total_return": 0.01,
                "total_return_pct": 1,
                "max_drawdown": 0,
                "profit_factor": 999,
            },
            "trades": [{"entry_time": "2026-01-01T00:00:00Z", "profit": 0.01}],
            "candles": [{"timestamp_utc": "2026-01-01T00:00:00Z", "close": 100}],
            "indicator_data": {"ema_short": [100]},
            "execution_mode": "fast_1d",
        }

    monkeypatch.setattr(favorites, "_run_favorite_optimization", fake_run_favorite_optimization)

    with SessionLocal() as db:
        created = favorites.create_favorite(
            favorites.FavoriteStrategyCreate(
                **{
                    **_favorite_payload("Missing trades").model_dump(),
                    "metrics": {
                        "total_trades": 1,
                        "win_rate": 1,
                        "total_return": 0.01,
                        "total_return_pct": 1,
                        "max_drawdown": 0,
                        "profit_factor": 999,
                    },
                }
            ),
            current_user_id="user-a",
            db=db,
        )

        response = asyncio.run(
            favorites.get_favorite_trades(created.id, current_user_id="user-a", db=db)
        )
        stored = db.query(favorites.FavoriteStrategy).filter_by(id=created.id).one().metrics

    assert response.regenerated is True
    assert response.metrics_match is True
    assert response.metrics_deltas == {}
    assert response.trades == [{"entry_time": "2026-01-01T00:00:00Z", "profit": 0.01}]
    assert response.candles == [{"timestamp_utc": "2026-01-01T00:00:00Z", "close": 100}]
    assert response.indicator_data == {"ema_short": [100]}
    assert stored["trades"] == response.trades
    assert stored["trades_history_cached"] is True
    assert stored["trades_metrics_match"] is True
    assert stored["analysis_candles"] == response.candles
    assert stored["analysis_indicator_data"] == response.indicator_data


def test_favorite_trades_reports_metric_mismatch(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    monkeypatch.setattr(favorites, "can_view_strategy_secrets", lambda *_args, **_kwargs: True)
    calls = {"count": 0}

    async def fake_run_favorite_optimization(_favorite):
        calls["count"] += 1
        return {
            "best_metrics": {
                "total_trades": 2,
                "win_rate": 0.5,
                "total_return": 0.02,
                "total_return_pct": 2,
                "max_drawdown": 0,
                "profit_factor": 1,
            },
            "trades": [{"entry_time": "2026-01-01T00:00:00Z", "profit": 0.01}],
            "candles": [{"timestamp_utc": "2026-01-01T00:00:00Z", "close": 100}],
            "indicator_data": {"sma_medium": [99]},
        }

    monkeypatch.setattr(favorites, "_run_favorite_optimization", fake_run_favorite_optimization)

    with SessionLocal() as db:
        created = favorites.create_favorite(
            _favorite_payload("Mismatch trades"),
            current_user_id="user-a",
            db=db,
        )
        response = asyncio.run(
            favorites.get_favorite_trades(created.id, current_user_id="user-a", db=db)
        )
        cached_response = asyncio.run(
            favorites.get_favorite_trades(created.id, current_user_id="user-a", db=db)
        )
        stored = db.query(favorites.FavoriteStrategy).filter_by(id=created.id).one().metrics

    assert response.metrics_match is False
    assert "total_return_pct" in response.metrics_deltas
    assert response.regenerated is True
    assert cached_response.regenerated is False
    assert cached_response.metrics_match is False
    assert cached_response.metrics_deltas == response.metrics_deltas
    assert cached_response.trades == response.trades
    assert calls["count"] == 1
    assert stored["trades"] == response.trades
    assert stored["trades_history_cached"] is True
    assert stored["trades_metrics_match"] is False
    assert stored["trades_metrics_deltas"] == response.metrics_deltas


def test_favorite_trade_regeneration_uses_fixed_optimize_ranges():
    ranges = favorites._fixed_optimization_ranges(
        {
            "ema_short": 9,
            "sma_medium": 21,
            "stop_loss": 0.015,
            "direction": "long",
            "data_source": "ccxt",
            "enabled": True,
        }
    )

    assert ranges == {
        "ema_short": {"min": 9, "max": 9, "step": 1},
        "sma_medium": {"min": 21, "max": 21, "step": 1},
        "stop_loss": {"min": 0.015, "max": 0.015, "step": 0.0001},
    }


def test_favorite_trades_rejects_protected_access(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    monkeypatch.setattr(favorites, "can_view_strategy_secrets", lambda *_args, **_kwargs: False)

    with SessionLocal() as db:
        created = favorites.create_favorite(
            _favorite_payload("Protected trades"),
            current_user_id="user-a",
            db=db,
        )
        try:
            asyncio.run(favorites.get_favorite_trades(created.id, current_user_id="user-b", db=db))
            raise AssertionError("protected favorite trades should be rejected")
        except HTTPException as exc:
            assert exc.status_code == 403
