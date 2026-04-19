"""Create baseline runtime PostgreSQL schema.

Revision ID: 20260419_0001
Revises:
Create Date: 2026-04-19 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260419_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auto_backtest_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("strategy", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("stage_1_result", sa.Text(), nullable=True),
        sa.Column("stage_2_result", sa.Text(), nullable=True),
        sa.Column("stage_3_result", sa.Text(), nullable=True),
        sa.Column("favorite_id", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auto_backtest_runs_run_id", "auto_backtest_runs", ["run_id"], unique=True)

    op.create_table(
        "backtest_results",
        sa.Column("run_id", sa.String(), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.Column("metrics_summary", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("run_id"),
    )

    op.create_table(
        "backtest_runs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("mode", sa.Text(), nullable=False),
        sa.Column("exchange", sa.Text(), nullable=False),
        sa.Column("symbol", sa.Text(), nullable=False),
        sa.Column("timeframe", sa.Text(), nullable=False),
        sa.Column("since", sa.String(), nullable=True),
        sa.Column("until", sa.String(), nullable=True),
        sa.Column("full_period", sa.Boolean(), nullable=True),
        sa.Column("strategies", sa.Text(), nullable=False),
        sa.Column("params", sa.Text(), nullable=True),
        sa.Column("fee", sa.Float(), nullable=True),
        sa.Column("slippage", sa.Float(), nullable=True),
        sa.Column("cash", sa.Float(), nullable=True),
        sa.Column("stop_pct", sa.Text(), nullable=True),
        sa.Column("take_pct", sa.Text(), nullable=True),
        sa.Column("fill_mode", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "combo_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("is_prebuilt", sa.Boolean(), nullable=True),
        sa.Column("is_example", sa.Boolean(), nullable=True),
        sa.Column("is_readonly", sa.Boolean(), nullable=True),
        sa.Column("template_data", sa.Text(), nullable=False),
        sa.Column("optimization_schema", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_combo_templates_name", "combo_templates", ["name"], unique=True)

    op.create_table(
        "favorite_strategies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("timeframe", sa.String(), nullable=False),
        sa.Column("strategy_name", sa.String(), nullable=False),
        sa.Column("parameters", sa.Text(), nullable=False),
        sa.Column("metrics", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("tier", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.String(), nullable=True),
        sa.Column("end_date", sa.String(), nullable=True),
        sa.Column("period_type", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_favorite_strategies_user_id", "favorite_strategies", ["user_id"], unique=False
    )

    op.create_table(
        "monitor_preferences",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("in_portfolio", sa.Boolean(), nullable=False),
        sa.Column("card_mode", sa.String(), nullable=False),
        sa.Column("price_timeframe", sa.String(), nullable=False),
        sa.Column("theme", sa.String(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("user_id", "symbol"),
    )
    op.create_index(
        "ix_monitor_preferences_symbol", "monitor_preferences", ["symbol"], unique=False
    )

    op.create_table(
        "onchain_signals",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("chain", sa.String(), nullable=False),
        sa.Column("tvl", sa.Float(), nullable=True),
        sa.Column("active_addresses", sa.Float(), nullable=True),
        sa.Column("exchange_flow", sa.Float(), nullable=True),
        sa.Column("github_commits", sa.Integer(), nullable=True),
        sa.Column("github_stars", sa.Integer(), nullable=True),
        sa.Column("github_prs", sa.Integer(), nullable=True),
        sa.Column("github_issues", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_onchain_signals_chain", "onchain_signals", ["chain"], unique=False)
    op.create_index(
        "ix_onchain_signals_created_at", "onchain_signals", ["created_at"], unique=False
    )
    op.create_index(
        "ix_onchain_signals_token_chain", "onchain_signals", ["token", "chain"], unique=False
    )
    op.create_index("ix_onchain_signals_token", "onchain_signals", ["token"], unique=False)

    op.create_table(
        "onchain_signals_history",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("chain", sa.String(), nullable=False),
        sa.Column("signal_type", sa.String(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("breakdown", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("tvl", sa.Float(), nullable=True),
        sa.Column("active_addresses", sa.Float(), nullable=True),
        sa.Column("exchange_flow", sa.Float(), nullable=True),
        sa.Column("github_commits", sa.Integer(), nullable=True),
        sa.Column("github_stars", sa.Integer(), nullable=True),
        sa.Column("github_prs", sa.Integer(), nullable=True),
        sa.Column("github_issues", sa.Integer(), nullable=True),
        sa.Column("price_at_signal", sa.Float(), nullable=True),
        sa.Column("price_after_1h", sa.Float(), nullable=True),
        sa.Column("price_after_4h", sa.Float(), nullable=True),
        sa.Column("price_after_24h", sa.Float(), nullable=True),
        sa.Column("outcome_1h", sa.String(), nullable=True),
        sa.Column("outcome_4h", sa.String(), nullable=True),
        sa.Column("outcome_24h", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_onchain_signals_history_archived",
        "onchain_signals_history",
        ["archived"],
        unique=False,
    )
    op.create_index(
        "ix_onchain_signals_history_chain", "onchain_signals_history", ["chain"], unique=False
    )
    op.create_index(
        "ix_onchain_signals_history_created_at",
        "onchain_signals_history",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_onchain_signals_history_signal_type",
        "onchain_signals_history",
        ["signal_type"],
        unique=False,
    )
    op.create_index(
        "ix_onchain_signals_history_status_created",
        "onchain_signals_history",
        ["status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_onchain_signals_history_status",
        "onchain_signals_history",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_onchain_signals_history_token_chain",
        "onchain_signals_history",
        ["token", "chain"],
        unique=False,
    )
    op.create_index(
        "ix_onchain_signals_history_token", "onchain_signals_history", ["token"], unique=False
    )

    op.create_table(
        "optimization_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.String(), nullable=False),
        sa.Column("result_index", sa.Integer(), nullable=False),
        sa.Column("params_json", sa.Text(), nullable=False),
        sa.Column("metrics_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id", "result_index", name="uq_optimization_results_job_idx"),
    )
    op.create_index(
        "idx_optimization_results_job_created",
        "optimization_results",
        ["job_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_optimization_results_job_id", "optimization_results", ["job_id"], unique=False
    )

    op.create_table(
        "portfolio_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=True),
        sa.Column("total_usd", sa.Float(), nullable=True),
        sa.Column("btc_value", sa.Float(), nullable=True),
        sa.Column("usdt_value", sa.Float(), nullable=True),
        sa.Column("eth_value", sa.Float(), nullable=True),
        sa.Column("other_usd", sa.Float(), nullable=True),
        sa.Column("pnl_today_pct", sa.Float(), nullable=True),
        sa.Column("drawdown_30d_pct", sa.Float(), nullable=True),
        sa.Column("drawdown_peak_date", sa.String(), nullable=True),
        sa.Column("btc_change_24h_pct", sa.Float(), nullable=True),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_portfolio_snapshots_user_id", "portfolio_snapshots", ["user_id"], unique=False
    )

    op.create_table(
        "signal_history",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("asset", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("target_price", sa.Float(), nullable=False),
        sa.Column("stop_loss", sa.Float(), nullable=False),
        sa.Column("indicators", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("risk_profile", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("entry_price", sa.Float(), nullable=True),
        sa.Column("exit_price", sa.Float(), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("pnl", sa.Float(), nullable=True),
        sa.Column("trigger_price", sa.Float(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived", sa.String(), nullable=True),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_signal_history_archived", "signal_history", ["archived"], unique=False)
    op.create_index("ix_signal_history_asset", "signal_history", ["asset"], unique=False)
    op.create_index(
        "ix_signal_history_asset_created", "signal_history", ["asset", "created_at"], unique=False
    )
    op.create_index("ix_signal_history_created_at", "signal_history", ["created_at"], unique=False)
    op.create_index("ix_signal_history_status", "signal_history", ["status"], unique=False)
    op.create_index(
        "ix_signal_history_status_created",
        "signal_history",
        ["status", "created_at"],
        unique=False,
    )

    op.create_table(
        "system_preferences",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("updated_by_user_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("key"),
    )

    op.create_table(
        "user_exchange_credentials",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("api_key", sa.String(), nullable=False),
        sa.Column("api_secret", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("user_id", "provider"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_table("user_exchange_credentials")
    op.drop_table("system_preferences")

    op.drop_index("ix_signal_history_status_created", table_name="signal_history")
    op.drop_index("ix_signal_history_status", table_name="signal_history")
    op.drop_index("ix_signal_history_created_at", table_name="signal_history")
    op.drop_index("ix_signal_history_asset_created", table_name="signal_history")
    op.drop_index("ix_signal_history_asset", table_name="signal_history")
    op.drop_index("ix_signal_history_archived", table_name="signal_history")
    op.drop_table("signal_history")

    op.drop_index("ix_portfolio_snapshots_user_id", table_name="portfolio_snapshots")
    op.drop_table("portfolio_snapshots")

    op.drop_index("ix_optimization_results_job_id", table_name="optimization_results")
    op.drop_index("idx_optimization_results_job_created", table_name="optimization_results")
    op.drop_table("optimization_results")

    op.drop_index("ix_onchain_signals_history_token", table_name="onchain_signals_history")
    op.drop_index("ix_onchain_signals_history_token_chain", table_name="onchain_signals_history")
    op.drop_index("ix_onchain_signals_history_status", table_name="onchain_signals_history")
    op.drop_index("ix_onchain_signals_history_status_created", table_name="onchain_signals_history")
    op.drop_index("ix_onchain_signals_history_signal_type", table_name="onchain_signals_history")
    op.drop_index("ix_onchain_signals_history_created_at", table_name="onchain_signals_history")
    op.drop_index("ix_onchain_signals_history_chain", table_name="onchain_signals_history")
    op.drop_index("ix_onchain_signals_history_archived", table_name="onchain_signals_history")
    op.drop_table("onchain_signals_history")

    op.drop_index("ix_onchain_signals_token", table_name="onchain_signals")
    op.drop_index("ix_onchain_signals_token_chain", table_name="onchain_signals")
    op.drop_index("ix_onchain_signals_created_at", table_name="onchain_signals")
    op.drop_index("ix_onchain_signals_chain", table_name="onchain_signals")
    op.drop_table("onchain_signals")

    op.drop_index("ix_monitor_preferences_symbol", table_name="monitor_preferences")
    op.drop_table("monitor_preferences")

    op.drop_index("ix_favorite_strategies_user_id", table_name="favorite_strategies")
    op.drop_table("favorite_strategies")

    op.drop_index("ix_combo_templates_name", table_name="combo_templates")
    op.drop_table("combo_templates")

    op.drop_table("backtest_runs")
    op.drop_table("backtest_results")

    op.drop_index("ix_auto_backtest_runs_run_id", table_name="auto_backtest_runs")
    op.drop_table("auto_backtest_runs")
