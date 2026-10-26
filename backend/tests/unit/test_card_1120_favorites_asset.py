"""Lista única de favoritos com a identidade do ativo e o contrato com o #1122 (card #1120, 3.5 e 5.1)."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.models import FavoriteStrategy
from app.routes import favorites
from app.services.favorite_uniqueness import find_existing_favorite, lock_and_find_duplicate
from app.services.opportunity_service import OpportunityService
from test_card_1118_api_and_catalog import _seed_catalog, public_db  # noqa: F401


@pytest.fixture
def env(public_db, unit_database_url, monkeypatch):  # noqa: F811
    _seed_catalog(public_db)

    class Disabled:
        enabled = False

    monkeypatch.setattr(favorites, "_FAVORITE_OHLCV_REPO", Disabled())
    Session = sessionmaker(bind=public_db)

    def _db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(favorites.router)
    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = lambda: "user-1"
    yield TestClient(app), Session


def _favorite(symbol, *, metrics=None, parameters=None, notes=None, tier=None):
    return FavoriteStrategy(
        user_id="user-1",
        name=f"multi_ma_crossover - {symbol} 1d (batch)",
        symbol=symbol,
        timeframe="1d",
        strategy_name="multi_ma_crossover",
        parameters=parameters or {"direction": "long"},
        metrics=metrics or {},
        notes=notes,
        tier=tier,
    )


def test_list_returns_the_asset_of_every_class_from_metrics_or_the_catalog(env):
    client, Session = env
    with Session() as db:
        db.add_all(
            [
                _favorite("BTC/USDT", tier=3),  # cripto antiga, sem metrics.asset
                _favorite(
                    "NVDA",
                    metrics={
                        "asset": {
                            "symbol": "NVDA",
                            "asset_id": "binance:equity:EQ_NVDA",
                            "asset_class": "stock",
                            "name": "NVIDIA",
                            "currency": "USD",
                        },
                        "batch_id": "7f3c2a91-0000-4000-8000-000000000000",
                        "execution": {"precision_effective": "candle"},
                    },
                    parameters={"direction": "long", "data_source": "binance_equity"},
                    notes="gerado em lote (7f3c2a91)",
                ),
                _favorite("SPY", parameters={"direction": "long", "data_source": "binance_equity"}),
                _favorite("XYZW"),  # fora do catálogo: sem classe, mas aparece na lista
            ]
        )
        db.commit()

    response = client.get("/api/favorites/")
    assert response.status_code == 200, response.text
    rows = {r["symbol"]: r for r in response.json()}
    assert set(rows) == {"BTC/USDT", "NVDA", "SPY", "XYZW"}  # lista única: cripto, ação e ETF
    assert rows["BTC/USDT"]["asset"] == {
        "symbol": "BTC/USDT",
        "asset_id": "binance:spot:BTC/USDT",
        "asset_class": "crypto",
        "name": "BTC",
        "currency": "USDT",
    }
    assert (
        rows["NVDA"]["asset"]["asset_class"] == "stock"
        and rows["NVDA"]["asset"]["currency"] == "USD"
    )
    assert rows["NVDA"]["metrics"]["batch_id"].startswith("7f3c2a91")  # a faixa do lote lê isto
    assert rows["NVDA"]["metrics"]["execution"]["precision_effective"] == "candle"
    assert rows["SPY"]["asset"]["asset_class"] == "etf"  # favorito sem metrics.asset: pelo catálogo
    assert rows["SPY"]["asset"]["asset_id"] == "binance:equity:EQ_SPY"
    assert rows["XYZW"]["asset"] is None


def test_uniqueness_contract_accepts_data_source_and_asset_without_changing_the_key(env):
    _, Session = env
    with Session() as db:
        db.add(_favorite("NVDA", parameters={"direction": "long", "data_source": "binance_equity"}))
        db.commit()
    with Session() as db:
        args = dict(
            user_id="user-1",
            strategy_name="multi_ma_crossover",
            symbol="NVDA",
            timeframe="1d",
            period_type=None,
            start_date=None,
            end_date=None,
        )
        asset = {"symbol": "NVDA", "asset_class": "stock"}
        found = find_existing_favorite(
            db, direction="long", data_source="binance_equity", asset=asset, **args
        )
        assert found is not None and found.symbol == "NVDA"
        assert find_existing_favorite(db, direction="short", **args) is None
        assert (
            lock_and_find_duplicate(
                db,
                parameters={"direction": "long"},
                data_source="binance_equity",
                asset=asset,
                **args,
            )
            is not None
        )
        db.rollback()


def test_manual_favoriting_of_equity_from_the_result_screen_is_accepted_since_1122(env):
    """Card #1122: ação e ETF são favoritáveis; o favorito nasce sem "Alertar" e com a configuração."""
    client, Session = env
    body = {
        "name": "x",
        "symbol": "NVDA",
        "timeframe": "1d",
        "strategy_name": "multi_ma_crossover",
        "parameters": {"direction": "long", "data_source": "binance_equity"},
        "notify_telegram": True,
    }
    response = client.post("/api/favorites/", json=body)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["notify_telegram"] is False
    assert payload["configuration"]["data_source"] == "binance_equity"
    assert payload["configuration"]["label_long"] == (
        "Binance Ações · pregão regular de NY · ajustado por split"
    )
    again = client.post("/api/favorites/", json=body)
    assert again.status_code == 409
    assert again.json()["detail"] == "Estratégia já existe nos favoritos com esta configuração"


def test_the_monitor_lists_equity_favorites_since_1122(env):
    _, Session = env
    with Session() as db:
        db.add_all(
            [
                _favorite("BTC/USDT", tier=3),
                _favorite(
                    "NVDA", parameters={"direction": "long", "data_source": "binance_equity"}
                ),
            ]
        )
        db.commit()
    service = OpportunityService()
    with Session() as db:
        rows = service._favorite_rows_for_user(db, "user-1")
    assert sorted(r.symbol for r in rows) == ["BTC/USDT", "NVDA"]
