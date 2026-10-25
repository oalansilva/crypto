"""Card #1118: GET /market/history, /market/candles com cobertura e cobertura no catálogo."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
import app.models_discovery  # noqa: F401
from app import api as api_module
from app.database import Base, get_db
from app.middleware.authMiddleware import get_current_admin, get_current_user
from app.models_asset_catalog import AssetCatalog
from app.routes import asset_catalog_routes, combo_routes, market_history_routes
from app.services import asset_catalog_service as catalog
from app.services import ohlcv_storage
from app.services.market_history import facade
from app.services.market_history.cache import ParquetReadCache
from app.services.market_history.equity_provider import (
    BinanceBusinessError,
    BinanceEquityProvider,
    BinanceRateLimited,
)
from app.services.market_history.schema import ADD_COLUMNS_SQL, execute_all, side_table_statements
from app.services.market_history.service import HistoryService
from market_history_support import FakeCcxt, FakeEquityProvider, crypto_frame, history_schema

NOW = pd.Timestamp("2026-10-23 01:30", tz="UTC")


@pytest.fixture
def public_db(unit_database_url):
    """Tabelas do histórico e do catálogo no banco de teste, limpas antes e depois."""

    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    tables = (
        "asset_catalog, asset_catalog_refresh, favorite_strategies, discovery_results, backtest_runs, market_series, market_series_coverage, "
        "market_series_fetch, market_series_stage, execution_data_snapshots, market_rate_limit, "
        "batch_backtest_jobs, batch_backtest_items"
    )
    with engine.begin() as conn:
        execute_all(conn, side_table_statements())
        execute_all(conn, ADD_COLUMNS_SQL)
        conn.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY"))
    yield engine
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY"))
    engine.dispose()


def _asset(asset_id, symbol, asset_class, name, state="tradable") -> AssetCatalog:
    now = datetime.now(timezone.utc)
    return AssetCatalog(
        asset_id=asset_id,
        asset_class=asset_class,
        symbol=symbol,
        name=name,
        binance_id=asset_id.rsplit(":", 1)[-1],
        state=state,
        search_key=f"{symbol.lower()}\n{name.lower()}",
        first_seen_at=now,
        last_seen_at=now,
        extra={},
    )


def _seed_catalog(engine):
    """Catálogo do #1117 (BTC, ETH, WAVES suspenso, NVDA, SPY, QQQ) mais AAPL e IBIT."""

    from test_card_1117_asset_catalog_api import _seed

    _seed()
    Session = sessionmaker(bind=engine)
    with Session() as db:
        db.add_all(
            [
                _asset("binance:equity:EQ_AAPL", "AAPL", "stock", "Apple Inc. Common Stock"),
                _asset("binance:equity:EQ_IBIT", "IBIT", "etf", "iShares Bitcoin Trust ETF"),
            ]
        )
        db.commit()


# --- GET /market/history ---------------------------------------------------------------


@pytest.fixture
def history(public_db, unit_database_url, tmp_path, monkeypatch):
    _seed_catalog(public_db)
    with history_schema(unit_database_url) as engine:
        daily = FakeEquityProvider(timeframe="1d", now=NOW, page_size=300)
        daily.build(pd.Timestamp("2022-01-03", tz="UTC"), NOW)
        ccxt = FakeCcxt({("BTC/USDT", "1d"): crypto_frame("2025-01-01", 600, "1D", 20000.0)})
        service = HistoryService(
            engine,
            equity_provider=daily,
            ccxt_client=ccxt,
            clock=lambda: NOW.to_pydatetime(),
            update_ttl_seconds=0,
            lease_wait_seconds=0.2,
        )
        facade.set_history_service(service, ParquetReadCache(tmp_path / "series"))
        Session = sessionmaker(bind=public_db)

        def _db():
            db = Session()
            try:
                yield db
            finally:
                db.close()

        app = FastAPI()
        app.include_router(market_history_routes.router)
        app.include_router(api_module.router)
        app.include_router(asset_catalog_routes.router)
        app.include_router(combo_routes.router)
        app.dependency_overrides[get_db] = _db
        app.dependency_overrides[get_current_user] = lambda: "user-1"
        app.dependency_overrides[get_current_admin] = lambda: "admin-1"
        app.dependency_overrides[combo_routes.get_current_admin] = lambda: "admin-1"
        yield TestClient(app), service, daily, engine
        facade.set_history_service(None, None)


