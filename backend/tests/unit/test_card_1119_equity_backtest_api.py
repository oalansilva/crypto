"""Backtest individual de ação e ETF pela API (card #1119, tarefas 5.1 a 5.6 e 6.1)."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.metrics.backtest_execution_costs import long_trade_profit_frac
from app.middleware.authMiddleware import get_current_user
from app.routes import combo_routes, favorites
from app.services import combo_service
from app.services.asset_catalog_service import EQUITY_BATCH_REASON
from app.services.market_history import facade
from app.services.market_history.cache import ParquetReadCache
from app.services.market_history.equity_provider import BinanceRateLimited
from app.services.market_history.service import HistoryService
from market_history_support import FakeEquityProvider, history_schema
from test_card_1118_api_and_catalog import _seed_catalog, public_db  # noqa: F401

NOW = pd.Timestamp("2026-10-23 01:30", tz="UTC")
# Card #1121: a Descoberta também roda ação e ETF; o motivo só sobra para a recusa dos caminhos legados
# (backtest legado e Otimização sem escopo), que diz que ação e ETF não rodam ali e aponta os certos.
NEW_REASON = (
    "ação e ETF não rodam neste caminho; use o Combo, a Otimização (1 ativo ou lote) ou a Descoberta"
)
NEW_MESSAGE = NEW_REASON[0].upper() + NEW_REASON[1:] + "."


class RoutedProvider(FakeEquityProvider):
    """Um provedor simulado por tempo (1d e 5m), com o registro dos pedidos."""

    def __init__(self, by_tf):
        super().__init__(now=NOW)
        self.by_tf = by_tf

    def fetch_page_once(self, symbol, timeframe, **kwargs):
        self.requests.append({"symbol": symbol, "tf": timeframe})
        inner = self.by_tf[timeframe]
        if self.fail_with is not None and (
            self.fail_after is None or len(self.requests) > self.fail_after
        ):
            raise self.fail_with
        return inner.fetch_page_once(symbol, timeframe, **kwargs)


@dataclass
class _FakeStrategy:
    stop_loss: float = 0.05
    direction: str = "long"
    indicators: list = field(
        default_factory=lambda: [{"type": "ema", "alias": "trend", "params": {"length": 21}}]
    )
    entry_logic: str = "close < trend"
    exit_logic: str = "close > trend"

    def generate_signals(self, df):
        out = df.copy()
        out["signal"] = 0
        if len(out) >= 4:
            out.iloc[1, out.columns.get_loc("signal")] = 1
            out.iloc[-2, out.columns.get_loc("signal")] = -1
        return out

    def get_indicator_columns(self):
        return []


@pytest.fixture
def env(public_db, unit_database_url, tmp_path, monkeypatch):  # noqa: F811
    _seed_catalog(public_db)
    monkeypatch.setenv("MARKET_HISTORY_SNAPSHOT_DIR", str(tmp_path / "snapshots"))
    monkeypatch.setattr(
        combo_service.ComboService,
        "create_strategy",
        lambda self, template_name, parameters: _FakeStrategy(
            direction=(parameters or {}).get("direction", "long")
        ),
    )
    with history_schema(unit_database_url) as engine:
        daily = FakeEquityProvider(timeframe="1d", now=NOW, page_size=400)
        daily.build(pd.Timestamp("2023-12-01", tz="UTC"), NOW)
        five = FakeEquityProvider(timeframe="5m", now=NOW, page_size=1000)
        five.build(pd.Timestamp("2026-09-01", tz="UTC"), NOW)
        provider = RoutedProvider({"1d": daily, "5m": five})
        service = HistoryService(
            engine,
            equity_provider=provider,
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
        app.include_router(combo_routes.router)
        app.include_router(favorites.router)
        app.dependency_overrides[get_db] = _db
        app.dependency_overrides[get_current_user] = lambda: "user-1"
        app.dependency_overrides[combo_routes.get_current_admin] = lambda: "admin-1"
        yield TestClient(app), provider, public_db, daily, five
        facade.set_history_service(None, None)


def _backtest(client, symbol="NVDA", timeframe="1d", **extra):
    payload = {
        "template_name": "ema_rsi",
        "symbol": symbol,
        "timeframe": timeframe,
        "parameters": {},
        "start_date": "2026-09-02",
        "end_date": "2026-10-20",
        **extra,
    }
    return client.post("/api/combos/backtest", json=payload)


# ---------------------------------------------------------------- 5.1 / 5.6 aceite e recusa


def test_nvda_individual_backtest_runs_with_identity_conventions_and_precision(env):
    client, provider, *_ = env
    response = _backtest(client)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["asset"]["symbol"] == "NVDA" and body["asset"]["asset_class"] == "stock"
    assert body["asset"]["currency"] == "USD"
    assert body["asset"]["name"].startswith("NVIDIA")
    prov = body["data_provenance"]
    assert prov["data_source"] == "Binance Ações" and prov["session"] == "rth"
    assert prov["adjustment"] == "adjusted" and prov["version_label"]
    assert prov["snapshot_id"] == body["snapshot_id"]
    execution = body["execution"]
    assert execution["precision_requested"] == "intrabar"
    assert execution["precision_effective"] == "intrabar_15m"  # o 5m cobre set. e out. de 2026
    assert execution["intraday_missing"] == [] and execution["intraday_reason"] is None
    assert execution["window"]["covered"]["candles"] > 10
    conv = body["conventions"]
    assert conv["fee"] == pytest.approx(0.001) and conv["fee_confirmed"] is True
    assert conv["slippage"] == pytest.approx(0.0002) and "periods_per_year" not in conv
    assert conv["fraction"]["confirms_account"] is False and conv["short"] is None
    assert conv["adjusted_prices"] is True
    assert body["execution_mode"] == "deep_15m"
    assert len(body["trades"]) == 1
    # a taxa confirmada de ação/ETF (0,10% por lado) é a que entra no lucro do trade, não a de cripto
    trade = body["trades"][0]
    paid = long_trade_profit_frac(
        trade["entry_price"], trade["exit_price"], fee=0.001, slippage=conv["slippage"]
    )
    assert trade["profit"] == pytest.approx(paid)
    # só NVDA foi coletado, e só o que a execução usa (1d e o 5m do intrabar)
    assert {r["symbol"] for r in provider.requests} == {"NVDA"}
    assert {r["tf"] for r in provider.requests} == {"1d", "5m"}


def test_spy_short_reports_the_simulated_short(env):
    client, *_ = env
    body = _backtest(client, symbol="SPY", direction="short").json()
    assert body["asset"]["asset_class"] == "etf"
    assert body["direction"] == "short"
    assert body["conventions"]["short"]["simulated"] is True


def test_equity_1h_collects_only_the_5m_that_builds_it(env):
    client, provider, *_ = env
    response = _backtest(client, timeframe="1h")
    assert response.status_code == 200, response.text
    assert {r["tf"] for r in provider.requests} == {"5m"}  # 1h é montado, nunca coletado nativo
    body = response.json()
    assert body["execution"]["timeframe"] == "1h"
    assert body["conventions"]["slippage"] == pytest.approx(0.0003)
    assert "periods_per_year" not in body["conventions"]
    # candles de 1h só dentro do pregão: 7 por pregão
    days = pd.Series(
        [c["timestamp_utc"][:10] for c in body["candles"]], dtype="string"
    ).value_counts()
    assert set(days.unique()) <= {7, 4}  # 4 no meio-pregão


def test_window_without_5m_runs_in_candle_precision_and_names_the_stretch(env):
    client, provider, *_ = env
    response = _backtest(client, start_date="2024-01-02", end_date="2024-01-31")
    assert response.status_code == 200, response.text
    execution = response.json()["execution"]
    assert execution["precision_requested"] == "intrabar"
    assert execution["precision_effective"] == "candle"
    assert execution["intraday_reason"] == "missing"
    assert execution["intraday_missing"][0]["from"].startswith("2024-01-0")
    assert execution["intraday_missing"][-1]["to"] == "2024-01-31"
    assert execution["timeframe"] == "1d"


def test_intrabar_off_is_a_chosen_daily_precision_without_warning(env):
    client, *_ = env
    execution = _backtest(client, deep_backtest=False).json()["execution"]
    assert execution["precision_requested"] == "daily"
    assert execution["precision_effective"] == "candle"
    assert execution["intraday_reason"] is None and execution["intraday_missing"] == []


def test_partial_intraday_coverage_is_one_stretch_not_a_silent_fall(env):
    client, provider, public_db, daily, five = env  # noqa: F811
    # o 5m simulado começa no pregão de 31 ago.; a janela pede desde 20 ago.: o trecho sem 15m é de 20 a 28 ago.
    response = _backtest(client, start_date="2026-08-20", end_date="2026-10-20")
    execution = response.json()["execution"]
    assert execution["precision_effective"] == "candle"
    assert execution["intraday_reason"] == "coverage"
    assert execution["intraday_missing"] == [{"from": "2026-08-20", "to": "2026-08-28"}]


def test_1m_and_5m_are_refused_for_equity_with_the_reason_and_nothing_is_collected(env):
    client, provider, *_ = env
    for tf in ("1m", "5m", "30m"):
        response = _backtest(client, timeframe=tf)
        assert response.status_code == 422, tf
        detail = response.json()["detail"]
        assert detail["code"] == "timeframe_not_supported"
        assert "15m, 1h, 4h ou 1d" in detail["message"]
    assert provider.requests == []


def test_binance_marked_equity_is_refused_without_collecting(env):
    client, provider, *_ = env
    response = _backtest(client, symbol="AVB")
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "asset_not_selectable"
    assert provider.requests == []


# ---------------------------------------------------------------- 5.3 coleta


def test_rate_limit_with_nothing_stored_refuses_without_an_empty_result(env):
    client, provider, *_ = env
    provider.fail_with = BinanceRateLimited(429, 30)
    response = _backtest(client, symbol="AAPL")
    assert response.status_code == 422, response.text
    detail = response.json()["detail"]
    assert detail["code"] == "history_unavailable"
    assert detail["message"] == (
        "Histórico de AAPL indisponível agora: limite de requisições da Binance. "
        "Tente de novo em alguns minutos."
    )
    assert "488006" not in response.text


def test_collection_that_stops_with_part_stored_runs_on_the_covered_stretch(env):
    client, provider, _public_db, daily, _five = env
    # o primeiro pedido grava a cauda; a falha vem na segunda página (o início da janela)
    provider.fail_with = BinanceRateLimited(429, 30)
    provider.fail_after = 1
    response = _backtest(
        client, symbol="NVDA", deep_backtest=False, start_date="2023-12-04", end_date="2026-10-20"
    )
    assert response.status_code == 200, response.text
    execution = response.json()["execution"]
    note = execution["collection"]
    assert note is not None and note["status"] == "partial"
    assert note["reason"] == "limite de requisições da Binance"
    assert note["series"] == "1d" and note["kind"] == "head"
    covered = execution["window"]["covered"]
    assert covered["start"] > "2023-12-04T05:00"  # o começo da janela ficou fora
    assert covered["end"].startswith("2026-10-20")
    assert note["covered"]["start"][:10] == covered["start"][:10]
    assert note["left_out"][0]["from"] == "2023-12-04"


def test_catalog_selection_and_refused_analyses_never_collect(env, monkeypatch):
    client, provider, *_ = env
    monkeypatch.setattr(combo_routes, "enqueue_batch_backtest", lambda *a, **k: "task-1")
    assert client.get("/api/favorites/exists", params={}).status_code in (200, 422)
    # Card #1120: o lote aceita ação e ETF, mas só o worker coleta; receber o pedido não coleta.
    batch = client.post(
        "/api/combos/backtest/batch",
        json={"template_name": "ema_rsi", "symbols": ["NVDA", "SPY"], "timeframe": "1d"},
    )
    assert batch.status_code == 200, batch.text
    assert provider.requests == []


# ---------------------------------------------------------------- recusa no lote, na mista e na Descoberta


@pytest.mark.parametrize(
    "symbols", [["NVDA", "SPY"], ["BTC/USDT", "NVDA"], ["NVDA", "NVDA", "AAPL"]]
)
def test_batch_accepts_equity_and_the_text_now_belongs_to_discovery(env, symbols, monkeypatch):
    """Card #1120: o lote aceita ação e ETF; a guarda sem escopo segue recusando, com o porquê novo."""

    client, provider, *_ = env
    monkeypatch.setattr(combo_routes, "enqueue_batch_backtest", lambda *a, **k: "task-1")
    response = client.post(
        "/api/combos/backtest/batch",
        json={"template_name": "ema_rsi", "symbols": symbols, "timeframe": "1d"},
    )
    assert response.status_code == 200, response.text
    assert provider.requests == []
    from app.services.asset_analysis_guard import refusal_for_symbols

    discovery = refusal_for_symbols(symbols, new_analysis=True)
    assert discovery["code"] == "asset_class_not_supported"
    assert discovery["message"].startswith(NEW_MESSAGE)
    assert "Análise ainda não disponível" not in discovery["message"]


