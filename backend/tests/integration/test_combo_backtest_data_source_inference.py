from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import FastAPI
import httpx

from app.routes import combo_routes
from app.services import combo_optimizer
from app.services import combo_service

from utils.market_data_mocks import (
    FixtureMarketDataProvider,
    install_market_data_provider_mock,
    load_ohlcv_fixture_csv,
)


@dataclass
class _FakeStrategy:
    stop_loss: float = 0.02
    direction: str = "long"
    indicators: list[dict] = field(
        default_factory=lambda: [{"type": "ema", "alias": "trend", "params": {"length": 21}}]
    )
    entry_logic: str = "close < trend"
    exit_logic: str = "close > trend"

    def generate_signals(self, df):
        out = df.copy()
        out["signal"] = 0
        if len(out) >= 2:
            out.iloc[0, out.columns.get_loc("signal")] = 1
            out.iloc[-1, out.columns.get_loc("signal")] = -1
        return out

    def get_indicator_columns(self):
        return []


def _patch_backtest_dependencies(monkeypatch):
    nvda_df = load_ohlcv_fixture_csv("nvda_1d.csv")
    btc_df = load_ohlcv_fixture_csv("btcusdt_1d.csv")

    providers = {
        "stooq": FixtureMarketDataProvider("stooq", {"NVDA": nvda_df}),
        "ccxt": FixtureMarketDataProvider("ccxt", {"BTC/USDT": btc_df}),
    }
    provider_calls = install_market_data_provider_mock(monkeypatch, [combo_routes], providers)

    monkeypatch.setattr(
        combo_service.ComboService,
        "create_strategy",
        lambda self, template_name, parameters: _FakeStrategy(),
    )

    monkeypatch.setattr(
        combo_optimizer,
        "extract_trades_from_signals",
        lambda df_with_signals, stop_loss_pct, direction: [
            {
                "entry_time": df_with_signals.index[0].isoformat(),
                "entry_price": float(df_with_signals.iloc[0]["open"]),
                "exit_time": df_with_signals.index[-1].isoformat(),
                "exit_price": float(df_with_signals.iloc[-1]["open"]),
                "profit": 0.01,
                "type": direction,
            }
        ],
    )

    return provider_calls


def _build_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(combo_routes.router)
    test_app.dependency_overrides[combo_routes.get_current_admin] = lambda: "admin-user"
    return test_app


def _build_public_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(combo_routes.router)
    return test_app


async def _post_backtest(app: FastAPI, payload: dict):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.post("/api/combos/backtest", json=payload)


async def _post_optimize(app: FastAPI, payload: dict):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.post("/api/combos/optimize", json=payload)


async def test_combo_strategy_tooling_requires_admin():
    app = _build_public_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        templates_response = await client.get("/api/combos/templates")
        backtest_response = await client.post(
            "/api/combos/backtest",
            json={"template_name": "ema_rsi", "symbol": "BTC/USDT", "timeframe": "1d"},
        )

    assert templates_response.status_code == 401
    assert backtest_response.status_code == 401


async def test_backtest_us_ticker_rejected_for_crypto_only_mvp(monkeypatch):
    provider_calls = _patch_backtest_dependencies(monkeypatch)
    app = _build_app()

    response = await _post_backtest(
        app,
        {
            "template_name": "ema_rsi",
            "symbol": "NVDA",
            "timeframe": "1d",
            "parameters": {},
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
        },
    )

    assert response.status_code == 400, response.text
    assert "MVP supports only crypto pairs" in response.json()["detail"]
    assert provider_calls == []


