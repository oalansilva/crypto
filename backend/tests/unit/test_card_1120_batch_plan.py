"""Plano do lote multiclasse (card #1120, tarefas 2.1 a 2.4): roda/fora, coleta e preview sem coletar."""

from __future__ import annotations

import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.routes import combo_routes
from app.services import batch_backtest_plan as plan_module
from app.services.asset_analysis_guard import discovery_symbol_reasons, refusal_for_symbols
from app.services.batch_backtest_plan import build_plan
from app.services.market_history import service as history_service
from test_card_1118_api_and_catalog import _seed_catalog, public_db  # noqa: F401

NOW = pd.Timestamp("2026-10-24 12:00", tz="UTC")
BTC = "binance:spot:BTC/USDT"
NVDA = "binance:equity:EQ_NVDA"
SPY = "binance:equity:EQ_SPY"


def _entry(first, last, *, starts_at="2014-11-11T05:00:00Z", **extra):
    return {
        "from": first,
        "to": last,
        "starts_at": starts_at,
        "state": "idle",
        "incomplete": False,
        "insufficient": False,
        **extra,
    }


def _stored(tf="1d", last="2026-10-23T04:00:00Z", first="2014-11-11T05:00:00Z", **extra):
    return {tf: _entry(first, last, **extra)}


@pytest.fixture
def seeded(public_db, unit_database_url, monkeypatch):  # noqa: F811
    _seed_catalog(public_db)
    coverage: dict = {}
    horizon = {"value": None}
    monkeypatch.setattr(plan_module, "_coverage", lambda db, ids: dict(coverage))
    monkeypatch.setattr(plan_module, "_equity_5m_horizon", lambda db: horizon["value"])
    Session = sessionmaker(bind=public_db)
    with Session() as db:
        yield db, coverage, horizon


def _body(symbols, timeframe="1d", **extra):
    return {
        "template_name": "multi_ma_crossover",
        "symbols": symbols,
        "timeframe": timeframe,
        "deep_backtest": True,
        **extra,
    }


def _by_symbol(plan):
    return {i["symbol"]: i for i in plan["items"]}


# ------------------------------------------------------------------ 2.1 aceite por escopo


def test_batch_scope_lets_equity_through_and_keeps_marked_and_missing_refused(
    public_db,
):  # noqa: F811
    _seed_catalog(public_db)
    assert (
        refusal_for_symbols(["NVDA", "SPY", "BTC/USDT"], new_analysis=True, batch_scope=True)
        is None
    )
    marked = refusal_for_symbols(["NVDA", "WAVES/USDT"], new_analysis=True, batch_scope=True)
    assert marked["code"] == "asset_not_selectable"
    missing = refusal_for_symbols(["ZZZZ/USDT", "NVDA"], new_analysis=True, batch_scope=True)
    assert missing["code"] == "asset_not_in_catalog"
    # sem o escopo do lote, a recusa por classe segue como antes (Otimização sem escopo)
    assert refusal_for_symbols(["NVDA"], new_analysis=True)["code"] == "asset_class_not_supported"


def test_discovery_now_runs_equity_without_a_class_reason(public_db):  # noqa: F811
    """Card #1121 (decisão 2): ação e ETF entram na Descoberta; só marcado e fora do catálogo ficam fora."""
    _seed_catalog(public_db)
    reasons = discovery_symbol_reasons(["NVDA", "SPY", "BTC/USDT"])
    assert reasons == {}


# ------------------------------------------------------------------ 2.3 plano por ativo


