"""Tests for strategy identity resolver and template identity API (card #549)."""

from __future__ import annotations

import pytest

from app.database import Base
from app.models import ComboTemplate
from app.services.combo_service import ComboService
from app.services.strategy_descriptions import (
    resolve_strategy_description,
    resolve_strategy_display_name,
    resolve_strategy_identity,
)


def test_resolve_strategy_identity_db_override_wins():
    identity = resolve_strategy_identity(
        "multi_ma_crossover",
        db_display_name="Título customizado",
        db_description="Descrição customizada no catálogo.",
    )
    assert identity["display_name"] == "Título customizado"
    assert identity["description"] == "Descrição customizada no catálogo."


def test_resolve_strategy_description_ignores_legacy_db_without_display_name():
    mapped = resolve_strategy_description(
        "short_ema200_pullback",
        db_description="Short-only: bearish trend with EMA200, EMA21, EMA50, RSI 45-70.",
    )
    assert "venda" in mapped.lower()
    assert "ema200" not in mapped.lower()


def test_resolve_strategy_display_name_falls_back_to_catalog_map():
    assert resolve_strategy_display_name("multi_ma_crossover") == "Médias Móveis: Tendência em Virada"


def test_resolve_strategy_display_name_raw_name_not_generic():
    raw = "quant_btc_custom_alpha"
    assert resolve_strategy_display_name(raw) == raw
    assert resolve_strategy_display_name(raw) != "Estratégia Cripto Farol"


def test_resolve_strategy_description_db_over_map():
    mapped = resolve_strategy_description("multi_ma_crossover")
    overridden = resolve_strategy_description(
        "multi_ma_crossover",
        db_display_name="Título customizado",
        db_description="Override persistido no banco.",
    )
    assert overridden == "Override persistido no banco."
    assert overridden != mapped


def test_update_template_identity_persists_readonly_template(
    postgres_isolation, unit_database_url
):
    service = ComboService(unit_database_url)
    with service._session_factory() as db:
        Base.metadata.create_all(db.get_bind())
        db.execute(
            __import__("sqlalchemy").text(
                "ALTER TABLE combo_templates ADD COLUMN IF NOT EXISTS display_name VARCHAR NULL"
            )
        )
        db.commit()
        row = ComboTemplate(
            name="card549_readonly_identity",
            description="Descrição original",
            is_readonly=True,
            is_prebuilt=True,
            is_example=False,
            template_data={"indicators": [], "entry_logic": "true", "exit_logic": "false", "stop_loss": 0.02},
        )
        db.add(row)
        db.commit()

    service.update_template_identity(
        "card549_readonly_identity",
        display_name="Nome público editado",
        description="Descrição pública editada no catálogo global.",
    )

    with service._session_factory() as db:
        row = db.query(ComboTemplate).filter(ComboTemplate.name == "card549_readonly_identity").one()
        assert row.display_name == "Nome público editado"
        assert row.description == "Descrição pública editada no catálogo global."
        assert row.is_readonly is True

    metadata = service.get_template_metadata("card549_readonly_identity")
    assert metadata is not None
    assert metadata["display_name"] == "Nome público editado"
    assert metadata["description"] == "Descrição pública editada no catálogo global."


def test_update_template_identity_rejects_empty_fields(postgres_isolation, unit_database_url):
    service = ComboService(unit_database_url)
    with service._session_factory() as db:
        Base.metadata.create_all(db.get_bind())
        db.execute(
            __import__("sqlalchemy").text(
                "ALTER TABLE combo_templates ADD COLUMN IF NOT EXISTS display_name VARCHAR NULL"
            )
        )
        db.commit()
        row = ComboTemplate(
            name="card549_empty_identity",
            description="ok",
            is_readonly=False,
            template_data={"indicators": [], "entry_logic": "true", "exit_logic": "false", "stop_loss": 0.02},
        )
        db.add(row)
        db.commit()

    with pytest.raises(ValueError, match="display_name"):
        service.update_template_identity("card549_empty_identity", display_name=" ", description="x")

    with pytest.raises(ValueError, match="description"):
        service.update_template_identity("card549_empty_identity", display_name="x", description=" ")


def test_identity_map_for_template_names(postgres_isolation, unit_database_url):
    service = ComboService(unit_database_url)
    with service._session_factory() as db:
        Base.metadata.create_all(db.get_bind())
        db.execute(
            __import__("sqlalchemy").text(
                "ALTER TABLE combo_templates ADD COLUMN IF NOT EXISTS display_name VARCHAR NULL"
            )
        )
        db.commit()
        row = ComboTemplate(
            name="card549_batch_lookup",
            display_name="Batch Title",
            description="Batch description",
            is_readonly=False,
            template_data={"indicators": [], "entry_logic": "true", "exit_logic": "false", "stop_loss": 0.02},
        )
        db.add(row)
        db.commit()

        identity_map = ComboService.identity_map_for_template_names(db, ["card549_batch_lookup", "missing"])
    assert identity_map["card549_batch_lookup"]["display_name"] == "Batch Title"
    assert identity_map["card549_batch_lookup"]["description"] == "Batch description"
    assert "missing" not in identity_map
