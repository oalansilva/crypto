"""Comparação com referência gravada e coluna extra do Decidir (#1123).

1. ``benchmark_comparisons``: uma linha por comparação gravada (dono ``result``, ``favorite`` ou
   ``discovery_result``), com o contrato inteiro em JSON.
2. ``discovery_reference_columns``: a escolha da coluna extra por varredura e por usuário, no máximo
   uma ativa por ``(sweep_id, actor)``.
3. ``favorite_strategies.benchmark_comparison_id`` (nula), com FK para ``benchmark_comparisons.id``
   ``ON DELETE SET NULL`` (como no modelo). Sem backfill: o favorito existente começa sem
   comparação e ganha a do próprio ativo no próximo refresh.

Idempotente: o app também cria as tabelas (``create_all``), a coluna e a FK
(``BENCHMARK_SCHEMA_SQL``); a FK só é criada quando ainda não existe uma do ponteiro para a tabela.

Revision ID: 20261028_0001
Revises: 20261026_0001
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20261028_0001"
down_revision = "20261026_0001"
branch_labels = None
depends_on = None

COMPARISONS = "benchmark_comparisons"
COLUMNS = "discovery_reference_columns"
FAVORITES = "favorite_strategies"
POINTER = "benchmark_comparison_id"
POINTER_FK = "fk_favorite_strategies_benchmark_comparison"


def _inspector():
    return sa.inspect(op.get_bind())


def _has_table(name: str) -> bool:
    return _inspector().has_table(name)


def _has_column(table: str, column: str) -> bool:
    if not _has_table(table):
        return False
    return column in {c["name"] for c in _inspector().get_columns(table)}


def _has_index(table: str, index: str) -> bool:
    if not _has_table(table):
        return False
    return index in {i["name"] for i in _inspector().get_indexes(table)}


def _has_pointer_fk() -> bool:
    if not _has_table(FAVORITES):
        return False
    return any(
        fk.get("referred_table") == COMPARISONS and fk.get("constrained_columns") == [POINTER]
        for fk in _inspector().get_foreign_keys(FAVORITES)
    )


def upgrade():
    if not _has_table(COMPARISONS):
        op.create_table(
            COMPARISONS,
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("user_id", sa.String()),
            sa.Column("favorite_id", sa.Integer()),
            sa.Column("owner_kind", sa.String(24), nullable=False),
            sa.Column("result_id", sa.String(64)),
            sa.Column("column_id", sa.String(36)),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("status", sa.String(16), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=False),
        )
    for name, cols in (
        ("ix_benchmark_comparisons_user", ["user_id"]),
        ("ix_benchmark_comparisons_favorite", ["favorite_id"]),
        ("ix_benchmark_comparisons_column", ["column_id", "result_id"]),
        ("ix_benchmark_comparisons_created", ["created_at"]),
    ):
        if not _has_index(COMPARISONS, name):
            op.create_index(name, COMPARISONS, cols)

    if not _has_table(COLUMNS):
        op.create_table(
            COLUMNS,
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("sweep_id", sa.String(64), nullable=False),
            sa.Column("actor", sa.String(128), nullable=False),
            sa.Column("reference", sa.JSON(), nullable=False),
            sa.Column("reference_snapshot_id", sa.String(40)),
            sa.Column("status", sa.String(16), nullable=False),
            sa.Column("done", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("total", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("error", sa.Text()),
            sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("completed_at", sa.DateTime()),
            sa.Column("deactivated_at", sa.DateTime()),
        )
    if not _has_index(COLUMNS, "ix_discovery_reference_columns_sweep_actor"):
        op.create_index(
            "ix_discovery_reference_columns_sweep_actor", COLUMNS, ["sweep_id", "actor"]
        )
    if not _has_index(COLUMNS, "uq_discovery_reference_columns_active"):
        op.create_index(
            "uq_discovery_reference_columns_active",
            COLUMNS,
            ["sweep_id", "actor"],
            unique=True,
            postgresql_where=sa.text("active"),
        )

    if _has_table(FAVORITES) and not _has_column(FAVORITES, "benchmark_comparison_id"):
        op.add_column(FAVORITES, sa.Column("benchmark_comparison_id", sa.String(36)))
    if _has_table(FAVORITES) and not _has_index(
        FAVORITES, "ix_favorite_strategies_benchmark_comparison"
    ):
        op.create_index(
            "ix_favorite_strategies_benchmark_comparison", FAVORITES, ["benchmark_comparison_id"]
        )
    if _has_table(FAVORITES) and _has_column(FAVORITES, POINTER) and not _has_pointer_fk():
        # Ponteiro órfão (comparação que não existe) vira nulo antes da FK, como o SET NULL faria.
        op.execute(
            sa.text(
                f"UPDATE {FAVORITES} SET {POINTER} = NULL WHERE {POINTER} IS NOT NULL "
                f"AND NOT EXISTS (SELECT 1 FROM {COMPARISONS} b WHERE b.id = {FAVORITES}.{POINTER})"
            )
        )
        op.create_foreign_key(
            POINTER_FK, FAVORITES, COMPARISONS, [POINTER], ["id"], ondelete="SET NULL"
        )


def downgrade():
    # As comparações gravadas são o que a tela e as planilhas mostram: o rollback do código
    # ignora a coluna, a FK e as tabelas, sem apagá-las (design, Migration Plan 3). A FK fica: com
    # ``ON DELETE SET NULL`` ela não impede apagar comparação e o código antigo não lê o ponteiro.
    raise RuntimeError("Conservative rollback retains recorded benchmark comparisons")
