"""Card #1123: gravação e leitura da comparação (rodada, troca, favorito, herança e refresh)."""

from __future__ import annotations

import asyncio

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import FavoriteStrategy
from app.models_benchmark import BenchmarkComparison
from app.routes import benchmark_routes, favorites as favorites_route
from app.services import benchmark_comparison as bench
from support_card_1123 import (
    BTC_TRADES,
    FakeSource,
    btc_result,
    client_for,
    ensure_snapshot_table,
    equity_frame,
    insert_snapshot,
    make_user,
    pinned,
)


@pytest.fixture
def db(postgres_isolation, unit_database_url):
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    ensure_snapshot_table(session)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def source(monkeypatch):
    fake = FakeSource()
    bench.set_reference_source(fake)
    yield fake
    bench.set_reference_source(None)


@pytest.fixture
def api(db, source, monkeypatch):
    class Disabled:
        enabled = False

    monkeypatch.setattr(favorites_route, "_FAVORITE_OHLCV_REPO", Disabled())
    admin = make_user(db, "alan", admin=True)
    other = make_user(db, "bia")
    state = {"user": str(admin.id), "admin": True}
    client = client_for(db, [benchmark_routes.router, favorites_route.router], state)
    return client, state, admin, other


def _post_result(client, reference="SPY", context=None):
    return client.post(
        "/api/benchmark-comparisons",
        json={"owner": "result", "reference_symbol": reference, "context": context or btc_result()},
    )


def _favorite_body(comparison_id=None):
    result = btc_result()
    body = {
        "name": "BTC Trend",
        "symbol": "BTC/USDT",
        "timeframe": "1d",
        "strategy_name": "multi_ma_crossover",
        "parameters": {"direction": "long"},
        "start_date": "2019-01-01",
        "end_date": "2024-12-31",
        "metrics": {
            "total_trades": len(BTC_TRADES),
            "trades": BTC_TRADES,
            "analysis_asset": result["asset"],
            "analysis_execution": result["execution"],
        },
    }
    if comparison_id:
        body["benchmark_comparison_id"] = comparison_id
    return body


def test_result_choice_records_spy_with_common_period_and_currency_warning(api, source):
    client, _, admin, _ = api
    res = _post_result(client)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["owner"]["kind"] == "result"
    assert body["trigger"] == "choice"
    assert body["user_id"] == str(admin.id)
    assert body["reference"]["symbol"] == "SPY" and body["reference"]["kind"] == "catalog"
    assert body["common_window"] == {"start": "2019-01-02", "end": "2024-12-31", "days": 2190}
    assert body["currency_note"] == "usdt_as_usd"
    assert body["samples"]["reference"]["snapshot_id"]
    again = client.get(f"/api/benchmark-comparisons/{body['id']}")
    assert again.status_code == 200
    assert again.json() == body


def test_reading_never_computes_nor_collects(api, source, monkeypatch):
    client, *_ = api
    created = _post_result(client).json()
    loads = list(source.loads)

    def boom(*_a, **_k):
        raise AssertionError("leitura não calcula")

    monkeypatch.setattr(bench, "compute", boom)
    monkeypatch.setattr(bench, "build_payload", boom)
    res = client.get(f"/api/benchmark-comparisons/{created['id']}")
    assert res.status_code == 200
    assert source.loads == loads


def test_only_owner_or_admin_reads_and_only_admin_records_results(api):
    client, state, _, other = api
    created = _post_result(client).json()
    state.update(user=str(other.id), admin=False)
    assert client.get(f"/api/benchmark-comparisons/{created['id']}").status_code == 404
    assert _post_result(client).status_code == 403


def test_collection_failure_records_nothing(api, source, db):
    client, *_ = api
    source.fail.add("QQQ")
    res = _post_result(client, reference="QQQ")
    assert res.status_code == 422
    assert res.json()["detail"]["code"] == "reference_collection_failed"
    assert "tempo esgotado" in res.json()["detail"]["message"]
    assert db.query(BenchmarkComparison).count() == 0


def test_saving_a_result_inherits_the_choice_and_pins_the_sample(api, source, db):
    client, *_ = api
    created = _post_result(client).json()
    sid = created["samples"]["reference"]["snapshot_id"]
    insert_snapshot(db, sid)
    res = client.post("/api/favorites/", json=_favorite_body(created["id"]))
    assert res.status_code == 200, res.text
    fav = res.json()
    assert fav["benchmark_comparison_id"] == created["id"]
    assert fav["benchmark_comparison"]["reference"]["symbol"] == "SPY"
    assert pinned(db, sid) is True
    listed = client.get("/api/favorites/").json()
    assert listed[0]["benchmark_comparison"]["reference"]["symbol"] == "SPY"