def test_mixed_1d_combo_plan_counts_only_what_is_not_stored_yet(seeded):
    db, coverage, _ = seeded
    coverage[BTC] = _stored()
    coverage[NVDA] = {**_stored(), **_stored("5m", first="2026-05-19T08:00:00Z")}
    # SPY: sob demanda, nada guardado
    plan = build_plan(_body(["BTC/USDT", "NVDA", "SPY"]), db=db, now=NOW)

    items = _by_symbol(plan)
    assert {s: i["plan"] for s, i in items.items()} == {
        "BTC/USDT": "run",
        "NVDA": "run",
        "SPY": "run",
    }
    assert items["BTC/USDT"]["asset_class"] == "crypto" and items["BTC/USDT"]["currency"] == "USDT"
    assert items["NVDA"]["asset_class"] == "stock" and items["NVDA"]["currency"] == "USD"
    assert items["SPY"]["asset_class"] == "etf"
    assert items["BTC/USDT"]["collect_kind"] == "none" and items["NVDA"]["collect_kind"] == "none"
    assert items["SPY"]["collect_kind"] == "missing"
    assert [(n["series"], n["role"]) for n in items["SPY"]["needs_collection"]] == [
        ("1d", "candles"),
        ("5m", "intraday"),
    ]
    assert items["BTC/USDT"]["data_source"] == "ccxt"
    assert items["NVDA"]["data_source"] == "binance_equity"
    totals = plan["totals"]
    assert totals["total"] == 3 and totals["run"] == 3 and totals["out"] == 0
    assert totals["collect"] == {"count": 1, "of": 3, "missing": 1, "tail": 0}
    assert totals["by_class"]["crypto"] == {"run": 1, "out": 0, "currency": "USDT"}
    assert totals["by_class"]["etf"]["currency"] == "USD"


def test_collect_kind_tail_is_the_stretch_since_the_last_collection(seeded):
    db, coverage, _ = seeded
    coverage[NVDA] = {
        **_stored(last="2026-09-01T04:00:00Z"),
        **_stored("5m", last="2026-09-01T20:00:00Z"),
    }
    plan = build_plan(_body(["NVDA"]), db=db, now=NOW)

    nvda = plan["items"][0]
    assert nvda["collect_kind"] == "tail" and plan["totals"]["collect"]["tail"] == 1
    assert nvda["covered_until"] == "2026-09-01T04:00:00Z"


def test_series_without_the_start_of_binance_still_counts_as_missing(seeded):
    db, coverage, _ = seeded
    coverage[NVDA] = _stored(first="2020-01-02T05:00:00Z", starts_at=None)
    plan = build_plan(_body(["NVDA"], deep_backtest=False), db=db, now=NOW)

    assert (
        plan["items"][0]["collect_kind"] == "missing"
    )  # a coleta nunca chegou ao começo da Binance


def test_what_binance_does_not_have_does_not_count(seeded):
    db, coverage, horizon = seeded
    horizon["value"] = pd.Timestamp("2026-05-19T08:00:00Z")
    plan = build_plan(
        _body(["SPY"], start_date="2024-01-01", end_date="2024-01-31", page="optimize"),
        db=db,
        now=NOW,
    )
    spy = plan["items"][0]
    # o 5m do intrabar não conta: a Binance não tem 5m de SPY em jan. 2024; só o 1d
    assert [(n["series"], n["role"]) for n in spy["needs_collection"]] == [("1d", "candles")]
    assert spy["collect_note"] == "O 5m de SPY não entra: a Binance não tem 5m dele em jan. 2024."


def test_5m_combo_plan_marks_equity_out_and_runs_the_crypto(seeded):
    db, coverage, _ = seeded
    coverage[BTC] = _stored("5m", last="2026-10-24T11:55:00Z")
    plan = build_plan(
        _body(["BTC/USDT", "NVDA", "SPY"], timeframe="5m", deep_backtest=False), db=db, now=NOW
    )

    items = _by_symbol(plan)
    assert items["BTC/USDT"]["plan"] == "run"
    for symbol in ("NVDA", "SPY"):
        assert items[symbol]["plan"] == "out" and items[symbol]["out_kind"] == "timeframe"
        assert items[symbol]["reason"] == (
            "ação e ETF não rodam em 5m; para incluí-los, use 15m, 1h, 4h ou 1d"
        )
    assert plan["totals"]["run"] == 1 and plan["totals"]["out"] == 2
    assert plan["totals"]["by_class"]["stock"] == {"run": 0, "out": 1, "currency": "USD"}


