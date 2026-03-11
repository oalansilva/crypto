#!/usr/bin/env python3
"""Generate Postgres DDL for the workflow schema.

Why:
- In early VPS setup we may not have the app wired with secrets yet.
- This script lets us generate the exact DDL from SQLAlchemy models and apply
  it with `psql` as an admin (optionally using `SET ROLE workflow_app`).

Usage:
  python backend/scripts/generate_workflow_schema_sql.py > /tmp/workflow_schema.sql

Then apply (example):
  sudo -u postgres psql -d workflow -v ON_ERROR_STOP=1 -f /tmp/workflow_schema.sql

If you want the objects owned by workflow_app:
  sudo -u postgres psql -d workflow -v ON_ERROR_STOP=1 -c "SET ROLE workflow_app;" -f /tmp/workflow_schema.sql
"""

from __future__ import annotations

import os
import sys

from sqlalchemy import create_mock_engine

# Ensure `backend/` is on sys.path so `import app.*` works when invoked from repo root.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.workflow_database import WorkflowBase  # noqa: E402

# Import models so metadata is populated.
import app.workflow_models  # noqa: F401,E402


def main() -> int:
    stmts: list[str] = []

    def dump(sql, *multiparams, **params):  # noqa: ANN001
        compiled = sql.compile(dialect=engine.dialect)
        stmts.append(str(compiled).rstrip(";"))

    engine = create_mock_engine("postgresql+psycopg2://", dump)
    WorkflowBase.metadata.create_all(engine)

    # SQLAlchemy already emits CREATE TYPE/CREATE TABLE/CREATE INDEX in order.
    out = ";\n\n".join(stmts).strip() + ";\n"
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
