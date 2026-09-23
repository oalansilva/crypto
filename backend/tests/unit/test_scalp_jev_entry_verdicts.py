"""Card #1028 — entry-gate verdicts, confidence origin, model version, toxicity
band, call timeout and non-regression of the decision (log only).

The visible contract proved here:

- a cycle with a model reply leaves **one** record with the verdict of every
  reply-fed entry gate (``hurdle``, ``regime``, ``toxic_book``,
  ``low_confidence``, ``jev_late``, ``hold``), even when an earlier gate closed
  the cycle;
- the record states the origin of the confidence used (``reply_field`` /
  ``choice_probability`` / ``none``) and the version that answered;
- the toxicity band only labels the record (the 0.5 cut-off still decides);
- a slow reply (1.5 s..3 s) is recorded and the cycle is still refused as late;
- with the same input the decision is unchanged.
"""

from __future__ import annotations

import logging
import re
import uuid
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import ScalpFill, ScalpUserState, UserExchangeCredential
from app.services import scalp_jev
from app.services.scalp_engine import (
    CONFIDENCE_MIN,
    JEV_CALL_TIMEOUT_MS,
    JEV_LATE_MS,
    JevSignal,
    decide_cycle,
    reply_gate_verdicts,
)
from app.services.scalp_jev import (
    _DEFAULT_JEV_MODEL,
    _map_systemone,
    jev_model,
    noul_label,
    request_jev,
)
from app.services.scalp_jev_log import (
    TailTruncatingFileHandler,
    logger as diagnostic_logger,
)
from app.services.scalp_service import set_switch, tick_user
from test_scalp_direcional_jev import (
    FakeExchange,
    _FakeHttpResponse,
    _add_key,
    _book,
    _capture_urlopen,
    _diagnostic_call_payload,
    _move_bp_to_score,
    _seed_stream_for_jev,
    _systemone_response,
)


@pytest.fixture(autouse=True)
def _scalp_stream_memory():
    _seed_stream_for_jev()
    yield
    from app.services.scalp_btcusdt_stream import get_scalp_btcusdt_memory

    get_scalp_btcusdt_memory().reset_for_tests()


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


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _lines_with(path: Path, needle: str) -> list[str]:
    return [line for line in _text(path).splitlines() if needle in line]


def _cycle_lines(path: Path) -> list[str]:
    return [line for line in _text(path).splitlines() if "scalp cycle" in line]


def _reply(**overrides) -> dict:
    return _systemone_response(**overrides)


def _green_reply(**overrides) -> dict:
    values = dict(side="BUY", confidence=0.9, move_bp=35.0, toxic=0.1)
    values.update(overrides)
    return _systemone_response(**values)


def _arming(scalp_db, user_id: str, monkeypatch, *, confidence_min: str | None = None):
    _add_key(scalp_db, user_id)
    monkeypatch.setenv("JEV_API_KEY", "secret-1028")
    if confidence_min is None:
        monkeypatch.delenv("SCALP_CONFIDENCE_MIN", raising=False)
    else:
        monkeypatch.setenv("SCALP_CONFIDENCE_MIN", confidence_min)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    return fx


