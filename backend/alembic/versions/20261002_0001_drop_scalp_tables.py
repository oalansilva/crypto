"""Drop the directional scalper tables (#1075).

Revision ID: 20261002_0001
Revises: 20260927_0001
Create Date: 2026-10-02 00:00:00

Historical create revisions stay in the tree. This revision removes the
tables and their rows from databases that already applied those creates.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20261002_0001"
down_revision = "20260927_0001"
branch_labels = None
depends_on = None

_TABLES = (
    "scalp_fills",
    "scalp_jev_diagnoses",
    "scalp_confidence_versions",
    "scalp_calibration_state",
    "scalp_user_states",
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    present = set(inspector.get_table_names())
    for name in _TABLES:
        if name in present:
            op.drop_table(name)


def downgrade() -> None:
    # A dropped database is restored from backup. The historical create
    # revisions remain and still build these tables on an empty database.
    pass
