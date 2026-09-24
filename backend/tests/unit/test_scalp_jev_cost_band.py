"""Card #1029 — the model reply as an observable band, not an interpolated bp.

Visible contract proved here (the three capabilities of the change):

* ``scalp-jev-cost-band``: the entry decision compares the **band of the level
  already reached** with the **real cost of the cycle** (below cost / covers
  cost / covers with slack), reusing the existing cost predicates; a position
  between two levels credits the lower one (rounded down); the question keeps
  the ten ordered options and labels each with its band.
* ``scalp-jev-scale-record``: the call return and the cycle record show the
  band and the position and never a bp derived by linear interpolation.
* ``scalp-jev-window-ab``: the read-only A/B of the state window declares the
  sample size, uses one fixed model version, and only concludes with 30+
  non-overlapping 900 s windows per arm — otherwise ``amostra insuficiente``.
"""

from __future__ import annotations

import importlib.util
import logging
import re
import uuid
from datetime import datetime, timedelta
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
    JevSignal,
    decide_cycle,
    reply_gate_verdicts,
)
from app.services.scalp_jev import (
    _EXPECTED_MOVE_BP_LEVELS_BP,
    _credited_level_bp,
    _credited_level_index,
    _expected_move_bp_criteria,
    _map_systemone,
    ab_arm,
    request_jev,
)
from app.services.scalp_jev_log import (
    TailTruncatingFileHandler,
    logger as diagnostic_logger,
)
from app.services.scalp_service import set_switch, tick_user
from app.services.scalp_window import (
    MOVE_BAND_BELOW_COST,
    MOVE_BAND_COVERS_COST,
    MOVE_BAND_COVERS_WITH_SLACK,
    entry_hurdle_bp,
    entry_hurdle_bp_with_slack,
    move_band,
    passes_entry_hurdle,
    passes_regime_gate,
)
from test_scalp_direcional_jev import (
    FakeExchange,
    _FakeHttpResponse,
    _add_key,
    _book,
    _capture_urlopen,
    _diagnostic_call_payload,
    _seed_stream_for_jev,
    _systemone_response,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
AB_SCRIPT_PATH = REPO_ROOT / "scripts" / "scalp_jev_window_ab.py"


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


def _lines_with(path: Path, needle: str) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if needle in line]


def _score_reply(score: float, *, confidence: float = 0.9, toxic: float = 0.1) -> dict:
    """Reply with a raw (possibly fractional) ladder score, not a ladder move."""
    return {
        "model": "jev-1.13.0",
        "answers": {
            "side": {"type": "choice", "choice": "BUY", "confidence": confidence},
            "expected_move_bp": {"type": "score", "score": score},
            "book_toxic": {"type": "noul", "noul": toxic},
        },
    }


def _cycle(
    *,
    expected_move_bp: Decimal,
    fee_bp: str = "10",
    spread_bp: str = "0.1",
    confidence: str = "0.9",
    confidence_min=CONFIDENCE_MIN,
):
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
        jev=JevSignal(
            side="BUY",
            confidence=Decimal(confidence),
            expected_move_bp=expected_move_bp,
            book_toxic=False,
            latency_ms=50,
        ),
        fee_bp=Decimal(fee_bp),
        spread_bp=Decimal(spread_bp),
        confidence_min=confidence_min,
    )


BAND_TEXT = {
    MOVE_BAND_BELOW_COST: "below cost",
    MOVE_BAND_COVERS_COST: "covers cost",
    MOVE_BAND_COVERS_WITH_SLACK: "covers cost with slack",
}


# --- scalp-jev-cost-band: the level already reached -------------------------


