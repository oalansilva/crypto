from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("ARBITRAGE_MONITOR_ENABLED", "0")

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

BACKEND_TESTS_ROOT = Path(__file__).resolve().parent
if str(BACKEND_TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_TESTS_ROOT))
