"""Card #1025 — A: the read-only Jev ruler and its insufficiency gate."""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
RULER_PATH = REPO_ROOT / "scripts" / "scalp_jev_eval.py"


def _load_ruler():
    import sys

    spec = importlib.util.spec_from_file_location("scalp_jev_eval", RULER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # dataclasses resolves string annotations through sys.modules[__module__].
    sys.modules["scalp_jev_eval"] = module
    spec.loader.exec_module(module)
    return module


ruler = _load_ruler()


def _entry_line(call_id: str, at: datetime, *, mid: str = "85000") -> str:
    state = {
        "symbol": "BTCUSDT",
        "horizon_s": 900,
        "touch": {"bid": mid, "ask": mid, "mid": mid, "spread_bp": "0.1"},
        "window": {"horizon_s": 900, "trade_count": 3, "ret_bp": "1.0", "vol_bp": "0.02"},
        "account": {"has_position": False, "has_balance": True},
        "resting": None,
    }
    stamp = at.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    return (
        f"{stamp} INFO scalp jev call entry id={call_id} "
        f"state={json.dumps(state, separators=(',', ':'))} "
        'questions={"side":"choice","expected_move_bp":"score","book_toxic":"noul"}'
    )


def _return_line(call_id: str, at: datetime, *, confidence: str = "0.2", score: str = "5.0") -> str:
    stamp = at.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    return (
        f"{stamp} INFO scalp jev call return id={call_id} status=200 latency_ms=100 "
        f"side=BUY expected_move_bp=25.00 score={score} book_toxic=False confidence={confidence}"
    )


def test_parse_joins_entry_window_with_the_return(tmp_path):
    at = datetime(2026, 9, 23, 13, 30, 0)
    log = tmp_path / "diag.log"
    log.write_text(
        "\n".join(
            [
                _entry_line("a1", at),
                _return_line("a1", at + timedelta(milliseconds=200), confidence="0.31"),
                _entry_line("a2", at + timedelta(minutes=1)),
                _return_line("a2", at + timedelta(minutes=1, milliseconds=200), score="6.5"),
                f"{at.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} INFO scalp cycle refused user=u skip_reason=regime",
                any_garbage := "not a record at all",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    decisions, refusals, malformed = ruler.parse_log(log)
    assert [d.call_id for d in decisions] == ["a1", "a2"]
    assert decisions[0].confidence == Decimal("0.31")
    assert decisions[0].entry_mid == Decimal("85000")
    assert decisions[0].status == "200"
    assert decisions[1].score == 6.5
    assert refusals == {"regime": 1}
    assert malformed == 0
    assert any_garbage


def test_non_overlapping_windows_are_nine_hundred_seconds_apart():
    base = datetime(2026, 9, 23, 12, 0, 0)
    decisions = [
        ruler.Decision(call_id=f"c{i}", at=base + timedelta(seconds=offset))
        for i, offset in enumerate((0, 60, 300, 900, 1200, 1800, 1810))
    ]
    kept = ruler.non_overlapping(decisions)
    assert [d.call_id for d in kept] == ["c0", "c3", "c5"]


def _windows(
    count: int, *, confidence: str, realized_bp: int, base_bp: int = 85000, start_s: int = 0
):
    base = datetime(2026, 9, 23, 0, 0, 0)
    decisions = []
    candles = []
    for index in range(count):
        at = base + timedelta(seconds=start_s + 900 * index)
        decisions.append(
            ruler.Decision(
                call_id=f"w{index}",
                at=at,
                side="BUY",
                confidence=Decimal(confidence),
                score=5.0,
                expected_move_bp=Decimal("60"),
                entry_mid=Decimal(base_bp),
                spread_bp=Decimal("0.1"),
                window={"vol_bp": "0.02", "ret_bp": "1.0"},
            )
        )
        price = Decimal(base_bp) * (Decimal("1") + Decimal(realized_bp) / Decimal("10000"))
        high = max(price, Decimal(base_bp) * Decimal("1.004"))
        low = min(price, Decimal(base_bp) * Decimal("0.996"))
        candles.append(
            {
                "timestamp_utc": (at + timedelta(seconds=900)).isoformat(),
                "open": str(Decimal(base_bp)),
                "high": str(high),
                "low": str(low),
                "close": str(price),
            }
        )
    return decisions, ruler.CandleSeries(candles)


def test_insufficient_sample_is_declared_and_no_threshold_is_proposed(tmp_path):
    log = tmp_path / "diag.log"
    at = datetime(2026, 9, 23, 13, 30, 0)
    log.write_text(
        "\n".join([_entry_line("a1", at), _return_line("a1", at)]) + "\n", encoding="utf-8"
    )
    decisions, refusals, malformed = ruler.parse_log(log)
    report, summary = ruler.build_report(
        log_path=log,
        decisions=decisions,
        refusals=refusals,
        malformed=malformed,
        series=ruler.CandleSeries([]),
        ohlcv_note="OHLCV sem candles",
        fee_bp=Decimal("14"),
    )
    assert summary["insufficient"] is True
    assert summary["suggested_confidence_min"] is None
    assert summary["suggested_exit_target_bp"] is None
    assert summary["suggested_exit_stop_bp"] is None
    assert "Amostra insuficiente" in report
    assert "amostra insuficiente" in report.lower()
    assert "CONFIDENCE_MIN" in report


def test_sufficient_sample_proposes_the_lowest_positive_bucket(tmp_path):
    decisions, series = _windows(20, confidence="0.15", realized_bp=-10)
    more, more_series = _windows(20, confidence="0.35", realized_bp=40, start_s=20 * 900)
    report, summary = ruler.build_report(
        log_path=tmp_path / "diag.log",
        decisions=decisions + more,
        refusals={},
        malformed=0,
        series=_merge(series, more_series),
        ohlcv_note="OHLCV BTC/USDT 15m",
        fee_bp=Decimal("14"),
    )
    assert summary["windows_non_overlapping"] == 40
    assert summary["insufficient"] is False
    assert summary["insufficient_reasons"] == []
    assert summary["suggested_confidence_min"] == "0.3"
    # No negative-expectancy bucket passes the gate.
    assert Decimal(summary["suggested_confidence_min"]) >= Decimal("0.2")
    assert "HOLD_AFTER_FILL_S" in report
    # Correção pós-CR (item 2): a régua não propõe geometria nenhuma — 35/−28 bp
    # são defaults de produto, não um valor confirmado por esta tabela.
    assert summary["suggested_exit_target_bp"] is None
    assert summary["suggested_exit_stop_bp"] is None
    assert summary["exit_geometry_derived"] is False
    assert summary["product_exit_target_bp"] == "35"
    assert summary["product_exit_stop_bp"] == "-28"
    assert "defaults de produto" in report
    assert "não derivados desta régua" in report


def test_a_bucket_below_the_minimum_trades_never_proposes_a_threshold(tmp_path):
    """Correção pós-CR (item 1): expectancy positiva em 10 trades não é limiar."""
    groups = [
        _windows(10, confidence="0.15", realized_bp=40),
        _windows(10, confidence="0.35", realized_bp=40, start_s=10 * 900),
        _windows(10, confidence="0.55", realized_bp=40, start_s=20 * 900),
    ]
    decisions = []
    series = None
    for group_decisions, group_series in groups:
        decisions.extend(group_decisions)
        series = group_series if series is None else _merge(series, group_series)
    report, summary = ruler.build_report(
        log_path=tmp_path / "diag.log",
        decisions=decisions,
        refusals={},
        malformed=0,
        series=series,
        ohlcv_note="OHLCV BTC/USDT 15m",
        fee_bp=Decimal("14"),
    )
    assert summary["windows_non_overlapping"] == 30, "a amostra total chega ao gate"
    assert summary["insufficient"] is False
    assert summary["insufficient_reasons"] == []
    # os 30 trades positivos estão repartidos em buckets de 10: todos ficam
    # abaixo de MIN_BUCKET_TRADES e nenhum pode nascer como sugestão.
    assert summary["suggested_confidence_min"] is None
    assert f"{ruler.MIN_BUCKET_TRADES}+ trades com preço" in report


def _merge(first, second):
    candles = []
    for series in (first, second):
        for stamp, _open, high, low, close in series.candles:
            candles.append(
                {
                    "timestamp_utc": stamp.isoformat(),
                    "open": str(_open),
                    "high": str(high),
                    "low": str(low),
                    "close": str(close),
                }
            )
    return ruler.CandleSeries(candles)


def test_the_instrument_is_read_only():
    source = RULER_PATH.read_text(encoding="utf-8").lower()
    for forbidden in (
        "insert into",
        "update ",
        "delete from",
        "create table",
        "write_candles",
        "to_sql",
        ".commit(",
        "session.add",
    ):
        assert forbidden not in source
    assert "scalp_loop" not in source, "the ruler does not need the scalp loop"
    assert "run_scalp_loop" not in source
    assert "read_recent_candles" in source and "get_latest_candle_time" in source


def test_missing_log_file_is_declared(monkeypatch, tmp_path, capsys):
    missing = tmp_path / "nope.log"
    code = ruler.main(["--log", str(missing), "--fee-bp", "14"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Log ausente" in out
    assert "Amostra insuficiente" in out
