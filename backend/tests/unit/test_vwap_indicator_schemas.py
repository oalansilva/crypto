"""VWAP indicator optimization schemas (card #1074)."""

from app.schemas.auto_indicator_schemas import get_all_auto_schemas


def test_vwap_daily_and_rolling_have_optimization_schemas():
    schemas = get_all_auto_schemas()
    assert "vwap_daily" in schemas
    assert "vwap_rolling" in schemas
    rolling = schemas["vwap_rolling"]
    assert "length" in rolling.parameters
    assert rolling.parameters["length"].optimization_range is not None
