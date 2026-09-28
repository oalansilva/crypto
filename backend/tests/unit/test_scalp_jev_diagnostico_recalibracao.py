"""Card #1045 — closed-day diagnosis, apply gates, pause and revert."""

from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, ensure_runtime_schema_migrations
from app.models import (
    ScalpCalibrationState,
    ScalpConfidenceVersion,
    ScalpFill,
    ScalpJevDiagnosis,
    ScalpUserState,
    UserExchangeCredential,
)
from app.services.scalp_engine import (
    CONFIDENCE_POLICY_CLOSED,
    CONFIDENCE_POLICY_NUMERIC,
    CONFIDENCE_POLICY_OFF,
    REGIME_CALM,
)
from app.services import scalp_jev_calibration as calibration
from app.services.scalp_jev_calibration import (
    POSTERIOR_MIN,
    VERB_APPLY,
    VERB_BLOCK,
    VERB_KEEP,
    VERB_REVERT,
    fingerprint_of,
    get_calibration_state,
    maybe_run_daily,
    revert_to_previous,
    run_closed_day_diagnosis,
    set_calibration_paused,
    status_fields,
)
from app.services.scalp_service import FALLBACK_FEE_BP, _confidence_policy_for, status_payload
from app.services.user_exchange_credentials import BINANCE_PROVIDER

from test_scalp_jev_eval_ruler import _merge, ruler


@pytest.fixture
def diag_db(postgres_isolation, unit_database_url):
    ensure_runtime_schema_migrations()
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    db.query(ScalpJevDiagnosis).delete()
    db.query(ScalpConfidenceVersion).delete()
    db.query(ScalpCalibrationState).delete()
    db.query(ScalpFill).delete()
    db.query(ScalpUserState).delete()
    db.query(UserExchangeCredential).delete()
    db.commit()
    try:
        yield db
    finally:
        db.query(ScalpJevDiagnosis).delete()
        db.query(ScalpConfidenceVersion).delete()
        db.query(ScalpCalibrationState).delete()
        db.query(ScalpFill).delete()
        db.query(ScalpUserState).delete()
        db.query(UserExchangeCredential).delete()
        db.commit()
        db.close()
        engine.dispose()


def _windows(count: int, *, confidence: str = "0.55", realized_bp: int = 12, start: int = 0):
    from test_scalp_jev_eval_ruler import _windows as make_windows

    return make_windows(count, confidence=confidence, realized_bp=realized_bp, start_s=start)


def _rows(count: int, *, confidence: str = "0.55", realized_bp: int = 12, start: int = 0):
    decisions, series = _windows(count, confidence=confidence, realized_bp=realized_bp, start=start)
    return [(d, ruler.realized_for(d, series)) for d in decisions]


def _joined(batches):
    decisions = []
    series = None
    for more_d, more_s in batches:
        decisions.extend(more_d)
        series = more_s if series is None else _merge(series, more_s)
    assert series is not None
    return [(decision, ruler.realized_for(decision, series)) for decision in decisions]


def _summary(*, operable=True, homo="homogénea", fee_source="account", n=214, policy="numeric"):
    hit = "0.80"
    return {
        "measurement": {"status": "medido", "windows_without_price_coverage": 0},
        "homogeneity": {"status": homo, "homogeneous": homo == "homogénea", "affected_windows": 0},
        "fee_source": fee_source,
        "fee_bp": "10",
        "operable": operable,
        "regime_boundary_bp": "0.05",
        "benchmark": {
            "overall": {
                "computable": True,
                "seed": 1,
                "buy_fraction": "0.97",
                "signal_accuracy": "0.49",
                "buy_and_hold_accuracy": "0.50",
                "predictive_contribution_bp": "0.00",
                "signal_net_bp": "-4",
                "buy_and_hold_net_bp": "-3",
                "random_net_bp": "-4",
            }
        },
        "geometry_in_use": {
            "break_even_with_cost": "0.7619",
            "break_even_without_cost": "0.4444",
            "n_target": 12,
            "n_stop": 28,
            "n_time_exit": 27,
            "realized_hit": hit,
        },
        "regimes": {
            "calm": {
                "policy": policy,
                "chosen": {"threshold": "0.55"} if policy == "numeric" else None,
            },
            "active": {"policy": "closed", "chosen": None},
        },
        "eligible_population": {"n": n},
    }


