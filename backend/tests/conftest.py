from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ["ARBITRAGE_MONITOR_ENABLED"] = "0"
os.environ["WORKFLOW_DB_ENABLED"] = "1"
os.environ["WORKFLOW_ALLOW_SHARED_PROJECT_DB"] = "1"
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:5432/crypto_app_test",
)
os.environ.setdefault(
    "WORKFLOW_DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:5432/crypto_workflow_test",
)
os.environ.setdefault("CRYPTO_DATABASE_URL", os.environ["DATABASE_URL"])
os.environ.setdefault("CRYPTO_WORKFLOW_DATABASE_URL", os.environ["WORKFLOW_DATABASE_URL"])

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

BACKEND_TESTS_ROOT = Path(__file__).resolve().parent
if str(BACKEND_TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_TESTS_ROOT))

from database_guard import assert_safe_test_database_url

for _database_variable in (
    "DATABASE_URL",
    "WORKFLOW_DATABASE_URL",
    "CRYPTO_DATABASE_URL",
    "CRYPTO_WORKFLOW_DATABASE_URL",
):
    _database_url = os.getenv(_database_variable)
    if _database_url:
        assert_safe_test_database_url(
            _database_url,
            variable_name=_database_variable,
        )

from app.config import get_settings

get_settings.cache_clear()