def test_a_position_between_two_levels_credits_the_level_already_reached():
    assert (_credited_level_index(4.5), _credited_level_bp(4.5)) == (4, Decimal("20"))
    # The false interpolation artifacts of the Design never come back.
    assert (_credited_level_index(3.07), _credited_level_bp(3.07)) == (3, Decimal("15"))
    assert (_credited_level_index(2.86), _credited_level_bp(2.86)) == (2, Decimal("10"))
    assert (_credited_level_index(0.92), _credited_level_bp(0.92)) == (0, Decimal("0"))
    # The ends of the scale clip; the reading is always one of the ten levels.
    for raw, expected_index, expected_bp in (
        (-3, 0, 0),
        (0, 0, 0),
        (9, 9, 80),
        (9.9, 9, 80),
        (12, 9, 80),
    ):
        assert _credited_level_index(raw) == expected_index
        assert _credited_level_bp(raw) == Decimal(expected_bp)
        assert _credited_level_bp(raw) in _EXPECTED_MOVE_BP_LEVELS_BP


def test_the_boundaries_follow_the_cycle_rate_and_the_existing_predicates():
    # DEV cost of the #1025 evidence: fee 10 bp/leg, spread 0.1 → 20.1 / 30.15.
    hurdle = entry_hurdle_bp(Decimal("10"), Decimal("0.1"))
    slack = entry_hurdle_bp_with_slack(Decimal("10"), Decimal("0.1"))
    assert hurdle == Decimal("20.10") and slack == Decimal("30.15")
    assert move_band(Decimal("15"), Decimal("10"), Decimal("0.1")) == MOVE_BAND_BELOW_COST
    assert move_band(Decimal("25"), Decimal("10"), Decimal("0.1")) == MOVE_BAND_COVERS_COST
    assert move_band(Decimal("35"), Decimal("10"), Decimal("0.1")) == MOVE_BAND_COVERS_WITH_SLACK
    # The boundaries are the cycle's own rate: the same level 25 flips band on a
    # cheaper cycle (fee 5, spread 0 → 10 / 15).
    assert move_band(Decimal("25"), Decimal("5"), Decimal("0")) == MOVE_BAND_COVERS_WITH_SLACK
    assert move_band(Decimal("5"), Decimal("5"), Decimal("0")) == MOVE_BAND_BELOW_COST
    # No new threshold: the reused semantics are the strict `>` and the `>=`.
    assert hurdle not in _EXPECTED_MOVE_BP_LEVELS_BP
    assert move_band(hurdle, Decimal("10"), Decimal("0.1")) == MOVE_BAND_BELOW_COST
    assert move_band(slack, Decimal("10"), Decimal("0.1")) == MOVE_BAND_COVERS_WITH_SLACK
    for level in _EXPECTED_MOVE_BP_LEVELS_BP:
        bp = Decimal(level)
        expected = (
            MOVE_BAND_COVERS_WITH_SLACK
            if passes_regime_gate(bp, Decimal("10"), Decimal("1.5"))
            else (
                MOVE_BAND_COVERS_COST
                if passes_entry_hurdle(bp, Decimal("10"), Decimal("1.5"))
                else MOVE_BAND_BELOW_COST
            )
        )
        assert move_band(bp, Decimal("10"), Decimal("1.5")) == expected


def test_below_cost_is_refused_by_cost_with_one_reason_without_the_confidence_gate():
    # fee 10, spread 0.1 → hurdle 20.1, slack 30.15.
    below = _cycle(expected_move_bp=Decimal("15"))
    assert below.send is False and below.skip_reason == "hurdle", "below cost, one reason"
    covers = _cycle(expected_move_bp=Decimal("25"))
    assert covers.send is False and covers.skip_reason == "regime", "clears cost, no slack"
    with_slack = _cycle(expected_move_bp=Decimal("35"))
    assert with_slack.send is True and with_slack.skip_reason is None

    # With the confidence gate removed, a position below cost still closes by
    # cost only (never by confidence) — card #1029, task 1.4.
    gate_off = _cycle(expected_move_bp=Decimal("15"), confidence="0.01", confidence_min=None)
    assert gate_off.send is False and gate_off.skip_reason == "hurdle"
    assert gate_off.gate_verdicts is not None
    assert gate_off.gate_verdicts.low_confidence == "not_applicable"
    assert gate_off.gate_verdicts.hurdle == "fail" and gate_off.gate_verdicts.regime == "fail"

    # With the gate on and failing, the confidence refusal still comes first.
    gate_on = _cycle(expected_move_bp=Decimal("15"), confidence="0.01")
    assert gate_on.skip_reason == "low_confidence"


