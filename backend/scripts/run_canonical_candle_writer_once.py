from __future__ import annotations

import logging
import os

from app.services.ohlcv_storage import run_ohlcv_ingestion_once


def main() -> int:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    runs = run_ohlcv_ingestion_once()
    print(f"canonical_candle_writer_runs={runs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
