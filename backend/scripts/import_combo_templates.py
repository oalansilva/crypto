"""Legacy combo-template import utility deprecated.

SQLite-backed template imports are no longer supported.
Use PostgreSQL-native data import procedures for combo templates.
"""

from __future__ import annotations


def main() -> None:
    raise SystemExit(
        "Template import via SQLite is deprecated; migrate template data through PostgreSQL."
    )


if __name__ == "__main__":
    main()
