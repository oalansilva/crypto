from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.routes import favorites


def _session_factory(tmp_path: Path):
    db_file = tmp_path / "favorites_test.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
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