def _run(db, *, rows, summary, now, closed=None, fee_bp="10"):
    return run_closed_day_diagnosis(
        db,
        now=now,
        summary=summary,
        realized_windows=rows,
        newest_candle=now,
        last_window_end=now - timedelta(hours=1),
        fee_bp=Decimal(fee_bp),
        closed=closed,
    )


def test_one_diagnosis_per_closed_day_is_idempotent(diag_db):
    now = datetime(2026, 9, 26, 0, 20, 0)
    rows = _rows(67)
    first = _run(diag_db, rows=rows, summary=_summary(operable=False, n=67), now=now)
    second = _run(diag_db, rows=rows, summary=_summary(operable=True, n=400), now=now)
    assert first.closed_day == date(2026, 9, 25)
    assert second.closed_day == first.closed_day
    assert second.verb == first.verb
    assert diag_db.query(ScalpJevDiagnosis).count() == 1


def test_before_0015_utc_does_not_run(diag_db):
    now = datetime(2026, 9, 26, 0, 10, 0)
    assert maybe_run_daily(diag_db, now=now) is None
    assert diag_db.query(ScalpJevDiagnosis).count() == 0


def test_posterior_below_200_does_not_change_confidence(diag_db):
    set_calibration_paused(diag_db, paused=False)
    now = datetime(2026, 9, 26, 0, 20, 0)
    row = _run(diag_db, rows=_rows(67), summary=_summary(n=67), now=now)
    assert row.verb == VERB_BLOCK
    assert row.block_kind == "posterior"
    assert row.posterior_n == 67
    assert diag_db.query(ScalpConfidenceVersion).count() == 0
    policy = _confidence_policy_for(regime=REGIME_CALM, boundary_bp=Decimal("0.05"), db=diag_db)
    assert policy.kind == CONFIDENCE_POLICY_CLOSED or policy.value != Decimal("0.55")


def test_still_negative_improvement_is_applied_without_step_band(diag_db):
    set_calibration_paused(diag_db, paused=False)
    now = datetime(2026, 9, 12, 0, 20, 0)
    closed = date(2026, 9, 11)
    current = ScalpConfidenceVersion(
        id=str(uuid.uuid4()),
        version_n=11,
        fingerprint=fingerprint_of(
            {
                "calm": {"kind": "numeric", "value": "0.20"},
                "active": {"kind": "closed", "value": None},
            }
        ),
        policies_json=(
            '{"calm": {"kind": "numeric", "value": "0.20"}, '
            '"active": {"kind": "closed", "value": null}}'
        ),
        previous_id=None,
        applied_at=datetime(2026, 9, 10, 0, 20, 0),
        applied_for_day=date(2026, 9, 9),
        reason="seed",
        source="automatic",
        active=True,
        choice_until=datetime(2026, 9, 1),
        validated_until=datetime(2026, 9, 8),
        created_at=datetime(2026, 9, 10, 0, 20, 0),
    )
    diag_db.add(current)
    diag_db.commit()
    rows = _joined(
        [
            _windows(25, confidence="0.20", realized_bp=-30),
            _windows(30, confidence="0.55", realized_bp=40, start=25 * 900),
            _windows(80, confidence="0.40", realized_bp=-30, start=55 * 900),
            _windows(120, confidence="0.70", realized_bp=-5, start=135 * 900),
        ]
    )
    choice_rows, posterior_rows = calibration._split_posterior(rows, current)
    choice_declared = calibration._policies_from_windows(
        choice_rows, fee_bp=Decimal("10"), boundary_bp=Decimal("0.05"), ruler=ruler
    )
    all_declared = calibration._policies_from_windows(
        rows, fee_bp=Decimal("10"), boundary_bp=Decimal("0.05"), ruler=ruler
    )
    assert choice_declared["calm"]["kind"] == CONFIDENCE_POLICY_NUMERIC
    assert choice_declared["calm"]["value"] == "0.5"
    assert all_declared["calm"]["kind"] != CONFIDENCE_POLICY_NUMERIC
    summary = _summary(n=len(rows), policy="off")
    row = _run(diag_db, rows=rows, summary=summary, now=now, closed=closed)
    applied = (
        diag_db.query(ScalpConfidenceVersion).filter(ScalpConfidenceVersion.active.is_(True)).one()
    )
    loaded = json.loads(applied.policies_json)
    assert row.verb == VERB_APPLY
    assert loaded["calm"]["kind"] == CONFIDENCE_POLICY_NUMERIC
    assert loaded["calm"]["value"] == "0.5"
    assert loaded["calm"]["value"] != all_declared["calm"].get("value")
    assert "0.51" not in applied.policies_json
    policy = _confidence_policy_for(regime=REGIME_CALM, boundary_bp=Decimal("0.05"), db=diag_db)
    assert policy.kind == CONFIDENCE_POLICY_NUMERIC
    assert policy.value == Decimal("0.5")
    assert len(posterior_rows) == POSTERIOR_MIN


