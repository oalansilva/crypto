from __future__ import annotations

import pandas as pd

from app.services.market_data_providers import CCXT_SOURCE, STOOQ_SOURCE
from app.services.opportunity_service import OpportunityService, _normalize_market_timeframe
from app.services import opportunity_service


def _sample_ohlcv():
    ts = pd.to_datetime(
        ["2026-04-20T00:00:00Z", "2026-04-21T00:00:00Z", "2026-04-22T00:00:00Z"],
        utc=True,
    )
    ts_values = (ts.astype("int64") // 1_000_000_000).astype("int64")
    return pd.DataFrame(
        {
            "timestamp": ts_values,
            "timestamp_utc": ts,
            "time": ts,
            "open": [100.0, 101.0, 102.0],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [10, 10, 10],
        },
        index=ts,
    )


class _FakeComboStrategy:
    def __init__(
        self, *args, entry_logic: str = "", exit_logic: str = "", stop_loss: float = 0.0, **kwargs
    ):
        self.entry_logic = entry_logic
        self.exit_logic = exit_logic
        self.stop_loss = stop_loss

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["short"] = out["close"] * 0.9
        out["medium"] = out["close"] * 1.0
        out["long"] = out["close"] * 1.1
        return out

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(signal=0, signal_reason=pd.NA)


class _FailingProvider:
    def __init__(self):
        self.calls = 0

    def fetch_ohlcv(self, *_args, **_kwargs):
        self.calls += 1
        raise RuntimeError("provider-failed")


class _MockProvider:
    def __init__(self, df):
        self.df = df
        self.calls = 0

    def fetch_ohlcv(self, *_args, **_kwargs):
        self.calls += 1
        return self.df.copy()


def _sample_favorite(
    symbol: str, timeframe: str, template="trend", data_source: str = STOOQ_SOURCE
):
    return {
        "id": 7,
        "name": "Test Favorite",
        "symbol": symbol,
        "timeframe": timeframe,
        "strategy_name": template,
        "parameters": {"data_source": data_source},
        "tier": 1,
        "notes": None,
    }


def test_normalize_market_timeframe():
    assert _normalize_market_timeframe("AAPL", "15m", STOOQ_SOURCE) == "1d"
    assert _normalize_market_timeframe("AAPL", "1d", STOOQ_SOURCE) == "1d"
    assert _normalize_market_timeframe("BTC/USDT", "4h", CCXT_SOURCE) == "4h"


def test_get_opportunities_stooq_error_fallback_to_yahoo(monkeypatch):
    service = OpportunityService(db_path=":memory:")
    favorite = _sample_favorite("AAPL", "4h", data_source=STOOQ_SOURCE)
    service.get_favorites = lambda *_args, **_kwargs: [favorite]

    stooq_provider = _FailingProvider()
    yahoo_provider = _MockProvider(_sample_ohlcv())

    monkeypatch.setattr(
        opportunity_service, "resolve_data_source_for_symbol", lambda *_args: STOOQ_SOURCE
    )
    monkeypatch.setattr(
        opportunity_service, "get_market_data_provider", lambda *_args: stooq_provider
    )
    monkeypatch.setattr(opportunity_service, "YahooMarketDataProvider", lambda: yahoo_provider)
    monkeypatch.setattr(
        service.combo_service,
        "get_template_metadata",
        lambda template_name: {
            "indicators": [],
            "entry_logic": "close > open",
            "exit_logic": "close < open",
            "stop_loss": 0.1,
        },
    )
    monkeypatch.setattr(opportunity_service, "ComboStrategy", _FakeComboStrategy)
    monkeypatch.setattr(
        service.analyzer,
        "analyze",
        lambda *args, **kwargs: {
            "status": "HOLD",
            "badge": "info",
            "message": "ok",
            "distance": 0.5,
        },
    )

    out = service.get_opportunities("user")

    assert len(out) == 1
    assert stooq_provider.calls == 1
    assert yahoo_provider.calls == 1
    assert out[0]["timeframe"] == "1d"


def test_get_opportunities_fetch_error_for_ccxt_is_skipped(monkeypatch):
    service = OpportunityService(db_path=":memory:")
    favorite = _sample_favorite("BTC/USDT", "15m", data_source=CCXT_SOURCE)
    service.get_favorites = lambda *_args, **_kwargs: [favorite]

    provider = _FailingProvider()
    monkeypatch.setattr(
        opportunity_service, "resolve_data_source_for_symbol", lambda *_args: CCXT_SOURCE
    )
    monkeypatch.setattr(opportunity_service, "_is_unsupported_symbol", lambda *_args: False)
    monkeypatch.setattr(opportunity_service, "get_market_data_provider", lambda *_args: provider)

    out = service.get_opportunities("user")
    assert out == []


def test_get_opportunities_ccxt_applies_continuity_fix(monkeypatch):
    service = OpportunityService(db_path=":memory:")
    favorite = _sample_favorite("BTC/USDT", "1h", data_source=CCXT_SOURCE)
    service.get_favorites = lambda *_args, **_kwargs: [favorite]

    provider = _MockProvider(_sample_ohlcv())
    fixed = {"called": False}

    def _fake_fix(df, timeframe):
        fixed["called"] = True
        return df

    monkeypatch.setattr(
        opportunity_service, "resolve_data_source_for_symbol", lambda *_args: CCXT_SOURCE
    )
    monkeypatch.setattr(opportunity_service, "_is_unsupported_symbol", lambda *_args: False)
    monkeypatch.setattr(opportunity_service, "get_market_data_provider", lambda *_args: provider)
    monkeypatch.setattr(
        service.combo_service,
        "get_template_metadata",
        lambda template_name: {
            "indicators": [],
            "entry_logic": "close > open",
            "exit_logic": "close < open",
            "stop_loss": 0.1,
        },
    )
    monkeypatch.setattr(opportunity_service, "ComboStrategy", _FakeComboStrategy)
    monkeypatch.setattr(
        service.analyzer,
        "analyze",
        lambda *args, **kwargs: {
            "status": "HOLD",
            "badge": "info",
            "message": "ok",
            "distance": 0.5,
        },
    )
    monkeypatch.setattr(opportunity_service, "_apply_crypto_continuity_fix", _fake_fix)

    out = service.get_opportunities("user")
    assert len(out) == 1
    assert fixed["called"] is True
    assert out[0]["timeframe"] == "1h"