def test_discovery_accepts_equity_and_the_text_no_longer_mentions_it_later(env):
    """Card #1121 (decisão 2): a Descoberta roda ação e ETF; o texto "a Descoberta vem depois" saiu."""
    from app.services.asset_analysis_guard import discovery_symbol_reasons

    reasons = discovery_symbol_reasons(["NVDA", "SPY", "BTC/USDT"])
    assert reasons == {}
    assert NEW_REASON == EQUITY_BATCH_REASON and "vem depois" not in EQUITY_BATCH_REASON


class _OptimizerSpy:
    calls: list = []

    def __init__(self, *args, **kwargs):
        self.collection_note = None

    def run_optimization(self, **kwargs):
        _OptimizerSpy.calls.append({**kwargs, "provider": getattr(self, "_provider", None)})
        return {
            "job_id": "x",
            "template_name": kwargs["template_name"],
            "symbol": kwargs["symbol"],
            "timeframe": kwargs["timeframe"],
            "stages": [],
            "best_parameters": {},
            "best_metrics": {},
            "total_stages": 0,
        }


def _optimize(client, **payload):
    base = {
        "template_name": "ema_rsi",
        "symbol": "NVDA",
        "timeframe": "1d",
        "custom_ranges": {},
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
    }
    return client.post("/api/combos/optimize", json={**base, **payload})


