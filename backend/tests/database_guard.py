from __future__ import annotations

import os

from sqlalchemy.engine import make_url


def assert_safe_test_database_url(database_url: str, *, variable_name: str) -> None:
    """Fail before collection when pytest targets a persistent runtime database."""

    if not str(database_url or "").strip():
        raise RuntimeError(f"{variable_name} is required for PostgreSQL tests")

    try:
        url = make_url(database_url)
    except Exception as exc:
        raise RuntimeError(f"{variable_name} is not a valid database URL") from exc

    backend = url.get_backend_name()
    if backend != "postgresql":
        raise RuntimeError(
            f"{variable_name} must use PostgreSQL for tests; refusing {backend or '<unknown>'}"
        )

    database_name = (url.database or "").lower()
    explicitly_test_db = database_name.startswith("test_") or database_name.endswith(
        ("_test", "_tests", "_testing")
    )
    disposable_github_db = (
        os.getenv("GITHUB_ACTIONS", "").strip().lower() == "true" and database_name == "postgres"
    )
    if not explicitly_test_db and not disposable_github_db:
        raise RuntimeError(
            "Refusing pytest against a non-test database "
            f"({database_name or '<empty>'}) from {variable_name}. "
            "Use a dedicated database whose name starts with test_ or ends with "
            "_test/_tests/_testing."
        )
