"""Card #1025 — C: confidence gate by env and the opt-in raw payload record."""

from __future__ import annotations

import json
import logging
from decimal import Decimal
from pathlib import Path

import pytest

from app.services.scalp_engine import (
    CLOSED_REGIME_SKIP,
    CONFIDENCE_MIN,
    CONFIDENCE_POLICY_CLOSED,
    CONFIDENCE_POLICY_NUMERIC,
    CONFIDENCE_POLICY_OFF,
    REGIME_ACTIVE,
    REGIME_CALM,
    REGIME_UNKNOWN,
    Book,
    ConfidencePolicy,
    JevSignal,
    decide_cycle,
)
from app.services.scalp_jev import request_jev
from app.services.scalp_jev_log import (
    TailTruncatingFileHandler,
    log_call_raw,
    logger as diagnostic_logger,
    raw_payload_enabled,
)
from app.services.scalp_service import (
    _confidence_in_use_token,
    _confidence_min,
    _confidence_policy_for,
    _regime_boundary_bp,
    market_regime_for,
)
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


# --- Card #1030: confidence policy per market regime -------------------------


def _signal_with(*, confidence: Decimal, expected_move_bp: Decimal = Decimal("60")) -> JevSignal:
    return JevSignal(
        side="BUY",
        confidence=confidence,
        expected_move_bp=expected_move_bp,
        book_toxic=False,
        latency_ms=50,
    )


def _with_policy(
    *, policy: ConfidencePolicy, confidence: Decimal, expected_move_bp: Decimal = Decimal("60")
):
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
        jev=_signal_with(confidence=confidence, expected_move_bp=expected_move_bp),
        confidence_policy=policy,
    )


def test_numeric_policy_applies_that_regime_value():
    calm = ConfidencePolicy(
        kind=CONFIDENCE_POLICY_NUMERIC, value=Decimal("0.2"), regime=REGIME_CALM
    )
    allowed = _with_policy(policy=calm, confidence=Decimal("0.25"))
    assert allowed.send is True and allowed.skip_reason is None
    assert allowed.market_regime == REGIME_CALM
    assert allowed.confidence_policy_kind == CONFIDENCE_POLICY_NUMERIC
    assert allowed.gate_verdicts.low_confidence == "pass"

    active = ConfidencePolicy(
        kind=CONFIDENCE_POLICY_NUMERIC, value=Decimal("0.3"), regime=REGIME_ACTIVE
    )
    refused = _with_policy(policy=active, confidence=Decimal("0.25"))
    assert refused.send is False
    assert refused.skip_reason == "low_confidence"
    assert refused.market_regime == REGIME_ACTIVE
    assert refused.gate_verdicts.low_confidence == "fail"


def test_turned_off_policy_produces_no_low_confidence():
    off = ConfidencePolicy(kind=CONFIDENCE_POLICY_OFF, value=None, regime=REGIME_CALM)
    allowed = _with_policy(policy=off, confidence=Decimal("0.01"))
    assert allowed.send is True and allowed.skip_reason is None
    assert allowed.confidence_policy_kind == CONFIDENCE_POLICY_OFF
    assert allowed.gate_verdicts.low_confidence == "not_applicable"


def test_closed_policy_closes_with_its_own_token_and_keeps_the_verdicts():
    closed = ConfidencePolicy(kind=CONFIDENCE_POLICY_CLOSED, value=None, regime=REGIME_ACTIVE)
    intent = _with_policy(policy=closed, confidence=Decimal("0.99"))
    assert intent.send is False
    assert intent.skip_reason == CLOSED_REGIME_SKIP
    assert intent.skip_reason not in {"regime", "low_confidence"}
    assert intent.market_regime == REGIME_ACTIVE
    assert intent.confidence_policy_kind == CONFIDENCE_POLICY_CLOSED
    assert intent.gate_verdicts.low_confidence == "not_applicable"
    # The other reply-fed verdicts are still computed (non-regression).
    assert intent.gate_verdicts.hurdle == "pass"
    assert intent.gate_verdicts.regime == "pass"
    assert intent.gate_verdicts.toxic_book == "pass"


