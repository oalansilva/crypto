# file: backend/app/models.py
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)

# from sqlalchemy.dialects.postgresql import UUID, JSONB  <-- Remove Postgres types
from app.database import Base
from sqlalchemy import TypeDecorator
import uuid
import json
from datetime import datetime


# Compatibility types for SQLite
class JSONType(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        # simple helper to handle NaN/Inf and Numpy types
        def safe_serialize(obj):
            import math
            import numpy as np

            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            if isinstance(obj, (np.floating, np.float64, np.float32)):
                val = float(obj)
                if math.isnan(val) or math.isinf(val):
                    return None
                return val
            if isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return None
                return obj
            if isinstance(obj, dict):
                return {k: safe_serialize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [safe_serialize(v) for v in obj]
            return obj

        try:
            cleaned = safe_serialize(value)
            return json.dumps(cleaned)
        except Exception as e:
            # Fallback for debugging
            print(f"JSON Serialization error: {e}")
            return json.dumps(value, default=str)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        # SQLite might return float/int directly if affinity matches
        if isinstance(value, (dict, list, int, float, bool)):
            return value
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            # Fallback for weird cases or if it's a plain string
            return value


class UUIDType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(value)


# Use conditional types based on DB engine? No, keep it simple for now.
# We'll use these custom types which work on both (String/Text are universal).
# Ideally we'd check dialect but for MVP SQLite local is fine.


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=None)  # handled by app or server_default
    status = Column(Text, nullable=False)
    mode = Column(Text, nullable=False)

    exchange = Column(Text, nullable=False)
    symbol = Column(Text, nullable=False)
    timeframe = Column(Text, nullable=False)
    since = Column(String, nullable=True)  # Store ISO string in simple DBs
    until = Column(String)
    full_period = Column(Boolean, default=False)

    strategies = Column(JSONType, nullable=False)
    params = Column(JSONType)

    fee = Column(Float, default=0.001)
    slippage = Column(Float, default=0.0005)
    cash = Column(Float, default=10000)
    stop_pct = Column(JSONType)
    take_pct = Column(JSONType)
    fill_mode = Column(Text, default="close")

    error_message = Column(Text)


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    run_id = Column(UUIDType, primary_key=True)
    result_json = Column(JSONType, nullable=False)
    metrics_summary = Column(JSONType)
    updated_at = Column(DateTime)


class FavoriteStrategy(Base):
    __tablename__ = "favorite_strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)
    name = Column(String, nullable=False)

    # Context
    symbol = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    strategy_name = Column(String, nullable=False)

    # Configuration
    parameters = Column(JSONType, nullable=False)

    # Cached Metrics
    metrics = Column(JSONType, nullable=True)
    auto_refresh_status = Column(String, nullable=True)
    auto_refresh_error = Column(String, nullable=True)
    auto_refresh_started_at = Column(DateTime, nullable=True)
    auto_refresh_completed_at = Column(DateTime, nullable=True)
    auto_refresh_run_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)

    # Tier system - para categorizar estratégias (1=Core obrigatório, 2=Bons complementares, 3=Outros)
    tier = Column(Integer, nullable=True)
    notify_telegram = Column(Boolean, nullable=False, default=True)

    # Período do backtest (6m / 2y / todo). Chave de unicidade junto com strategy_name, symbol, timeframe.
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    period_type = Column(
        String, nullable=True
    )  # '6m' | '2y' | 'all'; usado no skip (evita drift de datas)


class AutoBacktestRun(Base):
    """Model for Auto Backtest execution history"""

    __tablename__ = "auto_backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True, nullable=False)
    symbol = Column(String, nullable=False)
    strategy = Column(String, nullable=False)
    status = Column(String, default="PENDING", nullable=False)

    # Stage results stored as JSON
    stage_1_result = Column(JSONType, nullable=True)
    stage_2_result = Column(JSONType, nullable=True)
    stage_3_result = Column(JSONType, nullable=True)

    favorite_id = Column(Integer, nullable=True)
    error_message = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class ComboTemplate(Base):
    __tablename__ = "combo_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    display_name = Column(String, nullable=True)

    # Flags
    is_prebuilt = Column(Boolean, default=False)
    is_example = Column(Boolean, default=False)
    is_readonly = Column(Boolean, default=False)

    # Data (JSON)
    template_data = Column(JSONType, nullable=False)
    optimization_schema = Column(JSONType, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MonitorPreference(Base):
    __tablename__ = "monitor_preferences"

    user_id = Column(String, primary_key=True)
    symbol = Column(String, primary_key=True, index=True)
    in_portfolio = Column(Boolean, nullable=False, default=False)
    card_mode = Column(String, nullable=False, default="price")
    price_timeframe = Column(String, nullable=False, default="1d")
    # Monitor-only theme preference (defaults to dark-green).
    theme = Column(String, nullable=False, default="dark-green")
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)


class MonitorStrategyPreference(Base):
    __tablename__ = "monitor_strategy_preferences"

    user_id = Column(String, primary_key=True)
    favorite_id = Column(Integer, primary_key=True)
    liked = Column(Boolean, nullable=False, default=True)
    tier = Column(Integer, nullable=True)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("ix_monitor_strategy_preferences_user_liked", "user_id", "liked"),)


class User(Base):
    __tablename__ = "users"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="active", nullable=False)
    suspended_until = Column(DateTime, nullable=True, default=None)
    suspension_reason = Column(Text, nullable=True)
    is_banned = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    must_change_password = Column(Boolean, default=False, nullable=False)
    temporary_password_expires_at = Column(DateTime, nullable=True)
    temporary_password_used_at = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    access_invitation_source = Column(String, nullable=True)
    access_invitation_created_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True, default=None)
    telegram_chat_id = Column(String, nullable=True, index=True)
    telegram_username = Column(String, nullable=True)
    telegram_alerts_enabled = Column(Boolean, nullable=False, default=False)
    telegram_link_token = Column(String, nullable=True, index=True)
    telegram_link_expires_at = Column(DateTime, nullable=True)
    telegram_linked_at = Column(DateTime, nullable=True)
    telegram_username_mismatch = Column(Boolean, nullable=False, default=False)


