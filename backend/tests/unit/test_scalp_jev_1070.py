"""Card #1070 — price path, backtest, BNB, bundle promotion, monitor copy."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from decimal import Decimal

import importlib.util
from pathlib import Path

import pytest

from app.models import ScalpUserState
from app.services.scalp_jev_calibration import (
    _quality_block,
    backtest_promotion_ready,
    build_panel,
    bundle_from_summary,
    bundle_version_policies,
    fingerprint_of,
)
from app.services.scalp_service import (
    _apply_bnb_discount_to_fee,
    _apply_fill,
    fee_mismatch_for,
    tick_user,
)
from app.services.scalp_engine import Book, JevSignal


def _load_module(name: str):
    import sys

    path = Path(__file__).resolve().parents[3] / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def diag_db(postgres_isolation, unit_database_url):
    from app.database import Base, ensure_runtime_schema_migrations
    from app.models import (
        ScalpCalibrationState,
        ScalpConfidenceVersion,
        ScalpFill,
        ScalpJevDiagnosis,
        ScalpUserState,
        UserExchangeCredential,
    )
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    ensure_runtime_schema_migrations()
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    for model in (
        ScalpJevDiagnosis,
        ScalpConfidenceVersion,
        ScalpCalibrationState,
        ScalpFill,
        ScalpUserState,
        UserExchangeCredential,
    ):
        db.query(model).delete()
    db.commit()
    try:
        yield db
    finally:
        db.rollback()
        for model in (
            ScalpJevDiagnosis,
            ScalpConfidenceVersion,
            ScalpCalibrationState,
            ScalpFill,
            ScalpUserState,
            UserExchangeCredential,
        ):
            db.query(model).delete()
        db.commit()
        db.close()
        engine.dispose()


def test_bnb_discount_applies_once_when_balance_covers_clip():
    fee, applied = _apply_bnb_discount_to_fee(
        Decimal("10"),
        discount_enabled=True,
        spot_burn=True,
        bnb_free=Decimal("1"),
        bnb_price=Decimal("600"),
        discount_rate=Decimal("0.25"),
    )
    assert applied is True
    assert fee == Decimal("7.5")


def test_agg_trades_resolve_target_before_stop():
    ppm = _load_module("scalp_jev_price_path")
    start = datetime(2025, 9, 29, 12, 0, 0)
    entry = Decimal("100")
    target = entry * Decimal("1.0020")
    trades = []
    for i in range(5):
        trades.append(ppm.TradeTick(at=start + timedelta(seconds=i + 1), price=entry))
    trades.append(ppm.TradeTick(at=start + timedelta(seconds=6), price=target))
    store = ppm.MemoryPricePathStore(trades=tuple(trades))
    barrier, _ = ppm.barrier_for_window(
        store,
        side="BUY",
        entry=entry,
        start=start,
        end=start + timedelta(seconds=900),
        target_bp=Decimal("20"),
        stop_bp=Decimal("-14"),
    )
    assert barrier == "target"


def test_report_2909_indeterminate_fraction_below_five_percent():
    eval_mod = _load_module("scalp_jev_eval")
    ppm = _load_module("scalp_jev_price_path")
    start = datetime(2025, 9, 29, 0, 0, 0)
    entry = Decimal("100")
    ticks = [ppm.TradeTick(at=start + timedelta(seconds=i), price=entry) for i in range(1, 120)]
    ticks.append(ppm.TradeTick(at=start + timedelta(seconds=130), price=entry * Decimal("1.002")))
    store = ppm.MemoryPricePathStore(trades=tuple(ticks))
    candidates = [
        {"measurement_status": "measured"},
        {"measurement_status": "measured"},
        {"measurement_status": "indeterminate"},
    ]
    without = eval_mod.geometry_candidate_indeterminate_fraction(candidates)
    assert without == Decimal("1") / Decimal("3")
    resolved = [
        {
            "measurement_status": (
                "measured"
                if ppm.barrier_for_window(
                    store,
                    side="BUY",
                    entry=entry,
                    start=start,
                    end=start + timedelta(seconds=900),
                    target_bp=Decimal("20"),
                    stop_bp=Decimal("-14"),
                )[0]
                != "indeterminate"
                else "indeterminate"
            )
        }
        for _ in range(40)
    ]
    rate = eval_mod.geometry_candidate_indeterminate_fraction(resolved)
    assert rate < Decimal("0.05")


def test_backtest_bca_promotes_positive_mean():
    backtest = _load_module("scalp_jev_backtest")
    rows = [
        backtest.BacktestWindow("calm", Decimal("5"), Decimal("20"), Decimal("-14"), 900)
        for _ in range(220)
    ]
    summary = backtest.summarize_regimes(rows)
    assert summary["calm"]["promotable"] is True


def test_backtest_fees_maker_on_limit_exit():
    backtest = _load_module("scalp_jev_backtest")
    maker = Decimal("7.5")
    taker = Decimal("12")
    limit_net = backtest.net_round_trip_bp(
        signed_price_bp=Decimal("30"),
        maker_bp=maker,
        taker_bp=taker,
        entry_limit_filled=True,
        exit_limit_filled=True,
    )
    ioc_net = backtest.net_round_trip_bp(
        signed_price_bp=Decimal("30"),
        maker_bp=maker,
        taker_bp=taker,
        entry_limit_filled=True,
        exit_limit_filled=False,
        exit_used_taker=True,
    )
    assert limit_net > ioc_net


def test_backtest_two_hundred_windows_per_regime_without_live_log():
    backtest = _load_module("scalp_jev_backtest")
    tape = backtest.synthetic_trade_tape(n_windows=500, horizon_s=900)
    rows = backtest.replay_independent_windows(
        tape,
        fee_bp=Decimal("7.5"),
        horizon_s=900,
        target_bp=Decimal("20"),
        stop_bp=Decimal("-14"),
    )
    summary = backtest.summarize_regimes(rows)
    assert summary["calm"]["n"] >= 200
    assert summary["active"]["n"] >= 200
    bench = backtest.benchmark_metrics(rows)
    assert bench["computable"] is True
    assert backtest.returns_by_geometry(rows)


def test_backtest_uses_decide_cycle_and_jev_cache():
    backtest = _load_module("scalp_jev_backtest")
    tape = backtest.synthetic_trade_tape(n_windows=80, horizon_s=900)
    cache: dict = {}
    key_before = len(cache)
    rows = backtest.replay_with_decide_cycle(
        tape,
        fee_bp=Decimal("7.5"),
        horizon_s=900,
        target_bp=Decimal("20"),
        stop_bp=Decimal("-14"),
        jev_cache=cache,
    )
    assert len(cache) > key_before
    assert rows
    assert any(row.bought for row in rows)


def test_fill_fee_mismatch_surfaces_in_diagnosis_fields():
    from app.services import scalp_service

    scalp_service._last_screen_fee_bp["u1"] = Decimal("7.5")
    state = ScalpUserState(user_id="u1", inventory_btc=Decimal("0.001"))
    state.avg_entry_quote = Decimal("65000")
    state.inventory_btc = Decimal("0.001")
    _apply_fill(
        state,
        side="SELL",
        quantity=Decimal("0.001"),
        price=Decimal("65100"),
        fee=Decimal("1.0"),
    )
    assert fee_mismatch_for("u1") is not None


def test_bundle_fingerprint_includes_geometry_and_boundary():
    conf = {
        "calm": {"kind": "numeric", "value": "0.55"},
        "active": {"kind": "numeric", "value": "0.6"},
    }
    bundle = bundle_version_policies(
        conf,
        target_bp="20",
        stop_bp="-14",
        horizon_s=3600,
        regime_boundary_bp="0.05",
    )
    fp = fingerprint_of(bundle)
    assert fp != fingerprint_of(conf)
    summary = {
        "geometry_in_use": {"target_bp": "20", "stop_bp": "-14", "horizon_s": 3600},
        "regime_boundary_bp": "0.05",
        "backtest": {
            "promotable": True,
            "regimes": {
                "calm": {"n": 220, "promotable": True, "ci95_lower_bp": "1"},
                "active": {"n": 220, "promotable": True, "ci95_lower_bp": "1"},
            },
        },
    }
    merged = bundle_from_summary(conf, summary, backtest=summary["backtest"])
    assert merged["geometry"]["horizon_s"] == 3600
    assert backtest_promotion_ready(summary) is True


def test_bundle_from_summary_prefers_log_measured_boundary_over_offline_backtest():
    conf = {
        "calm": {"kind": "numeric", "value": "0.55"},
        "active": {"kind": "numeric", "value": "0.6"},
    }
    summary = {
        "geometry_in_use": {"target_bp": "35", "stop_bp": "-28", "horizon_s": 900},
        "regime_boundary_bp": "0.042",
        "regime_boundary_status": "measured",
        "backtest": {"regime_boundary_bp": "0.99", "promotable": False, "regimes": {}},
    }
    merged = bundle_from_summary(conf, summary, backtest=summary["backtest"])
    assert merged["regime_boundary_bp"] == "0.042"


def test_geometry_search_skips_not_operable_block():
    summary = {
        "viability_status": "not_operable",
        "geometry_search_active": True,
        "regime_boundary_bp": "0.05",
        "measurement": {"status": "medido"},
        "homogeneity": {"status": "homogénea"},
        "fee_source": "account",
        "benchmark": {"overall": {"computable": True}},
    }
    assert _quality_block(summary, newest_candle=None, last_window_end=None) is None


def test_panel_includes_backtest_trader_phrases():
    summary = {
        "measurement": {"n_priced": 400, "status": "medido"},
        "regime_boundary_bp": "0.05",
        "geometry_in_use": {"target_bp": "20", "stop_bp": "-14", "horizon_s": 900},
        "backtest": {
            "regimes": {
                "calm": {"n": 220, "ci95_lower_bp": "2", "promotable": True},
                "active": {"n": 220, "ci95_lower_bp": "1", "promotable": True},
            },
            "promotable": True,
        },
        "benchmark": {"overall": {"computable": True}},
        "viability_status": "viable",
    }
    policies = bundle_from_summary(
        {
            "calm": {"kind": "numeric", "value": "0.5"},
            "active": {"kind": "numeric", "value": "0.5"},
        },
        summary,
    )
    panel = build_panel(
        closed=datetime(2025, 9, 28).date(),
        shown_on=datetime(2025, 9, 29).date(),
        verb="aplicar",
        reason="test",
        posterior_n=220,
        comparable=True,
        summary=summary,
        policies=policies,
        version=None,
        period=None,
    )
    assert "Backtest:" in panel["backtest_sample"]
    assert "Conjunto aplicado" in panel["geometry_bundle"]


def test_dev_cycle_posts_post_only_buy(diag_db, monkeypatch):
    from app.services.scalp_engine import CycleIntent
    from app.services.scalp_service import LiveExchange, get_or_create_state

    state = get_or_create_state(diag_db, "dev-user")
    state.enabled = True
    diag_db.commit()
    sent: list[dict] = []

    class Port(LiveExchange):
        def book(self):
            return Book(bid=Decimal("100"), ask=Decimal("100.02"))

        def free_balances(self, api_key, api_secret):
            return Decimal("100"), Decimal("0")

        def fee_terms(self, api_key, api_secret):
            return Decimal("7.5"), True, True

        def place_post_only(self, **kwargs):
            sent.append(kwargs)
            return {
                "status": "FILLED",
                "executedQty": kwargs["quantity"],
                "cummulativeQuoteQty": "10",
            }

        def place_aggressive_exit(self, **kwargs):
            raise AssertionError("no market")

        def cancel_bot_orders(self, **kwargs):
            return 0

        def cancel_bot_order(self, **kwargs):
            return None

        def query_order(self, **kwargs):
            return {"status": "FILLED"}

    jev = JevSignal(
        side="BUY",
        confidence=Decimal("0.9"),
        expected_move_bp=Decimal("50"),
        book_toxic=False,
        latency_ms=100,
        model="jev-test",
        confidence_origin="calibrated",
    )

    monkeypatch.setenv("SCALP_REGIME_BOUNDARY_BP", "0.01")
    monkeypatch.setattr(
        "app.services.scalp_service._confidence_policy_for",
        lambda **kwargs: __import__(
            "app.services.scalp_engine", fromlist=["ConfidencePolicy"]
        ).ConfidencePolicy(
            kind="numeric",
            value=Decimal("0.1"),
            regime=kwargs.get("regime"),
        ),
    )
    monkeypatch.setattr("app.services.scalp_service.jev_api_key", lambda: "key")
    monkeypatch.setattr(
        "app.services.scalp_service._credential",
        lambda db, uid: type("C", (), {"api_key": "k", "api_secret": "s"})(),
    )

    result = tick_user(
        diag_db,
        "dev-user",
        exchange=Port(),
        jev_fn=lambda _payload: jev,
        book=Port().book(),
        free_usdt=Decimal("100"),
        free_btc=Decimal("0"),
    )
    assert result.sent or sent
    if sent:
        assert sent[0]["side"] == "BUY"
        assert Decimal(str(sent[0]["quantity"])) * Decimal("100") <= Decimal("10.01")


def test_last_trade_net_visible_after_round_trip():
    state = ScalpUserState(user_id="u2", inventory_btc=Decimal("0"))
    _apply_fill(
        state, side="BUY", quantity=Decimal("0.001"), price=Decimal("100"), fee=Decimal("0.01")
    )
    _apply_fill(
        state, side="SELL", quantity=Decimal("0.001"), price=Decimal("99"), fee=Decimal("0.01")
    )
    assert state.last_trade_quote is not None
    assert state.last_trade_bp is not None


def test_not_operable_continues_geometry_search_without_loss_refusal():
    summary = {
        "viability_status": "not_operable",
        "geometry_search_active": True,
        "regime_boundary_bp": "0.05",
        "measurement": {"status": "medido"},
        "homogeneity": {"status": "homogénea"},
        "fee_source": "account",
        "benchmark": {"overall": {"computable": True}},
        "backtest": {"promotable": False, "regimes": {}},
    }
    block = _quality_block(summary, newest_candle=None, last_window_end=None)
    assert block is None
    panel = build_panel(
        closed=datetime(2025, 9, 28).date(),
        shown_on=datetime(2025, 9, 29).date(),
        verb="manter",
        reason="A grelha continua.",
        posterior_n=0,
        comparable=False,
        summary=summary,
        policies=bundle_from_summary(
            {
                "calm": {"kind": "numeric", "value": "0.5"},
                "active": {"kind": "numeric", "value": "0.5"},
            },
            summary,
        ),
        version=None,
        period=None,
    )
    assert "preju" not in panel["reason"].lower()
    assert "grelha" in panel["backtest_sample"].lower()


def test_window_end_mode_posts_limit_then_ioc_when_stuck():
    from app.services.scalp_engine import EXIT_SLIPPAGE_CAP_BP, Book, decide_exit_cycle
    from app.services.scalp_service import _window_end_limit_after_ioc_cap, _window_end_mode

    book = Book(bid=Decimal("65000"), ask=Decimal("65010"))
    limit = decide_exit_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        inventory_btc=Decimal("0.001"),
        free_btc=Decimal("0.01"),
        floor_btc=Decimal("0"),
        avg_entry=Decimal("65000"),
        book=book,
        resting=None,
        seconds_since_fill=905.0,
        stuck=False,
        window_end_mode=_window_end_mode("u", seconds_since_fill=905.0, stuck=False),
    )
    assert limit.aggressive_exit is False
    assert limit.order_type == "LIMIT"

    ioc = decide_exit_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        inventory_btc=Decimal("0.001"),
        free_btc=Decimal("0.01"),
        floor_btc=Decimal("0"),
        avg_entry=Decimal("65000"),
        book=book,
        resting=None,
        seconds_since_fill=940.0,
        stuck=True,
        window_end_mode=_window_end_mode("u", seconds_since_fill=940.0, stuck=True),
    )
    assert ioc.aggressive_exit is True
    assert ioc.time_in_force == "IOC"
    cap = book.mid * (Decimal("1") - EXIT_SLIPPAGE_CAP_BP / Decimal("10000"))
    assert ioc.price == cap

    weak = Book(bid=Decimal("64800"), ask=Decimal("65000"))
    blocked = decide_exit_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        inventory_btc=Decimal("0.001"),
        free_btc=Decimal("0.01"),
        floor_btc=Decimal("0"),
        avg_entry=Decimal("65000"),
        book=weak,
        resting=None,
        seconds_since_fill=940.0,
        stuck=True,
        window_end_mode="ioc",
    )
    assert blocked.send is False
    assert blocked.skip_reason == "beyond_slippage_cap"
    _window_end_limit_after_ioc_cap.add("u2")
    assert _window_end_mode("u2", seconds_since_fill=940.0, stuck=True) == "limit"


def test_decide_exit_cycle_respects_version_geometry():
    from app.services.scalp_engine import Book, decide_exit_cycle, should_post_exit

    book = Book(bid=Decimal("100"), ask=Decimal("100.02"))
    assert should_post_exit(ret_bp=Decimal("19"), exit_target_bp=Decimal("20")) is False
    assert should_post_exit(ret_bp=Decimal("21"), exit_target_bp=Decimal("20")) is True

    hold_s = 3600
    intent = decide_exit_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        inventory_btc=Decimal("0.001"),
        free_btc=Decimal("0.01"),
        floor_btc=Decimal("0"),
        avg_entry=Decimal("100"),
        book=book,
        resting=None,
        seconds_since_fill=float(hold_s) + 5.0,
        stuck=False,
        window_end_mode="limit",
        hold_after_fill_s=hold_s,
        exit_target_bp=Decimal("20"),
        exit_stop_bp=Decimal("-14"),
    )
    assert intent.send is True
    assert intent.aggressive_exit is False

    cap_bp = Decimal("25")
    ioc = decide_exit_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        inventory_btc=Decimal("0.001"),
        free_btc=Decimal("0.01"),
        floor_btc=Decimal("0"),
        avg_entry=Decimal("100"),
        book=book,
        resting=None,
        seconds_since_fill=float(hold_s) + 40.0,
        stuck=True,
        window_end_mode="ioc",
        hold_after_fill_s=hold_s,
        slippage_cap_bp=cap_bp,
    )
    expected_cap = book.mid * (Decimal("1") - cap_bp / Decimal("10000"))
    assert ioc.price == expected_cap


def _rows_with_vol_bps(count: int, *, low: Decimal, high: Decimal):
    from test_scalp_jev_eval_ruler import _merge, _windows, ruler

    half = count // 2
    low_decisions, low_series = _windows(half, confidence="0.55", realized_bp=12, start_s=0)
    for decision in low_decisions:
        decision.vol_bp = low
    high_decisions, high_series = _windows(
        count - half, confidence="0.55", realized_bp=12, start_s=half * 900
    )
    for decision in high_decisions:
        decision.vol_bp = high
    series = _merge(low_series, high_series)
    decisions = low_decisions + high_decisions
    return [(decision, ruler.realized_for(decision, series)) for decision in decisions]


def test_measured_regime_boundary_from_log_vol_bp_persists_version(diag_db, monkeypatch):
    from app.services import scalp_jev_calibration as calibration
    from app.services.scalp_jev_calibration import (
        active_version,
        compute_regime_boundary_bp,
        policies_of,
        run_closed_day_diagnosis,
    )
    from app.services.scalp_engine import CONFIDENCE_POLICY_NUMERIC, REGIME_ACTIVE, REGIME_CALM
    from app.services.scalp_service import _confidence_policy_for, _regime_boundary_bp
    from test_scalp_jev_diagnostico_recalibracao import _summary

    monkeypatch.delenv("SCALP_REGIME_BOUNDARY_BP", raising=False)
    monkeypatch.delenv("SCALP_CONFIDENCE_MIN", raising=False)

    low = Decimal("0.02")
    high = Decimal("0.08")
    rows = _rows_with_vol_bps(400, low=low, high=high)
    vols = [decision.vol_bp for decision, _realized in rows]
    expected = compute_regime_boundary_bp(vols)
    assert expected is not None

    backtest = calibration._load_backtest()
    real_offline = backtest.run_offline_backtest

    def fake_offline_backtest(**kwargs):
        payload = real_offline(**kwargs)
        payload = dict(payload)
        payload["regime_boundary_bp"] = "0.99"
        return payload

    monkeypatch.setattr(backtest, "run_offline_backtest", fake_offline_backtest)

    summary = _summary(n=400, operable=True)
    summary["regime_boundary_bp"] = None
    summary["regime_boundary_status"] = "absent"

    calibration.set_calibration_paused(diag_db, paused=True)
    row = run_closed_day_diagnosis(
        diag_db,
        now=datetime(2026, 9, 26, 0, 20, 0),
        summary=summary,
        realized_windows=rows,
        newest_candle=datetime(2026, 9, 26, 0, 20, 0),
        last_window_end=datetime(2026, 9, 25, 23, 0, 0),
        fee_bp=Decimal("10"),
    )

    assert row.block_kind != "regime_boundary"
    assert summary["regime_boundary_bp"] == str(expected)
    assert summary["regime_boundary_status"] == "measured"
    version = active_version(diag_db)
    assert version is not None
    policies = policies_of(version)
    assert policies["regime_boundary_bp"] == str(expected)
    assert policies["calm"]["kind"] == CONFIDENCE_POLICY_NUMERIC
    assert policies["active"]["kind"] == CONFIDENCE_POLICY_NUMERIC
    assert policies["calm"]["value"] == "0.7"
    assert policies["active"]["value"] == "0.7"
    assert _regime_boundary_bp(diag_db) == expected
    assert (
        _confidence_policy_for(regime=REGIME_CALM, boundary_bp=expected, db=diag_db).kind
        == CONFIDENCE_POLICY_NUMERIC
    )
    assert (
        _confidence_policy_for(regime=REGIME_ACTIVE, boundary_bp=expected, db=diag_db).kind
        == CONFIDENCE_POLICY_NUMERIC
    )
    stored_summary = json.loads(row.summary_json)
    assert stored_summary["regime_boundary_bp"] == str(expected)
    assert stored_summary["regime_boundary_status"] == "measured"
    panel = json.loads(row.panel_json)
    assert panel["regime_boundary_bp"] == str(expected)
    assert panel["regime_boundary_status"] == "measured"
    assert "ausente" not in panel["geometry_bundle"].lower()


def test_existing_diagnosis_still_measures_boundary_from_log(diag_db, monkeypatch, tmp_path):
    from app.models import ScalpConfidenceVersion, ScalpJevDiagnosis
    from app.services import scalp_jev_calibration as calibration
    from app.services.scalp_jev_calibration import (
        active_version,
        compute_regime_boundary_bp,
        policies_of,
        run_closed_day_diagnosis,
    )
    from app.services.scalp_service import _regime_boundary_bp
    from test_scalp_jev_diagnostico_recalibracao import _run, _summary

    monkeypatch.delenv("SCALP_REGIME_BOUNDARY_BP", raising=False)

    summary = _summary(operable=True, n=214)
    summary["regime_boundary_bp"] = None
    summary["regime_boundary_status"] = "absent"
    first = _run(
        diag_db,
        rows=_rows_with_vol_bps(214, low=Decimal("0.02"), high=Decimal("0.08")),
        summary=summary,
        now=datetime(2026, 9, 26, 0, 20, 0),
    )
    assert first.block_kind == "regime_boundary"
    assert diag_db.query(ScalpConfidenceVersion).count() == 0

    low = Decimal("0.02")
    high = Decimal("0.08")
    log_decisions = [
        decision for decision, _realized in _rows_with_vol_bps(400, low=low, high=high)
    ]
    expected = compute_regime_boundary_bp([d.vol_bp for d in log_decisions])
    assert expected is not None

    log_file = tmp_path / "scalp_jev_diagnostic.log"
    log_file.write_text("stub\n", encoding="utf-8")
    module = calibration._load_ruler()
    monkeypatch.setattr(calibration, "log_file_path", lambda: log_file)
    monkeypatch.setattr(module, "parse_log", lambda _p: (log_decisions, {}, 0))

    second = run_closed_day_diagnosis(diag_db, now=datetime(2026, 9, 26, 0, 20, 0))
    assert second.closed_day == first.closed_day
    assert diag_db.query(ScalpJevDiagnosis).count() == 1
    version = active_version(diag_db)
    assert version is not None
    assert policies_of(version)["regime_boundary_bp"] == str(expected)
    assert _regime_boundary_bp(diag_db) == expected
    assert second.block_kind != "regime_boundary"
    stored_summary = json.loads(second.summary_json)
    assert stored_summary["regime_boundary_bp"] == str(expected)
    assert stored_summary["regime_boundary_status"] == "measured"
    panel = json.loads(second.panel_json)
    assert panel["regime_boundary_bp"] == str(expected)
    assert panel["regime_boundary_status"] == "measured"
    assert "ausente" not in panel["geometry_bundle"].lower()


def test_daily_run_with_offline_backtest_uses_log_measured_boundary(diag_db, monkeypatch, tmp_path):
    from app.services import scalp_jev_calibration as calibration
    from app.services.scalp_jev_calibration import (
        active_version,
        compute_regime_boundary_bp,
        policies_of,
        run_closed_day_diagnosis,
    )

    monkeypatch.delenv("SCALP_REGIME_BOUNDARY_BP", raising=False)
    calibration.set_calibration_paused(diag_db, paused=True)

    low = Decimal("0.02")
    high = Decimal("0.08")
    log_decisions = [
        decision for decision, _realized in _rows_with_vol_bps(400, low=low, high=high)
    ]
    expected = compute_regime_boundary_bp([d.vol_bp for d in log_decisions])
    assert expected is not None

    log_file = tmp_path / "scalp_jev_diagnostic.log"
    log_file.write_text("stub\n", encoding="utf-8")
    module = calibration._load_ruler()
    monkeypatch.setattr(calibration, "log_file_path", lambda: log_file)
    monkeypatch.setattr(module, "parse_log", lambda _p: (log_decisions, {}, 0))
    monkeypatch.setattr(
        module,
        "load_candles",
        lambda **_k: (
            module.CandleSeries([]),
            module.OhlcvRead(module.MEASUREMENT_NOT_APPLICABLE, "x", module.OhlcvConnection()),
        ),
    )

    backtest = calibration._load_backtest()
    real_offline = backtest.run_offline_backtest

    def fake_offline_backtest(**kwargs):
        payload = dict(real_offline(**kwargs))
        payload["regime_boundary_bp"] = "0.99"
        return payload

    monkeypatch.setattr(backtest, "run_offline_backtest", fake_offline_backtest)

    from test_scalp_jev_diagnostico_recalibracao import _summary

    def fake_build_report(**kwargs):
        summary = _summary(n=400, operable=True)
        summary["regime_boundary_bp"] = None
        summary["regime_boundary_status"] = "absent"
        return "report", summary

    monkeypatch.setattr(module, "build_report", fake_build_report)
    monkeypatch.setattr(
        "app.services.scalp_service._regime_boundary_bp",
        lambda _db=None: None,
    )

    row = run_closed_day_diagnosis(diag_db, now=datetime(2026, 9, 26, 0, 20, 0))
    version = active_version(diag_db)
    assert version is not None
    assert policies_of(version)["regime_boundary_bp"] == str(expected)
    assert row.block_kind != "regime_boundary"
    stored_summary = json.loads(row.summary_json)
    assert stored_summary["regime_boundary_bp"] == str(expected)
    assert stored_summary.get("backtest", {}).get("regime_boundary_bp") == "0.99"
    panel = json.loads(row.panel_json)
    assert panel["regime_boundary_bp"] == str(expected)


def test_measured_regime_boundary_requires_four_hundred_finite_vols(diag_db, monkeypatch):
    from app.models import ScalpConfidenceVersion
    from test_scalp_jev_diagnostico_recalibracao import _rows, _run, _summary

    monkeypatch.delenv("SCALP_REGIME_BOUNDARY_BP", raising=False)
    summary = _summary(operable=True, n=214)
    summary["regime_boundary_bp"] = None
    summary["regime_boundary_status"] = "absent"

    row = _run(
        diag_db,
        rows=_rows(214),
        summary=summary,
        now=datetime(2026, 9, 26, 0, 20, 0),
    )
    assert row.block_kind == "regime_boundary"
    assert diag_db.query(ScalpConfidenceVersion).count() == 0


def test_attach_offline_backtest_fills_summary():
    from decimal import Decimal

    from app.services.scalp_jev_calibration import (
        _attach_offline_backtest,
        backtest_promotion_ready,
    )

    summary = {
        "geometry_in_use": {"target_bp": "20", "stop_bp": "-14", "horizon_s": 900},
    }
    _attach_offline_backtest(summary, fee_bp=Decimal("7.5"))
    assert "backtest" in summary
    assert summary["backtest"].get("regimes")
    assert isinstance(backtest_promotion_ready(summary), bool)