def test_the_model_sees_the_band_the_decision_reads():
    fee_bp, spread_bp = Decimal("10"), Decimal("1.5")
    criteria = _expected_move_bp_criteria(fee_bp, spread_bp)
    assert len(criteria) == len(_EXPECTED_MOVE_BP_LEVELS_BP) == 10
    assert all("bp (" in label and label.endswith(")") for label in criteria)
    for level, label in zip(_EXPECTED_MOVE_BP_LEVELS_BP, criteria):
        assert label.startswith(f"{level} bp"), "the ordered position stays readable"
        band = move_band(Decimal(level), fee_bp, spread_bp)
        assert label == f"{level} bp ({BAND_TEXT[band]})"


def test_the_answer_is_still_a_position_and_the_band_matches_the_label():
    fee_bp, spread_bp = Decimal("10"), Decimal("1.5")
    criteria = _expected_move_bp_criteria(fee_bp, spread_bp)
    # score 5.0 → level 5 = 25 bp → "covers cost" (hurdle 21.5, slack 32.25).
    signal = _map_systemone(_score_reply(5.0), latency_ms=1, fee_bp=fee_bp, spread_bp=spread_bp)
    assert signal.move_position == 5
    assert signal.move_band == MOVE_BAND_COVERS_COST
    assert criteria[5] == "25 bp (covers cost)"


# --- scalp-jev-scale-record: band + position, never an interpolated bp -------


def test_call_return_records_the_band_and_the_position_without_interpolation(
    monkeypatch, diagnostic_log
):
    monkeypatch.setenv("JEV_API_KEY", "secret-1029")
    _capture_urlopen(monkeypatch, lambda _r, _t, _c: _FakeHttpResponse(_score_reply(3.07)))

    signal = request_jev(_diagnostic_call_payload())

    # The decision value is the exact bp of the credited level, never 15.35.
    assert signal.expected_move_bp == Decimal("15")
    assert signal.move_position == 3
    assert signal.move_band == MOVE_BAND_BELOW_COST

    returned = _lines_with(diagnostic_log, "call return")[0]
    assert "expected_move_bp=15 score=3.07" in returned
    assert "move_band=below_cost move_position=3" in returned
    assert "ab_arm=current" in returned
    # The quantized interpolation artifact is no longer produced.
    for artifact in ("15.35", "14.30", "14.3", "9.60", "9.6", "22.5"):
        assert artifact not in returned
    recorded = re.search(r"expected_move_bp=(\S+)", returned)
    assert recorded is not None
    assert Decimal(recorded.group(1)) in _EXPECTED_MOVE_BP_LEVELS_BP


def test_cycle_record_carries_the_band_and_the_position(scalp_db, diagnostic_log, monkeypatch):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    monkeypatch.setenv("JEV_API_KEY", "secret-1029")
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    _capture_urlopen(monkeypatch, lambda _r, _t, _c: _FakeHttpResponse(_score_reply(2.86)))

    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert result.skipped == "hurdle", "level 2 = 10 bp is below the cycle cost"

    cycle = _lines_with(diagnostic_log, "scalp cycle")[0]
    # #1025 ruler shape preserved: prefix and user=/skip_reason= adjacency.
    assert re.search(r"scalp cycle refused user=(\S+) skip_reason=(\S+)", cycle)
    assert f"scalp cycle refused user={user_id} skip_reason=hurdle" in cycle
    assert "move_band=below_cost move_position=2" in cycle
    assert "ab_arm=current" in cycle
    # A single cost reason, no own token for the lowest band.
    assert "skip_reason=below_cost" not in cycle


