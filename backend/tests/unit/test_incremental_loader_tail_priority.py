from __future__ import annotations

import pandas as pd

from src.data.incremental_loader import IncrementalLoader


def test_incremental_loader_refreshes_tail_before_missing_head(tmp_path):
    loader = IncrementalLoader(cache_dir=tmp_path)
    parquet_path = loader._get_parquet_path("A2Z/USDT", "1d")

    stale_day = pd.Timestamp("2026-04-01T00:00:00Z")
    cached = pd.DataFrame(
        {
            "timestamp": [int(stale_day.timestamp() * 1000)],
            "timestamp_utc": [stale_day],
            "open": [1.0],
            "high": [1.1],
            "low": [0.9],
            "close": [1.0],
            "volume": [10.0],
        }
    )
    loader._atomic_to_parquet(cached, parquet_path)

    calls: list[dict[str, int]] = []

    def fake_download_loop(symbol, timeframe, fetch_since_ts, until_ts_download, limit):
        calls.append(
            {
                "fetch_since_ts": fetch_since_ts,
                "until_ts_download": until_ts_download,
                "limit": limit,
            }
        )
        fresh_day = pd.Timestamp("2026-05-19T00:00:00Z")
        return pd.DataFrame(
            {
                "timestamp": [int(fresh_day.timestamp() * 1000)],
                "timestamp_utc": [fresh_day],
                "open": [1.2],
                "high": [1.3],
                "low": [1.1],
                "close": [1.25],
                "volume": [20.0],
            }
        )

    loader._download_loop = fake_download_loop  # type: ignore[method-assign]

    output = loader.fetch_data(
        "A2Z/USDT",
        "1d",
        "2017-01-01",
        "2026-05-19",
        limit=1000,
    )

    assert calls
    expected_tail_fetch = int((stale_day - pd.Timedelta(days=1)).timestamp() * 1000) + 1
    assert calls[0]["fetch_since_ts"] == expected_tail_fetch
    assert int(output.index.max().timestamp() * 1000) == int(
        pd.Timestamp("2026-05-19T00:00:00Z").timestamp() * 1000
    )
