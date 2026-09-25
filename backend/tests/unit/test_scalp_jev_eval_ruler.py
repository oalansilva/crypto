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
                # Card #1030: a reply with a latency and a σ so the eligible
                # population and the market regime are defined.
                latency_ms=100,
                vol_bp=Decimal("0.02"),
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
    # Card #1030: sem fronteira de regime (e com amostra insuficiente) as
    # políticas por regime ficam fechadas e o valor em uso é preservado.
    assert summary["regimes"]["calm"]["policy"] == "closed"
    assert summary["regimes"]["active"]["policy"] == "closed"
    assert summary["confidence_in_use"] == "0.70"
    assert summary["fee_source"] == "fallback"
    assert summary["suggested_exit_target_bp"] is None
    assert summary["suggested_exit_stop_bp"] is None
    assert "Amostra insuficiente" in report
    assert "amostra insuficiente" in report.lower()
    assert "CONFIDENCE_MIN" in report


def test_sufficient_sample_picks_the_threshold_by_expected_net_return(tmp_path):
    """Card #1030: o limiar é o argmax do retorno líquido esperado × cobertura."""
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
        regime_boundary_bp=Decimal("0.05"),
    )
    assert summary["windows_non_overlapping"] == 40
    assert summary["stats"]["n_priced"] == 40, "todas as janelas têm preço (E2)"
    assert summary["insufficient"] is False
    assert summary["insufficient_reasons"] == []
    calm = summary["regimes"]["calm"]
    # Elegível = 40 (previsão 60 bp limpa o regime a 14 bp/perna, spread 0,1).
    assert calm["sample"]["n_priced"] == 40
    # A faixa [0.1,0.2) rende −38 bp (20 × −10 − 28) e a [0.3,0.4) rende +12 bp
    # (40 − 28); aceitar tudo dá −13 bp e o limiar 0.3 dá 0,5 × 12 = 6 bp.
    assert Decimal(calm["expected_net_accept_all_bp"]) == Decimal("-13")
    assert calm["separates"] is True
    assert calm["policy"] == "numeric"
    assert calm["chosen"]["threshold"] == "0.3"
    assert calm["chosen"]["n_pass"] == 20
    assert Decimal(calm["chosen"]["coverage"]) == Decimal("0.5")
    assert Decimal(calm["chosen"]["expected_net_bp"]) == Decimal("6")
    # A acurácia é reportada em cada faixa, nunca critério de escolha.
    assert Decimal(calm["bands"]["[0.3, 0.4)"]["accuracy"]) == Decimal("1")
    assert Decimal(calm["bands"]["[0.1, 0.2)"]["accuracy"]) == Decimal("0")
    # O lado activo não tem amostra com esta fronteira: fechado, não opera.
    assert summary["regimes"]["active"]["policy"] == "closed"
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
        regime_boundary_bp=Decimal("0.05"),
    )
    assert summary["windows_non_overlapping"] == 30, "a amostra total chega ao gate"
    assert summary["insufficient"] is False
    assert summary["insufficient_reasons"] == []
    # os 30 trades positivos estão repartidos em buckets de 10: todos ficam
    # abaixo de MIN_BUCKET_TRADES e nenhum pode nascer como sugestão.
    calm = summary["regimes"]["calm"]
    assert calm["policy"] == "closed"
    assert calm["chosen"] is None
    assert any(
        f"{ruler.MIN_BUCKET_TRADES}+ trades com preço" in reason
        for reason in calm["closed_reasons"]
    )
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
    assert summary["regimes"]["calm"]["policy"] == "closed"
    assert summary["regimes"]["active"]["policy"] == "closed"
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


# --- Card #1030: net-return ruler and per-regime threshold -------------------


def _report_with(*, decisions, series, fee_bp="14", boundary="0.05", **overrides):
    kwargs = dict(
        log_path=Path("/tmp/diag.log"),
        decisions=decisions,
        refusals={},
        malformed=0,
        series=series,
        ohlcv_note="OHLCV BTC/USDT 15m",
        fee_bp=Decimal(fee_bp),
        regime_boundary_bp=None if boundary is None else Decimal(boundary),
    )
    kwargs.update(overrides)
    return ruler.build_report(**kwargs)