def test_optimize_plan_advises_1d_and_the_combo(seeded):
    db, _, _ = seeded
    plan = build_plan(
        _body(
            ["NVDA"],
            timeframe="30m",
            start_date="2024-01-01",
            end_date="2024-01-31",
            page="optimize",
        ),
        db=db,
        now=NOW,
    )
    assert plan["items"][0]["reason"] == (
        "ação e ETF não rodam em 30m; para incluí-los, use 1d aqui ou o Combo, que tem período"
    )


@pytest.mark.parametrize("timeframe", ["15m", "1h", "4h"])
def test_optimize_plan_marks_equity_out_when_the_5m_does_not_cover_the_fixed_window(
    seeded, timeframe
):
    db, coverage, horizon = seeded
    coverage[NVDA] = _stored("5m", first="2026-05-19T08:00:00Z")
    horizon["value"] = pd.Timestamp("2026-05-19T08:00:00Z")  # SPY sob demanda: o começo da classe
    plan = build_plan(
        _body(
            ["BTC/USDT", "NVDA", "SPY"],
            timeframe=timeframe,
            start_date="2024-01-01",
            end_date="2024-01-31",
            page="optimize",
        ),
        db=db,
        now=NOW,
    )
    items = _by_symbol(plan)
    assert items["BTC/USDT"]["plan"] == "run"
    for symbol in ("NVDA", "SPY"):
        assert items[symbol]["plan"] == "out" and items[symbol]["out_kind"] == "coverage"
        assert items[symbol]["reason"] == (
            f"o 5m de {symbol} começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, "
            "o período fixo desta tela; use 1d aqui ou o Combo, que tem período"
        )
    # a mesma regra no Combo (com período) não tira ninguém
    combo = build_plan(_body(["NVDA"], timeframe=timeframe), db=db, now=NOW)
    assert combo["items"][0]["plan"] == "run"


def test_marked_missing_and_unknown_assets_are_out_with_the_reason(seeded):
    db, _, _ = seeded
    plan = build_plan(_body(["WAVES/USDT", "ZZZZ/USDT", "NVDA", "nvda"]), db=db, now=NOW)

    items = _by_symbol(plan)
    assert len(plan["items"]) == 3  # NVDA repetido entra uma vez
    assert items["WAVES/USDT"]["plan"] == "out" and items["WAVES/USDT"]["out_kind"] == "marked"
    assert items["WAVES/USDT"]["reason"].endswith("; não entra em análise nova")
    assert items["ZZZZ/USDT"]["reason"] == "ativo fora do catálogo da Binance"
    assert items["NVDA"]["plan"] == "run"


# ------------------------------------------------------------------ 2.2 / 2.3 / 2.5 rotas


@pytest.fixture
def client(public_db, unit_database_url, monkeypatch):  # noqa: F811
    _seed_catalog(public_db)
    Session = sessionmaker(bind=public_db)

    def _db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    enqueued: list = []
    monkeypatch.setattr(
        combo_routes, "enqueue_batch_backtest", lambda job_id, payload: enqueued.append(job_id)
    )
    monkeypatch.setattr(
        history_service.HistoryService, "ensure", lambda *a, **k: pytest.fail("coletou")
    )
    app = FastAPI()
    app.include_router(combo_routes.router)
    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[combo_routes.get_current_admin] = lambda: "user-1"
    test_client = TestClient(app)
    test_client.enqueued = enqueued  # type: ignore[attr-defined]
    return test_client


