"""Legacy project migration script for PostgreSQL-only operations.

The old SQLite migration paths were removed, so this script now refuses to run
when SQLite sources are provided.
"""

from __future__ import annotations

import argparse
from urllib.parse import urlparse


def _is_postgres_url(value: str) -> bool:
    scheme = urlparse(value or "").scheme.lower()
    return scheme in {"postgresql", "postgresql+psycopg2"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-db-url", required=True, help="PostgreSQL source runtime DB URL")
    parser.add_argument("--workflow-db-url", required=True, help="PostgreSQL workflow DB URL")
    args = parser.parse_args()

    if not _is_postgres_url(args.main_db_url) or not _is_postgres_url(args.workflow_db_url):
        raise SystemExit("Only PostgreSQL URLs are supported for migration inputs.")

    raise SystemExit(
        "Legacy SQLite project migrations were removed. "
        "Run this migration only with PostgreSQL-native backup/restore procedures."
    )


if __name__ == "__main__":
    main()
