from __future__ import annotations

from dataclasses import dataclass

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
    return test_app


async def _post_backtest(app: FastAPI, payload: dict):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.post("/api/combos/backtest", json=payload)


async def test_backtest_us_ticker_defaults_to_stooq(monkeypatch):
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

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["parameters"]["data_source"] == "stooq"
    assert provider_calls[-1] == "stooq"


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


async def test_backtest_explicit_data_source_overrides_default(monkeypatch):
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

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["parameters"]["data_source"] == "stooq"
    assert provider_calls[-1] == "stooq"
