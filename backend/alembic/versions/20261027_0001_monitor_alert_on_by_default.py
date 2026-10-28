"""Alerta = estratégia própria no Monitor, ligado por padrão (#1122, Design d2).

Decisões de Alan de 27/10/2026 (design.md, decisão 20, d2-1 e d2-2):

1. ``favorite_strategies.notify_telegram`` passa a ter ``server_default`` verdadeiro: o campo quer
   dizer "alerta ligado" (opt-out no Monitor) e só vale com estrela (``tier`` 1, 2 ou 3).
2. d2-1: a estrela automática de lote e Descoberta sai. Favoritos com nota "gerado em lote …" ou
   "descoberta via sweep …" que ainda estão com 1 estrela (``tier = 3``) ficam sem estrela (saem
   do Monitor); os que a pessoa subiu para 2 ou 3 estrelas ficam.
3. d2-2: todo favorito fica com o alerta ligado (as marcas "Alertar" de antes não contam).
4. O estado por favorito (``monitor_favorite_alert_states``) é semeado de
   ``monitor_observed_statuses`` pelo par ``(symbol, timeframe)`` para os favoritos que passam a
   alertar (com estrela e alerta ligado) e ainda não têm estado, para a primeira varredura não
   perder nem repetir uma transição em curso.
5. Antes de tudo, sai o estado dos favoritos que a varredura anterior não avaliava (alerta
   desmarcado, cujo PATCH antigo não apagava o estado, ou fora do filtro de estrelas do sistema):
   é um estado parado, e a primeira varredura o compararia com a leitura atual e mandaria entrada
   ou saída de uma mudança antiga. É o mesmo efeito, em massa, do PATCH novo que apaga o estado
   quando muda quem alerta. Esses favoritos voltam a ser semeados no passo 4 (ou, sem par
   observado, a primeira leitura é só base). O estado de quem já era avaliado fica: é a leitura
   do próprio favorito, mais nova que ``monitor_observed_statuses`` (que nada mais grava).

Não mexe em ``monitor_telegram_favorite_origin_at`` nem na marca da transição.

Downgrade: devolve só o ``server_default`` falso; as estrelas tiradas e os alertas ligados não
voltam (Migration Plan).

Revision ID: 20261027_0001
Revises: 20261026_0001
"""

from __future__ import annotations

import os

import sqlalchemy as sa
from alembic import op

revision = "20261027_0001"
down_revision = "20261026_0001"
branch_labels = None
depends_on = None

FAVORITES = "favorite_strategies"
STATES = "monitor_favorite_alert_states"
OBSERVED = "monitor_observed_statuses"
PREFERENCES = "system_preferences"
TIER_FILTER_KEY = "monitor_telegram_tier_filter"
TIER_FILTER_ENV = "MONITOR_TELEGRAM_TIER_FILTER"
AUTO_STAR_TIER = 3  # 1 estrela
AUTO_NOTES = ("gerado em lote%", "descoberta via sweep%")


def _inspector():
    return sa.inspect(op.get_bind())


def _has_table(name: str) -> bool:
    return _inspector().has_table(name)


def _has_column(table: str, column: str) -> bool:
    if not _has_table(table):
        return False
    return column in {c["name"] for c in _inspector().get_columns(table)}


def _previous_tier_filter(bind) -> str:
    """O filtro de estrelas que a varredura anterior aplicava (preferência, variável, ``all``)."""

    value = None
    if _has_table(PREFERENCES):
        value = bind.execute(
            sa.text(f"SELECT value FROM {PREFERENCES} WHERE key = :key"),
            {"key": TIER_FILTER_KEY},
        ).scalar()
    return str(value or os.getenv(TIER_FILTER_ENV) or "all").strip().lower() or "all"


def _previously_evaluated_condition(tier_filter: str) -> str:
    """SQL dos favoritos que a varredura anterior avaliava (``get_alert_favorites``).

    Espelha ``OpportunityService._apply_tier_filter``: ``all`` ou valor sem estrela válida não
    filtram; ``none`` é só sem estrela; ``1,2`` são essas estrelas.
    """

    if tier_filter == "none":
        return "f.notify_telegram AND f.tier IS NULL"
    tiers = sorted({int(t.strip()) for t in tier_filter.split(",") if t.strip().isdigit()})
    if tier_filter == "all" or not tiers:
        return "f.notify_telegram"
    return f"f.notify_telegram AND f.tier IN ({', '.join(str(t) for t in tiers)})"


def _drop_states_not_evaluated(bind) -> None:
    """Tira o estado parado dos favoritos que a varredura anterior não avaliava."""

    if not _has_table(STATES):
        return
    if _has_column(FAVORITES, "tier"):
        evaluated = _previously_evaluated_condition(_previous_tier_filter(bind))
    else:
        evaluated = "f.notify_telegram"
    bind.execute(sa.text(f"""
            DELETE FROM {STATES} s
            WHERE NOT EXISTS (
                SELECT 1 FROM {FAVORITES} f WHERE f.id = s.favorite_id AND {evaluated}
            )
            """))


def _remove_auto_star(bind) -> None:
    """d2-1: tira a 1 estrela automática de lote e Descoberta."""

    bind.execute(
        sa.text(
            f"UPDATE {FAVORITES} SET tier = NULL "
            "WHERE tier = :tier AND (notes LIKE :batch OR notes LIKE :discovery)"
        ),
        {"tier": AUTO_STAR_TIER, "batch": AUTO_NOTES[0], "discovery": AUTO_NOTES[1]},
    )


def _switch_all_alerts_on(bind) -> None:
    """d2-2: tudo o que fica no Monitor sai com o alerta ligado."""

    bind.execute(sa.text(f"UPDATE {FAVORITES} SET notify_telegram = true"))


def _seed_states(bind) -> None:
    if not _has_table(STATES) or not _has_table(OBSERVED):
        return
    bind.execute(sa.text(f"""
            INSERT INTO {STATES} (favorite_id, status, candle_time, observed_at, payload_json)
            SELECT f.id, o.status, NULL, o.observed_at, o.payload_json
            FROM {FAVORITES} f
            JOIN {OBSERVED} o
              ON o.symbol = upper(trim(f.symbol)) AND o.timeframe = lower(trim(f.timeframe))
            WHERE f.notify_telegram
              AND f.tier IN (1, 2, 3)
              AND NOT EXISTS (SELECT 1 FROM {STATES} s WHERE s.favorite_id = f.id)
            """))


def upgrade():
    bind = op.get_bind()
    if not _has_column(FAVORITES, "notify_telegram"):
        return
    op.alter_column(FAVORITES, "notify_telegram", server_default=sa.text("true"))
    _drop_states_not_evaluated(bind)
    if _has_column(FAVORITES, "tier") and _has_column(FAVORITES, "notes"):
        _remove_auto_star(bind)
    _switch_all_alerts_on(bind)
    if _has_column(FAVORITES, "tier"):
        _seed_states(bind)


def downgrade():
    # As estrelas tiradas (d2-1) e os alertas ligados (d2-2) não voltam.
    if _has_column(FAVORITES, "notify_telegram"):
        op.alter_column(FAVORITES, "notify_telegram", server_default=sa.text("false"))
