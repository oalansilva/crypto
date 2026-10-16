"""Freeze the recovered original window and record honest source provenance."""

from pathlib import Path
import hashlib
import json
import pandas as pd

SOURCE = Path("/srv/apps/dev/criptofarol/source/data/storage/binance/BTC_USDT_15m.parquet")
TARGET = Path(
    "/srv/apps/dev/criptofarol/crypto-worktrees/card-1093-discovery-memory/backend/tests/fixtures/discovery_memory"
)


def main():
    raw = SOURCE.read_bytes()
    frame = pd.read_parquet(SOURCE)
    stamps = pd.to_datetime(frame.timestamp_utc, utc=True)
    selected = frame.loc[
        (stamps >= pd.Timestamp("2025-10-06", tz="UTC"))
        & (stamps <= pd.Timestamp("2026-10-06", tz="UTC"))
    ].copy()
    assert len(selected) == 35041, "Recovered data must match the journal's listing length"
    path = TARGET / "original_candles.parquet"
    selected.to_parquet(path, index=False)
    manifest = {
        "symbol": "BTC/USDT",
        "timeframe": "15m",
        "direction": "long",
        "start_date": "2025-10-06",
        "end_date": "2026-10-06",
        "rows": len(selected),
        "train_rows": 24528,
        "holdout_rows": 10513,
        "burnin": 250,
        "r1_trials": 492480,
        "source": str(SOURCE),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_mtime_ns": SOURCE.stat().st_mtime_ns,
        "parquet_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "candle_values_sha256": hashlib.sha256(
            pd.util.hash_pandas_object(selected, index=False).to_numpy().tobytes()
        ).hexdigest(),
        "first": str(selected.timestamp_utc.min()),
        "last": str(selected.timestamp_utc.max()),
        "provenance": "Recovered 2026-10-13 from DEV cache written 2026-10-12. Journal identifies the same immutable historical window and row count; no historical byte digest was recorded, so historical byte identity is unproven.",
    }
    (TARGET / "original_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
