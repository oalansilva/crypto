"""Make the bollinger_rsi_adx rules follow the optimized RSI/ADX parameters (#1120).

The pre-built template optimizes ``rsi_length`` and ``adx_length`` (10 to 20) and
``adx_threshold`` (15 to 30), but its rules named the default columns (``RSI_14``,
``ADX_14``) and the literal ``20``. Only the combinations with both lengths at 14 could be
evaluated, and the threshold never changed anything. The rules now read the stable aliases
``rsi`` and ``adx`` and the ``adx_threshold`` column (the ADX indicator carries
``threshold`` as a parameter), the same mechanism the other templates use (``bb``, ``trend``).

Data migration, idempotent, for the single pre-built record named ``bollinger_rsi_adx``.
Other templates and user copies (other names) are not touched. A record whose rules were
edited by hand (neither the old nor the new text) is left as it is.

Revision ID: 20261025_0001
Revises: 20261024_0001
"""

from __future__ import annotations

import json

from alembic import op
import sqlalchemy as sa

revision = "20261025_0001"
down_revision = "20261024_0001"
branch_labels = None
depends_on = None

TEMPLATE = "bollinger_rsi_adx"
OLD_ENTRY = "(close < bb_lower) & (RSI_14 < 30) & (ADX_14 > 20)"
OLD_EXIT = "(close > bb_middle) | (RSI_14 > 70)"
NEW_ENTRY = "(close < bb_lower) & (rsi < 30) & (adx > adx_threshold)"
NEW_EXIT = "(close > bb_middle) | (rsi > 70)"
DEFAULT_THRESHOLD = 20


def _indicator(data: dict, kind: str) -> dict | None:
    matches = [
        item
        for item in data.get("indicators") or []
        if isinstance(item, dict) and str(item.get("type", "")).lower() == kind
    ]
    return matches[0] if len(matches) == 1 else None


def upgraded(data: dict) -> dict | None:
    """Template data with the rules following the parameters; ``None`` if nothing to change."""
    if not isinstance(data, dict) or data.get("entry_logic") != OLD_ENTRY:
        return None
    if data.get("exit_logic") != OLD_EXIT:
        return None
    rsi, adx = _indicator(data, "rsi"), _indicator(data, "adx")
    if rsi is None or adx is None or rsi.get("alias") or adx.get("alias"):
        return None
    result = json.loads(json.dumps(data))
    rsi, adx = _indicator(result, "rsi"), _indicator(result, "adx")
    rsi["alias"] = "rsi"
    adx["alias"] = "adx"
    adx.setdefault("params", {})
    adx["params"].setdefault("threshold", DEFAULT_THRESHOLD)
    result["entry_logic"] = NEW_ENTRY
    result["exit_logic"] = NEW_EXIT
    return result


def downgraded(data: dict) -> dict | None:
    if not isinstance(data, dict) or data.get("entry_logic") != NEW_ENTRY:
        return None
    if data.get("exit_logic") != NEW_EXIT:
        return None
    rsi, adx = _indicator(data, "rsi"), _indicator(data, "adx")
    if rsi is None or adx is None or rsi.get("alias") != "rsi" or adx.get("alias") != "adx":
        return None
    result = json.loads(json.dumps(data))
    rsi, adx = _indicator(result, "rsi"), _indicator(result, "adx")
    rsi["alias"] = None
    adx["alias"] = None
    if isinstance(adx.get("params"), dict):
        adx["params"].pop("threshold", None)
    result["entry_logic"] = OLD_ENTRY
    result["exit_logic"] = OLD_EXIT
    return result


def _rewrite(transform) -> None:
    conn = op.get_bind()
    if not sa.inspect(conn).has_table("combo_templates"):
        return
    row = conn.execute(
        sa.text("SELECT id, template_data FROM combo_templates WHERE name = :name"),
        {"name": TEMPLATE},
    ).fetchone()
    if row is None:
        return
    raw = row[1]
    data = json.loads(raw) if isinstance(raw, (str, bytes)) else raw
    changed = transform(data)
    if changed is None:
        return
    conn.execute(
        sa.text(
            "UPDATE combo_templates SET template_data = :data, "
            "updated_at = CURRENT_TIMESTAMP WHERE id = :id"
        ),
        {"data": json.dumps(changed), "id": row[0]},
    )


def upgrade() -> None:
    _rewrite(upgraded)


def downgrade() -> None:
    _rewrite(downgraded)