def test_history_requires_authentication(history):
    client, *_ = history
    app = FastAPI()
    app.include_router(market_history_routes.router)
    response = TestClient(app).get(
        "/api/market/history", params={"symbol": "NVDA", "timeframe": "1d"}
    )
    assert response.status_code in (401, 403)


def test_nvda_daily_query_collects_and_reports_coverage(history):
    client, service, provider, _ = history
    response = client.get(
        "/api/market/history",
        params={"symbol": "NVDA", "timeframe": "1d", "start": "2022-01-03", "limit": 5000},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["series"]["source"] == "binance_equity" and body["series"]["session"] == "rth"
    assert body["series"]["adjustment"] == "adjusted" and body["timeframe"] == "1d"
    assert body["count"] == len(body["candles"]) > 500
    coverage = body["coverage"]
    assert coverage["status"] == "covered" and coverage["gap_count"] == 0
    assert coverage["requested"]["start"] == "2022-01-03T00:00:00Z"
    assert coverage["covered"]["start"].startswith("2022-01-0")
    assert coverage["calendar_timezone"] == "America/New_York"
    assert body["collection"]["status"] == "ok" and body["collection"]["pages"] >= 2
    assert body["data_version"] == "1"
    # Repetir sem candle novo: só a verificação da página mais recente.
    provider.requests.clear()
    again = client.get(
        "/api/market/history", params={"symbol": "NVDA", "timeframe": "1d", "start": "2022-01-03"}
    )
    assert again.json()["collection"]["status"] == "ok"
    assert len(provider.requests) == 1 and provider.requests[0]["end"] is None


def test_asset_id_selects_the_same_series_and_etf_is_collected_by_its_own_query(history):
    client, service, provider, _ = history
    spy = client.get(
        "/api/market/history", params={"asset_id": "binance:equity:EQ_SPY", "timeframe": "1d"}
    )
    assert spy.status_code == 200 and spy.json()["series"]["symbol"] == "SPY"
    assert spy.json()["series"]["asset_class"] == "etf"
    assert {r["symbol"] for r in provider.requests} == {"SPY"}  # ETF verificado por conta própria


def test_rate_limit_and_business_errors_surface_as_failures_without_the_raw_code(history):
    client, service, provider, _ = history
    provider.fail_with = BinanceRateLimited(429, 30)
    limited = client.get("/api/market/history", params={"symbol": "QQQ", "timeframe": "1d"}).json()
    assert limited["collection"]["status"] == "failed"
    assert limited["coverage"]["status"] == "failed" and limited["candles"] == []
    assert limited["coverage"]["error"]["message"] == "limite de requisições da Binance"
    provider.fail_with = BinanceBusinessError("488006")
    business = client.get("/api/market/history", params={"symbol": "IBIT", "timeframe": "1d"})
    assert "488006" not in business.text  # o código cru não aparece para o usuário
    assert business.json()["coverage"]["error"]["message"] == "a Binance recusou o pedido"


def test_deferred_timeframes_and_unknown_assets_are_clear_errors(history):
    client, *_ = history
    # 1h e 4h entraram no #1119 (montados do 5m); 30m e 1m seguem fora para ação/ETF.
    thirty = client.get("/api/market/history", params={"symbol": "NVDA", "timeframe": "30m"})
    assert (
        thirty.status_code == 422 and thirty.json()["detail"]["code"] == "timeframe_not_supported"
    )
    unknown = client.get("/api/market/history", params={"symbol": "ZZZZ", "timeframe": "1d"})
    assert unknown.status_code == 404 and unknown.json()["detail"]["code"] == "asset_not_in_catalog"
    missing = client.get("/api/market/history", params={"timeframe": "1d"})
    assert missing.status_code == 400


def test_crypto_goes_through_the_same_service_and_route(history):
    client, *_ = history
    body = client.get(
        "/api/market/history", params={"symbol": "BTC/USDT", "timeframe": "1d", "limit": 50}
    ).json()
    assert body["series"]["source"] == "binance_spot" and body["series"]["session"] == "24x7"
    assert (
        body["count"] == 50
        and body["coverage"]["note"] == "Binance Spot · 24/7 · ajuste não se aplica"
    )


def test_fifteen_minute_equity_is_derived_and_flagged(history):
    client, service, provider, _ = history
    five = FakeEquityProvider(timeframe="5m", now=NOW)
    five.build(pd.Timestamp("2026-10-12", tz="UTC"), NOW)
    service._equity = five
    body = client.get(
        "/api/market/history", params={"symbol": "NVDA", "timeframe": "15m", "start": "2026-10-12"}
    ).json()
    assert body["coverage"]["origin"] == "derived" and body["coverage"]["derived_from"] == "5m"
    assert body["series"]["origin"] == "derived" and body["count"] == 26 * 9
    assert body["data_version"].endswith("+r1")


# --- /market/candles continua só cripto e devolve a cobertura ---------------------------


def test_candles_route_stays_crypto_only_and_never_collects_equity(history):
    client, service, provider, _ = history
    response = client.get("/api/market/candles", params={"symbol": "NVDA", "timeframe": "1d"})
    assert response.status_code == 400
    assert provider.requests == []


def test_candles_route_returns_the_coverage_when_unified(history, monkeypatch):
    client, service, provider, engine = history
    monkeypatch.setenv("MARKET_HISTORY_UNIFIED", "1")
    monkeypatch.setattr(ohlcv_storage, "engine", engine)
    monkeypatch.setattr(api_module, "_CANDLES_CACHE", {})
    service.ensure(
        service.resolve(
            __import__("app.services.market_history.model", fromlist=["x"]).crypto_spec(
                "BTC/USDT", "1d"
            )
        ),
        "2025-01-01",
    )
    response = client.get(
        "/api/market/candles", params={"symbol": "BTC/USDT", "timeframe": "1d", "limit": 30}
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["count"] == 30 and body["coverage"]["status"] in {"covered", "partial"}
    assert body["coverage"]["series"]["asset_id"] == "binance:spot:BTC/USDT"
    assert body["coverage"]["updated_at"] and body["data_version"] == "1"
    monkeypatch.setenv("MARKET_HISTORY_UNIFIED", "0")
    monkeypatch.setattr(api_module, "_CANDLES_CACHE", {})
    assert (
        "coverage"
        not in client.get(
            "/api/market/candles", params={"symbol": "BTC/USDT", "timeframe": "1d", "limit": 30}
        ).json()
    )


# --- 3.8 / 7.3: análise recusada e "Todos do filtro" não coletam -------------------------


def test_refused_analysis_and_select_all_never_collect(history, monkeypatch):
    client, service, provider, _ = history

    def forbidden(*_a, **_k):
        raise AssertionError("ensure não pode rodar para análise recusada nem para a seleção")

    monkeypatch.setattr(HistoryService, "ensure", forbidden)
    monkeypatch.setattr(BinanceEquityProvider, "fetch_page_once", forbidden)
    monkeypatch.setattr(BinanceEquityProvider, "fetch_page", forbidden)

    # "Todos do filtro" em ETFs: só devolve ids, sem coleta.
    resolved = client.post("/api/assets/catalog/resolve", json={"class": "etf"}).json()
    assert set(resolved["asset_ids"]) == {
        "binance:equity:EQ_SPY",
        "binance:equity:EQ_QQQ",
        "binance:equity:EQ_IBIT",
    }
    # Abrir, filtrar e pesquisar o catálogo.
    assert client.get("/api/assets/catalog", params={"class": "etf", "q": "spy"}).status_code == 200
    # Iniciar com os ETFs: recusa estruturada antes de qualquer coleta.
    refused = client.post(
        "/api/combos/optimize",
        json={"template_name": "ema_rsi", "symbol": "SPY", "timeframe": "1d"},
    )
    assert refused.status_code == 422
    assert refused.json()["detail"]["code"] == "asset_class_not_supported"
    # Card #1120: o lote aceita ETFs, mas a coleta acontece no worker, nunca ao receber o pedido.
    from app.routes import combo_routes as routes

    monkeypatch.setattr(routes, "enqueue_batch_backtest", lambda *a, **k: "task-1")
    batch = client.post(
        "/api/combos/backtest/batch",
        json={"template_name": "ema_rsi", "symbols": ["SPY", "QQQ", "IBIT"], "timeframe": "1d"},
    )
    assert batch.status_code == 200, batch.text
    preview = client.post(
        "/api/combos/backtest/batch/preview",
        json={"template_name": "ema_rsi", "symbols": ["SPY", "QQQ", "IBIT"], "timeframe": "1d"},
    )
    assert preview.status_code == 200, preview.text  # o plano não coleta
    assert {i["plan"] for i in preview.json()["items"]} == {"run"}
    from app.services.asset_analysis_guard import discovery_symbol_reasons

    reasons = discovery_symbol_reasons(["SPY", "QQQ", "IBIT"])
    assert {r["kind"] for r in reasons.values()} == {"class"}
    assert provider.requests == []


def test_only_the_history_route_and_the_equity_provider_may_collect_equity():
    """Regressão estática do mecanismo: quem pode chamar ``ensure`` ou o provedor de ação/ETF hoje.

    O #1119 acrescenta o backtest de 1 ativo (``equity_backtest.prepare_equity_history``, chamado por
    ``/backtest`` e ``/optimize`` só depois da recusa por classe e por escopo).
    """

    root = Path(__file__).resolve().parents[2] / "app"
    callers = set()
    for path in root.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        if re.search(
            r"\.ensure\(|ensure=|equity_provider|BinanceEquityProvider\(|BinanceEquityMarketDataProvider",
            source,
        ):
            callers.add(path.relative_to(root).as_posix())
    assert callers == {
        "routes/combo_routes.py",  # backtest de 1 ativo: leitura sem nova coleta (ensure=False)
        "services/batch_backtest_service.py",  # lote (#1120): coleta ativo por ativo no worker
        "routes/market_history_routes.py",  # a consulta (history ... ensure=collect)
        "services/equity_backtest.py",  # coleta sob demanda do backtest de 1 ação/ETF (#1119)
        "services/market_data_providers.py",  # provedor de ação/ETF
        "services/market_history/facade.py",  # loader_frame (só cripto)
        "services/market_history/service.py",  # a própria coleta
        "services/market_history/rate_limit.py",  # limitador compartilhado (importa os erros do provedor)
    }


# --- 6.1 cobertura no catálogo -----------------------------------------------------------


def _series(
    conn, asset_id, symbol, timeframe, *, source, adjustment="adjusted", session="rth", version=1
) -> int:
    return conn.execute(
        text(
            "INSERT INTO market_series (asset_id, symbol, asset_class, source, session, adjustment, "
            "timeframe, data_version) VALUES (:a, :s, 'x', :src, :se, :adj, :tf, :v) RETURNING series_id"
        ),
        {
            "a": asset_id,
            "s": symbol,
            "src": source,
            "se": session,
            "adj": adjustment,
            "tf": timeframe,
            "v": version,
        },
    ).scalar()


def _coverage(conn, sid, first, last, *, gaps=None, updated="2026-10-22T20:12:00Z", count=100):
    gaps = gaps or []
    conn.execute(
        text(
            "INSERT INTO market_series_coverage (series_id, first_candle, last_candle, candle_count, "
            "gap_count, gaps, updated_at) VALUES (:s, :f, :l, :n, :gc, CAST(:g AS jsonb), :u)"
        ),
        {
            "s": sid,
            "f": first,
            "l": last,
            "n": count,
            "gc": len(gaps),
            "g": json.dumps(gaps),
            "u": updated,
        },
    )


def _fetch(conn, sid, **fields):
    cols = ", ".join(["series_id", *fields])
    vals = ", ".join([":s", *[f":{k}" for k in fields]])
    conn.execute(
        text(f"INSERT INTO market_series_fetch ({cols}) VALUES ({vals})"), {"s": sid, **fields}
    )


def test_catalog_items_carry_per_timeframe_coverage_states(public_db):
    _seed_catalog(public_db)
    now = datetime.now(timezone.utc)
    fresh = now.isoformat()
    with public_db.begin() as conn:
        # BTC: 4 timeframes com o mesmo início (cripto, 24/7).
        for tf in ("1d", "4h", "1h", "15m"):
            sid = _series(
                conn,
                "binance:spot:BTC/USDT",
                "BTC/USDT",
                tf,
                source="binance_spot",
                adjustment="na",
                session="24x7",
            )
            _coverage(
                conn,
                sid,
                "2017-08-17T00:00:00Z",
                "2026-10-22T18:00:00Z",
                updated="2026-10-22T21:00:00Z",
            )
        # NVDA: 1d desde 2014 e 5m desde 2026.
        sid = _series(conn, "binance:equity:EQ_NVDA", "NVDA", "1d", source="binance_equity")
        _coverage(conn, sid, "2014-11-11T05:00:00Z", "2026-10-22T04:00:00Z")
        sid5 = _series(conn, "binance:equity:EQ_NVDA", "NVDA", "5m", source="binance_equity")
        _coverage(conn, sid5, "2026-05-19T13:30:00Z", "2026-10-22T19:55:00Z")
        # SPY: uma lacuna no 5m (10:05-10:40 de Nova York, 14 out.).
        sid = _series(conn, "binance:equity:EQ_SPY", "SPY", "1d", source="binance_equity")
        _coverage(conn, sid, "2014-11-11T05:00:00Z", "2026-10-22T04:00:00Z")
        sid5 = _series(conn, "binance:equity:EQ_SPY", "SPY", "5m", source="binance_equity")
        _coverage(
            conn,
            sid5,
            "2026-07-01T13:30:00Z",
            "2026-10-22T19:55:00Z",
            gaps=[{"start": "2026-10-14T14:05:00Z", "end": "2026-10-14T14:40:00Z", "count": 8}],
        )
        # QQQ: coleta em andamento (1d, página 2).
        sid = _series(conn, "binance:equity:EQ_QQQ", "QQQ", "1d", source="binance_equity")
        _fetch(conn, sid, state="running", pages_done=1, requested_at=now, updated_at=now)
        # IBIT: parcial (pedido desde 2021; a Binance tem desde 2024).
        sid = _series(conn, "binance:equity:EQ_IBIT", "IBIT", "1d", source="binance_equity")
        _coverage(conn, sid, "2024-01-11T05:00:00Z", "2026-10-21T04:00:00Z")
        _fetch(
            conn,
            sid,
            state="idle",
            reached_start=True,
            binance_earliest=datetime(2024, 1, 11, 5, tzinfo=timezone.utc),
            requested_since=datetime(2021, 10, 22, tzinfo=timezone.utc),
        )
        # WAVES: ativo suspenso, histórico congelado.
        sid = _series(
            conn,
            "binance:spot:WAVES/USDT",
            "WAVES/USDT",
            "1d",
            source="binance_spot",
            adjustment="na",
            session="24x7",
        )
        _coverage(
            conn,
            sid,
            "2018-01-01T00:00:00Z",
            "2024-05-31T00:00:00Z",
            updated="2024-05-31T21:00:00Z",
        )
    Session = sessionmaker(bind=public_db)
    with Session() as db:
        items = {i["symbol"]: i for i in catalog.search_catalog(db, page_size=50)["items"]}

    btc = items["BTC/USDT"]["history"]
    assert btc["status"] == "covered" and [t["timeframe"] for t in btc["timeframes"]] == [
        "1d",
        "4h",
        "1h",
        "15m",
    ]
    assert {t["from"] for t in btc["timeframes"]} == {"2017-08-17T00:00:00Z"}  # início comum
    assert btc["gap_count"] == 0 and btc["note"] == "Binance Spot · 24/7 · ajuste não se aplica"

    nvda = items["NVDA"]["history"]
    assert nvda["status"] == "covered"
    assert [(t["timeframe"], t["origin"]) for t in nvda["timeframes"]] == [
        ("1d", "native"),
        ("4h", "derived"),
        ("1h", "derived"),
        ("15m", "derived"),
        ("5m", "native"),
    ]
    assert nvda["timeframes"][0]["from"].startswith("2014-11-11")
    # 15m, 1h e 4h aparecem "montado do 5m" com o mesmo período coberto do 5m (#1119)
    assert {t["from"][:10] for t in nvda["timeframes"][1:]} == {"2026-05-19"}
    assert nvda["calendar_timezone"] == "America/New_York" and nvda["note"].endswith(
        "ajustado por split"
    )

    spy = items["SPY"]["history"]
    assert spy["gap_count"] == 1  # a lacuna herdada pelo 15m não soma de novo
    five = next(t for t in spy["timeframes"] if t["timeframe"] == "5m")
    fifteen = next(t for t in spy["timeframes"] if t["timeframe"] == "15m")
    assert five["gap_count"] == 1 and five["gaps"][0]["start"] == "2026-10-14T14:05:00Z"
    assert fifteen["gap_count"] == 0 and fifteen["gaps"][0]["inherited_from"] == "5m"
    assert fifteen["gaps"][0]["start"] == "2026-10-14T14:00:00Z"  # bloco 10:00 de Nova York

    qqq = items["QQQ"]["history"]
    assert (
        qqq["status"] == "collecting"
        and qqq["collecting"]["timeframe"] == "1d"
        and qqq["collecting"]["page"] == 2
    )

    ibit = items["IBIT"]["history"]
    assert ibit["status"] == "partial" and ibit["partial"]["insufficient"] is True
    assert ibit["partial"]["starts_at"].startswith("2024-01-11") and ibit["partial"][
        "requested_since"
    ].startswith("2021-10-22")

    assert items["WAVES/USDT"]["history"]["status"] == "frozen"
    aapl = items["AAPL"]["history"]
    assert aapl["status"] == "on_demand" and aapl["timeframes"] == []
    assert "not_collected" not in json.dumps(items)  # "Histórico não coletado" deixou de existir


def test_failed_collection_carries_reason_and_what_was_already_collected(public_db):
    _seed_catalog(public_db)
    with public_db.begin() as conn:
        sid = _series(conn, "binance:equity:EQ_QQQ", "QQQ", "1d", source="binance_equity")
        _coverage(conn, sid, "2023-01-05T05:00:00Z", "2026-10-22T04:00:00Z")
        _fetch(
            conn,
            sid,
            state="failed",
            last_error_code="binance_rate_limited",
            last_error="HTTP 429",
            pages_done=2,
            requested_since=datetime(2014, 1, 1, tzinfo=timezone.utc),
        )
    with sessionmaker(bind=public_db)() as db:
        qqq = next(i for i in catalog.search_catalog(db, q="qqq")["items"] if i["symbol"] == "QQQ")
    history = qqq["history"]
    assert history["status"] == "failed"
    assert history["error"]["message"] == "limite de requisições da Binance"
    assert history["error"]["code"] == "binance_rate_limited"
    assert history["timeframes"][0]["from"].startswith("2023-01-05")  # "já coletado: 1d desde …"
    assert "HTTP 429" not in json.dumps(history)


def test_catalog_pages_never_trigger_collection_or_scan_candles(public_db, monkeypatch):
    _seed_catalog(public_db)
    statements: list[str] = []
    from sqlalchemy import event

    @event.listens_for(public_db, "before_cursor_execute")
    def _spy(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    with sessionmaker(bind=public_db)() as db:
        catalog.search_catalog(db, page_size=25)
    assert not any("FROM market_ohlcv" in s or "market_ohlcv_v2" in s for s in statements)
    assert any("market_series_coverage" in s for s in statements)