def test_every_band_reports_accuracy_net_return_and_sample(tmp_path):
    decisions, series = _windows(20, confidence="0.15", realized_bp=-10)
    more, more_series = _windows(20, confidence="0.35", realized_bp=40, start_s=20 * 900)
    report, summary = _report_with(decisions=decisions + more, series=_merge(series, more_series))
    calm = summary["regimes"]["calm"]
    low = calm["bands"]["[0.1, 0.2)"]
    high = calm["bands"]["[0.3, 0.4)"]
    assert low["n_priced"] == 20 and high["n_priced"] == 20
    assert Decimal(low["accuracy"]) == Decimal("0")
    assert Decimal(high["accuracy"]) == Decimal("1")
    # Retorno líquido = realizado assinado − 2 × taxa por perna.
    assert Decimal(low["expectancy_net_bp"]) == Decimal("-38")
    assert Decimal(high["expectancy_net_bp"]) == Decimal("12")
    assert "acurácia" in report
    # A acurácia é reportada e nunca escolhe o limiar: o limiar escolhido é o
    # argmax do retorno líquido esperado, não a faixa mais acurada.
    assert calm["chosen"]["threshold"] == "0.3"


def test_the_threshold_curve_shows_coverage_and_expected_net_return():
    decisions, series = _windows(20, confidence="0.15", realized_bp=-10)
    more, more_series = _windows(20, confidence="0.35", realized_bp=40, start_s=20 * 900)
    _, summary = _report_with(decisions=decisions + more, series=_merge(series, more_series))
    curve = {row["threshold"]: row for row in summary["regimes"]["calm"]["curve"]}
    assert Decimal(curve["0"]["coverage"]) == Decimal("1")
    assert curve["0"]["n_pass"] == 40
    assert Decimal(curve["0.1"]["coverage"]) == Decimal("1")
    assert curve["0.3"]["n_pass"] == 20
    assert Decimal(curve["0.3"]["coverage"]) == Decimal("0.5")
    assert Decimal(curve["0.3"]["expected_gain_bp"]) == Decimal("12")
    assert Decimal(curve["0.3"]["expected_net_bp"]) == Decimal("6")


def test_a_confidence_that_does_not_separate_turns_the_threshold_off():
    """Nenhum limiar bate aceitar tudo com amostra suficiente → desligado."""
    decisions, series = _windows(40, confidence="0.35", realized_bp=40)
    report, summary = _report_with(decisions=decisions, series=series, fee_bp="5")
    calm = summary["regimes"]["calm"]
    assert calm["sample"]["n_priced"] == 40
    assert calm["policy"] == "off"
    assert calm["separates"] is False
    assert "não separa" in report
    assert "desligado" in report
    # O limiar proposto (só para leitura) empata com aceitar tudo: não separa.
    assert Decimal(calm["chosen"]["expected_net_bp"]) == Decimal(calm["expected_net_accept_all_bp"])


def test_a_regime_without_a_boundary_is_closed_and_insufficient():
    decisions, series = _windows(40, confidence="0.35", realized_bp=40)
    report, summary = _report_with(decisions=decisions, series=series, boundary=None)
    assert summary["regime_boundary_bp"] is None
    for regime in ("calm", "active"):
        assert summary["regimes"][regime]["policy"] == "closed"
        assert "fronteira de regime ausente" in summary["regimes"][regime]["closed_reasons"]
    assert "ausente" in report


def test_a_mixed_model_or_origin_blocks_the_threshold():
    decisions, series = _windows(40, confidence="0.35", realized_bp=40)
    for index, decision in enumerate(decisions):
        decision.model = "jev-a" if index < 20 else "jev-b"
        decision.confidence_origin = "reply_field"
    report, summary = _report_with(decisions=decisions, series=series, fee_bp="5")
    calm = summary["regimes"]["calm"]
    assert calm["homogeneous"] is False
    assert calm["policy"] == "closed"
    assert any("homogénea" in reason for reason in calm["closed_reasons"])
    assert summary["homogeneity"]["excluded_windows"] == 20
    assert "NÃO homogénea" in report


def test_the_registered_verdicts_are_the_authority_over_the_predicates():
    decisions, _series = _windows(4, confidence="0.35", realized_bp=40)
    realized = [
        (d, ruler.Realized(Decimal("1"), Decimal("40"), Decimal("40"), "none")) for d in decisions
    ]
    # A reconstrução passa (60 bp limpa o regime com 5 bp/perna)...
    eligible, sources = ruler.eligible_population(realized, fee_bp=Decimal("5"))
    assert len(eligible) == 4
    assert sources == {"registered": 0, "reconstructed": 4}
    # ...mas o veredicto **registado** (#1028) diz `hurdle=fail` e é a autoridade.
    for decision, _ in realized:
        decision.gate_verdicts = {
            "jev_late": "pass",
            "hold": "pass",
            "low_confidence": "pass",
            "hurdle": "fail",
            "regime": "pass",
            "toxic_book": "pass",
        }
        decision.verdict_source = "registered"
    eligible, _sources = ruler.eligible_population(realized, fee_bp=Decimal("5"))
    assert eligible == []


