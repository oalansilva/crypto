import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.market_data_providers import StooqEodProvider
from app.strategies.combos.combo_strategy import ComboStrategy


_SAMPLE_STOOQ_CSV = """Date,Open,High,Low,Close,Volume
2024-01-02,100,101,99,100.5,1200000
2024-01-03,100.5,102,100,101.7,1350000
2024-01-04,101.7,103,101.2,102.4,1100000
2024-01-05,102.4,103.2,101.5,102.1,980000
2024-01-08,102.1,104.1,101.8,103.9,1400000
2024-01-09,103.9,105.0,103.5,104.6,1500000
2024-01-10,104.6,106.2,104.1,105.7,1600000
"""


def test_stooq_symbol_mapping() -> None:
    assert StooqEodProvider.map_symbol("AAPL") == "aapl.us"
    assert StooqEodProvider.map_symbol("spy") == "spy.us"
    assert StooqEodProvider.map_symbol("BRK.B") == "brk-b.us"


def test_stooq_rejects_non_daily_timeframe(tmp_path: Path) -> None:
    provider = StooqEodProvider(cache_dir=tmp_path)
    with pytest.raises(ValueError, match="timeframe '1d'"):
        provider.fetch_ohlcv(symbol="AAPL", timeframe="1h")


def test_stooq_uses_cache_for_same_symbol_and_timeframe(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    provider = StooqEodProvider(cache_dir=tmp_path, ttl_seconds=3600)
    calls: list[str] = []

    def _fake_download(provider_symbol: str) -> str:
        calls.append(provider_symbol)
        return _SAMPLE_STOOQ_CSV

    monkeypatch.setattr(provider, "_download_csv", _fake_download)

    df_first = provider.fetch_ohlcv(symbol="AAPL", timeframe="1d")
    df_second = provider.fetch_ohlcv(symbol="AAPL", timeframe="1d")

    assert not df_first.empty
    assert len(df_second) == len(df_first)
    assert calls == ["aapl.us"]


def test_stooq_smoke_fetch_and_indicator_compute(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    provider = StooqEodProvider(cache_dir=tmp_path, ttl_seconds=3600)
    monkeypatch.setattr(provider, "_download_csv", lambda provider_symbol: _SAMPLE_STOOQ_CSV)

    df = provider.fetch_ohlcv(
        symbol="AAPL",
        timeframe="1d",
        since_str="2024-01-02",
        until_str="2024-01-10",
    )

    assert not df.empty
    assert {"time", "open", "high", "low", "close", "volume"}.issubset(set(df.columns))

    strategy = ComboStrategy(
        indicators=[
            {"type": "ema", "alias": "fast", "params": {"length": 2}},
            {"type": "ema", "alias": "slow", "params": {"length": 3}},
        ],
        entry_logic="fast > slow",
        exit_logic="fast < slow",
        stop_loss=0.02,
    )
    df_with_signals = strategy.generate_signals(df)

    assert "fast" in df_with_signals.columns
    assert "slow" in df_with_signals.columns
    assert "signal" in df_with_signals.columns
