"""Une as duas heads do develop: ``20261027_0001`` (#1122) e ``20261028_0001`` (#1123).

As duas migrações saíram do mesmo pai (``20261026_0001``) em PRs paralelos, e o
``alembic upgrade head`` passou a recusar a cadeia ("Multiple head revisions are present").
Esta revisão só junta as duas pontas: não muda o schema.

Revision ID: 20261028_0002
Revises: 20261027_0001, 20261028_0001
"""

from __future__ import annotations

revision = "20261028_0002"
down_revision = ("20261027_0001", "20261028_0001")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
