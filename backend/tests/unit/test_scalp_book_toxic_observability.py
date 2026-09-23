"""Card #1025 — G: book_toxic drivers in the diagnostic record (log only)."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import ScalpFill, ScalpUserState, UserExchangeCredential
from app.services.scalp_jev import (
    _map_systemone,
    _noul_value,
    _window_features,
    request_jev,
)
from app.services.scalp_jev_log import (
    TailTruncatingFileHandler,
    logger as diagnostic_logger,
)
from app.services.scalp_service import status_payload
from test_scalp_direcional_jev import (
    _FakeHttpResponse,
    _add_key,
    _capture_urlopen,
    _diagnostic_call_payload,
    _systemone_response,
)


@pytest.fixture
def diagnostic_log(tmp_path):
    path = tmp_path / "scalp_jev_diagnostic.log"
    handler = TailTruncatingFileHandler(path)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    previous_level = diagnostic_logger.level
    diagnostic_logger.addHandler(handler)
    diagnostic_logger.setLevel(logging.INFO)
    try:
        yield path
    finally:
        diagnostic_logger.removeHandler(handler)
        diagnostic_logger.setLevel(previous_level)
        handler.close()


@pytest.fixture
def scalp_db(postgres_isolation, unit_database_url):
    from app.database import ensure_runtime_schema_migrations

    ensure_runtime_schema_migrations()
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    db.query(ScalpFill).delete()
    db.query(ScalpUserState).delete()
    db.query(UserExchangeCredential).delete()
    db.commit()
    try:
        yield db
    finally:
        db.query(ScalpFill).delete()
        db.query(ScalpUserState).delete()
        db.query(UserExchangeCredential).delete()
        db.commit()
        db.close()
        engine.dispose()


def _payload_with_features() -> dict:
    payload = _diagnostic_call_payload()
    payload["state"]["window"] = {
        "horizon_s": 900,
        "trade_count": 42,
        "ret_bp": "-3.5",
        "vol_bp": "0.8",
        "aggressor_flow": "-0.42",
        "spread_bp_mean": "0.004",
    }
    return payload


def test_return_record_carries_noul_and_the_window_features(diagnostic_log, monkeypatch):
    monkeypatch.setenv("JEV_API_KEY", "k")

    def ok(_req, _timeout, _captured):
        response = _FakeHttpResponse(
            _systemone_response(side="BUY", toxic=0.9, move_bp=25.0, confidence=0.2)
        )
        response.status = 200
        return response

    _capture_urlopen(monkeypatch, ok)
    payload = _payload_with_features()
    signal = request_jev(payload)
    assert signal.book_toxic is True

    line = next(
        line
        for line in diagnostic_log.read_text(encoding="utf-8").splitlines()
        if "call return" in line
    )
    assert "book_toxic=True" in line
    assert "noul=0.9" in line
    assert "window_ret_bp=-3.5" in line
    assert "window_vol_bp=0.8" in line
    assert "window_aggressor_flow=-0.42" in line
    assert "window_spread_bp_mean=0.004" in line
    assert "window_trade_count=42" in line


def test_model_opinion_can_be_told_apart_from_a_wrong_mapping(diagnostic_log, monkeypatch):
    monkeypatch.setenv("JEV_API_KEY", "k")

    def toxic_reply(_req, _timeout, _captured):
        response = _FakeHttpResponse(_systemone_response(toxic=0.8))
        response.status = 200
        return response

    def calm_reply(_req, _timeout, _captured):
        response = _FakeHttpResponse(_systemone_response(toxic=0.1))
        response.status = 200
        return response

    _capture_urlopen(monkeypatch, toxic_reply)
    request_jev(_payload_with_features())
    _capture_urlopen(monkeypatch, calm_reply)
    request_jev(_payload_with_features())

    returns = [
        line
        for line in diagnostic_log.read_text(encoding="utf-8").splitlines()
        if "call return" in line
    ]
    assert len(returns) == 2
    assert "noul=0.8" in returns[0] and "book_toxic=True" in returns[0]
    assert "noul=0.1" in returns[1] and "book_toxic=False" in returns[1]


def test_noul_threshold_is_not_retuned():
    assert (
        _map_systemone(
            {"answers": {"book_toxic": {"type": "noul", "noul": 0.5}}}, latency_ms=1
        ).book_toxic
        is True
    )
    assert (
        _map_systemone(
            {"answers": {"book_toxic": {"type": "noul", "noul": 0.49}}}, latency_ms=1
        ).book_toxic
        is False
    )
    assert _map_systemone({"answers": {}}, latency_ms=1).book_toxic is False
    assert _noul_value({"answers": {"book_toxic": {"noul": 0.42}}}) == Decimal("0.42")
    assert _noul_value({"answers": {}}) is None
    assert _window_features({"state": {"window": {"trade_count": 3}}}) == {"trade_count": 3}
    assert _window_features({}) == {}


def test_drivers_stay_out_of_the_product_surface(scalp_db):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    payload = status_payload(scalp_db, user_id, free_usdt=Decimal("80"), mid=Decimal("65005"))
    blob = str(payload).lower()
    assert "noul" not in blob
    assert "book_toxic" not in blob
    assert not any("window" in str(key) for key in payload)
