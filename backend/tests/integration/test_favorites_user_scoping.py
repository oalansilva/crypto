from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
import uuid

from fastapi import HTTPException
import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import AutoBacktestRun, MonitorStrategyPreference, User
from app.routes import favorites
from app.services.favorite_backtest_refresh_service import (
    FavoriteBacktestRefreshService,
    REFRESH_STATUS_FAILED,
    REFRESH_STATUS_SUCCESS,
)
from app.services.opportunity_service import OpportunityService
from app.services.strategy_transparency import (
    build_strategy_transparency,
    build_strategy_transparency_from_candles,
)


@pytest.fixture(autouse=True)
def _disable_live_favorite_candle_repository(monkeypatch):
    class DisabledRepository:
        enabled = False

    monkeypatch.setattr(favorites, "_FAVORITE_OHLCV_REPO", DisabledRepository())


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
            text(
                "ALTER TABLE favorite_strategies ADD COLUMN IF NOT EXISTS notify_telegram BOOLEAN NOT NULL DEFAULT TRUE"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE favorite_strategies ADD COLUMN IF NOT EXISTS auto_refresh_status VARCHAR NULL"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE favorite_strategies ADD COLUMN IF NOT EXISTS auto_refresh_error TEXT NULL"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE favorite_strategies ADD COLUMN IF NOT EXISTS auto_refresh_started_at TIMESTAMP NULL"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE favorite_strategies ADD COLUMN IF NOT EXISTS auto_refresh_completed_at TIMESTAMP NULL"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE favorite_strategies ADD COLUMN IF NOT EXISTS auto_refresh_run_id VARCHAR NULL"
            )
        )
        connection.execute(
            text("DELETE FROM monitor_strategy_preferences WHERE user_id IN ('user-a', 'user-b')")
        )
        connection.execute(
            text(
                "DELETE FROM monitor_strategy_preferences "
                "WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'admin-%@example.com' OR email LIKE 'common-%@example.com')"
            )
        )
        connection.execute(
            text(
                "DELETE FROM favorite_strategies "
                "WHERE user_id IN ('user-a', 'user-b', 'admin-user') "
                "OR user_id IN (SELECT id FROM users WHERE email LIKE 'admin-%@example.com' OR email LIKE 'common-%@example.com')"
            )
        )
        connection.execute(
            text(
                "DELETE FROM users WHERE email LIKE 'admin-%@example.com' OR email LIKE 'common-%@example.com'"
            )
        )
    return TestingSessionLocal