def test_switch_on_favorite_records_on_it_and_releases_the_previous_sample(api, source, db):
    client, *_ = api
    created = _post_result(client).json()
    first_sid = created["samples"]["reference"]["snapshot_id"]
    insert_snapshot(db, first_sid)
    fav = client.post("/api/favorites/", json=_favorite_body(created["id"])).json()
    assert pinned(db, first_sid) is True

    source.missing.add("QQQ")  # sem histórico guardado: coletado na escolha
    res = client.post(
        "/api/benchmark-comparisons",
        json={"owner": "favorite", "favorite_id": fav["id"], "reference_symbol": "QQQ"},
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["owner"]["kind"] == "favorite" and body["owner"]["favorite_id"] == fav["id"]
    assert body["collected"] is True
    new_sid = body["samples"]["reference"]["snapshot_id"]
    insert_snapshot(db, new_sid)
    db.expire_all()
    row = db.query(FavoriteStrategy).filter(FavoriteStrategy.id == fav["id"]).one()
    assert row.benchmark_comparison_id == body["id"]
    assert pinned(db, first_sid) is False  # a anterior volta para os 30 dias
    listed = client.get("/api/favorites/").json()
    assert listed[0]["benchmark_comparison"]["reference"]["symbol"] == "QQQ"


def test_reopen_after_new_reference_candles_shows_the_same_numbers(api, source):
    client, *_ = api
    created = _post_result(client, reference="QQQ").json()
    source.frames["QQQ"] = equity_frame("2003-01-02", "2026-10-27", base=999.0, step=3.0)
    again = client.get(f"/api/benchmark-comparisons/{created['id']}").json()
    assert again["reference_result"] == created["reference_result"]
    assert again["common_window"] == created["common_window"]
    assert again["samples"] == created["samples"]


def test_other_user_cannot_switch_someone_elses_favorite(api, db):
    client, state, _, other = api
    created = _post_result(client).json()
    fav = client.post("/api/favorites/", json=_favorite_body(created["id"])).json()
    state.update(user=str(other.id), admin=False)
    res = client.post(
        "/api/benchmark-comparisons",
        json={"owner": "favorite", "favorite_id": fav["id"], "reference_symbol": "QQQ"},
    )
    assert res.status_code == 404


def test_favorite_refresh_redoes_with_the_same_reference_and_new_date(api, source, db):
    client, *_ = api
    created = _post_result(client, reference="SPY").json()
    fav = client.post("/api/favorites/", json=_favorite_body(created["id"])).json()
    redone = bench.refresh_favorite_comparison(db, fav["id"], source=source)
    assert redone["trigger"] == "favorite_refresh"
    assert redone["reference"]["symbol"] == "SPY"
    assert redone["id"] != created["id"]
    db.expire_all()
    assert db.query(FavoriteStrategy).get(fav["id"]).benchmark_comparison_id == redone["id"]


def test_old_favorite_without_comparison_refreshes_with_the_own_asset(api, source, db):
    client, *_ = api
    fav = client.post("/api/favorites/", json=_favorite_body()).json()
    assert fav["benchmark_comparison"] is None
    redone = bench.refresh_favorite_comparison(db, fav["id"], source=source)
    assert redone["reference"]["kind"] == "own"
    assert redone["reference"]["symbol"] == "BTC/USDT"


def test_refresh_service_calls_the_comparison_only_when_enabled(monkeypatch):
    from app.services.favorite_backtest_refresh_service import FavoriteBacktestRefreshService

    calls = []
    service = FavoriteBacktestRefreshService.__new__(FavoriteBacktestRefreshService)
    monkeypatch.setattr(bench, "refresh_favorite_comparison", lambda db, fid: calls.append(fid))
    monkeypatch.setenv("BENCHMARK_AUTO_RECORD", "0")
    service._refresh_comparison(None, 7)
    assert calls == []
    monkeypatch.setenv("BENCHMARK_AUTO_RECORD", "1")
    service._refresh_comparison(None, 7)
    assert calls == [7]


def test_run_records_the_own_asset_default(db, source, monkeypatch):
    monkeypatch.setenv("BENCHMARK_AUTO_RECORD", "1")
    admin = make_user(db, "alan2", admin=True)
    payload, error = bench.record_run_default(btc_result(), str(admin.id), source=source)
    assert error is None
    assert payload["trigger"] == "run"
    assert payload["reference"]["kind"] == "own"
    assert payload["status"] == "valid"
    # Período comum igual à janela: o retorno da estratégia é o "Retorno total" da tela.
    equity = 1.0
    for t in BTC_TRADES:
        equity *= 1 + t["profit"]
    assert payload["strategy"]["return"] == pytest.approx(equity - 1)


def test_attach_default_comparison_fills_the_result(monkeypatch):
    from app.routes import combo_routes

    monkeypatch.setattr(bench, "record_run_default", lambda result, user: ({"id": "x"}, None))
    result = {"symbol": "BTC/USDT"}
    asyncio.run(combo_routes._attach_default_comparison(result, "u"))
    assert result["benchmark_comparison"] == {"id": "x"}
    assert result["benchmark_comparison_error"] is None


def test_summary_is_small_and_has_no_trades():
    payload = bench.compute(
        bench.strategy_side(
            symbol="BTC/USDT",
            asset=None,
            window={"start": "2019-01-01", "end": "2024-12-31"},
            trades=BTC_TRADES,
        ),
        {"symbol": "SPY", "asset_class": "etf", "currency": "USD", "kind": "catalog"},
        bench.daily_closes(equity_frame("2003-01-02", "2026-10-27"), "etf"),
    )
    payload.update(id="abc", created_at="2026-10-27T12:14:00Z", owner={"kind": "favorite"})
    summary = bench.summary(payload)
    assert summary["reference"]["symbol"] == "SPY"
    assert "trades" not in str(summary)
    assert isinstance(pd.Timestamp(summary["created_at"]), pd.Timestamp)
