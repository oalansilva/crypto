from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.routes import favorites


def _session_factory(tmp_path: Path):
    db_file = tmp_path / "favorites_test.db"
    engine = create_engine(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE favorite_strategies RESTART IDENTITY CASCADE"))
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