def test_optimize_runs_one_equity_only_with_run_scope_single(env, monkeypatch):
    client, provider, *_ = env
    _OptimizerSpy.calls = []
    monkeypatch.setattr(combo_routes, "ComboOptimizer", _OptimizerSpy)
    refused = _optimize(client)
    assert refused.status_code == 422
    assert refused.json()["detail"]["code"] == "asset_class_not_supported"
    assert refused.json()["detail"]["message"].startswith(NEW_MESSAGE)
    assert _OptimizerSpy.calls == [] and provider.requests == []

    ok = _optimize(client, run_scope="single")
    assert ok.status_code == 200, ok.text
    call = _OptimizerSpy.calls[0]
    assert call["symbol"] == "NVDA" and call["data_source"] == "binance_equity"
    assert call["provider"]._ensure is False  # a coleta foi feita antes, só leitura depois
    assert {r["tf"] for r in provider.requests} <= {"1d", "5m"}


def test_optimize_with_an_equity_and_run_scope_single_still_refuses_a_marked_asset(
    env, monkeypatch
):
    client, provider, *_ = env
    monkeypatch.setattr(combo_routes, "ComboOptimizer", _OptimizerSpy)
    response = _optimize(client, symbol="AVB", run_scope="single")
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "asset_not_selectable"
    assert provider.requests == []