def test_parse_matches_the_cycle_record_to_its_return_and_hurdle_verdict(tmp_path):
    at = datetime(2026, 9, 23, 13, 30, 0)
    log = tmp_path / "diag.log"
    stamp = (at + timedelta(milliseconds=205)).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    log.write_text(
        "\n".join(
            [
                _entry_line("a1", at),
                _return_line("a1", at + timedelta(milliseconds=200), confidence="0.31"),
                f"{stamp} INFO scalp cycle refused user=u skip_reason=hurdle "
                "jev_late=pass hold=pass low_confidence=pass hurdle=fail regime=pass "
                "toxic_book=pass confidence=0.31 market_regime=calm confidence_policy=numeric",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    decisions, _refusals, _malformed = ruler.parse_log(log)
    assert decisions[0].gate_verdicts is not None
    assert decisions[0].gate_verdicts["hurdle"] == "fail"
    assert decisions[0].verdict_source == "registered"


def test_the_report_records_the_fee_source_and_the_value_in_use():
    decisions, series = _windows(40, confidence="0.35", realized_bp=40)
    report, summary = _report_with(
        decisions=decisions,
        series=series,
        fee_bp="7.5",
        fee_source="account",
        confidence_in_use=Decimal("0.7"),
    )
    assert summary["fee_bp"] == "7.5"
    assert summary["fee_source"] == "account"
    assert summary["confidence_in_use"] == "0.70"
    assert "origem: **account**" in report
    assert "valor em uso preservado" in report


def test_the_value_in_use_reads_the_product_default_and_the_off_token(monkeypatch):
    monkeypatch.delenv("SCALP_CONFIDENCE_MIN", raising=False)
    assert ruler._confidence_in_use(None) == ruler.DEFAULT_CONFIDENCE_IN_USE
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN", "0.42")
    assert ruler._confidence_in_use(None) == Decimal("0.42")
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN", "nan")
    assert ruler._confidence_in_use(None) == ruler.DEFAULT_CONFIDENCE_IN_USE
    monkeypatch.setenv("SCALP_CONFIDENCE_MIN", "none")
    assert ruler._confidence_in_use(None) is None
    assert ruler._confidence_in_use("0.3") == Decimal("0.3")


def test_main_accepts_the_boundary_and_the_fee_source(tmp_path, capsys):
    log = tmp_path / "diag.log"
    log.write_text("", encoding="utf-8")
    code = ruler.main(
        [
            "--log",
            str(log),
            "--fee-bp",
            "7.5",
            "--fee-source",
            "account",
            "--regime-boundary-bp",
            "0.05",
            "--json",
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert '"fee_source": "account"' in out
    assert '"regime_boundary_bp": "0.05"' in out


def test_the_boundary_flag_falls_back_to_the_configured_env(monkeypatch):
    """Card #1030: without the flag the ruler uses the decision's boundary."""
    monkeypatch.delenv(ruler.REGIME_BOUNDARY_ENV, raising=False)
    assert ruler._regime_boundary_bp(None) is None
    for raw in ("nan", "inf", "-1", ""):
        monkeypatch.setenv(ruler.REGIME_BOUNDARY_ENV, raw)
        assert ruler._regime_boundary_bp(None) is None, raw
    monkeypatch.setenv(ruler.REGIME_BOUNDARY_ENV, "0.05")
    assert ruler._regime_boundary_bp(None) == Decimal("0.05")
    # O flag presente tem precedência sobre o ambiente.
    assert ruler._regime_boundary_bp("0.07") == Decimal("0.07")


def test_the_boundary_flag_warns_when_it_diverges_from_the_env(monkeypatch, capsys):
    """Card #1030: a divergência entre flag e configuração é avisada."""
    monkeypatch.setenv(ruler.REGIME_BOUNDARY_ENV, "0.05")
    assert ruler._regime_boundary_bp("0.07") == Decimal("0.07")
    err = capsys.readouterr().err
    assert ruler.REGIME_BOUNDARY_ENV in err
    assert "diverge" in err
    # Sem divergência não há aviso.
    assert ruler._regime_boundary_bp("0.05") == Decimal("0.05")
    assert capsys.readouterr().err == ""


def test_the_fallback_fee_is_declared_as_a_report_defect():
    """Card #1030: o fallback com a taxa real ausente é defeito, não neutro."""
    decisions, series = _windows(40, confidence="0.35", realized_bp=40)
    report, summary = _report_with(decisions=decisions, series=series, fee_bp="7.5")
    assert summary["fee_source"] == "fallback"
    assert summary["fee_source_defect"] is True
    assert "defeito do relatório" in report
    # Com a taxa real da conta não há defeito.
    report, summary = _report_with(
        decisions=decisions, series=series, fee_bp="7.5", fee_source="account"
    )
    assert summary["fee_source_defect"] is False
    assert "defeito do relatório" not in report
