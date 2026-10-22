"""Card #1117: rotas do catálogo e recusa estruturada 422 nas análises."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

import app.models  # noqa: F401  (registra as tabelas no reset)
import app.models_discovery  # noqa: F401
from app import api as api_module
from app.database import Base
from app.middleware.authMiddleware import get_current_admin, get_current_user
from app.routes import asset_catalog_routes, combo_routes
from app.services import asset_catalog_adapters as adapters
from app.services import asset_catalog_service as catalog
from app.services.asset_catalog_adapters import CatalogSourceError


@pytest.fixture(autouse=True)
def _catalog_db(unit_database_url):
    """Isolamento barato por teste: só as tabelas que o teste toca (o reset global custa segundos).

    Também limpa depois, porque outros testes assumem catálogo vazio (validação fail-open).
    """
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    tables = "asset_catalog, asset_catalog_refresh, favorite_strategies, discovery_results, backtest_runs"
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY"))
    yield
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY"))
    engine.dispose()


def _ok(data):
    return {"code": "000000", "data": data}


def _crypto(rows):
    return adapters.parse_spot_exchange_info(
        {
            "symbols": [
                {
                    "symbol": f"{base}USDT",
                    "status": status,
                    "baseAsset": base,
                    "quoteAsset": "USDT",
                    "isSpotTradingAllowed": True,
                }
                for base, status in rows
            ]
        }
    )


def _equity():
    return adapters.parse_equity_payloads(
        _ok(
            [
                {
                    "ac": "EQ_NVDA",
                    "s": "NVDA",
                    "n": "NVIDIA Corporation Common Stock",
                    "t": "STOCK",
                },
                {
                    "ac": "EQ_SPY",
                    "s": "SPY",
                    "n": "State Street SPDR S&P 500 ETF Trust",
                    "t": "ETF",
                },
                {"ac": "EQ_QQQ", "s": "QQQ", "n": "Invesco QQQ Trust, Series 1", "t": "ETF"},
                {"ac": "EQ_AVB", "s": "AVB", "n": "AvalonBay Communities, Inc.", "t": "STOCK"},
            ]
        ),
        _ok(
            {
                "symbols": [
                    {"assetCode": "EQ_NVDA", "symbol": "NVDA", "tradability": "BUY_SELL"},
                    {"assetCode": "EQ_SPY", "symbol": "SPY", "tradability": "BUY_SELL"},
                    {"assetCode": "EQ_QQQ", "symbol": "QQQ", "tradability": "BUY_SELL"},
                    {"assetCode": "EQ_AVB", "symbol": "AVB", "tradability": "OFFMARKET"},
                ]
            }
        ),
    )


def _seed(*, crypto: bool = True, equity: bool = True):
    if crypto:
        parsed = _crypto([("BTC", "TRADING"), ("ETH", "TRADING"), ("WAVES", "BREAK")])
        assert catalog.refresh_group("crypto", fetcher=lambda: parsed)["status"] == "ok"
    if equity:
        parsed_eq = _equity()
        assert catalog.refresh_group("equity", fetcher=lambda: parsed_eq)["status"] == "ok"


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(asset_catalog_routes.router)
    app.include_router(combo_routes.router)
    app.include_router(api_module.router)
    app.dependency_overrides[get_current_user] = lambda: "user-1"
    app.dependency_overrides[get_current_admin] = lambda: "admin-1"
    app.dependency_overrides[combo_routes.get_current_admin] = lambda: "admin-1"
    return TestClient(app)


# --- Rotas do catálogo --------------------------------------------------------------


def test_catalog_route_search_pagination_counts_and_freshness(client):
    _seed()

    body = client.get("/api/assets/catalog", params={"q": "nvidia"}).json()
    assert [i["symbol"] for i in body["items"]] == ["NVDA"]
    assert body["items"][0]["asset_id"] == "binance:equity:EQ_NVDA"
    assert body["total"] == 1 and body["eligible_total"] == 1
    assert body["counts"]["all"]["total"] == 7
    assert body["freshness"]["crypto"]["status"] == "ok"
    assert body["freshness"]["etf"]["updated_at"]

    etfs = client.get(
        "/api/assets/catalog", params={"class": "etf", "page": 1, "page_size": 1}
    ).json()
    assert etfs["total"] == 2 and etfs["pages"] == 2 and len(etfs["items"]) == 1

    assert client.get("/api/assets/catalog", params={"class": "bond"}).status_code == 422


def test_catalog_route_reports_failure_per_class_without_inventing_a_list(client):
    _seed(crypto=False, equity=True)
    catalog.refresh_group(
        "crypto", fetcher=lambda: (_ for _ in ()).throw(CatalogSourceError("network", "offline"))
    )

    body = client.get("/api/assets/catalog", params={"q": "btc"}).json()

    assert body["items"] == [] and body["total"] == 0
    assert body["freshness"]["crypto"]["status"] == "unavailable"
    assert body["freshness"]["crypto"]["reason"] == "offline"
    assert body["freshness"]["stock"]["status"] == "ok"
    assert body["counts"]["crypto"] == {"total": None, "eligible": None}


def test_catalog_resolve_and_lookup_routes(client):
    _seed()

    resolved = client.post("/api/assets/catalog/resolve", json={"class": "etf"}).json()
    assert sorted(resolved["asset_ids"]) == ["binance:equity:EQ_QQQ", "binance:equity:EQ_SPY"]
    assert resolved["marked_total"] == 0

    everything = client.post("/api/assets/catalog/resolve", json={}).json()
    assert "binance:spot:WAVES/USDT" not in everything["asset_ids"]
    assert "binance:equity:EQ_AVB" not in everything["asset_ids"]
    assert everything["marked_total"] == 2

    looked = client.post(
        "/api/assets/catalog/lookup",
        json={"asset_ids": ["binance:spot:WAVES/USDT"], "symbols": ["nvda"]},
    ).json()
    states = {i["symbol"]: i["state"] for i in looked["items"]}
    assert states == {"WAVES/USDT": "suspended", "NVDA": "tradable"}


def test_manual_refresh_route_reports_failure_and_keeps_last_list(client, monkeypatch):
    _seed()
    monkeypatch.setitem(
        catalog.FETCHERS,
        "equity",
        lambda: (_ for _ in ()).throw(CatalogSourceError("rate_limited", "429")),
    )

    body = client.post("/api/assets/catalog/refresh", json={"group": "equity"}).json()

    assert body["results"][0]["status"] == "error"
    assert body["freshness"]["stock"]["status"] == "stale"
    assert client.get("/api/assets/catalog", params={"q": "spy"}).json()["total"] == 1
    assert client.post("/api/assets/catalog/refresh", json={"group": "bonds"}).status_code == 422


def test_binance_symbols_compat_route_lists_only_tradable_crypto_from_catalog(client):
    _seed()
    body = client.get("/api/exchanges/binance/symbols").json()
    assert body == {"symbols": ["BTC/USDT", "ETH/USDT"], "count": 2}


def test_binance_symbols_compat_route_is_503_without_a_valid_list_never_empty_or_fixed(client):
    response = client.get("/api/exchanges/binance/symbols")
    assert response.status_code == 503
    assert "indisponível" in response.json()["detail"]


# --- Recusa estruturada nas análises --------------------------------------------------


def _optimize(client: TestClient, symbol: str):
    return client.post(
        "/api/combos/optimize",
        json={"template_name": "ema_rsi", "symbol": symbol, "timeframe": "1d", "custom_ranges": {}},
    )


def _batch(client: TestClient, symbols: list[str]):
    return client.post(
        "/api/combos/backtest/batch",
        json={"template_name": "ema_rsi", "symbols": symbols, "timeframe": "1d"},
    )


def test_optimize_refuses_equity_with_class_code_in_portuguese(client):
    _seed()
    response = _optimize(client, "NVDA")

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "asset_class_not_supported"
    assert detail["asset_class"] == "stock"
    assert detail["assets"][0]["symbol"] == "NVDA"
    assert detail["message"].startswith("Análise ainda não disponível para ações e ETFs")


def test_optimize_refuses_marked_and_unknown_assets(client):
    _seed()

    marked = _optimize(client, "WAVES/USDT").json()["detail"]
    assert marked["code"] == "asset_not_selectable"
    assert marked["state"] == "suspended"
    assert "BREAK" in marked["reason"]
    assert "não entra em análise nova" in marked["message"]

    unknown = _optimize(client, "XYZ/USDT").json()["detail"]
    assert unknown["code"] == "asset_not_in_catalog"
    assert unknown["assets"] == [{"symbol": "XYZ/USDT"}]


def test_batch_refuses_the_whole_call_when_it_contains_equity_etf_or_marked(client, monkeypatch):
    _seed()
    enqueued = []
    monkeypatch.setattr(combo_routes, "enqueue_batch_backtest", lambda *a, **k: enqueued.append(a))

    mixed = _batch(client, ["BTC/USDT", "ETH/USDT", "SPY"])
    assert mixed.status_code == 422
    assert mixed.json()["detail"]["code"] == "asset_class_not_supported"
    assert mixed.json()["detail"]["assets"][0]["symbol"] == "SPY"

    marked = _batch(client, ["BTC/USDT", "WAVES/USDT"])
    assert marked.status_code == 422
    assert marked.json()["detail"]["code"] == "asset_not_selectable"

    assert enqueued == []  # nada foi enfileirado


def test_batch_with_only_tradable_crypto_still_starts(client, monkeypatch):
    _seed()
    enqueued = []
    monkeypatch.setattr(combo_routes, "enqueue_batch_backtest", lambda *a, **k: enqueued.append(a))

    response = _batch(client, ["BTC/USDT", "ETH/USDT"])

    assert response.status_code == 200, response.text
    assert response.json()["job_id"]
    assert len(enqueued) == 1


def test_backtest_guard_keeps_paused_and_removed_results_reopenable():
    _seed()
    combo_routes._ensure_crypto_symbol("WAVES/USDT")  # reabrir resultado salvo: não levanta
    combo_routes._ensure_crypto_symbol("NEW/USDT")
    with pytest.raises(Exception) as exc:
        combo_routes._ensure_crypto_symbol("NVDA")
    assert exc.value.status_code == 422
    assert exc.value.detail["code"] == "asset_class_not_supported"
    with pytest.raises(Exception) as exc:
        combo_routes._ensure_crypto_symbols(["WAVES/USDT"], new_analysis=True)
    assert exc.value.detail["code"] == "asset_not_selectable"