def _tick(scalp_db, user_id: str, fx: FakeExchange, **overrides):
    values = dict(
        exchange=fx,
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    values.update(overrides)
    return tick_user(scalp_db, user_id, **values)


# --- verdicts of every reply-fed gate in the same record -------------------


def test_confidence_refusal_records_every_reply_gate_verdict(scalp_db, diagnostic_log, monkeypatch):
    user_id = str(uuid.uuid4())
    fx = _arming(scalp_db, user_id, monkeypatch)
    _capture_urlopen(
        monkeypatch,
        lambda _r, _t, _c: _FakeHttpResponse(_reply(confidence=0.1, move_bp=35.0, toxic=0.1)),
    )

    result = _tick(scalp_db, user_id, fx)
    assert result.sent is False
    assert result.skipped == "low_confidence"

    lines = _cycle_lines(diagnostic_log)
    assert len(lines) == 1, "one record per cycle"
    line = lines[0]
    # The #1025 ruler regex must keep matching: user= then skip_reason= (adjacent).
    matched = re.search(r"scalp cycle refused user=(\S+) skip_reason=(\S+)", line)
    assert matched is not None
    assert matched.group(1) == user_id
    assert matched.group(2) == "low_confidence"
    # Every reply-fed gate carries exactly one verdict, even the later ones.
    for token in (
        "jev_late=pass",
        "hold=pass",
        "low_confidence=fail",
        "hurdle=pass",
        "regime=pass",
        "toxic_book=pass",
    ):
        assert token in line
    assert "model=jev-1.13.0" in line
    assert "confidence=0.1 confidence_origin=reply_field" in line
    assert "noul=0.1 noul_label=not_toxic" in line
    assert "book_toxic=False" in line


def test_earlier_refusal_still_shows_the_later_failing_gates(scalp_db, diagnostic_log, monkeypatch):
    user_id = str(uuid.uuid4())
    fx = _arming(scalp_db, user_id, monkeypatch)
    # 5 bp: below cost and below cost-with-slack; noul 0.9: toxic. Confidence 0.9 passes.
    _capture_urlopen(
        monkeypatch,
        lambda _r, _t, _c: _FakeHttpResponse(_reply(confidence=0.9, move_bp=5.0, toxic=0.9)),
    )

    result = _tick(scalp_db, user_id, fx)
    assert result.sent is False
    assert result.skipped == "hurdle", "the first refusal is still the first refusal"

    line = _cycle_lines(diagnostic_log)[0]
    assert "skip_reason=hurdle" in line
    assert "hurdle=fail" in line
    assert "regime=fail" in line
    assert "toxic_book=fail" in line
    assert "low_confidence=pass" in line


def test_sent_cycle_leaves_the_verdict_record_with_not_applicable_gate(
    scalp_db, diagnostic_log, monkeypatch
):
    user_id = str(uuid.uuid4())
    fx = _arming(scalp_db, user_id, monkeypatch, confidence_min="none")
    _capture_urlopen(
        monkeypatch,
        lambda _r, _t, _c: _FakeHttpResponse(_reply(confidence=0.01, move_bp=35.0, toxic=0.1)),
    )

    result = _tick(scalp_db, user_id, fx)
    assert result.sent is True
    assert result.skipped is None

    line = _cycle_lines(diagnostic_log)[0]
    assert f"scalp cycle sent user={user_id} skip_reason=none" in line
    assert "low_confidence=not_applicable" in line
    assert "hurdle=pass" in line
    assert "regime=pass" in line
    assert "toxic_book=pass" in line
    assert "jev_late=pass" in line and "hold=pass" in line


def test_pre_call_refusal_keeps_the_old_record_shape(scalp_db, diagnostic_log, monkeypatch):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    # switch off (default): a pre-call close without a model reply.
    result = _tick(scalp_db, user_id, FakeExchange())
    assert result.skipped == "switch_off"
    line = _cycle_lines(diagnostic_log)[0]
    assert line.rstrip().endswith(f"scalp cycle refused user={user_id} skip_reason=switch_off")
    assert "model=" not in line


# --- origin of the confidence ----------------------------------------------


def test_side_confidence_origin_is_produced_with_the_value():
    reply_field = _map_systemone(
        {"answers": {"side": {"choice": "BUY", "confidence": 0.31}}}, latency_ms=1
    )
    assert (reply_field.confidence, reply_field.confidence_origin) == (
        Decimal("0.31"),
        "reply_field",
    )

    from_probability = _map_systemone(
        {"answers": {"side": {"choice": "BUY", "probabilities": {"BUY": 0.42}}}}, latency_ms=1
    )
    assert (from_probability.confidence, from_probability.confidence_origin) == (
        Decimal("0.42"),
        "choice_probability",
    )

    none_origin = _map_systemone({"answers": {"side": {"choice": "BUY"}}}, latency_ms=1)
    assert (none_origin.confidence, none_origin.confidence_origin) == (
        Decimal("0"),
        "none",
    )


def test_return_and_cycle_records_state_the_confidence_origin(
    scalp_db, diagnostic_log, monkeypatch
):
    user_id = str(uuid.uuid4())
    fx = _arming(scalp_db, user_id, monkeypatch)
    _capture_urlopen(
        monkeypatch,
        lambda _r, _t, _c: _FakeHttpResponse(
            _reply(
                confidence=None,
                move_bp=35.0,
                toxic=0.1,
                probabilities={"BUY": 0.55, "SELL": 0.3, "HOLD": 0.15},
            )
        ),
    )

    result = _tick(scalp_db, user_id, fx)
    assert result.skipped == "low_confidence", "the chosen probability decides"

    returned = _lines_with(diagnostic_log, "call return")[0]
    assert "confidence_origin=choice_probability" in returned
    assert "confidence=0.55" in returned, "the BUY probability of the fixture"

    cycle = _cycle_lines(diagnostic_log)[0]
    assert "confidence=0.55 confidence_origin=choice_probability" in cycle


def test_return_and_cycle_records_state_origin_none_without_value(
    scalp_db, diagnostic_log, monkeypatch
):
    user_id = str(uuid.uuid4())
    fx = _arming(scalp_db, user_id, monkeypatch)
    reply = {
        "model": "jev-1.13.0",
        "answers": {
            "side": {"type": "choice", "choice": "BUY"},
            "expected_move_bp": {"type": "score", "score": _move_bp_to_score(35.0)},
            "book_toxic": {"type": "noul", "noul": 0.1},
        },
    }
    _capture_urlopen(monkeypatch, lambda _r, _t, _c: _FakeHttpResponse(reply))

    result = _tick(scalp_db, user_id, fx)
    assert result.skipped == "low_confidence"

    returned = _lines_with(diagnostic_log, "call return")[0]
    assert "confidence_origin=none" in returned
    cycle = _cycle_lines(diagnostic_log)[0]
    assert "confidence=0 confidence_origin=none" in cycle


# --- version of the model ---------------------------------------------------


def test_answered_model_version_is_recorded_without_the_raw_opt_in(
    scalp_db, diagnostic_log, monkeypatch
):
    user_id = str(uuid.uuid4())
    fx = _arming(scalp_db, user_id, monkeypatch)
    monkeypatch.delenv("SCALP_JEV_RAW_PAYLOAD", raising=False)
    _capture_urlopen(monkeypatch, lambda _r, _t, _c: _FakeHttpResponse(_green_reply()))

    result = _tick(scalp_db, user_id, fx)
    assert result.sent is True

    assert _lines_with(diagnostic_log, "call raw") == []
    returned = _lines_with(diagnostic_log, "call return")[0]
    assert "model=jev-1.13.0" in returned
    cycle = _cycle_lines(diagnostic_log)[0]
    assert "model=jev-1.13.0" in cycle


def test_reply_without_model_version_records_unknown(scalp_db, diagnostic_log, monkeypatch):
    user_id = str(uuid.uuid4())
    fx = _arming(scalp_db, user_id, monkeypatch)
    reply = _green_reply()
    reply.pop("model")
    _capture_urlopen(monkeypatch, lambda _r, _t, _c: _FakeHttpResponse(reply))

    result = _tick(scalp_db, user_id, fx)
    assert result.sent is True

    assert "model=unknown" in _lines_with(diagnostic_log, "call return")[0]
    assert "model=unknown" in _cycle_lines(diagnostic_log)[0]


def test_pinned_model_never_falls_back_to_the_alias(monkeypatch):
    monkeypatch.delenv("SCALP_JEV_MODEL", raising=False)
    assert _DEFAULT_JEV_MODEL == "jev-1.13.0"
    assert jev_model() == _DEFAULT_JEV_MODEL

    monkeypatch.setenv("SCALP_JEV_MODEL", "jev-9.9.9")
    assert jev_model() == "jev-9.9.9"

    for raw in ("", "   ", "jev-latest", "JEV-LATEST"):
        monkeypatch.setenv("SCALP_JEV_MODEL", raw)
        assert jev_model() == _DEFAULT_JEV_MODEL
        assert jev_model() != "jev-latest"


def test_request_body_carries_the_pinned_override(monkeypatch):
    monkeypatch.setenv("JEV_API_KEY", "k")
    monkeypatch.setenv("SCALP_JEV_MODEL", "jev-9.9.9")
    captured = _capture_urlopen(monkeypatch, lambda _r, _t, _c: _FakeHttpResponse(_green_reply()))
    request_jev(_diagnostic_call_payload())
    assert captured["body"]["model"] == "jev-9.9.9"
    assert captured["body"]["model"] != "jev-latest"


# --- toxicity band (label only) ---------------------------------------------


def test_toxicity_labels_and_decision_value_are_unchanged():
    for noul, expected_label, expected_decision in (
        (0.39, "not_toxic", False),
        (0.4, "indeterminate", False),
        (0.45, "indeterminate", False),
        (0.5, "indeterminate", True),
        (0.6, "indeterminate", True),
        (0.61, "toxic", True),
    ):
        signal = _map_systemone({"answers": {"book_toxic": {"noul": noul}}}, latency_ms=1)
        assert signal.noul_label == expected_label, noul
        assert signal.book_toxic is expected_decision, noul

    assert _map_systemone({"answers": {}}, latency_ms=1).noul_label == "unknown"
    assert noul_label(None) == "unknown"


def test_indeterminate_reading_keeps_today_decision(scalp_db, diagnostic_log, monkeypatch):
    user_id = str(uuid.uuid4())
    fx = _arming(scalp_db, user_id, monkeypatch)
    _capture_urlopen(
        monkeypatch,
        lambda _r, _t, _c: _FakeHttpResponse(_reply(confidence=0.9, move_bp=35.0, toxic=0.45)),
    )

    result = _tick(scalp_db, user_id, fx)
    assert result.sent is True, "0.45 is not refused by the 0.5 cut-off"

    cycle = _cycle_lines(diagnostic_log)[0]
    assert "noul=0.45 noul_label=indeterminate" in cycle
    assert "book_toxic=False" in cycle


def test_band_boundary_0_5_still_refuses(scalp_db, diagnostic_log, monkeypatch):
    user_id = str(uuid.uuid4())
    fx = _arming(scalp_db, user_id, monkeypatch)
    _capture_urlopen(
        monkeypatch,
        lambda _r, _t, _c: _FakeHttpResponse(_reply(confidence=0.9, move_bp=35.0, toxic=0.5)),
    )

    result = _tick(scalp_db, user_id, fx)
    assert result.sent is False
    assert result.skipped == "toxic_book"

    cycle = _cycle_lines(diagnostic_log)[0]
    assert "noul=0.5 noul_label=indeterminate" in cycle
    assert "book_toxic=True" in cycle


# --- timeout 3 s with the 1.5 s late refusal --------------------------------


def test_slow_reply_between_late_and_timeout_is_recorded_and_still_refused(
    scalp_db, diagnostic_log, monkeypatch
):
    user_id = str(uuid.uuid4())
    fx = _arming(scalp_db, user_id, monkeypatch)

    class _Clock:
        def __init__(self, start: float, end: float) -> None:
            self._values = [start, end]
            self._last = end

        def perf_counter(self) -> float:
            if self._values:
                self._last = self._values.pop(0)
            return self._last

    # The call takes 2.0 s: above the 1.5 s late gate, within the 3 s timeout.
    monkeypatch.setattr(scalp_jev, "time", _Clock(100.0, 102.0))
    captured = _capture_urlopen(monkeypatch, lambda _r, _t, _c: _FakeHttpResponse(_green_reply()))

    result = _tick(scalp_db, user_id, fx)
    assert captured["timeout"] == JEV_CALL_TIMEOUT_MS / 1000.0 == 3.0
    assert result.sent is False
    assert result.skipped == "jev_late", "the late gate is unchanged"

    text = _text(diagnostic_log)
    assert "call error" not in text, "the reply arrived instead of a transport error"
    returned = _lines_with(diagnostic_log, "call return")[0]
    assert "latency_ms=2000" in returned
    assert "status=200" in returned

    cycle = _cycle_lines(diagnostic_log)[0]
    assert "skip_reason=jev_late" in cycle
    assert "jev_late=fail" in cycle
    assert "model=jev-1.13.0" in cycle
    assert JEV_LATE_MS == 1500


# --- non-regression of the decision -----------------------------------------


def _signal(**overrides) -> JevSignal:
    values = dict(
        side="BUY",
        confidence=Decimal("0.9"),
        expected_move_bp=Decimal("35"),
        book_toxic=False,
        latency_ms=50,
    )
    values.update(overrides)
    return JevSignal(**values)


def _decide(jev: JevSignal):
    return decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=JEV_CALL_TIMEOUT_MS * 10,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=jev,
    )


