from __future__ import annotations

import socket
from pathlib import Path
from typing import Any

import pandas as pd

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
_LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1", "testserver"}


def load_ohlcv_fixture_csv(name: str) -> pd.DataFrame:
    path = FIXTURES_DIR / name
    df = pd.read_csv(path)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    df = df.set_index("timestamp_utc", drop=False).sort_index()
    df["time"] = df["timestamp_utc"]
    df["timestamp"] = (df["timestamp_utc"].astype("int64") // 1_000_000).astype("int64")
    return df


class FixtureMarketDataProvider:
    def __init__(self, source: str, symbol_to_df: dict[str, pd.DataFrame]):
        self.source = source
        self._symbol_to_df = symbol_to_df

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since_str: str | None = None,
        until_str: str | None = None,
        limit: int | None = None,
    ) -> pd.DataFrame:
        base = self._symbol_to_df.get(symbol)
        if base is None:
            base = next(iter(self._symbol_to_df.values())).copy()
        else:
            base = base.copy()

        if since_str:
            since = pd.to_datetime(since_str, utc=True)
            base = base[base.index >= since]
        if until_str:
            until = pd.to_datetime(until_str, utc=True)
            base = base[base.index <= until]
        if isinstance(limit, int) and limit > 0:
            base = base.tail(limit)
        return base


def install_market_data_provider_mock(
    monkeypatch: Any, targets: list[Any], providers: dict[str, Any]
) -> list[str]:
    aliases = {
        "": "ccxt",
        "default": "ccxt",
        "binance": "ccxt",
        "crypto": "ccxt",
        "stooq-eod": "stooq",
        "stooq_eod": "stooq",
    }
    calls: list[str] = []

    def fake_get_market_data_provider(data_source: str | None):
        raw = str(data_source or "").strip().lower()
        resolved = aliases.get(raw, raw)
        calls.append(resolved)
        if resolved not in providers:
            raise AssertionError(f"Unexpected data_source '{data_source}' in test")
        return providers[resolved]

    for target in targets:
        monkeypatch.setattr(target, "get_market_data_provider", fake_get_market_data_provider)
    return calls


def block_external_network(monkeypatch: Any) -> None:
    original_connect = socket.socket.connect

    def guarded_connect(self: socket.socket, address: Any):
        if isinstance(address, tuple) and address:
            host = str(address[0])
            if host not in _LOCAL_HOSTS:
                raise AssertionError(f"External network access blocked in tests: {host}")
        return original_connect(self, address)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