async def test_backtest_crypto_pair_defaults_to_ccxt(monkeypatch):
    provider_calls = _patch_backtest_dependencies(monkeypatch)
    app = _build_app()

    response = await _post_backtest(
        app,
        {
            "template_name": "ema_rsi",
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "parameters": {},
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["parameters"]["data_source"] == "ccxt"
    assert provider_calls[-1] == "ccxt"


async def test_backtest_uses_template_direction_when_request_omits_it(monkeypatch):
    _patch_backtest_dependencies(monkeypatch)
    monkeypatch.setattr(
        combo_service.ComboService,
        "create_strategy",
        lambda self, template_name, parameters: _FakeStrategy(direction="short"),
    )
    app = _build_app()

    response = await _post_backtest(
        app,
        {
            "template_name": "quant_btc_1d_short_ma_breakdown_chain_w2_20260629",
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "parameters": {},
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["direction"] == "short"
    assert payload["parameters"]["direction"] == "short"
    assert payload["strategy_transparency"]["direction"] == "short"


async def test_backtest_passes_explicit_direction_into_strategy_parameters(monkeypatch):
    _patch_backtest_dependencies(monkeypatch)
    received_parameters = {}

    def create_strategy(_self, template_name, parameters):
        del template_name
        received_parameters.update(parameters)
        return _FakeStrategy(direction=parameters["direction"])

    monkeypatch.setattr(combo_service.ComboService, "create_strategy", create_strategy)
    app = _build_app()

    response = await _post_backtest(
        app,
        {
            "template_name": "ema_rsi",
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "parameters": {},
            "direction": "short",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
        },
    )

    assert response.status_code == 200, response.text
    assert received_parameters["direction"] == "short"
    assert response.json()["direction"] == "short"


async def test_backtest_explicit_stock_data_source_rejected(monkeypatch):
    provider_calls = _patch_backtest_dependencies(monkeypatch)
    app = _build_app()

    response = await _post_backtest(
        app,
        {
            "template_name": "ema_rsi",
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "data_source": "stooq",
            "parameters": {},
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
        },
    )

    assert response.status_code == 400, response.text
    assert "only CCXT crypto market data" in response.json()["detail"]
    assert provider_calls == []


async def test_optimize_us_ticker_returns_400_not_500(monkeypatch):
    provider_calls = _patch_backtest_dependencies(monkeypatch)
    app = _build_app()

    response = await _post_optimize(
        app,
        {
            "template_name": "ema_rsi",
            "symbol": "NVDA",
            "timeframe": "1d",
            "data_source": "stooq",
            "custom_ranges": {},
            "deep_backtest": True,
        },
    )

    assert response.status_code == 400, response.text
    assert "MVP supports only crypto pairs" in response.json()["detail"]
    assert provider_calls == []


async def test_optimize_uses_template_direction_when_request_omits_it(monkeypatch):
    directions = []

    monkeypatch.setattr(
        combo_service.ComboService,
        "get_template_metadata",
        lambda self, template_name: {"direction": "short"},
    )

    def run_optimization(_self, **kwargs):
        directions.append(kwargs["direction"])
        return {
            "job_id": "job-short-template",
            "template_name": kwargs["template_name"],
            "symbol": kwargs["symbol"],
            "timeframe": kwargs["timeframe"],
            "stages": [],
            "best_parameters": {"direction": kwargs["direction"]},
            "best_metrics": {},
            "direction": kwargs["direction"],
        }

    monkeypatch.setattr(combo_optimizer.ComboOptimizer, "run_optimization", run_optimization)
    app = _build_app()

    response = await _post_optimize(
        app,
        {
            "template_name": "quant_btc_1d_short_ma_breakdown_chain_w2_20260629",
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "custom_ranges": {},
            "deep_backtest": False,
        },
    )

    assert response.status_code == 200, response.text
    assert directions == ["short"]
    assert response.json()["direction"] == "short"


async def test_optimize_invalid_explicit_direction_falls_back_to_template(monkeypatch):
    directions = []
    monkeypatch.setattr(
        combo_service.ComboService,
        "get_template_metadata",
        lambda self, template_name: {"direction": "short"},
    )

    def run_optimization(_self, **kwargs):
        directions.append(kwargs["direction"])
        return {
            "job_id": "job-invalid-direction",
            "template_name": kwargs["template_name"],
            "symbol": kwargs["symbol"],
            "timeframe": kwargs["timeframe"],
            "stages": [],
            "best_parameters": {"direction": kwargs["direction"]},
            "best_metrics": {},
            "direction": kwargs["direction"],
        }

    monkeypatch.setattr(combo_optimizer.ComboOptimizer, "run_optimization", run_optimization)
    app = _build_app()

    response = await _post_optimize(
        app,
        {
            "template_name": "quant_btc_1d_short_ma_breakdown_chain_w2_20260629",
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "direction": "sideways",
            "custom_ranges": {},
            "deep_backtest": False,
        },
    )

    assert response.status_code == 200, response.text
    assert directions == ["short"]
    assert response.json()["direction"] == "short"
