from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ["ARBITRAGE_MONITOR_ENABLED"] = "0"
os.environ["WORKFLOW_DB_ENABLED"] = "1"
os.environ["WORKFLOW_ALLOW_SHARED_PROJECT_DB"] = "1"
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
os.environ["WORKFLOW_DATABASE_URL"] = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

BACKEND_TESTS_ROOT = Path(__file__).resolve().parent
if str(BACKEND_TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_TESTS_ROOT))

from app.config import get_settings

get_settings.cache_clear()
