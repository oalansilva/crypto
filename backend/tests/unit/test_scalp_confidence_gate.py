"""Card #1025 — C: confidence gate by env and the opt-in raw payload record."""

from __future__ import annotations

import json
import logging
from decimal import Decimal
from pathlib import Path

import pytest

from app.services.scalp_engine import CONFIDENCE_MIN, Book, JevSignal, decide_cycle
from app.services.scalp_jev import request_jev
from app.services.scalp_jev_log import (
    TailTruncatingFileHandler,
    log_call_raw,
    logger as diagnostic_logger,
    raw_payload_enabled,
)
from app.services.scalp_service import _confidence_min
from test_scalp_direcional_jev import (
    _FakeHttpResponse,
    _capture_urlopen,
    _diagnostic_call_payload,
    _systemone_response,
)

DEFAULT_CONFIDENCE_MIN = "0.7"


def _book() -> Book:
    return Book(bid=Decimal("65000"), ask=Decimal("65010"))


def _signal(*, confidence: Decimal, expected_move_bp: Decimal = Decimal("60")) -> JevSignal:
    return JevSignal(
        side="BUY",
        confidence=confidence,
        expected_move_bp=expected_move_bp,
        book_toxic=False,
        latency_ms=50,
    )


def _cycle(*, confidence_min, confidence: Decimal):
    return decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=1000,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=_signal(confidence=confidence),
        confidence_min=confidence_min,
    )


def test_current_threshold_still_blocks_the_observed_confidence_range():
    """Card A: amostra insuficiente → o default fica (evidência da etapa)."""
    assert CONFIDENCE_MIN == Decimal(DEFAULT_CONFIDENCE_MIN)
    assert _confidence_min() == CONFIDENCE_MIN
    blocked = _cycle(confidence_min=CONFIDENCE_MIN, confidence=Decimal("0.39"))
    assert blocked.send is False
    assert blocked.skip_reason == "low_confidence"


def test_gate_threshold_is_configurable_by_env_and_applied_by_the_engine(monkeypatch):
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN", "0.2")
    assert _confidence_min() == Decimal("0.2")
    allowed = _cycle(confidence_min=_confidence_min(), confidence=Decimal("0.25"))
    assert allowed.send is True
    assert allowed.skip_reason is None

    monkeypatch.setenv("SCALP_CONFIDENCE_MIN", "0.3")
    refused = _cycle(confidence_min=_confidence_min(), confidence=Decimal("0.25"))
    assert refused.send is False
    assert refused.skip_reason == "low_confidence"


def test_invalid_or_absent_env_keeps_the_default(monkeypatch):
    monkeypatch.delenv("SCALP_CONFIDENCE_MIN", raising=False)
    assert _confidence_min() == CONFIDENCE_MIN
    # N2: não finitos («nan»/«inf») comparam False contra tudo e desligavam o
    # gate em silêncio — têm de cair no default conservador (falha fechada).
    for raw in ("", "abc", "-1", "1.5", "2", "nan", "NaN", "-nan", "inf", "-inf", "Infinity"):
        monkeypatch.setenv("SCALP_CONFIDENCE_MIN", raw)
        assert _confidence_min() == CONFIDENCE_MIN, raw


def test_gate_can_be_removed_explicitly_with_no_low_confidence(monkeypatch):
    """3.3/3.4: caminho explícito de remoção do gate (confiança não separa)."""
    for raw in ("none", "off", "disabled", "NONE", "Off"):
        monkeypatch.setenv("SCALP_CONFIDENCE_MIN", raw)
        assert _confidence_min() is None, raw
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN", "none")
    allowed = _cycle(confidence_min=_confidence_min(), confidence=Decimal("0.01"))
    assert allowed.send is True
    assert allowed.skip_reason is None, "sem limiar, nenhum low_confidence"


def test_engine_default_threshold_does_not_read_the_environment(monkeypatch):
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN", "0.1")
    # The pure engine keeps its own default: the value arrives as a parameter.
    refused = _cycle(confidence_min=CONFIDENCE_MIN, confidence=Decimal("0.2"))
    assert refused.skip_reason == "low_confidence"


def _raw_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if "call raw" in line]


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


def _reply_with_confidence_origin() -> dict:
    return _systemone_response(
        side="BUY",
        confidence=0.31,
        move_bp=25.0,
        toxic=0.42,
        probabilities={"BUY": 0.33, "SELL": 0.6, "HOLD": 0.07},
    )


def test_raw_payload_record_is_opt_in_and_shows_the_origin_of_confidence(
    monkeypatch, diagnostic_log
):
    monkeypatch.setenv("JEV_API_KEY", "super-secret-jev-token")

    def ok(_req, _timeout, _captured):
        response = _FakeHttpResponse(_reply_with_confidence_origin())
        response.status = 200
        return response

    # Disabled (default): the #1015 records stay exactly as they are.
    monkeypatch.delenv("SCALP_JEV_RAW_PAYLOAD", raising=False)
    assert raw_payload_enabled() is False
    _capture_urlopen(monkeypatch, ok)
    request_jev(_diagnostic_call_payload())
    assert _raw_lines(diagnostic_log) == []

    # Enabled: the raw fields that carry the confidence are recorded.
    monkeypatch.setenv("SCALP_JEV_RAW_PAYLOAD", "1")
    assert raw_payload_enabled() is True
    _capture_urlopen(monkeypatch, ok)
    request_jev(_diagnostic_call_payload())
    lines = _raw_lines(diagnostic_log)
    assert len(lines) == 1
    raw = lines[0]
    assert "side_confidence=0.31" in raw
    assert "choice_probability=0.33" in raw
    assert '"BUY":0.33' in raw and '"SELL":0.6' in raw
    assert "expected_move_score=" in raw
    assert "noul=0.42" in raw


def test_raw_payload_record_has_no_secret_and_no_exact_account_value(monkeypatch, diagnostic_log):
    monkeypatch.setenv("JEV_API_KEY", "super-secret-jev-token")
    monkeypatch.setenv("SCALP_JEV_RAW_PAYLOAD", "true")

    def ok(_req, _timeout, _captured):
        response = _FakeHttpResponse(
            _reply_with_confidence_origin()
            | {"usage": {"input_tokens": 296}, "account": {"balance": "77.5"}}
        )
        response.status = 200
        return response

    _capture_urlopen(monkeypatch, ok)
    request_jev(_diagnostic_call_payload(inventory_btc="0.12345678", t="77.5"))
    text = diagnostic_log.read_text(encoding="utf-8")
    assert "super-secret-jev-token" not in text
    assert "Bearer" not in text
    assert "0.12345678" not in text
    assert "77.5" not in text
    assert "input_tokens" not in text


def test_log_call_raw_never_writes_an_unbounded_payload(diagnostic_log):
    huge = {"answers": {"side": {"choice": "BUY", "probabilities": {"B" * 5000: 0.1}}}}
    log_call_raw(call_id="deadbeef", raw=huge)
    line = _raw_lines(diagnostic_log)[0]
    assert len(line) < 1200
