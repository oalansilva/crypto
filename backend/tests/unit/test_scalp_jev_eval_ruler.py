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
                call_id=f"w{start_s}_{index}",
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
        # Candles de 60 s inteiramente dentro da janela e fechados no horizonte:
        # o percurso é plano no preço realizado (N5), pelo que a barreira
        # avaliada depende só do valor final e não de oscilações do fixture.
        for step in range(60, 901, 60):
            stamp = at + timedelta(seconds=step)
            candles.append(
                {
                    "timestamp_utc": stamp.isoformat(),
                    "open": str(price),
                    "high": str(price),
                    "low": str(price),
                    "close": str(price),
                }
            )
    return decisions, ruler.CandleSeries(candles, step=timedelta(seconds=60))


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
    assert summary["stats"]["n_priced"] == 40, "todas as janelas têm preço (E2)"
    assert summary["insufficient"] is False
    assert summary["insufficient_reasons"] == []
    assert summary["suggested_confidence_min"] == "0.3"
    # No negative-expectancy bucket passes the gate.
    assert Decimal(summary["suggested_confidence_min"]) >= Decimal("0.2")
    assert "HOLD_AFTER_FILL_S" in report
    # E4: a régua deriva geometria quando um candidato paga o round-trip; nesta
    # amostra mista (20 janelas a −10 bp, 20 a +40 bp) nenhum candidato limpa o
    # custo, logo 35/−28 bp mantêm-se como defaults de produto, não derivados.
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


def test_partial_coverage_declares_insufficiency_on_the_priced_windows(tmp_path):
    """E2: 40 janelas não sobrepostas sem preço não são amostra suficiente.

    O OHLCV pode cobrir só parte da janela do log: a lista de candles existe,
    mas ``n_priced`` é 0 — e é a contagem **com preço** que decide a
    insuficiência, não a existência da lista.
    """
    decisions, _series = _windows(40, confidence="0.35", realized_bp=40)
    stale = ruler.CandleSeries(
        [
            {
                "timestamp_utc": (datetime(2026, 8, 1, 0, 0) + timedelta(minutes=i)).isoformat(),
                "open": "85000",
                "high": "85000",
                "low": "85000",
                "close": "85000",
            }
            for i in range(60)
        ]
    )
    report, summary = ruler.build_report(
        log_path=tmp_path / "diag.log",
        decisions=decisions,
        refusals={},
        malformed=0,
        series=stale,
        ohlcv_note="OHLCV com cobertura parcial",
        fee_bp=Decimal("5"),
    )
    assert summary["windows_non_overlapping"] == 40
    assert summary["stats"]["n_priced"] == 0
    assert summary["insufficient"] is True
    assert summary["suggested_confidence_min"] is None
    assert summary["exit_geometry_derived"] is False
    assert "n_priced" in summary["insufficient_reasons"][-1]
    assert "Amostra insuficiente" in report


def test_sufficient_sample_derives_the_geometry_from_the_barriers(tmp_path):
    """E4: com amostra suficiente a régua volta a derivar alvo/stop.

    40 janelas que fecham a +40 bp sem tocar o stop: nenhum candidato acima do
    realizado é atingido (sai-se ao preço do horizonte) e o melhor par é o de
    maior expectancy líquida com a taxa maker **por perna**.
    """
    decisions, series = _windows(40, confidence="0.35", realized_bp=40)
    report, summary = ruler.build_report(
        log_path=tmp_path / "diag.log",
        decisions=decisions,
        refusals={},
        malformed=0,
        series=series,
        ohlcv_note="OHLCV BTC/USDT 1m",
        fee_bp=Decimal("5"),
    )
    assert summary["stats"]["n_priced"] == 40
    assert summary["insufficient"] is False
    assert summary["exit_geometry_derived"] is True
    assert Decimal(summary["suggested_exit_target_bp"]) == Decimal("50")
    assert Decimal(summary["suggested_exit_stop_bp"]) == Decimal("-14")
    # +40 bp de realizado contra 2 × 5 bp de round-trip.
    assert Decimal(summary["exit_geometry_expectancy_bp"]) == Decimal("30")
    break_even = Decimal(summary["exit_geometry_break_even_hit_rate"])
    assert Decimal("0") < break_even < Decimal("1")
    assert "derivada" in report
    assert "break-even" in report


def test_the_cost_uses_the_maker_fee_per_leg_everywhere():
    """N1: a taxa é **por perna**; todo o custo é ``2 × taxa`` (nunca somado)."""
    assert ruler.DEFAULT_FEE_BP == Decimal("10")
    assert ruler.hurdle_bp(fee_bp=Decimal("10"), spread_bp=Decimal("0")) == Decimal("20")
    for leg in (Decimal("7.5"), Decimal("10")):
        assert ruler.hurdle_bp(fee_bp=leg, spread_bp=Decimal("0")) == 2 * leg
    at_threshold = ruler.Decision(
        call_id="c", at=datetime(2026, 9, 23, 12, 0, 0), expected_move_bp=Decimal("30")
    )
    below = ruler.Decision(
        call_id="b", at=datetime(2026, 9, 23, 12, 0, 0), expected_move_bp=Decimal("29.9")
    )
    assert ruler.regime_gate_predicate(decision=at_threshold, fee_bp=Decimal("10")) is True
    assert ruler.regime_gate_predicate(decision=below, fee_bp=Decimal("10")) is False


def test_sell_barriers_are_mirrored_by_side():
    """E1: no SELL o alvo fica **abaixo** e o stop **acima** da entrada."""
    entry = Decimal("100")
    up = [(Decimal("100.39"), Decimal("100.1"))]  # +40 bp: toca o stop do short
    down = [(Decimal("100.2"), Decimal("99.6"))]  # −40 bp: toca o alvo do short
    assert ruler._barrier_for(side="SELL", entry=entry, path=up) == "stop"
    assert ruler._barrier_for(side="SELL", entry=entry, path=down) == "target"
    assert ruler._barrier_for(side="BUY", entry=entry, path=up) == "target"
    assert ruler._barrier_for(side="BUY", entry=entry, path=down) == "stop"


def test_only_closed_candles_inside_the_window_are_read():
    """N5: só candles **já fechados** dentro de ``[start, end]`` contam."""
    start = datetime(2026, 9, 23, 12, 0, 0)
    end = start + timedelta(seconds=900)
    series = ruler.CandleSeries(
        [
            {
                "timestamp_utc": (start + timedelta(seconds=60 * k)).isoformat(),
                "open": "100",
                "high": "100",
                "low": "100",
                "close": "100",
            }
            for k in range(16)  # inclui a candle que abre exactamente em ``end``
        ],
        step=timedelta(seconds=60),
    )
    # k=0 (abre na decisão) entra; a candle que abre em ``end`` ainda não fechou.
    assert len(series.path(start, end)) == 15
    assert series.price_at(end) == Decimal("100")
    # A cobertura termina bem antes do horizonte: nada de realização inventada.
    assert series.price_at(end + timedelta(hours=3)) is None