@pytest.mark.parametrize(
    "jev,expected_send,expected_skip,expected_late,expected_toxic",
    (
        (_signal(confidence=Decimal("0.5")), False, "low_confidence", "pass", "pass"),
        (_signal(expected_move_bp=Decimal("10")), False, "hurdle", "pass", "pass"),
        (_signal(expected_move_bp=Decimal("25")), False, "regime", "pass", "pass"),
        (_signal(book_toxic=True), False, "toxic_book", "pass", "fail"),
        (_signal(latency_ms=JEV_LATE_MS + 500), False, "jev_late", "fail", "pass"),
        (_signal(side=None), False, "hold", "pass", "pass"),
        (_signal(), True, None, "pass", "pass"),
    ),
)
def test_same_input_same_decision(jev, expected_send, expected_skip, expected_late, expected_toxic):
    intent = _decide(jev)

    assert intent.send is expected_send
    assert intent.skip_reason == expected_skip
    assert intent.gate_verdicts is not None
    assert intent.gate_verdicts.jev_late == expected_late
    assert intent.gate_verdicts.toxic_book == expected_toxic
    # The side-effect map is exactly the independent recomputation: it never
    # enters the decision above.
    assert intent.gate_verdicts == reply_gate_verdicts(
        jev=jev, confidence_min=CONFIDENCE_MIN, fee_bp=Decimal("10"), spread_bp=Decimal("0")
    )


def test_no_reply_has_no_verdict_map():
    intent = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=None,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=None,
    )
    assert intent.skip_reason == "need_jev"
    assert intent.gate_verdicts is None


# --- no secret and no exact account value -----------------------------------


def test_verdict_records_carry_no_secret_or_exact_account_value(
    scalp_db, diagnostic_log, monkeypatch
):
    user_id = str(uuid.uuid4())
    fx = _arming(scalp_db, user_id, monkeypatch)
    monkeypatch.setenv("JEV_API_KEY", "super-secret-1028")
    _capture_urlopen(monkeypatch, lambda _r, _t, _c: _FakeHttpResponse(_green_reply()))

    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        free_usdt=Decimal("77.531"),
        free_btc=Decimal("0.01234567"),
        book=_book(),
    )
    assert result.sent is True

    text = _text(diagnostic_log)
    assert "super-secret-1028" not in text
    assert "Bearer" not in text
    assert "77.531" not in text
    assert "0.01234567" not in text
