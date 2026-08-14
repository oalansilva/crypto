"""Testes do gate walk-forward combinado Treino (IS) / Holdout (OOS) (card #503)."""

from __future__ import annotations

import pytest

from app.metrics.criteria import (
    DEFAULT_CRITERIA,
    OOS_CRITERIA,
    evaluate_go_nogo,
    evaluate_walk_forward,
)


def _metrics(
    *,
    sharpe: float = 0.8,
    trades: int = 100,
    cagr: float = 0.30,
    bh_cagr: float = 0.10,
    max_dd: float = 0.15,
    calmar: float = 1.5,
    profit_factor: float = 1.6,
    expectancy: float = 10.0,
    concentration: float = 0.5,
) -> dict:
    """Métricas que aprovam DEFAULT_CRITERIA por padrão (GO no IS)."""
    return {
        "sharpe_ratio": sharpe,
        "total_trades": trades,
        "cagr": cagr,
        "benchmark": {"cagr": bh_cagr},
        "max_drawdown": max_dd,
        "calmar_ratio": calmar,
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        "trade_concentration": concentration,
    }


def _oos_metrics(*, sharpe: float = 0.5, trades: int = 40, **overrides) -> dict:
    """Métricas que aprovam o perfil OOS por padrão."""
    return _metrics(sharpe=sharpe, trades=trades, **overrides)


class TestSegmentedCriteria:
    def test_oos_criteria_is_explicit_copy_without_mutating_default(self):
        assert OOS_CRITERIA["min_trades"] == 20
        assert OOS_CRITERIA["min_sharpe_ratio"] == 0.30
        assert DEFAULT_CRITERIA["min_trades"] == 100
        assert DEFAULT_CRITERIA["min_sharpe_ratio"] == 0.8
        assert {
            k: v for k, v in OOS_CRITERIA.items() if k not in ("min_trades", "min_sharpe_ratio")
        } == {
            k: v for k, v in DEFAULT_CRITERIA.items() if k not in ("min_trades", "min_sharpe_ratio")
        }

    def test_non_walk_forward_evaluation_uses_default_unchanged(self):
        result = evaluate_go_nogo(_metrics(sharpe=0.7))
        assert result.status == "NO-GO"
        assert any("0.8" in r for r in result.reasons)


