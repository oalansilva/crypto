from __future__ import annotations

import app.services.binance_symbol_universe as symbol_universe


def test_resolve_binance_ohlcv_symbols_defaults_to_all_usdt(monkeypatch):
    monkeypatch.delenv("MARKET_OHLCV_SYMBOLS", raising=False)
    monkeypatch.delenv("MARKET_OHLCV_SYMBOL_LIMIT", raising=False)
    monkeypatch.setattr(
        symbol_universe,
        "_fetch_trading_spot_usdt_symbols",
        lambda: [
            "ETH/USDT",
            "BTC/USDT",
            "AION/USDT",
            "ADAUP/USDT",
            "BTC/BUSD",
            "SOL/USDT",
        ],
    )

    assert symbol_universe.resolve_binance_ohlcv_symbols() == [
        "ETH/USDT",
        "BTC/USDT",
        "SOL/USDT",
    ]


def test_resolve_binance_ohlcv_symbols_supports_explicit_list_and_limit(monkeypatch):
    monkeypatch.setenv("MARKET_OHLCV_SYMBOLS", " btc/usdt,eth/usdt, btc/usdt, ")
    monkeypatch.setenv("MARKET_OHLCV_SYMBOL_LIMIT", "1")

    assert symbol_universe.resolve_binance_ohlcv_symbols() == ["BTC/USDT"]


def test_resolve_binance_ohlcv_symbols_limit_keeps_majors_first(monkeypatch):
    monkeypatch.delenv("MARKET_OHLCV_SYMBOLS", raising=False)
    monkeypatch.setenv("MARKET_OHLCV_SYMBOL_LIMIT", "3")
    monkeypatch.setattr(
        symbol_universe,
        "_fetch_trading_spot_usdt_symbols",
        lambda: [
            "0G/USDT",
            "1000CAT/USDT",
            "AAVE/USDT",
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "ZEC/USDT",
        ],
    )

    assert symbol_universe.resolve_binance_ohlcv_symbols() == [
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
    ]


def test_slice_symbol_universe_for_ingestion_run_rotates_with_limit():
    universe = ["AAA/USDT", "BBB/USDT", "CCC/USDT", "BTC/USDT", "ETH/USDT"]
    first_batch, next_offset = symbol_universe.slice_symbol_universe_for_ingestion_run(
        universe,
        priority_symbols=["BTC/USDT"],
        limit=3,
        offset=0,
    )
    assert first_batch == ["BTC/USDT", "AAA/USDT", "BBB/USDT"]
    assert next_offset == 3

    second_batch, second_offset = symbol_universe.slice_symbol_universe_for_ingestion_run(
        universe,
        priority_symbols=["BTC/USDT"],
        limit=3,
        offset=next_offset,
    )
    assert second_batch == ["CCC/USDT", "ETH/USDT", "BTC/USDT"]
    assert second_offset == 1


def test_resolve_binance_ohlcv_symbol_universe_skips_apply_limit(monkeypatch):
    monkeypatch.delenv("MARKET_OHLCV_SYMBOLS", raising=False)
    monkeypatch.setenv("MARKET_OHLCV_SYMBOL_LIMIT", "2")
    monkeypatch.setattr(
        symbol_universe,
        "_fetch_trading_spot_usdt_symbols",
        lambda: ["BTC/USDT", "ETH/USDT", "SOL/USDT", "DOGE/USDT"],
    )

    assert symbol_universe.resolve_binance_ohlcv_symbol_universe() == [
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
        "DOGE/USDT",
    ]
    assert symbol_universe.resolve_binance_ohlcv_symbols() == ["BTC/USDT", "ETH/USDT"]


def test_resolve_binance_ohlcv_symbols_falls_back_on_exchange_error(monkeypatch):
    class _ExchangeService:
        def fetch_binance_symbols(self):
            raise RuntimeError("offline")

    monkeypatch.setenv("MARKET_OHLCV_SYMBOLS", "binance:all")
    monkeypatch.delenv("MARKET_OHLCV_SYMBOL_LIMIT", raising=False)
    monkeypatch.setattr(
        symbol_universe,
        "_fetch_trading_spot_usdt_symbols",
        lambda: (_ for _ in ()).throw(RuntimeError("offline")),
    )
    monkeypatch.setattr(symbol_universe, "ExchangeService", _ExchangeService)

    assert symbol_universe.resolve_binance_ohlcv_symbols() == [
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
        "BNB/USDT",
        "XRP/USDT",
    ]