def test_no_record_field_carries_an_interpolated_bp(monkeypatch, diagnostic_log):
    monkeypatch.setenv("JEV_API_KEY", "secret-1029")
    _capture_urlopen(monkeypatch, lambda _r, _t, _c: _FakeHttpResponse(_score_reply(0.92)))

    signal = request_jev(_diagnostic_call_payload())
    assert signal.expected_move_bp == Decimal("0"), "level 0 = 0 bp"
    assert signal.move_position == 0
    returned = _lines_with(diagnostic_log, "call return")[0]
    assert "expected_move_bp=0 score=0.92" in returned
    assert "move_band=below_cost move_position=0" in returned, "level 0 is not 'unknown'"
    for artifact in ("9.60", "9.6", "4.60", "4.6"):
        assert artifact not in returned


def test_position_token_keeps_the_valid_level_zero():
    from app.services.scalp_jev_log import position_token

    assert position_token(0) == "0"
    assert position_token(7) == "7"
    assert position_token(None) == "unknown"


def test_legacy_number_fallback_stays_literal_and_outside_the_band_contract(
    monkeypatch, diagnostic_log
):
    """The ``number``/``value`` fallbacks keep today's literal reading (P3)."""
    monkeypatch.setenv("JEV_API_KEY", "secret-1029")
    reply = {
        "model": "jev-1.13.0",
        "answers": {
            "side": {"type": "choice", "choice": "BUY", "confidence": 0.9},
            "expected_move_bp": {"type": "number", "number": 18},
            "book_toxic": {"type": "noul", "noul": 0.1},
        },
    }
    _capture_urlopen(monkeypatch, lambda _r, _t, _c: _FakeHttpResponse(reply))

    signal = request_jev(_diagnostic_call_payload())
    assert signal.expected_move_bp == Decimal("18"), "literal, never a ladder credit"
    assert signal.move_position is None
    assert signal.move_band == "unknown"
    returned = _lines_with(diagnostic_log, "call return")[0]
    assert "expected_move_bp=18" in returned
    assert "move_band=unknown move_position=unknown" in returned


# --- scalp-jev-window-ab: read-only, declared sample, 30-window gate --------