def _favorite_payload(
    name: str,
    symbol: str = "BTC/USDT",
    strategy_name: str = "multi_ma_crossover",
) -> favorites.FavoriteStrategyCreate:
    return favorites.FavoriteStrategyCreate(
        name=name,
        symbol=symbol,
        timeframe="1d",
        strategy_name=strategy_name,
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
    assert listed_a[0].strategy_display_name == "Médias Móveis: Tendência em Virada"
    assert listed_a[0].parameters == {}
    assert listed_a[0].is_strategy_protected is True
    assert "tendência" in (listed_a[0].strategy_description or "").lower()


def test_favorites_list_keeps_strategy_details_for_admin(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    monkeypatch.setattr(favorites, "can_view_strategy_secrets", lambda *_args, **_kwargs: True)

    with SessionLocal() as db:
        created = favorites.create_favorite(
            _favorite_payload("A favorite"), current_user_id="admin-user", db=db
        )
        updated = favorites.update_favorite(
            created.id,
            favorites.FavoriteStrategyUpdate(notify_telegram=False),
            current_user_id="admin-user",
            db=db,
        )
        listed = favorites.list_favorites(current_user_id="admin-user", db=db)

    assert listed[0].strategy_name == "multi_ma_crossover"
    assert "tendência" in (listed[0].strategy_description or "").lower()
    assert listed[0].notify_telegram is False
    assert updated.notify_telegram is False
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


def test_common_user_cannot_update_admin_catalog_telegram_notification(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    admin_id = str(uuid.uuid4())
    common_id = str(uuid.uuid4())
    admin_email = f"admin-{uuid.uuid4()}@example.com"
    monkeypatch.setattr(favorites, "ADMIN_EMAILS", {admin_email})
    monkeypatch.setattr(
        favorites, "is_admin_email", lambda email: str(email).lower() == admin_email
    )

    with SessionLocal() as db:
        db.add(User(id=admin_id, email=admin_email, password_hash="x", name="Admin"))
        db.add(
            User(
                id=common_id,
                email=f"common-{uuid.uuid4()}@example.com",
                password_hash="x",
                name="Common",
            )
        )
        db.commit()
        admin_favorite = favorites.create_favorite(
            _favorite_payload("Admin generated", symbol="BTC/USDT"),
            current_user_id=admin_id,
            db=db,
        )

        try:
            favorites.update_favorite(
                admin_favorite.id,
                favorites.FavoriteStrategyUpdate(notify_telegram=False),
                current_user_id=common_id,
                db=db,
            )
            raise AssertionError("common user should not update Telegram notification")
        except HTTPException as exc:
            assert exc.status_code == 403


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
        admin_second_favorite = favorites.create_favorite(
            _favorite_payload(
                "Admin generated second",
                symbol="ETH/USDT",
                strategy_name="ema_rsi",
            ),
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

    assert [item.id for item in common_list] == [admin_favorite.id, admin_second_favorite.id]
    assert common_list[0].tier is None
    assert common_list[0].strategy_name == "Estratégia protegida"
    assert common_list[0].strategy_display_name == "Médias Móveis: Tendência em Virada"
    assert common_list[1].strategy_name == "Estratégia protegida"
    assert common_list[1].strategy_display_name == "RSI: Retomada com Força"
    assert common_list[0].parameters == {}
    assert common_list[1].parameters == {}
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


def test_favorite_trades_removes_future_cached_exit_but_keeps_open_entry(
    tmp_path: Path, monkeypatch
):
    SessionLocal = _session_factory(tmp_path)
    monkeypatch.setattr(favorites, "can_view_strategy_secrets", lambda *_args, **_kwargs: True)

    with SessionLocal() as db:
        created = favorites.create_favorite(
            favorites.FavoriteStrategyCreate(
                **{
                    **_favorite_payload("Future cached exit").model_dump(),
                    "metrics": {
                        "total_trades": 1,
                        "trades_history_cached": True,
                        "trades": [
                            {
                                "entry_time": "2026-07-10T00:00:00Z",
                                "entry_price": 63230.01,
                                "exit_time": "2026-07-12T00:00:00Z",
                                "exit_price": 64344.76,
                                "profit": 0.0161,
                                "exit_reason": "signal_15m",
                            },
                            {
                                "entry_time": "2026-07-11T00:00:00Z",
                                "entry_price": 64000.00,
                                "exit_time": "invalid",
                                "exit_price": 65000.00,
                                "profit": 0.02,
                            },
                        ],
                        "analysis_candles": [
                            {"timestamp_utc": "2026-07-10T00:00:00Z", "close": 63230.01},
                            {"timestamp_utc": "2026-07-11T00:00:00Z", "close": 64000.00},
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
        listed = favorites.list_favorites(current_user_id="user-a", db=db)

    expected = [
        {"entry_time": "2026-07-10T00:00:00Z", "entry_price": 63230.01},
        {"entry_time": "2026-07-11T00:00:00Z", "entry_price": 64000.00},
    ]
    assert response.regenerated is False
    assert response.trades == expected
    assert listed[0].metrics["trades"] == expected


def test_favorite_trades_preserves_history_before_partial_candle_window():
    trades = [
        {
            "entry_time": "2026-05-09T00:00:00Z",
            "exit_time": "2026-05-20T00:00:00Z",
            "profit": -0.0438,
        }
    ]
    candles = [{"timestamp_utc": "2026-05-20T00:00:00Z", "close": 0.08877}]

    assert favorites._safe_cached_trades(trades, candles, "1d") == trades


def test_safe_cached_metrics_preserves_missing_trades_key():
    assert "trades" not in favorites._safe_cached_metrics({"total_trades": 1}, "1d")


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


def test_favorite_trades_accepts_reconstructed_metrics_and_keeps_investigation_deltas(
    tmp_path: Path, monkeypatch
):
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

    assert response.metrics_match is True
    assert "total_return_pct" in response.metrics_deltas
    assert response.regenerated is True
    assert cached_response.regenerated is False
    assert cached_response.metrics_match is True
    assert cached_response.metrics_deltas == response.metrics_deltas
    assert cached_response.trades == response.trades
    assert calls["count"] == 1
    assert stored["trades"] == response.trades
    assert stored["trades_history_cached"] is True
    assert stored["trades_metrics_match"] is True
    assert stored["trades_reconciled_from_mismatch"] is True
    assert stored["trades_metrics_deltas"] == response.metrics_deltas
    assert stored["trades_previous_summary"]["total_return_pct"] == 12.3
    assert stored["trades_reconciled_summary"]["total_return_pct"] == 2
    assert stored["total_trades"] == 2
    assert stored["total_return_pct"] == 2
    assert isinstance(stored["trades_reconciled_at"], str)


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
            assert exc.status_code == 404


def test_common_user_can_read_cached_admin_catalog_chart_trades(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    admin_id = str(uuid.uuid4())
    common_id = str(uuid.uuid4())
    admin_email = f"admin-{uuid.uuid4()}@example.com"
    monkeypatch.setattr(favorites, "ADMIN_EMAILS", {admin_email})
    monkeypatch.setattr(
        favorites, "is_admin_email", lambda email: str(email).lower() == admin_email
    )
    monkeypatch.setattr(
        favorites,
        "can_view_strategy_secrets",
        lambda _db, user_id: str(user_id) == admin_id,
    )

    with SessionLocal() as db:
        db.add(User(id=admin_id, email=admin_email, password_hash="x", name="Admin"))
        db.add(
            User(
                id=common_id,
                email=f"common-{uuid.uuid4()}@example.com",
                password_hash="x",
                name="Common",
            )
        )
        db.commit()
        created = favorites.create_favorite(
            favorites.FavoriteStrategyCreate(
                **{
                    **_favorite_payload("Admin cached trades", symbol="HBAR/USDT").model_dump(),
                    "metrics": {
                        "total_trades": 1,
                        "win_rate": 0,
                        "total_return_pct": -4.3,
                        "trades": [
                            {
                                "entry_time": "2026-05-09T00:00:00+00:00",
                                "entry_price": 0.0927,
                                "exit_time": "2026-05-20T00:00:00+00:00",
                                "exit_price": 0.08877,
                                "profit": -0.0438,
                            }
                        ],
                        "analysis_candles": [
                            {"timestamp_utc": "2026-05-20T00:00:00+00:00", "close": 0.08877}
                        ],
                        "analysis_indicator_data": {"short": [0.09]},
                    },
                }
            ),
            current_user_id=admin_id,
            db=db,
        )

        response = asyncio.run(
            favorites.get_favorite_trades(created.id, current_user_id=common_id, db=db)
        )

    assert response.regenerated is False
    assert response.trades[0]["exit_time"] == "2026-05-20T00:00:00+00:00"
    assert response.candles == [{"timestamp_utc": "2026-05-20T00:00:00+00:00", "close": 0.08877}]
    assert response.indicator_data == {}
    assert response.metrics == {
        "total_trades": 1,
        "win_rate": 0,
        "total_return_pct": -4.3,
    }


def test_common_user_get_favorite_trades_rebuilds_legacy_timestamped_manifest(
    tmp_path: Path, monkeypatch
):
    SessionLocal = _session_factory(tmp_path)
    admin_id = str(uuid.uuid4())
    common_id = str(uuid.uuid4())
    admin_email = f"admin-{uuid.uuid4()}@example.com"
    timestamps = [
        "2026-06-26T00:00:00Z",
        "2026-06-27T00:00:00Z",
        "2026-06-28T00:00:00Z",
    ]
    template_data = {
        "indicators": [
            {"type": "ema", "alias": "short", "params": {"length": 18}},
            {"type": "sma", "alias": "medium", "params": {"length": 20}},
            {"type": "sma", "alias": "long", "params": {"length": 35}},
        ],
        "entry_logic": "(short > long) & crossover(short, medium)",
        "exit_logic": "crossunder(short, long)",
        "stop_loss": 0.042,
    }
    monkeypatch.setattr(favorites, "ADMIN_EMAILS", {admin_email})
    monkeypatch.setattr(
        favorites,
        "is_admin_email",
        lambda email: str(email).lower() == admin_email,
    )
    monkeypatch.setattr(
        favorites,
        "can_view_strategy_secrets",
        lambda _db, user_id: str(user_id) == admin_id,
    )
    monkeypatch.setattr(
        favorites,
        "_strategy_templates_for_rows",
        lambda _db, rows: {str(row.strategy_name): template_data for row in rows},
    )

    with SessionLocal() as db:
        db.add(User(id=admin_id, email=admin_email, password_hash="x", name="Admin"))
        db.add(
            User(
                id=common_id,
                email=f"common-{uuid.uuid4()}@example.com",
                password_hash="x",
                name="Common",
            )
        )
        db.commit()
        created = favorites.create_favorite(
            favorites.FavoriteStrategyCreate(
                **{
                    **_favorite_payload(
                        "Legacy transparent cache",
                        symbol="SOL/USDT",
                        strategy_name="multi_ma_crossoverV2",
                    ).model_dump(),
                    "parameters": {
                        "direction": "long",
                        "ema_short": 16,
                        "sma_medium": 17,
                        "sma_long": 33,
                        "stop_loss": 0.085,
                    },
                    "metrics": {
                        "total_trades": 1,
                        "win_rate": 1,
                        "total_return_pct": 3.2,
                        "trades_history_cached": True,
                        "trades": [
                            {
                                "entry_time": timestamps[0],
                                "entry_price": 135,
                                "exit_time": timestamps[2],
                                "exit_price": 139,
                                "profit": 0.032,
                            }
                        ],
                        "analysis_candles": [
                            {"timestamp_utc": timestamp, "close": close}
                            for timestamp, close in zip(timestamps, [135, 137, 139], strict=True)
                        ],
                        "analysis_indicator_data": {
                            "short": [134.5, 135.5, 137.0],
                            "medium": [133.0, 134.0, 135.0],
                            "long": [130.0, 131.0, 132.0],
                            "ADX_14": [22.0, 23.0, 24.0],
                            "private_diagnostic": [999.0, 999.0, 999.0],
                        },
                    },
                }
            ),
            current_user_id=admin_id,
            db=db,
        )
        stored_metrics = db.query(favorites.FavoriteStrategy).filter_by(id=created.id).one().metrics
        assert "analysis_strategy_transparency" not in stored_metrics

        response = asyncio.run(
            favorites.get_favorite_trades(created.id, current_user_id=common_id, db=db)
        )

    manifest = response.strategy_transparency
    assert response.regenerated is False
    assert response.indicator_data == {}
    assert manifest is not None
    assert manifest.status == "available"
    assert manifest.timeframe == "1d"
    assert manifest.parameters == {
        "short_length": 16,
        "medium_length": 17,
        "long_length": 33,
        "stop_loss": 0.085,
    }
    assert [indicator.key for indicator in manifest.indicators] == ["short", "medium", "long"]
    assert [indicator.execution_columns for indicator in manifest.indicators] == [
        ["short"],
        ["medium"],
        ["long"],
    ]
    assert all(indicator.series_status == "available" for indicator in manifest.indicators)
    assert [
        [(point.timestamp_utc, point.value) for point in indicator.series]
        for indicator in manifest.indicators
    ] == [
        [
            ("2026-06-26T00:00:00+00:00", 134.5),
            ("2026-06-27T00:00:00+00:00", 135.5),
            ("2026-06-28T00:00:00+00:00", 137.0),
        ],
        [
            ("2026-06-26T00:00:00+00:00", 133.0),
            ("2026-06-27T00:00:00+00:00", 134.0),
            ("2026-06-28T00:00:00+00:00", 135.0),
        ],
        [
            ("2026-06-26T00:00:00+00:00", 130.0),
            ("2026-06-27T00:00:00+00:00", 131.0),
            ("2026-06-28T00:00:00+00:00", 132.0),
        ],
    ]
    assert "ADX_14" not in {
        column for indicator in manifest.indicators for column in indicator.execution_columns
    }


def test_common_user_get_favorite_trades_extends_manifest_to_current_candle_without_optimizer(
    tmp_path: Path, monkeypatch
):
    SessionLocal = _session_factory(tmp_path)
    admin_id = str(uuid.uuid4())
    common_id = str(uuid.uuid4())
    admin_email = f"admin-{uuid.uuid4()}@example.com"
    template_data = {
        "indicators": [
            {"type": "ema", "alias": "short", "params": {"length": 16}},
            {"type": "sma", "alias": "medium", "params": {"length": 17}},
            {"type": "sma", "alias": "long", "params": {"length": 33}},
        ],
        "entry_logic": "(short > long) & crossover(short, medium)",
        "exit_logic": "crossunder(short, long)",
        "stop_loss": 0.085,
    }
    current_candles = [
        {
            "timestamp_utc": timestamp.isoformat(),
            "open": float(99 + index),
            "high": float(101 + index),
            "low": float(98 + index),
            "close": float(100 + index),
            "volume": 1000.0,
        }
        for index, timestamp in enumerate(pd.date_range("2026-06-01", periods=42, tz="UTC"))
    ]

    class CurrentRepository:
        enabled = True

        def __init__(self):
            self.limits = []

        def read_recent_candles(self, symbol, timeframe, limit):
            assert (symbol, timeframe) == ("SOL/USDT", "1d")
            self.limits.append(limit)
            return current_candles

    repository = CurrentRepository()
    monkeypatch.setattr(favorites, "_FAVORITE_OHLCV_REPO", repository)
    monkeypatch.setattr(favorites, "ADMIN_EMAILS", {admin_email})
    monkeypatch.setattr(
        favorites, "is_admin_email", lambda email: str(email).lower() == admin_email
    )
    monkeypatch.setattr(
        favorites,
        "can_view_strategy_secrets",
        lambda _db, user_id: str(user_id) == admin_id,
    )
    monkeypatch.setattr(
        favorites,
        "_strategy_templates_for_rows",
        lambda _db, rows: {str(row.strategy_name): template_data for row in rows},
    )

    async def fail_if_optimized(_favorite):
        raise AssertionError("cached favorite chart refresh must not optimize")

    monkeypatch.setattr(favorites, "_run_favorite_optimization", fail_if_optimized)

    with SessionLocal() as db:
        db.add(User(id=admin_id, email=admin_email, password_hash="x", name="Admin"))
        db.add(
            User(
                id=common_id,
                email=f"common-{uuid.uuid4()}@example.com",
                password_hash="x",
                name="Common",
            )
        )
        db.commit()
        created = favorites.create_favorite(
            favorites.FavoriteStrategyCreate(
                **{
                    **_favorite_payload(
                        "Current transparent cache",
                        symbol="SOL/USDT",
                        strategy_name="multi_ma_crossoverV2",
                    ).model_dump(),
                    "parameters": {
                        "direction": "long",
                        "ema_short": 16,
                        "sma_medium": 17,
                        "sma_long": 33,
                        "stop_loss": 0.085,
                    },
                    "metrics": {
                        "total_trades": 1,
                        "trades_history_cached": True,
                        "trades": [{"entry_time": current_candles[0]["timestamp_utc"]}],
                        "analysis_candles": current_candles[:35],
                        "analysis_indicator_data": {"private_diagnostic": [999.0] * 35},
                    },
                }
            ),
            current_user_id=admin_id,
            db=db,
        )
        favorite_id = created.id
        before_metrics = dict(
            db.query(favorites.FavoriteStrategy).filter_by(id=favorite_id).one().metrics
        )

        response = asyncio.run(
            favorites.get_favorite_trades(favorite_id, current_user_id=common_id, db=db)
        )
        after_metrics = db.query(favorites.FavoriteStrategy).filter_by(id=favorite_id).one().metrics

    manifest = response.strategy_transparency
    assert response.regenerated is False
    assert response.indicator_data == {}
    assert response.trades == before_metrics["trades"]
    assert response.candles[-1]["timestamp_utc"] == "2026-07-12T00:00:00+00:00"
    assert manifest is not None
    assert [indicator.color for indicator in manifest.indicators] == [
        "#f6465d",
        "#ff9f43",
        "#3b82f6",
    ]
    assert all(
        indicator.series[-1].timestamp_utc == "2026-07-12T00:00:00+00:00"
        for indicator in manifest.indicators
    )
    assert repository.limits == [5000]
    assert after_metrics == before_metrics
    assert "private_diagnostic" not in {
        column for indicator in manifest.indicators for column in indicator.execution_columns
    }


def test_current_favorite_chart_context_falls_back_atomically_for_partial_manifest(monkeypatch):
    template_data = {
        "indicators": [
            {"type": "ema", "alias": "short", "params": {"length": 3}},
            {"type": "sma", "alias": "medium", "params": {"length": 4}},
            {"type": "sma", "alias": "long", "params": {"length": 5}},
        ],
        "entry_logic": "short > medium and medium > long",
        "exit_logic": "short < long",
    }
    current_candles = [
        {
            "timestamp_utc": timestamp.isoformat(),
            "open": float(99 + index),
            "high": float(101 + index),
            "low": float(98 + index),
            "close": float(100 + index),
            "volume": 1000.0,
        }
        for index, timestamp in enumerate(pd.date_range("2026-07-01", periods=8, tz="UTC"))
    ]
    saved_candles = current_candles[:6]
    fallback = build_strategy_transparency(
        "multi_ma_crossoverV2",
        template_data,
        timeframe="1d",
    )
    partial = build_strategy_transparency_from_candles(
        "multi_ma_crossoverV2",
        template_data,
        effective_parameters={},
        timeframe="1d",
        candles=current_candles,
    )
    partial.indicators[1].series = partial.indicators[1].series[:-1]

    class CurrentRepository:
        enabled = True

        def read_recent_candles(self, _symbol, _timeframe, _limit):
            return current_candles

    monkeypatch.setattr(favorites, "_FAVORITE_OHLCV_REPO", CurrentRepository())
    monkeypatch.setattr(
        favorites,
        "build_strategy_transparency_from_candles",
        lambda *_args, **_kwargs: partial,
    )

    candles, manifest = favorites._current_favorite_chart_context(
        strategy_name="multi_ma_crossoverV2",
        template_data=template_data,
        effective_parameters={},
        symbol="SOL/USDT",
        timeframe="1d",
        saved_candles=saved_candles,
        fallback_manifest=fallback,
    )

    assert candles == saved_candles
    assert manifest is fallback


def test_common_user_cannot_regenerate_admin_catalog_chart_trades(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    admin_id = str(uuid.uuid4())
    common_id = str(uuid.uuid4())
    admin_email = f"admin-{uuid.uuid4()}@example.com"
    monkeypatch.setattr(favorites, "ADMIN_EMAILS", {admin_email})
    monkeypatch.setattr(
        favorites, "is_admin_email", lambda email: str(email).lower() == admin_email
    )
    monkeypatch.setattr(favorites, "can_view_strategy_secrets", lambda *_args, **_kwargs: False)

    class FailIfReadRepository:
        enabled = True

        def read_recent_candles(self, *_args, **_kwargs):
            raise AssertionError("protected request must not read or calculate current candles")

    monkeypatch.setattr(favorites, "_FAVORITE_OHLCV_REPO", FailIfReadRepository())

    with SessionLocal() as db:
        db.add(User(id=admin_id, email=admin_email, password_hash="x", name="Admin"))
        db.add(
            User(
                id=common_id,
                email=f"common-{uuid.uuid4()}@example.com",
                password_hash="x",
                name="Common",
            )
        )
        db.commit()
        created = favorites.create_favorite(
            favorites.FavoriteStrategyCreate(
                **{
                    **_favorite_payload("Admin summary only", symbol="SOL/USDT").model_dump(),
                    "metrics": {"total_trades": 1},
                }
            ),
            current_user_id=admin_id,
            db=db,
        )

        try:
            asyncio.run(favorites.get_favorite_trades(created.id, current_user_id=common_id, db=db))
            raise AssertionError("common user should not regenerate protected favorite trades")
        except HTTPException as exc:
            assert exc.status_code == 403
            assert exc.detail == "Favorite trade regeneration is protected"


def test_favorite_auto_refresh_persists_success_and_failure(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    monkeypatch.setenv("FAVORITE_BACKTEST_REFRESH_STATE_FILE", str(tmp_path / "refresh-state.json"))
    optimizer_calls = []
    provider_calls = []

    class FakeOptimizer:
        def run_optimization(self, *, symbol: str, **kwargs):
            optimizer_calls.append({"symbol": symbol, **kwargs})
            if symbol == "ETH/USDT":
                raise RuntimeError("market data unavailable")
            return {
                "best_metrics": {"total_return_pct": 8.5, "total_trades": 1},
                "trades": [{"entry_time": "2026-05-01T00:00:00Z", "profit": 0.085}],
                "candles": [{"timestamp_utc": datetime.utcnow().isoformat(), "close": 100}],
                "indicator_data": {"sma_medium": [99]},
                "execution_mode": "favorite_auto_refresh",
            }

    class FakeProvider:
        def fetch_ohlcv(self, **kwargs):
            provider_calls.append(kwargs)
            timestamp = pd.Timestamp.now("UTC")
            return pd.DataFrame(
                {
                    "timestamp_utc": [timestamp],
                    "open": [100.0],
                    "high": [101.0],
                    "low": [99.0],
                    "close": [100.0],
                    "volume": [1.0],
                }
            ).set_index("timestamp_utc", drop=False)

    with SessionLocal() as db:
        short_payload = favorites.FavoriteStrategyCreate(
            **{
                **_favorite_payload("Refresh success", symbol="BTC/USDT").model_dump(),
                "parameters": {
                    "ema_short": 9,
                    "sma_medium": 21,
                    "sma_long": 50,
                    "direction": "short",
                },
            }
        )
        ok = favorites.create_favorite(
            short_payload,
            current_user_id="user-a",
            db=db,
        )
        fail = favorites.create_favorite(
            _favorite_payload("Refresh failure", symbol="ETH/USDT"),
            current_user_id="user-a",
            db=db,
        )
        ok_id = ok.id
        fail_id = fail.id
        (
            db.query(favorites.FavoriteStrategy)
            .filter(favorites.FavoriteStrategy.id.notin_([ok_id, fail_id]))
            .update(
                {
                    "auto_refresh_status": REFRESH_STATUS_SUCCESS,
                    "auto_refresh_completed_at": datetime.utcnow(),
                },
                synchronize_session=False,
            )
        )
        db.commit()

    service = FavoriteBacktestRefreshService(
        db_factory=SessionLocal,
        optimizer_factory=FakeOptimizer,
        market_data_provider_factory=lambda _source: FakeProvider(),
    )
    summary = service.run_due_refreshes(
        interval_seconds=86400,
        cpu_limit_percent=100,
        cpu_pause_seconds=0,
        delete_delisted_binance_favorites=False,
    )

    with SessionLocal() as db:
        ok_row = db.query(favorites.FavoriteStrategy).filter_by(id=ok_id).one()
        fail_row = db.query(favorites.FavoriteStrategy).filter_by(id=fail_id).one()
        runs = (
            db.query(AutoBacktestRun)
            .filter(AutoBacktestRun.run_id.like("favorite-refresh-%"))
            .filter(AutoBacktestRun.favorite_id.in_([ok_id, fail_id]))
            .order_by(AutoBacktestRun.id.asc())
            .all()
        )

    assert summary["due"] == 2
    assert summary["selected"] == 2
    assert summary["success"] == 1
    assert summary["failed"] == 1
    assert summary["skipped_cpu"] == 0
    assert summary["skipped_limit"] == 0
    assert ok_row.auto_refresh_status == REFRESH_STATUS_SUCCESS
    assert ok_row.auto_refresh_error is None
    assert ok_row.auto_refresh_started_at is not None
    assert ok_row.auto_refresh_completed_at is not None
    assert ok_row.auto_refresh_run_id
    assert ok_row.metrics["total_return_pct"] == 8.5
    assert ok_row.metrics["trades_history_cached"] is True
    assert ok_row.metrics["analysis_execution_mode"] == "favorite_auto_refresh"
    success_call = next(call for call in optimizer_calls if call["symbol"] == "BTC/USDT")
    assert success_call["deep_backtest"] is True
    assert success_call["direction"] == "short"
    assert [call["timeframe"] for call in provider_calls[:2]] == ["1d", "15m"]
    assert fail_row.auto_refresh_status == REFRESH_STATUS_FAILED
    assert "market data unavailable" in fail_row.auto_refresh_error
    assert fail_row.metrics["total_return_pct"] == 12.3
    assert {run.status for run in runs} == {REFRESH_STATUS_SUCCESS, REFRESH_STATUS_FAILED}


def test_favorite_auto_refresh_pauses_when_cpu_limit_is_exceeded(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    state_path = tmp_path / "refresh-state.json"
    monkeypatch.setenv("FAVORITE_BACKTEST_REFRESH_STATE_FILE", str(state_path))
    optimizer_calls = []

    class FakeOptimizer:
        def run_optimization(self, **kwargs):
            optimizer_calls.append(kwargs)
            return {
                "best_metrics": {"total_return_pct": 8.5, "total_trades": 1},
                "trades": [{"entry_time": "2026-05-01T00:00:00Z", "profit": 0.085}],
                "candles": [{"timestamp_utc": datetime.utcnow().isoformat(), "close": 100}],
                "indicator_data": {"sma_medium": [99]},
                "execution_mode": "favorite_auto_refresh",
            }

    class FakeProvider:
        def fetch_ohlcv(self, **_kwargs):
            timestamp = pd.Timestamp.now("UTC")
            return pd.DataFrame(
                {
                    "timestamp_utc": [timestamp],
                    "open": [100.0],
                    "high": [101.0],
                    "low": [99.0],
                    "close": [100.0],
                    "volume": [1.0],
                }
            ).set_index("timestamp_utc", drop=False)

    with SessionLocal() as db:
        favorite_a = favorites.create_favorite(
            _favorite_payload("CPU paused A", symbol="BTC/USDT"),
            current_user_id="user-a",
            db=db,
        )
        favorite_b = favorites.create_favorite(
            _favorite_payload("CPU paused B", symbol="ETH/USDT"),
            current_user_id="user-a",
            db=db,
        )
        favorite_ids = [favorite_a.id, favorite_b.id]

    service = FavoriteBacktestRefreshService(
        db_factory=SessionLocal,
        optimizer_factory=FakeOptimizer,
        market_data_provider_factory=lambda _source: FakeProvider(),
        cpu_sampler=lambda: 75.0,
        sleep_fn=lambda _seconds: None,
    )
    summary = service.run_due_refreshes(
        interval_seconds=86400,
        cpu_limit_percent=60,
        cpu_pause_seconds=30,
        delete_delisted_binance_favorites=False,
    )

    with SessionLocal() as db:
        runs = db.query(AutoBacktestRun).filter(AutoBacktestRun.favorite_id.in_(favorite_ids)).all()

    assert summary["status"] == "paused_cpu"
    assert summary["due"] == 2
    assert summary["selected"] == 2
    assert summary["skipped_cpu"] == 2
    assert summary["success"] == 0
    assert summary["failed"] == 0
    assert summary["pause_seconds"] == 30
    assert "above limit" in summary["reason"]
    assert optimizer_calls == []
    assert runs == []
    stored_state = json.loads(state_path.read_text(encoding="utf-8"))
    assert stored_state["status"] == "paused_cpu"


def test_favorite_auto_refresh_rejects_stale_candles(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    optimizer_called = False

    class StaleOptimizer:
        def run_optimization(self, **_kwargs):
            nonlocal optimizer_called
            optimizer_called = True
            return {
                "best_metrics": {"total_return_pct": 8.5, "total_trades": 1},
                "trades": [{"entry_time": "2024-07-01T00:00:00Z", "profit": 0.085}],
                "candles": [{"timestamp_utc": "2024-07-01T00:00:00Z", "close": 100}],
                "indicator_data": {"sma_medium": [99]},
                "execution_mode": "favorite_auto_refresh",
            }

    class StaleProvider:
        def fetch_ohlcv(self, **_kwargs):
            timestamp = pd.Timestamp("2024-07-01T00:00:00Z")
            return pd.DataFrame(
                {
                    "timestamp_utc": [timestamp],
                    "open": [100.0],
                    "high": [101.0],
                    "low": [99.0],
                    "close": [100.0],
                    "volume": [1.0],
                }
            ).set_index("timestamp_utc", drop=False)

    with SessionLocal() as db:
        favorite = favorites.create_favorite(
            _favorite_payload("Stale refresh", symbol="AGIX/USDT"),
            current_user_id="user-a",
            db=db,
        )

    service = FavoriteBacktestRefreshService(
        db_factory=SessionLocal,
        optimizer_factory=StaleOptimizer,
        market_data_provider_factory=lambda _source: StaleProvider(),
    )
    result = service.refresh_favorite(favorite.id)

    with SessionLocal() as db:
        stored = db.query(favorites.FavoriteStrategy).filter_by(id=favorite.id).one()
        run = db.query(AutoBacktestRun).filter_by(favorite_id=favorite.id).one()

    assert result["status"] == REFRESH_STATUS_FAILED
    assert stored.auto_refresh_status == REFRESH_STATUS_FAILED
    assert "Stale candles for AGIX/USDT 1d" in stored.auto_refresh_error
    assert stored.metrics["total_return_pct"] == 12.3
    assert run.status == REFRESH_STATUS_FAILED
    assert optimizer_called is False


def test_favorites_list_exposes_refresh_state(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    monkeypatch.setattr(favorites, "can_view_strategy_secrets", lambda *_args, **_kwargs: True)

    with SessionLocal() as db:
        created = favorites.create_favorite(
            _favorite_payload("Refresh state"),
            current_user_id="user-a",
            db=db,
        )
        stored = db.query(favorites.FavoriteStrategy).filter_by(id=created.id).one()
        stored.auto_refresh_status = REFRESH_STATUS_SUCCESS
        stored.auto_refresh_run_id = "favorite-refresh-test"
        db.commit()
        listed = favorites.list_favorites(current_user_id="user-a", db=db)

    assert listed[0].auto_refresh_status == REFRESH_STATUS_SUCCESS
    assert listed[0].auto_refresh_run_id == "favorite-refresh-test"
