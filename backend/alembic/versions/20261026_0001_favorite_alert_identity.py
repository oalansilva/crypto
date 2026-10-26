"""Alertas por favorito, identidade de configuração e atraso de dado (#1122).

1. ``favorite_strategies`` ganha ``data_source``, ``session`` e ``adjustment``, com backfill:
   - par com ``/`` → ``ccxt``/``24x7``/``none``;
   - ``parameters.data_source = binance_equity`` → ``binance_equity``/``regular_ny``/``split``
     (ou o que ``analysis_conventions`` disser sobre o ajuste);
   - ticker sem fonte → ``stooq``/``eod``/``legacy`` (fonte antiga).
2. ``notify_telegram`` passa a ter default falso; as marcas de quem não é admin vão para falso (o
   default ``True`` nunca foi escolha dessas pessoas). Admin = e-mail em ``ADMIN_EMAILS`` ou papel
   ``admin`` persistido.
3. ``monitor_favorite_alert_states`` (estado por favorito, ``ON DELETE CASCADE``), semeada de
   ``monitor_observed_statuses`` pelo par ``(symbol, timeframe)`` para os favoritos marcados.
4. ``monitor_data_health`` (episódio de atraso por fonte e ativo).
5. ``monitor_telegram_alerts`` ganha ``favorite_id`` e ``event_key``, com índice único parcial
   ``(user_id, event_key)`` para ``sending``/``sent``/``dry_run``/``unknown`` (PostgreSQL).
6. ``system_preferences.monitor_telegram_favorite_origin_at``: o instante da troca (a data da faixa
   "Até <data> você recebia…" e o corte de "recebia pelo catálogo").

Idempotente: o app também cria tabelas e colunas na subida (``create_all`` e
``ensure_runtime_schema_migrations``).

Revision ID: 20261026_0001
Revises: 20261025_0001
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision = "20261026_0001"
down_revision = "20261025_0001"
branch_labels = None
depends_on = None

FAVORITES = "favorite_strategies"
STATES = "monitor_favorite_alert_states"
HEALTH = "monitor_data_health"
ALERTS = "monitor_telegram_alerts"
EVENT_INDEX = "ix_monitor_telegram_alerts_event_key_reserved"
ORIGIN_KEY = "monitor_telegram_favorite_origin_at"


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


def _admin_emails() -> list[str]:
    raw = os.getenv("ADMIN_EMAILS", "") or ""
    return list(dict.fromkeys(e.strip().lower() for e in raw.split(",") if e.strip()))


def _decode(value):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            return None
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (TypeError, ValueError):
                return None
    return value


def configuration_for(symbol: str, parameters, adjusted: bool = True) -> tuple[str, str, str]:
    """Regra do backfill (espelha ``app.services.favorite_configuration.derive_configuration``)."""

    if "/" in str(symbol or ""):
        return ("ccxt", "24x7", "none")
    params = _decode(parameters)
    params = params if isinstance(params, dict) else {}
    source = str(params.get("data_source") or "").strip().lower()
    if source in {"binance_equity", "binance-equity"}:
        return ("binance_equity", "regular_ny", "split" if adjusted else "none")
    return ("stooq", "eod", "legacy")


def _backfill_configuration(bind) -> None:
    rows = bind.execute(
        sa.text(f"SELECT id, symbol, parameters FROM {FAVORITES} WHERE data_source IS NULL")
    ).fetchall()
    unadjusted: set[int] = set()
    equity_ids = [
        int(r.id) for r in rows if configuration_for(r.symbol, r.parameters)[0] == "binance_equity"
    ]
    if equity_ids:
        # Só o ajuste das convenções, sem trazer as métricas (com candles) para fora do banco.
        found = bind.execute(
            sa.text(
                f"SELECT id FROM {FAVORITES} WHERE id IN :ids AND "
                "(metrics LIKE :spaced OR metrics LIKE :compact)"
            ).bindparams(sa.bindparam("ids", expanding=True)),
            {
                "ids": equity_ids,
                "spaced": '%"adjusted_prices": false%',
                "compact": '%"adjusted_prices":false%',
            },
        ).fetchall()
        unadjusted = {int(r.id) for r in found}
    update = sa.text(
        f"UPDATE {FAVORITES} SET data_source = :source, session = :session, "
        "adjustment = :adjustment WHERE id = :id"
    )
    for row in rows:
        source, session, adjustment = configuration_for(
            row.symbol, row.parameters, adjusted=int(row.id) not in unadjusted
        )
        bind.execute(
            update,
            {"source": source, "session": session, "adjustment": adjustment, "id": int(row.id)},
        )


def _clear_non_admin_marks(bind) -> None:
    admin_ids: set[str] = set()
    if _has_table("users"):
        has_role = _has_column("users", "role")
        users = bind.execute(
            sa.text("SELECT id, email" + (", role" if has_role else "") + " FROM users")
        ).fetchall()
        emails = set(_admin_emails())
        for user in users:
            role = str(getattr(user, "role", "") or "").strip().lower() if has_role else ""
            if str(user.email or "").strip().lower() in emails or role == "admin":
                admin_ids.add(str(user.id))
    if admin_ids:
        bind.execute(
            sa.text(
                f"UPDATE {FAVORITES} SET notify_telegram = false "
                "WHERE notify_telegram AND (user_id IS NULL OR user_id NOT IN :ids)"
            ).bindparams(sa.bindparam("ids", expanding=True)),
            {"ids": sorted(admin_ids)},
        )
    else:
        bind.execute(sa.text(f"UPDATE {FAVORITES} SET notify_telegram = false"))


def _seed_states(bind) -> None:
    if not _has_table("monitor_observed_statuses"):
        return
    bind.execute(sa.text(f"""
            INSERT INTO {STATES} (favorite_id, status, candle_time, observed_at, payload_json)
            SELECT f.id, o.status, NULL, o.observed_at, o.payload_json
            FROM {FAVORITES} f
            JOIN monitor_observed_statuses o
              ON o.symbol = upper(trim(f.symbol)) AND o.timeframe = lower(trim(f.timeframe))
            WHERE f.notify_telegram
              AND NOT EXISTS (SELECT 1 FROM {STATES} s WHERE s.favorite_id = f.id)
            """))


def upgrade():
    bind = op.get_bind()
    postgres = bind.dialect.name == "postgresql"

    for column in ("data_source", "session", "adjustment"):
        if not _has_column(FAVORITES, column):
            op.add_column(FAVORITES, sa.Column(column, sa.String(), nullable=True))
    _backfill_configuration(bind)

    if _has_column(FAVORITES, "notify_telegram"):
        op.alter_column(FAVORITES, "notify_telegram", server_default=sa.text("false"))
        _clear_non_admin_marks(bind)

    if not _has_table(STATES):
        op.create_table(
            STATES,
            sa.Column(
                "favorite_id",
                sa.Integer(),
                sa.ForeignKey(f"{FAVORITES}.id", ondelete="CASCADE"),
                primary_key=True,
            ),
            sa.Column("status", sa.String(), nullable=False),
            sa.Column("candle_time", sa.String(), nullable=True),
            sa.Column("observed_at", sa.DateTime(), nullable=False),
            sa.Column("payload_json", sa.Text(), nullable=True),
        )
    _seed_states(bind)

    if not _has_table(HEALTH):
        op.create_table(
            HEALTH,
            sa.Column("data_source", sa.String(), primary_key=True),
            sa.Column("symbol", sa.String(), primary_key=True),
            sa.Column("state", sa.String(), nullable=False),
            sa.Column("stale_since", sa.DateTime(), nullable=True),
            sa.Column("episode_id", sa.String(64), nullable=True),
            sa.Column("detail_json", sa.Text(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )

    if _has_table(ALERTS):
        if not _has_column(ALERTS, "favorite_id"):
            op.add_column(ALERTS, sa.Column("favorite_id", sa.Integer(), nullable=True))
        if not _has_column(ALERTS, "event_key"):
            op.add_column(ALERTS, sa.Column("event_key", sa.String(64), nullable=True))
        if not _has_index(ALERTS, "ix_monitor_telegram_alerts_favorite_id"):
            op.create_index("ix_monitor_telegram_alerts_favorite_id", ALERTS, ["favorite_id"])
        if postgres and not _has_index(ALERTS, EVENT_INDEX):
            op.create_index(
                EVENT_INDEX,
                ALERTS,
                ["user_id", "event_key"],
                unique=True,
                postgresql_where=sa.text(
                    "event_key IS NOT NULL AND "
                    "result_status IN ('sending','sent','dry_run','unknown')"
                ),
            )

    if _has_table("system_preferences"):
        exists = bind.execute(
            sa.text("SELECT 1 FROM system_preferences WHERE key = :key"), {"key": ORIGIN_KEY}
        ).first()
        if exists is None:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            bind.execute(
                sa.text(
                    "INSERT INTO system_preferences (key, value, updated_at) "
                    "VALUES (:key, :value, :now)"
                ),
                {"key": ORIGIN_KEY, "value": now.isoformat(), "now": now},
            )


def downgrade():
    if _has_table(ALERTS):
        if _has_index(ALERTS, EVENT_INDEX):
            op.drop_index(EVENT_INDEX, table_name=ALERTS)
        if _has_index(ALERTS, "ix_monitor_telegram_alerts_favorite_id"):
            op.drop_index("ix_monitor_telegram_alerts_favorite_id", table_name=ALERTS)
        for column in ("event_key", "favorite_id"):
            if _has_column(ALERTS, column):
                op.drop_column(ALERTS, column)
    if _has_table(HEALTH):
        op.drop_table(HEALTH)
    if _has_table(STATES):
        op.drop_table(STATES)
    if _has_column(FAVORITES, "notify_telegram"):
        # As marcas zeradas não voltam: nunca tiveram efeito para quem não é admin.
        op.alter_column(FAVORITES, "notify_telegram", server_default=sa.text("true"))
    for column in ("adjustment", "session", "data_source"):
        if _has_column(FAVORITES, column):
            op.drop_column(FAVORITES, column)
    if _has_table("system_preferences"):
        op.get_bind().execute(
            sa.text("DELETE FROM system_preferences WHERE key = :key"), {"key": ORIGIN_KEY}
        )