def test_the_engine_default_policy_is_still_the_1025_contract():
    # Sem política por parâmetro o motor mantém o contrato #1025 (alias).
    assert _cycle(confidence_min=CONFIDENCE_MIN, confidence=Decimal("0.39")).skip_reason == (
        "low_confidence"
    )
    assert _cycle(confidence_min=None, confidence=Decimal("0.01")).skip_reason is None


def test_policy_is_numeric_off_or_closed_per_regime(monkeypatch):
    boundary = Decimal("0.05")
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN_CALM", "0.3")
    calm = _confidence_policy_for(regime=REGIME_CALM, boundary_bp=boundary)
    assert (calm.kind, calm.value, calm.regime) == (
        CONFIDENCE_POLICY_NUMERIC,
        Decimal("0.3"),
        REGIME_CALM,
    )
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN_CALM", "0.2")
    assert _confidence_policy_for(regime=REGIME_CALM, boundary_bp=boundary).value == Decimal("0.2")
    for raw in ("none", "off", "disabled", "NONE", "Off"):
        monkeypatch.setenv("SCALP_CONFIDENCE_MIN_ACTIVE", raw)
        active = _confidence_policy_for(regime=REGIME_ACTIVE, boundary_bp=boundary)
        assert active.kind == CONFIDENCE_POLICY_OFF, raw
        assert active.threshold is None
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN_ACTIVE", "closed")
    assert (
        _confidence_policy_for(regime=REGIME_ACTIVE, boundary_bp=boundary).kind
        == CONFIDENCE_POLICY_CLOSED
    )


def test_absent_or_invalid_policy_fails_closed(monkeypatch):
    boundary = Decimal("0.05")
    for raw in (None, "", "abc", "-1", "1.5", "2", "nan", "NaN", "inf", "-inf"):
        if raw is None:
            monkeypatch.delenv("SCALP_CONFIDENCE_MIN_CALM", raising=False)
        else:
            monkeypatch.setenv("SCALP_CONFIDENCE_MIN_CALM", raw)
        policy = _confidence_policy_for(regime=REGIME_CALM, boundary_bp=boundary)
        assert policy.kind == CONFIDENCE_POLICY_CLOSED, raw
        assert policy.threshold is None


def test_no_boundary_closes_both_regimes(monkeypatch):
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN_CALM", "0.2")
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN_ACTIVE", "0.2")
    for regime in (REGIME_CALM, REGIME_ACTIVE, REGIME_UNKNOWN):
        assert _confidence_policy_for(regime=regime, boundary_bp=None).kind == (
            CONFIDENCE_POLICY_CLOSED
        )


def test_market_regime_from_the_window_sigma_against_the_boundary():
    assert market_regime_for(Decimal("0.04"), Decimal("0.05")) == REGIME_CALM
    assert market_regime_for(Decimal("0.05"), Decimal("0.05")) == REGIME_ACTIVE
    assert market_regime_for(Decimal("0.06"), Decimal("0.05")) == REGIME_ACTIVE
    assert market_regime_for(None, Decimal("0.05")) == REGIME_UNKNOWN
    assert market_regime_for(Decimal("0.05"), None) == REGIME_UNKNOWN
    assert market_regime_for(Decimal("nan"), Decimal("0.05")) == REGIME_UNKNOWN


def test_regime_boundary_from_env_fails_closed(monkeypatch):
    monkeypatch.delenv("SCALP_REGIME_BOUNDARY_BP", raising=False)
    assert _regime_boundary_bp() is None
    for raw in ("abc", "nan", "inf", "-1", ""):
        monkeypatch.setenv("SCALP_REGIME_BOUNDARY_BP", raw)
        assert _regime_boundary_bp() is None, raw
    monkeypatch.setenv("SCALP_REGIME_BOUNDARY_BP", "0.05")
    assert _regime_boundary_bp() == Decimal("0.05")


def test_the_value_in_use_is_preserved_and_reported(monkeypatch):
    monkeypatch.delenv("SCALP_CONFIDENCE_MIN", raising=False)
    assert _confidence_in_use_token() == "0.7"
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN", "0.42")
    assert _confidence_in_use_token() == "0.42"
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN", "none")
    assert _confidence_in_use_token() == "off"
