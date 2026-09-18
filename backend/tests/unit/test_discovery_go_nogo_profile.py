"""Discovery GO/NO-GO profile (card #969) vs Combo walk-forward."""

from app.metrics.criteria import evaluate_discovery_go_nogo, evaluate_walk_forward


def _btc_rs_e0e30719cc_train():
    return {
        "total_trades": 43,
        "sharpe_ratio": 0.50,
        "calmar_ratio": 10.6,
        "profit_factor": 2.0,
        "max_drawdown": 0.12,
        "cagr": 0.45,
        "benchmark": {"cagr": 0.20},
    }


def _btc_rs_e0e30719cc_oos():
    return {
        "total_trades": 24,
        "sharpe_ratio": 0.35,
        "calmar_ratio": 1.2,
        "profit_factor": 1.6,
        "max_drawdown": 0.15,
    }


def test_btc_fixture_go_discovery_no_go_combo():
    train = _btc_rs_e0e30719cc_train()
    oos = _btc_rs_e0e30719cc_oos()
    discovery = evaluate_discovery_go_nogo(train, oos)
    combo = evaluate_walk_forward(train, oos)
    assert discovery.status == "GO"
    assert combo.status == "NO-GO"


def test_holdout_sharpe_non_positive_is_nogo_holdout():
    train = _btc_rs_e0e30719cc_train()
    oos = {**_btc_rs_e0e30719cc_oos(), "sharpe_ratio": -0.18}
    result = evaluate_discovery_go_nogo(train, oos)
    assert result.status == "NO-GO"
    assert any(r.startswith("Holdout") for r in result.reasons)


def test_weak_train_portrait_nogo_treino_with_positive_oos():
    train = {
        **_btc_rs_e0e30719cc_train(),
        "calmar_ratio": 0.42,
    }
    oos = _btc_rs_e0e30719cc_oos()
    result = evaluate_discovery_go_nogo(train, oos)
    assert result.status == "NO-GO"
    assert any(r.startswith("Treino") and "Calmar" in r for r in result.reasons)


def test_missing_oos_sharpe_fail_closed():
    train = _btc_rs_e0e30719cc_train()
    oos = {**_btc_rs_e0e30719cc_oos(), "sharpe_ratio": float("nan")}
    result = evaluate_discovery_go_nogo(train, oos)
    assert result.status == "NO-GO"
    assert any("Holdout" in r and "não finito" in r for r in result.reasons)


def test_4h_short_same_rule_as_1d_long():
    train = {
        "total_trades": 35,
        "sharpe_ratio": 0.55,
        "calmar_ratio": 1.4,
        "profit_factor": 1.7,
        "max_drawdown": 0.20,
    }
    oos = {"total_trades": 22, "sharpe_ratio": 0.12}
    assert evaluate_discovery_go_nogo(train, oos).status == "GO"


def test_persist_metrics_snapshot_uses_discovery_profile(monkeypatch):
    from app.tasks import discovery_tasks

    captured = {}

    def fake_eval(is_metrics, oos_metrics):
        captured["called"] = True
        return type("R", (), {"status": "GO", "reasons": ["ok"], "warnings": []})()

    monkeypatch.setattr(
        "app.metrics.criteria.evaluate_discovery_go_nogo",
        fake_eval,
    )
    best = {"sharpe_ratio": 0.5, "calmar_ratio": 2.0, "profit_factor": 2.0, "max_drawdown": 0.1}
    result = {
        "oos_metrics": {"sharpe_ratio": 0.3, "total_trades": 20},
        "oos_verdict": {"status": "NO-GO", "reasons": ["Combo"], "holdout_trades": 20},
    }
    metrics = discovery_tasks._persist_metrics_snapshot(best, result, 40, eligible=True)
    assert captured.get("called")
    assert metrics["oos_verdict"]["status"] == "GO"
    assert metrics["oos_verdict"]["holdout_trades"] == 20

    low_sample_metrics = discovery_tasks._persist_metrics_snapshot(best, result, 40, eligible=False)
    assert "oos_verdict" not in low_sample_metrics


def test_persist_metrics_snapshot_fail_closed_without_oos_dict():
    from app.tasks import discovery_tasks

    best = {
        "sharpe_ratio": 0.5,
        "calmar_ratio": 2.0,
        "profit_factor": 2.0,
        "max_drawdown": 0.1,
    }
    result = {
        "oos_metrics": None,
        "oos_verdict": {"status": "ERROR", "reasons": ["holdout falhou"]},
    }
    metrics = discovery_tasks._persist_metrics_snapshot(best, result, 40, eligible=True)
    assert metrics["oos_verdict"]["status"] == "NO-GO"
    assert any("Holdout" in r for r in metrics["oos_verdict"]["reasons"])


def test_row_oos_verdict_sanitizes_low_sample():
    from types import SimpleNamespace

    from app.services.discovery_service import _row_oos_verdict

    row = SimpleNamespace(
        eligibility="low_sample",
        metrics={"oos_verdict": {"status": "NO-GO", "reasons": ["legado"]}},
    )
    assert _row_oos_verdict(row) is None
