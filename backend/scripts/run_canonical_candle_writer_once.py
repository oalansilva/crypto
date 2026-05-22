from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.ohlcv_storage import run_ohlcv_ingestion_once


def main() -> int:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    runs = run_ohlcv_ingestion_once()
    print(f"canonical_candle_writer_runs={runs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
