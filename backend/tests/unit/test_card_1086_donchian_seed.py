"""Corrected export reaches empty and existing catalogs through the real seed."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from app.database import SessionLocal
from app.models import ComboTemplate
from app.startup_seed import seed_combo_templates_if_empty

BACKEND = Path(__file__).resolve().parents[2]
EXPORT = BACKEND / "config/combo_templates_export.json"
BASELINE = BACKEND / "tests/fixtures/card_1086/templates_before.json"
NAME = "donchian_volume_breakout"
CORRECTED_ENTRY = "(close > dc_upper.shift(1)) & (volume > vol_avg)"


def catalog_snapshot():
    with SessionLocal() as db:
        return {
            row.name: {
                "id": row.id,
                "description": row.description,
                "template_data": deepcopy(row.template_data),
                "optimization_schema": deepcopy(row.optimization_schema),
                "is_prebuilt": row.is_prebuilt,
                "is_example": row.is_example,
                "is_readonly": row.is_readonly,
            }
            for row in db.query(ComboTemplate).all()
        }


@pytest.mark.usefixtures("postgres_isolation")
def test_initial_seed_loads_corrected_export_and_repeats_without_definition_changes():
    exported = json.loads(EXPORT.read_text(encoding="utf-8"))
    assert seed_combo_templates_if_empty(str(EXPORT)) == len(exported)
    initial = catalog_snapshot()
    assert initial[NAME]["template_data"]["entry_logic"] == CORRECTED_ENTRY
    for row in exported:
        assert initial[row["name"]]["template_data"] == row["template_data"]
        assert initial[row["name"]]["optimization_schema"] == row.get("optimization_schema")
    assert seed_combo_templates_if_empty(str(EXPORT)) == 0
    assert seed_combo_templates_if_empty(str(EXPORT)) == 0
    assert catalog_snapshot() == initial


@pytest.mark.usefixtures("postgres_isolation")
def test_existing_catalog_refreshes_donchian_idempotently_and_preserves_others():
    assert seed_combo_templates_if_empty(str(BASELINE)) == 4
    # A saved user template must also survive the named catalog refresh.
    with SessionLocal() as db:
        db.add(
            ComboTemplate(name="user_saved_strategy", template_data={"entry_logic": "close > 42"})
        )
        db.commit()
    original = catalog_snapshot()
    assert (
        original[NAME]["template_data"]["entry_logic"] == "(close > dc_upper) & (volume > vol_avg)"
    )
    assert seed_combo_templates_if_empty(str(EXPORT)) == 0
    refreshed = catalog_snapshot()
    expected = deepcopy(original)
    expected[NAME]["template_data"]["entry_logic"] = CORRECTED_ENTRY
    assert refreshed == expected
    for _ in range(2):
        assert seed_combo_templates_if_empty(str(EXPORT)) == 0
        assert catalog_snapshot() == expected