class BetaAccessAuditLog(Base):
    __tablename__ = "beta_access_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    email = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    source = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False, index=True)
    result = Column(String, nullable=False, index=True)
    metadata_json = Column(JSONType, nullable=True)

    __table_args__ = (
        Index("ix_beta_access_audit_logs_created_at", "created_at"),
        Index("ix_beta_access_audit_logs_email_created", "email", "created_at"),
    )


class AdminActionLog(Base):
    __tablename__ = "admin_action_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_user_id = Column(String, nullable=False)
    target_user_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    target_subject = Column(String, nullable=True)
    reason = Column(Text, nullable=False)
    metadata_json = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_admin_action_logs_actor", "actor_user_id"),
        Index("ix_admin_action_logs_target", "target_user_id"),
        Index("ix_admin_action_logs_action", "action"),
        Index("ix_admin_action_logs_created_at", "created_at"),
    )


class MonitorTelegramAlert(Base):
    __tablename__ = "monitor_telegram_alerts"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(String, nullable=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    timeframe = Column(String, nullable=False, index=True)
    previous_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False, index=True)
    severity = Column(String, nullable=False)
    destination_chat_id = Column(String, nullable=True, index=True)
    destination_thread_id = Column(String, nullable=True)
    result_status = Column(String, nullable=False, index=True)
    error_text = Column(Text, nullable=True)
    payload_hash = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False, default="monitor")
    payload_json = Column(JSONType, nullable=True)

    __table_args__ = (
        Index(
            "ix_monitor_telegram_alerts_dedupe",
            "symbol",
            "timeframe",
            "new_status",
            "created_at",
        ),
        Index("ix_monitor_telegram_alerts_result_created", "result_status", "created_at"),
    )


class MonitorObservedStatus(Base):
    __tablename__ = "monitor_observed_statuses"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True)
    observed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    opportunity_id = Column(String, nullable=True)
    payload_json = Column(JSONType, nullable=True)

    __table_args__ = (
        UniqueConstraint("symbol", "timeframe", name="uq_monitor_observed_status_pair"),
        Index("ix_monitor_observed_statuses_pair", "symbol", "timeframe"),
        Index("ix_monitor_observed_statuses_observed_at", "observed_at"),
    )


class UserExchangeCredential(Base):
    __tablename__ = "user_exchange_credentials"

    user_id = Column(String, primary_key=True)
    provider = Column(String, primary_key=True)
    api_key = Column(String, nullable=False)
    api_secret = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MonitorSpotOrderRequest(Base):
    """Durable, user-scoped audit and idempotency record for direct Spot orders."""

    __tablename__ = "monitor_spot_order_requests"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    idempotency_key = Column(String(64), nullable=False)
    client_order_id = Column(String(36), nullable=False)
    symbol = Column(String(32), nullable=False, index=True)
    strategy_symbol = Column(String(32), nullable=False, index=True)
    side = Column(String(8), nullable=False)
    state = Column(String(24), nullable=False, default="submitting", index=True)
    submitting_account_identity_hash = Column(String(64), nullable=False)
    requested_quote_amount = Column(Numeric(36, 18), nullable=True)
    calculated_base_quantity = Column(Numeric(36, 18), nullable=True)
    executed_base_quantity = Column(Numeric(36, 18), nullable=True)
    executed_quote_amount = Column(Numeric(36, 18), nullable=True)
    average_price = Column(Numeric(36, 18), nullable=True)
    external_order_id = Column(String(64), nullable=True)
    error_code = Column(String(64), nullable=True)
    result_summary = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_reconciled_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "client_order_id",
            name="uq_monitor_spot_order_requests_client_order_id",
        ),
        UniqueConstraint(
            "user_id",
            "idempotency_key",
            name="uq_monitor_spot_order_requests_user_key",
        ),
        Index(
            "ix_monitor_spot_order_requests_user_state_created",
            "user_id",
            "state",
            "created_at",
        ),
        Index(
            "uq_monitor_spot_order_requests_unresolved_strategy",
            "user_id",
            "strategy_symbol",
            unique=True,
            postgresql_where=text("state IN ('submitting', 'reconciling')"),
        ),
    )


class SystemPreference(Base):
    __tablename__ = "system_preferences"

    key = Column(String, primary_key=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_user_id = Column(String, nullable=True)


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    total_usd = Column(Float, nullable=True)
    btc_value = Column(Float, nullable=True)
    usdt_value = Column(Float, nullable=True)
    eth_value = Column(Float, nullable=True)
    other_usd = Column(Float, nullable=True)
    pnl_today_pct = Column(Float, nullable=True)
    drawdown_30d_pct = Column(Float, nullable=True)
    drawdown_peak_date = Column(String, nullable=True)
    btc_change_24h_pct = Column(Float, nullable=True)
    user_id = Column(String, nullable=True, index=True)


class OptimizationResult(Base):
    __tablename__ = "optimization_results"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, nullable=False, index=True)
    result_index = Column(Integer, nullable=False)
    params_json = Column(JSONType, nullable=False)
    metrics_json = Column(JSONType, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("job_id", "result_index", name="uq_optimization_results_job_idx"),
        Index("idx_optimization_results_job_created", "job_id", "created_at"),
    )


# Import onchain models so Base.metadata.create_all() picks them up
from app.models_onchain import OnchainSignal, OnchainSignalHistory  # noqa: F401, E402
