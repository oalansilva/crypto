"""Leads da landing salvos no passo 1 (#1160, D1).

Cria ``landing_leads``: um lead por e-mail normalizado (único), com nome, WhatsApp, nível,
dificuldade, origem, atribuição sanitizada (JSON), passo alcançado e criado/atualizado em.
O passo 1 cria ou atualiza; o passo 2 só enriquece o mesmo lead.

Idempotente: o app também cria a tabela (``create_all``); o upgrade só cria o que falta.

Downgrade: apaga a tabela (os leads salvos nela se perdem; a auditoria do #689 em
``beta_access_audit_logs`` fica).

Revision ID: 20261030_0001
Revises: 20261028_0002
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20261030_0001"
down_revision = "20261028_0002"
branch_labels = None
depends_on = None

TABLE = "landing_leads"
CREATED_INDEX = "ix_landing_leads_created_at"
ID_INDEX = "ix_landing_leads_id"


def _inspector():
    return sa.inspect(op.get_bind())


def _has_table(name: str) -> bool:
    return _inspector().has_table(name)


def _has_index(table: str, index: str) -> bool:
    if not _has_table(table):
        return False
    return index in {i["name"] for i in _inspector().get_indexes(table)}


def upgrade() -> None:
    if not _has_table(TABLE):
        op.create_table(
            TABLE,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(length=320), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=True),
            sa.Column("whatsapp", sa.String(length=40), nullable=True),
            sa.Column("profile", sa.String(length=80), nullable=True),
            sa.Column("pain", sa.String(length=500), nullable=True),
            sa.Column("origin", sa.String(length=80), nullable=True),
            sa.Column("attribution_json", sa.Text(), nullable=True),
            sa.Column("step_reached", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint("email", name="uq_landing_leads_email"),
        )
    if not _has_index(TABLE, ID_INDEX):
        op.create_index(ID_INDEX, TABLE, ["id"])
    if not _has_index(TABLE, CREATED_INDEX):
        op.create_index(CREATED_INDEX, TABLE, ["created_at"])


def downgrade() -> None:
    if _has_table(TABLE):
        op.drop_table(TABLE)
