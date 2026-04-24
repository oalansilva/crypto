from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.indicator_score_service import IndicatorScoreService


def _sample_row(index: int) -> dict[str, float | str]:
    close = 100.0 + (index % 17)
    return {
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "ts": datetime.now(timezone.utc).isoformat(),
        "ema_9": close * 1.01,
        "ema_21": close,
        "sma_20": close * 1.005,
        "sma_50": close,
        "rsi_14": 35.0 + (index % 30),
        "macd_histogram": -1.0 + ((index % 200) / 100.0),
        "bb_upper_20_2": close * 1.04,
        "bb_middle_20_2": close,
        "bb_lower_20_2": close * 0.96,
        "atr_14": close * 0.018,
        "stoch_k_14_3_3": 25.0 + (index % 55),
        "ichimoku_tenkan_9": close * 1.006,
        "ichimoku_kijun_26": close,
        "pivot_point": close,
        "support_1": close * 0.98,
        "resistance_1": close * 1.02,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark indicator score normalization.")
    parser.add_argument("--rows", type=int, default=10000)
    args = parser.parse_args()

    rows = [_sample_row(index) for index in range(args.rows)]
    service = IndicatorScoreService()

    started = time.perf_counter()
    scored = service.score_rows(rows)
    elapsed = time.perf_counter() - started
    score_count = sum(len(row["scores"]) for row in scored)
    rows_per_second = args.rows / elapsed if elapsed else float("inf")

    print(f"ruleset_version={service.version}")
    print(f"rows={args.rows}")
    print(f"scores={score_count}")
    print(f"elapsed_ms={elapsed * 1000:.3f}")
    print(f"rows_per_second={rows_per_second:.2f}")


if __name__ == "__main__":
    main()