def test_preview_returns_the_plan_and_never_collects(client):
    response = client.post(
        "/api/combos/backtest/batch/preview",
        json=_body(["BTC/USDT", "NVDA", "SPY", "WAVES/USDT"], timeframe="1d"),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert [i["symbol"] for i in body["items"]] == ["BTC/USDT", "NVDA", "SPY", "WAVES/USDT"]
    assert body["totals"]["run"] == 3 and body["totals"]["out"] == 1
    assert body["config"]["timeframe"] == "1d"
    assert client.enqueued == []  # preview não cria lote


def test_post_returns_422_only_when_nothing_runs_with_the_reason_per_asset(client):
    nothing = client.post("/api/combos/backtest/batch", json=_body(["NVDA", "SPY"], timeframe="5m"))
    assert nothing.status_code == 422
    detail = nothing.json()["detail"]
    assert detail["code"] == "batch_nothing_to_run"
    assert {a["symbol"]: a["kind"] for a in detail["assets"]} == {
        "NVDA": "timeframe",
        "SPY": "timeframe",
    }
    assert client.enqueued == []

    some = client.post(
        "/api/combos/backtest/batch", json=_body(["BTC/USDT", "NVDA"], timeframe="5m")
    )
    assert some.status_code == 200, some.text  # roda a cripto; ação fica fora
    assert len(client.enqueued) == 1


def test_non_ccxt_source_is_refused_only_for_crypto(client):
    crypto = client.post(
        "/api/combos/backtest/batch", json={**_body(["BTC/USDT"]), "data_source": "stooq"}
    )
    assert crypto.status_code in (400, 422)
    equity = client.post(
        "/api/combos/backtest/batch", json={**_body(["NVDA"]), "data_source": "ccxt"}
    )
    assert equity.status_code == 200, equity.text


def test_paused_batch_blocks_a_new_batch_and_its_preview_with_409(client):
    first = client.post("/api/combos/backtest/batch", json=_body(["BTC/USDT", "NVDA"]))
    job_id = first.json()["job_id"]
    assert (
        client.post(f"/api/combos/backtest/batch/{job_id}/pause").status_code == 200
    )  # na fila: pausa já

    for path in ("/api/combos/backtest/batch", "/api/combos/backtest/batch/preview"):
        blocked = client.post(path, json=_body(["BTC/USDT"]))
        assert blocked.status_code == 409, path
        detail = blocked.json()["detail"]
        assert detail["code"] == "batch_paused" and detail["job_id"] == job_id
        assert detail["message"] == f"Retome ou encerre o lote {job_id[:8]} antes de começar outro."
    assert len(client.enqueued) == 1

    # encerrado não bloqueia
    assert client.post(f"/api/combos/backtest/batch/{job_id}/cancel").status_code == 200
    assert (
        client.post("/api/combos/backtest/batch/preview", json=_body(["BTC/USDT"])).status_code
        == 200
    )


def test_resume_active_and_progress_endpoints(client):
    job_id = client.post(
        "/api/combos/backtest/batch", json=_body(["BTC/USDT", "NVDA", "SPY"])
    ).json()["job_id"]
    progress = client.get(f"/api/combos/backtest/batch/{job_id}").json()
    assert progress["status"] == "queued" and progress["total"] == 3
    assert [i["symbol"] for i in progress["items"]] == ["BTC/USDT", "NVDA", "SPY"]
    assert progress["totals"] == {"queued": 3}
    assert progress["config"]["timeframe"] == "1d" and "payload" not in progress

    active = client.get("/api/combos/backtest/batch/active").json()
    assert active["job_id"] == job_id and active["status"] == "queued"

    assert (
        client.post(f"/api/combos/backtest/batch/{job_id}/resume").status_code == 409
    )  # não está pausado
    client.post(f"/api/combos/backtest/batch/{job_id}/pause")
    assert client.get(f"/api/combos/backtest/batch/{job_id}").json()["status"] == "paused"
    resumed = client.post(f"/api/combos/backtest/batch/{job_id}/resume")
    assert resumed.status_code == 200
    assert client.get(f"/api/combos/backtest/batch/{job_id}").json()["status"] == "queued"
    assert client.enqueued == [job_id, job_id]  # o mesmo lote foi para a fila de novo
    assert client.post("/api/combos/backtest/batch/missing/resume").status_code == 404

    client.post(f"/api/combos/backtest/batch/{job_id}/cancel")
    assert client.get("/api/combos/backtest/batch/active").json() is None
    final = client.get(f"/api/combos/backtest/batch/{job_id}").json()
    assert final["status"] == "cancelled" and final["totals"] == {"not_run": 3}
