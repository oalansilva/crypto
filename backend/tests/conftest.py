from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ["ARBITRAGE_MONITOR_ENABLED"] = "0"
os.environ["ASSET_CATALOG_REFRESH_ENABLED"] = "0"
os.environ["WORKFLOW_DB_ENABLED"] = "1"
os.environ["WORKFLOW_ALLOW_SHARED_PROJECT_DB"] = "1"
os.environ["JWT_SECRET"] = "pytest-jwt-secret-do-not-use-elsewhere"
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/crypto_app_test",
)
os.environ.setdefault(
    "WORKFLOW_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/crypto_workflow_test",
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
            allow_github_disposable=True,
        )

from app.config import get_settings

get_settings.cache_clear()


import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _card_1118_provenance_columns():
    """Bancos de teste persistentes podem ser anteriores ao card #1118: garante as colunas novas.

    ``ALTER TABLE IF EXISTS ... ADD COLUMN IF NOT EXISTS`` é idempotente e não toca tabela ausente
    (CI nasce com banco novo; o ``create_all`` já traz as colunas dos modelos).
    """

    try:
        from sqlalchemy import create_engine

        from app.services.market_history.schema import ADD_COLUMNS_SQL, execute_all

        engine = create_engine(os.environ["DATABASE_URL"])
        try:
            with engine.begin() as connection:
                execute_all(connection, ADD_COLUMNS_SQL)
            # Card #1122: colunas novas de favoritos e alertas em bancos de teste persistentes.
            from sqlalchemy import text

            from app.database import FAVORITE_ALERT_SCHEMA_SQL

            with engine.begin() as connection:
                for statement in FAVORITE_ALERT_SCHEMA_SQL:
                    connection.execute(text(statement))
        finally:
            engine.dispose()
    except Exception:
        pass
    yield