def _load_ab():
    import sys

    spec = importlib.util.spec_from_file_location("scalp_jev_window_ab", AB_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["scalp_jev_window_ab"] = module
    spec.loader.exec_module(module)
    return module


ab = _load_ab()


def _observation(index: int, *, arm: str, confidence: str, model: str = "jev-1.13.0"):
    base = datetime(2026, 9, 23, 0, 0, 0)
    return ab.Observation(
        call_id=f"{arm}-{index}",
        at=base + timedelta(seconds=900 * index),
        arm=arm,
        confidence=Decimal(confidence),
        model=model,
    )


def _report(observations, *, model: str = "jev-1.13.0"):
    return ab.build_report(
        log_path=Path("diag.log"), observations=observations, malformed=0, model=model
    )


def test_ab_declares_the_sample_and_concludes_with_thirty_windows():
    observations = [_observation(i, arm="current", confidence="0.2") for i in range(30)]
    observations += [_observation(i, arm="larger", confidence="0.4") for i in range(30)]
    report, summary = _report(observations)
    assert summary["concludes"] is True
    assert summary["model"] == "jev-1.13.0"
    assert summary["windows"] == {"current": 30, "larger": 30}
    assert summary["observations"] == {"current": 30, "larger": 30}
    assert Decimal(summary["mean_confidence"]["current"]) == Decimal("0.2")
    assert Decimal(summary["mean_confidence"]["larger"]) == Decimal("0.4")
    assert "amostra insuficiente" not in report.lower()
    assert "janela actual" in report and "janela maior" in report


def test_ab_below_thirty_windows_does_not_conclude_and_declares_insufficiency():
    observations = [_observation(i, arm="current", confidence="0.2") for i in range(29)]
    observations += [_observation(i, arm="larger", confidence="0.4") for i in range(29)]
    report, summary = _report(observations)
    assert summary["concludes"] is False
    assert summary["declaration"] == "amostra insuficiente"
    assert "amostra insuficiente" in report.lower()
    assert "não conclui" in report


def test_ab_counts_overlapping_observations_once():
    base = datetime(2026, 9, 23, 0, 0, 0)
    observations = [
        ab.Observation(
            f"c{i}", base + timedelta(seconds=offset), "current", Decimal("0.2"), "jev-1.13.0"
        )
        for i, offset in enumerate((0, 60, 300, 900, 1200))
    ]
    kept = ab.non_overlapping(observations)
    assert [o.call_id for o in kept] == ["c0", "c3"]


def test_ab_excludes_another_model_version_and_declares_it():
    observations = [_observation(i, arm="current", confidence="0.2") for i in range(30)]
    observations += [_observation(i, arm="larger", confidence="0.4") for i in range(30)]
    observations.append(_observation(99, arm="current", confidence="0.9", model="jev-9.9.9"))
    report, summary = _report(observations)
    assert summary["excluded_other_model"] == 1
    assert summary["concludes"] is True
    assert "outra versão de modelo" in report


def test_ab_parses_the_arm_of_the_return_record(tmp_path):
    at = datetime(2026, 9, 23, 13, 30, 0)
    stamp = at.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    log = tmp_path / "diag.log"
    log.write_text(
        f"{stamp} INFO scalp jev call return id=a1 status=200 latency_ms=100 side=BUY "
        "expected_move_bp=25 score=5.0 move_band=covers_cost move_position=5 ab_arm=larger "
        "book_toxic=False confidence=0.31 model=jev-1.13.0\n",
        encoding="utf-8",
    )
    observations, malformed = ab.parse_returns(log)
    assert malformed == 0
    assert len(observations) == 1
    assert observations[0].arm == "larger"
    assert observations[0].confidence == Decimal("0.31")
    assert observations[0].model == "jev-1.13.0"


def test_ab_is_read_only_and_never_changes_the_decision(monkeypatch):
    source = AB_SCRIPT_PATH.read_text(encoding="utf-8").lower()
    for forbidden in (
        "insert into",
        "update ",
        "delete from",
        "create table",
        "to_sql",
        ".commit(",
        "session.add",
        "scalp_loop",
    ):
        assert forbidden not in source

    monkeypatch.setenv("SCALP_JEV_AB_ARM", "current")
    before = _cycle(expected_move_bp=Decimal("25"))
    monkeypatch.setenv("SCALP_JEV_AB_ARM", "larger")
    after = _cycle(expected_move_bp=Decimal("25"))
    assert before.send is False and before.skip_reason == "regime"
    assert after.send is before.send and after.skip_reason == before.skip_reason


def test_ab_arm_label_reads_the_operator_env(monkeypatch):
    monkeypatch.delenv("SCALP_JEV_AB_ARM", raising=False)
    assert ab_arm() == "current"
    for raw in ("larger", "LARGER", " Larger "):
        monkeypatch.setenv("SCALP_JEV_AB_ARM", raw)
        assert ab_arm() == "larger"
    for raw in ("", "current", "anything-else"):
        monkeypatch.setenv("SCALP_JEV_AB_ARM", raw)
        assert ab_arm() == "current"


def test_ab_script_prints_insufficient_sample_for_a_short_log(tmp_path, capsys):
    at = datetime(2026, 9, 23, 13, 30, 0)
    stamp = at.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    log = tmp_path / "diag.log"
    log.write_text(
        f"{stamp} INFO scalp jev call return id=a1 status=200 latency_ms=100 side=BUY "
        "expected_move_bp=25 score=5.0 move_band=covers_cost move_position=5 ab_arm=current "
        "book_toxic=False confidence=0.31 model=jev-1.13.0\n",
        encoding="utf-8",
    )
    code = ab.main(["--log", str(log)])
    assert code == 0
    out = capsys.readouterr().out
    assert "amostra insuficiente" in out.lower()
    assert "não conclui" in out
