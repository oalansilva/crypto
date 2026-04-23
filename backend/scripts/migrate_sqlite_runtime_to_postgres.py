"""Legacy SQLite migration entrypoint (deprecated).

SQLite runtime migrations are no longer supported in this repository.
Use PostgreSQL-native migration/pipeline tooling only.
"""

from __future__ import annotations


def main() -> None:
    raise SystemExit(
        "SQLite source migrations are no longer supported. "
        "Use PostgreSQL-native migration tooling instead."
    )


if __name__ == "__main__":
    main()