class TestWalkForwardGate:
    def test_is_ok_oos_too_few_trades(self):
        result = evaluate_walk_forward(_metrics(), _oos_metrics(trades=19))
        assert result.status == "NO-GO"
        assert any("Holdout (OOS)" in r and "19" in r and "20" in r for r in result.reasons)

    def test_oos_20_to_29_trades_passes_count_with_warning(self):
        result = evaluate_walk_forward(_metrics(), _oos_metrics(trades=25, sharpe=0.45))
        assert any("amostra pequena" in w and "25" in w for w in result.warnings)

    def test_is_ok_oos_low_sharpe(self):
        result = evaluate_walk_forward(_metrics(), _oos_metrics(sharpe=0.29))
        assert result.status == "NO-GO"
        assert any("0.29" in r and "0.30" in r for r in result.reasons)

    def test_degradation_above_tolerance(self):
        result = evaluate_walk_forward(_metrics(sharpe=1.00), _oos_metrics(sharpe=0.45, trades=40))
        assert result.status == "NO-GO"
        assert any(
            "Consistência IS→OOS" in r and "45%" in r and "50%" in r and "0.50" in r
            for r in result.reasons
        )

    def test_reference_case_23_trades_sharpe_032(self):
        result = evaluate_walk_forward(_metrics(sharpe=0.80), _oos_metrics(sharpe=0.32, trades=23))
        assert result.status == "NO-GO"
        assert any("amostra pequena" in w for w in result.warnings)
        assert any(
            "Consistência IS→OOS" in r
            and "0.80" in r
            and "0.32" in r
            and "40%" in r
            and "0.40" in r
            for r in result.reasons
        )

    def test_boundary_approved(self):
        result = evaluate_walk_forward(_metrics(sharpe=0.80), _oos_metrics(sharpe=0.40, trades=20))
        assert result.status == "GO"
        assert any("GO walk-forward" in r for r in result.reasons)

    def test_is_weak_oos_strong_does_not_compensate(self):
        result = evaluate_walk_forward(
            _metrics(sharpe=0.5, trades=80), _oos_metrics(sharpe=1.2, trades=50)
        )
        assert result.status == "NO-GO"
        assert any("Treino (IS)" in r for r in result.reasons)

    def test_is_strong_oos_weak_does_not_compensate(self):
        result = evaluate_walk_forward(_metrics(sharpe=1.2), _oos_metrics(sharpe=0.2, trades=50))
        assert result.status == "NO-GO"
        assert any("Holdout (OOS)" in r or "Consistência IS→OOS" in r for r in result.reasons)

    def test_missing_and_non_finite_metrics_fail_closed(self):
        result = evaluate_walk_forward({"total_trades": 120}, _oos_metrics())
        assert result.status == "NO-GO"
        assert any("Treino (IS)" in r and "sharpe_ratio" in r for r in result.reasons)

        result_nan = evaluate_walk_forward(_metrics(), _oos_metrics(sharpe=float("nan"), trades=30))
        assert result_nan.status == "NO-GO"
        assert any("Holdout (OOS)" in r and "sharpe_ratio" in r for r in result_nan.reasons)

        result_inf = evaluate_walk_forward(_metrics(sharpe=float("inf")), _oos_metrics(sharpe=0.5))
        assert result_inf.status == "NO-GO"
        assert any("Treino (IS)" in r and "sharpe_ratio" in r for r in result_inf.reasons)

    def test_non_positive_is_sharpe_does_not_compute_retention(self):
        result = evaluate_walk_forward(
            _metrics(sharpe=0.0, trades=200), _oos_metrics(sharpe=0.5, trades=50)
        )
        assert result.status == "NO-GO"
        assert not any("retenção" in r for r in result.reasons)
        assert any("Treino (IS)" in r for r in result.reasons)


class TestMessages:
    def test_reasons_ordered_is_then_oos_then_consistency(self):
        result = evaluate_walk_forward(
            _metrics(sharpe=0.5, trades=80), _oos_metrics(sharpe=0.2, trades=15)
        )
        indexes = [
            next(i for i, r in enumerate(result.reasons) if prefix in r)
            for prefix in ("Treino (IS)", "Holdout (OOS)", "Consistência IS→OOS")
        ]
        assert indexes == sorted(indexes)

    def test_go_summary_confirms_all_three(self):
        result = evaluate_walk_forward(_metrics(), _oos_metrics(sharpe=0.5, trades=40))
        assert result.status == "GO"
        assert any(
            "Treino (IS)" in r and "Holdout (OOS)" in r and "consistência" in r
            for r in result.reasons
        )

    def test_messages_include_observed_and_threshold(self):
        result = evaluate_walk_forward(_metrics(), _oos_metrics(sharpe=0.28, trades=19))
        joined = " | ".join(result.reasons)
        assert "19" in joined and "20" in joined
        assert "0.28" in joined and "0.30" in joined


class TestOverrideIntegration:
    def test_override_policy_unchanged(self):
        from app.services.walk_forward_revalidation import oos_gate_decision

        verdict = {
            "status": "NO-GO",
            "reasons": ["Holdout (OOS) — Sharpe Ratio muito baixo: 0.28 < 0.3"],
            "warnings": [],
        }
        blocked = oos_gate_decision(verdict)
        assert blocked["allowed"] is False
        allowed = oos_gate_decision(verdict, override=True, is_admin=True)
        assert allowed["allowed"] is True
        assert "override admin explícito" in allowed["reason"]
        no_admin = oos_gate_decision(verdict, override=True, is_admin=False)
        assert no_admin["allowed"] is False
        # Razões originais preservadas para auditoria.
        assert "Holdout (OOS)" in blocked["reason"]