def test_optimization_of_nvda_1h_in_jan_2024_without_5m_runs_nothing(env, monkeypatch):
    client, provider, *_ = env
    _OptimizerSpy.calls = []
    monkeypatch.setattr(combo_routes, "ComboOptimizer", _OptimizerSpy)
    response = _optimize(client, timeframe="1h", run_scope="single")
    assert response.status_code == 422, response.text
    detail = response.json()["detail"]
    assert detail["code"] == "history_unavailable"
    assert "NVDA" in detail["message"]
    assert _OptimizerSpy.calls == []  # nada vazio rodou


def test_optimize_5m_and_30m_are_refused_for_equity(env, monkeypatch):
    client, provider, *_ = env
    monkeypatch.setattr(combo_routes, "ComboOptimizer", _OptimizerSpy)
    for tf in ("1m", "5m", "30m"):
        response = _optimize(client, timeframe=tf, run_scope="single")
        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "timeframe_not_supported"
    assert provider.requests == []


def test_optimize_crypto_does_not_need_run_scope(env, monkeypatch):
    client, provider, *_ = env
    _OptimizerSpy.calls = []
    monkeypatch.setattr(combo_routes, "ComboOptimizer", _OptimizerSpy)
    response = _optimize(client, symbol="BTC/USDT", data_source="ccxt")
    assert response.status_code == 200, response.text
    assert _OptimizerSpy.calls[0]["data_source"] == "ccxt"
    assert provider.requests == []


# ---------------------------------------------------------------- 6.1 favoritos


def _favorite(symbol):
    return {
        "name": f"{symbol} teste",
        "symbol": symbol,
        "timeframe": "1d",
        "strategy_name": "ema_rsi",
        "parameters": {"direction": "long"},
        "metrics": {"total_trades": 1},
    }


def test_favoriting_an_equity_is_refused_with_422_and_nothing_is_stored(env):
    client, _provider, engine, *_ = env
    for symbol in ("SPY", "NVDA", "AAPL"):
        response = client.post("/api/favorites/", json=_favorite(symbol))
        assert response.status_code == 422, response.text
        detail = response.json()["detail"]
        assert detail["code"] == "asset_class_not_favoritable"
        assert detail["message"] == (
            "Ações e ETFs ainda não podem ser favoritados: atualização diária e alertas "
            "dessas classes ainda não existem."
        )
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM favorite_strategies")).scalar() == 0
    assert detail["assets"][0]["symbol"] == "AAPL"


def test_favoriting_an_etf_reports_its_class_from_the_catalog(env):
    client, *_ = env
    detail = client.post("/api/favorites/", json=_favorite("SPY")).json()["detail"]
    assert detail["assets"] == [
        {"symbol": "SPY", "asset_id": "binance:equity:EQ_SPY", "asset_class": "etf"}
    ]
