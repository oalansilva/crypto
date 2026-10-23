"""Histórico de candles com identidade de série e amostras de execução (#1118).

Cria ``market_series``, a hypertable nova de candles (``market_ohlcv_v2``, chave
``(series_id, candle_time)``), ``market_series_fetch``, ``market_series_coverage``,
``execution_data_snapshots`` e o balde de fichas, mais as colunas
``favorite_strategies.snapshot_id``, ``auto_backtest_runs.snapshot_id`` e a
proveniência de ``discovery_results``.

A revisão só tira a política de retenção de 2 anos de ``market_ohlcv`` (passo 3 do plano
de migração: nada pode apagar candles por idade antes da cópia). Não toca nos candles: a
cópia, a conferência e a troca de nomes são do script
``backend/scripts/market_history/migrate_market_ohlcv.py``, que segue
``docs/prod-migration-runbook.md``. Idempotente: o app também cria estas tabelas na subida.
O downgrade não recoloca a retenção (ela apagaria histórico).
"""

from alembic import op

from app.services.market_history import schema

revision = "20261023_0001"
down_revision = "20261020_0001"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    # Retenção primeiro: sem a extensão Timescale (DEV hoje) é um no-op.
    schema.remove_retention_policy(conn, schema.LIVE_OHLCV_TABLE)
    schema.execute_all(conn, schema.side_table_statements())
    if not schema.ohlcv_table_is_new_shape(conn):
        schema.execute_all(conn, schema.ohlcv_table_sql(schema.STAGING_OHLCV_TABLE))
        # Hypertable + compressão aos 30 dias quando a extensão existe; nunca retenção.
        schema.configure_timescale(conn, schema.STAGING_OHLCV_TABLE)
    schema.execute_all(conn, schema.ADD_COLUMNS_SQL)


def downgrade():
    conn = op.get_bind()
    if schema.ohlcv_table_is_new_shape(conn):
        raise RuntimeError(
            "market_ohlcv já é a tabela nova (com series_id): rode a reversão do script "
            "migrate_market_ohlcv.py (--rollback) antes de reverter esta revisão."
        )
    for statement in (
        "ALTER TABLE IF EXISTS discovery_results DROP COLUMN IF EXISTS snapshot_id",
        "ALTER TABLE IF EXISTS discovery_results DROP COLUMN IF EXISTS data_version",
        "ALTER TABLE IF EXISTS discovery_results DROP COLUMN IF EXISTS period_covered",
        "ALTER TABLE IF EXISTS discovery_results DROP COLUMN IF EXISTS period_requested",
        "ALTER TABLE IF EXISTS discovery_results DROP COLUMN IF EXISTS timeframe_origin",
        "ALTER TABLE IF EXISTS discovery_results DROP COLUMN IF EXISTS adjustment",
        "ALTER TABLE IF EXISTS discovery_results DROP COLUMN IF EXISTS session",
        "ALTER TABLE IF EXISTS discovery_results DROP COLUMN IF EXISTS asset_class",
        "ALTER TABLE IF EXISTS discovery_results DROP COLUMN IF EXISTS data_source",
        "ALTER TABLE IF EXISTS auto_backtest_runs DROP COLUMN IF EXISTS snapshot_id",
        "ALTER TABLE IF EXISTS favorite_strategies DROP COLUMN IF EXISTS snapshot_id",
        "DROP TABLE IF EXISTS market_rate_limit",
        "DROP TABLE IF EXISTS execution_data_snapshots",
        "DROP TABLE IF EXISTS market_series_stage",
        "DROP TABLE IF EXISTS market_series_coverage",
        "DROP TABLE IF EXISTS market_series_fetch",
        f"DROP TABLE IF EXISTS {schema.STAGING_OHLCV_TABLE}",
        "DROP TABLE IF EXISTS market_series",
    ):
        op.execute(statement)
