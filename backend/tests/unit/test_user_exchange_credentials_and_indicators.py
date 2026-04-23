from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import UserExchangeCredential
from app.services import pandas_ta_inspector
from app.services.user_exchange_credentials import (
    BINANCE_PROVIDER,
    delete_user_exchange_credential,
    get_user_exchange_credential,
    upsert_user_exchange_credential,
)
from app.schemas import indicator_params
from app.database import Base


@pytest.fixture
def app_db_session():
    engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/postgres")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def test_user_exchange_credentials_flow(app_db_session):
    assert get_user_exchange_credential(app_db_session, "u1", BINANCE_PROVIDER) is None

    created = upsert_user_exchange_credential(
        app_db_session,
        user_id="u1",
        provider=BINANCE_PROVIDER,
        api_key="k1",
        api_secret="s1",
    )
    assert created.user_id == "u1"
    assert created.provider == BINANCE_PROVIDER
    assert created.api_key == "k1"

    existing = get_user_exchange_credential(app_db_session, "u1", BINANCE_PROVIDER)
    assert existing is not None
    assert existing.api_key == "k1"
    assert existing.api_secret == "s1"

    updated = upsert_user_exchange_credential(
        app_db_session,
        user_id="u1",
        provider=BINANCE_PROVIDER,
        api_key="k2",
        api_secret="s2",
    )
    assert updated.api_key == "k2"
    assert updated.api_secret == "s2"

    assert (
        delete_user_exchange_credential(app_db_session, user_id="u1", provider=BINANCE_PROVIDER)
        is True
    )
    assert get_user_exchange_credential(app_db_session, "u1", BINANCE_PROVIDER) is None
    assert (
        delete_user_exchange_credential(app_db_session, user_id="u1", provider=BINANCE_PROVIDER)
        is False
    )


def test_indicator_schema_models_and_pandas_ta_inspector_metadata(monkeypatch):
    # Import-time for indicators module.
    assert indicator_params.MACD_SCHEMA.name == "MACD"
    assert indicator_params.BOLLINGER_SCHEMA.parameters["std"].optimization_range is not None
    assert indicator_params.OptimizationRange(min=1, max=3, step=0.5).min == 1
    assert isinstance(indicator_params.OptimizationRange(min=1, max=3, step=0.5), object)

    class _DummyTA:
        Category = {"trend": ["macd", "sma"]}

        @staticmethod
        def macd(
            close,
            fast: int = 12,
            slow: float | int = 26.0,
            signal=None,
            *,
            length: int = 10,
        ):
            """MACD wrapper."""
            return None

        @staticmethod
        def sma(close, length: int = 20):
            return None

    monkeypatch.setattr(pandas_ta_inspector, "ta", _DummyTA())

    from app.services import pandas_ta_inspector as target

    metadata = target.get_all_indicators_metadata()
    assert "trend" in metadata
    assert {item["id"] for item in metadata["trend"]} == {"macd", "sma"}
    macd_item = next(item for item in metadata["trend"] if item["id"] == "macd")
    assert macd_item["name"] == "MACD"
    assert macd_item["description"] != ""
    assert [param["name"] for param in macd_item["params"]][:1] == ["fast"]

    bad = _DummyTA()
    bad.Category = {"broken": ["missing"]}
    monkeypatch.setattr(pandas_ta_inspector, "ta", bad)
    metadata2 = target.get_all_indicators_metadata()
    assert "broken" not in metadata2 or metadata2["broken"] == []