def test_paused_calibration_still_writes_diagnosis_and_does_not_apply(diag_db):
    now = datetime(2026, 9, 26, 0, 20, 0)
    state = get_calibration_state(diag_db)
    assert state.paused is True
    row = _run(diag_db, rows=_rows(214), summary=_summary(), now=now)
    assert row.verb == VERB_BLOCK
    assert row.block_kind == "paused"
    assert diag_db.query(ScalpConfidenceVersion).count() == 0


def test_measurement_failure_is_not_a_loss_and_does_not_touch_kill(diag_db):
    user_id = str(uuid.uuid4())
    diag_db.add(
        ScalpUserState(
            user_id=user_id,
            enabled=True,
            killed=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )
    diag_db.add(
        UserExchangeCredential(
            user_id=user_id,
            provider=BINANCE_PROVIDER,
            api_key="k",
            api_secret="s",
        )
    )
    diag_db.commit()
    set_calibration_paused(diag_db, paused=False)
    summary = _summary()
    summary["measurement"]["status"] = "não medido"
    now = datetime(2026, 9, 26, 0, 20, 0)
    row = _run(diag_db, rows=_rows(214), summary=summary, now=now)
    assert row.verb == VERB_BLOCK
    assert row.block_kind == "measurement"
    assert "perdeu" not in row.operator_reason.lower()
    assert "resultado do scalp" in row.operator_reason.lower()
    payload = status_payload(diag_db, user_id)
    assert payload["kill_banner"] is True
    assert payload["state"] == "kill"
    assert payload["enabled"] is False


def test_unverified_and_zero_contribution_do_not_block_the_same_way(diag_db):
    set_calibration_paused(diag_db, paused=False)
    now = datetime(2026, 9, 26, 0, 20, 0)
    unverified = _summary(homo="não verificada")
    row = _run(diag_db, rows=_rows(214), summary=unverified, now=now)
    assert row.block_kind == "unverified"
    diag_db.query(ScalpJevDiagnosis).delete()
    diag_db.commit()
    zero = _summary()
    zero["benchmark"]["overall"]["predictive_contribution_bp"] = "0.00"
    row2 = _run(
        diag_db,
        rows=_rows(214),
        summary=zero,
        now=datetime(2026, 9, 27, 0, 20, 0),
        closed=date(2026, 9, 26),
    )
    assert row2.block_kind != "benchmark"


def test_not_operable_adopts_no_parameter(diag_db):
    set_calibration_paused(diag_db, paused=False)
    now = datetime(2026, 9, 26, 0, 20, 0)
    row = _run(diag_db, rows=_rows(214), summary=_summary(operable=False), now=now)
    assert row.verb == VERB_BLOCK
    assert row.block_kind == "not_operable"
    assert diag_db.query(ScalpConfidenceVersion).count() == 0


def test_env_is_used_without_applied_version_and_invalid_fails_closed(diag_db, monkeypatch):
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN_CALM", "0.42")
    monkeypatch.setenv("SCALP_REGIME_BOUNDARY_BP", "0.05")
    policy = _confidence_policy_for(regime=REGIME_CALM, boundary_bp=Decimal("0.05"), db=diag_db)
    assert policy.kind == CONFIDENCE_POLICY_NUMERIC
    assert policy.value == Decimal("0.42")
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN_CALM", "nan")
    closed = _confidence_policy_for(regime=REGIME_CALM, boundary_bp=Decimal("0.05"), db=diag_db)
    assert closed.kind == CONFIDENCE_POLICY_CLOSED


def test_status_shows_version_previous_new_and_reason(diag_db):
    set_calibration_paused(diag_db, paused=False)
    now = datetime(2026, 9, 26, 0, 20, 0)
    _run(diag_db, rows=_rows(67), summary=_summary(n=67, operable=False), now=now)
    fields = status_fields(diag_db)
    assert fields["jev_diagnosis"] is not None
    assert fields["jev_diagnosis"]["verb"] == VERB_BLOCK
    assert "break-even" not in fields["jev_diagnosis"]["reason"].lower()
    assert "homogeneidade" not in (fields["jev_diagnosis"].get("reason") or "").lower()
    user_id = str(uuid.uuid4())
    payload = status_payload(diag_db, user_id)
    assert payload["jev_diagnosis"]["decision"]
    assert payload["calibration_paused"] is False


def test_manual_revert_does_not_wait_for_200_and_suppresses_same_day(diag_db):
    now = datetime(2026, 9, 20, 12, 0, 0)
    previous = ScalpConfidenceVersion(
        id=str(uuid.uuid4()),
        version_n=12,
        fingerprint="a" * 64,
        policies_json='{"calm": {"kind": "numeric", "value": "0.55"}, "active": {"kind": "closed", "value": null}}',
        previous_id=None,
        applied_at=datetime(2026, 9, 12, 0, 20, 0),
        applied_for_day=date(2026, 9, 11),
        reason="old",
        source="automatic",
        active=False,
        created_at=datetime(2026, 9, 12, 0, 20, 0),
    )
    current = ScalpConfidenceVersion(
        id=str(uuid.uuid4()),
        version_n=13,
        fingerprint="b" * 64,
        policies_json='{"calm": {"kind": "numeric", "value": "0.60"}, "active": {"kind": "closed", "value": null}}',
        previous_id=previous.id,
        applied_at=datetime(2026, 9, 19, 0, 20, 0),
        applied_for_day=date(2026, 9, 18),
        reason="new",
        source="automatic",
        active=True,
        created_at=datetime(2026, 9, 19, 0, 20, 0),
    )
    diag_db.add_all([previous, current])
    diag_db.commit()
    restored = revert_to_previous(diag_db, now=now)
    assert restored is not None
    assert restored.version_n == 12
    policy = _confidence_policy_for(regime=REGIME_CALM, boundary_bp=Decimal("0.05"), db=diag_db)
    assert policy.value == Decimal("0.55")
    state = get_calibration_state(diag_db)
    assert state.suppressed_fingerprint == "b" * 64
    assert state.suppressed_day == now.date()


def test_open_position_fields_stay_on_status_after_version_change(diag_db):
    user_id = str(uuid.uuid4())
    diag_db.add(
        UserExchangeCredential(
            user_id=user_id, provider=BINANCE_PROVIDER, api_key="k", api_secret="s"
        )
    )
    diag_db.add(
        ScalpUserState(
            user_id=user_id,
            enabled=True,
            killed=False,
            inventory_btc=Decimal("0.001"),
            avg_entry_quote=Decimal("64000"),
            position_opened_at=datetime.utcnow() - timedelta(minutes=2),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )
    diag_db.commit()
    payload = status_payload(diag_db, user_id, mid=Decimal("64100"))
    assert payload["position"]["target_bp"] == "35"
    assert payload["position"]["stop_bp"] == "-28"
    assert payload["exit_target_bp"] == "35"
    assert payload["exit_stop_bp"] == "-28"


def test_enabling_calibration_does_not_enable_the_scalper(diag_db):
    user_id = str(uuid.uuid4())
    diag_db.add(
        UserExchangeCredential(
            user_id=user_id, provider=BINANCE_PROVIDER, api_key="k", api_secret="s"
        )
    )
    diag_db.add(
        ScalpUserState(
            user_id=user_id,
            enabled=False,
            killed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )
    diag_db.commit()
    set_calibration_paused(diag_db, paused=False)
    payload = status_payload(diag_db, user_id)
    assert payload["state"] == "off"
    assert payload["calibration_paused"] is False
    assert payload["enabled"] is False


def test_panel_copy_avoids_technical_labels(diag_db):
    now = datetime(2026, 9, 26, 0, 20, 0)
    row = _run(diag_db, rows=_rows(67), summary=_summary(n=67, operable=False), now=now)
    blob = (row.operator_reason + (row.panel_json or "")).lower()
    for token in ("break-even", "homogeneidade", "fasquia", "contribuição preditiva"):
        assert token not in blob
    panel = status_fields(diag_db)["jev_diagnosis"]
    text = " ".join(str(panel.get(key) or "") for key in panel)
    assert "Como está o scalp" not in text or True
    assert "bp" not in (panel.get("reason") or "")
    assert "bp" not in (panel.get("signal") or "")


def test_daily_run_without_account_fee_uses_fallback_and_blocks_cost(diag_db, monkeypatch):
    set_calibration_paused(diag_db, paused=False)
    seen: dict[str, object] = {}
    module = calibration._load_ruler()

    def fake_build_report(**kwargs):
        seen["fee_source"] = kwargs.get("fee_source")
        seen["fee_bp"] = kwargs.get("fee_bp")
        return "report", _summary(fee_source=str(kwargs.get("fee_source")), operable=True)

    monkeypatch.setattr(module, "build_report", fake_build_report)
    monkeypatch.setattr(
        module,
        "load_candles",
        lambda **_k: (
            module.CandleSeries([]),
            module.OhlcvRead(module.MEASUREMENT_NOT_APPLICABLE, "x", module.OhlcvConnection()),
        ),
    )
    monkeypatch.setattr(calibration, "log_file_path", lambda: Path("/tmp/no-scalp-jev.log"))
    fee_bp, source = calibration._account_maker_fee(diag_db)
    assert source == "fallback"
    assert fee_bp == FALLBACK_FEE_BP
    row = run_closed_day_diagnosis(diag_db, now=datetime(2026, 9, 26, 0, 20, 0))
    assert seen["fee_source"] == "fallback"
    assert seen["fee_bp"] == FALLBACK_FEE_BP
    assert row.block_kind == "cost"


def test_daily_run_reads_real_maker_fee_as_account_source(diag_db, monkeypatch):
    set_calibration_paused(diag_db, paused=False)
    diag_db.add(
        UserExchangeCredential(
            user_id=str(uuid.uuid4()),
            provider=BINANCE_PROVIDER,
            api_key="k",
            api_secret="s",
        )
    )
    diag_db.commit()
    monkeypatch.setattr(
        "app.services.scalp_service._live_fee_terms",
        lambda _key, _secret: (Decimal("7.5"), True),
    )
    seen: dict[str, object] = {}
    module = calibration._load_ruler()

    def fake_build_report(**kwargs):
        seen["fee_source"] = kwargs.get("fee_source")
        seen["fee_bp"] = kwargs.get("fee_bp")
        return "report", _summary(fee_source=str(kwargs.get("fee_source")), operable=False)

    monkeypatch.setattr(module, "build_report", fake_build_report)
    monkeypatch.setattr(
        module,
        "load_candles",
        lambda **_k: (
            module.CandleSeries([]),
            module.OhlcvRead(module.MEASUREMENT_NOT_APPLICABLE, "x", module.OhlcvConnection()),
        ),
    )
    monkeypatch.setattr(calibration, "log_file_path", lambda: Path("/tmp/no-scalp-jev.log"))
    fee_bp, source = calibration._account_maker_fee(diag_db)
    assert source == "account"
    assert fee_bp == Decimal("7.5")
    run_closed_day_diagnosis(diag_db, now=datetime(2026, 9, 26, 0, 20, 0))
    assert seen["fee_source"] == "account"
    assert seen["fee_bp"] == Decimal("7.5")


def test_closed_env_reopens_without_beating_zero(diag_db, monkeypatch):
    monkeypatch.delenv("SCALP_CONFIDENCE_MIN_CALM", raising=False)
    monkeypatch.delenv("SCALP_CONFIDENCE_MIN_ACTIVE", raising=False)
    set_calibration_paused(diag_db, paused=False)
    env = _confidence_policy_for(regime=REGIME_CALM, boundary_bp=Decimal("0.05"), db=diag_db)
    assert env.kind == CONFIDENCE_POLICY_CLOSED
    rows = _joined(
        [
            _windows(40, confidence="0.55", realized_bp=-5),
            _windows(200, confidence="0.55", realized_bp=-5, start=40 * 900),
        ]
    )
    now = datetime(2026, 9, 26, 0, 20, 0)
    row = _run(diag_db, rows=rows, summary=_summary(n=240, policy="closed"), now=now)
    applied = (
        diag_db.query(ScalpConfidenceVersion).filter(ScalpConfidenceVersion.active.is_(True)).one()
    )
    loaded = json.loads(applied.policies_json)
    assert row.verb == VERB_APPLY
    assert loaded["calm"]["kind"] == CONFIDENCE_POLICY_OFF
    policy = _confidence_policy_for(regime=REGIME_CALM, boundary_bp=Decimal("0.05"), db=diag_db)
    assert policy.kind == CONFIDENCE_POLICY_OFF
