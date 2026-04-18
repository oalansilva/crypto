from __future__ import annotations

import math

import pandas as pd
import pytest

from app.metrics import (
    calculate_alpha,
    calculate_avg_drawdown,
    calculate_buy_and_hold,
    calculate_calmar_ratio,
    calculate_cagr,
    calculate_correlation,
    calculate_expectancy,
    calculate_max_consecutive_losses,
    calculate_max_consecutive_wins,
    calculate_max_dd_duration,
    calculate_monthly_return,
    calculate_recovery_factor,
    calculate_sortino_ratio,
    calculate_trade_concentration,
    evaluate_go_nogo,
)
from app.metrics.indicators import calculate_avg_indicators
from app.metrics.regime import calculate_regime_classification
from app.metrics.risk import calculate_drawdown_series


def test_calculate_buy_and_hold_handles_short_and_invalid_entry_series():
    short_prices = pd.Series([100.0])
    invalid_entry_prices = pd.Series([0.0, 110.0])

    assert calculate_buy_and_hold(short_prices, 1000.0) == {
        "return_pct": 0.0,
        "cagr": 0.0,
        "final_value": 1000.0,
    }
    assert calculate_buy_and_hold(invalid_entry_prices, 500.0) == {
        "return_pct": 0.0,
        "cagr": 0.0,
        "final_value": 500.0,
    }


def test_calculate_buy_and_hold_supports_datetime_and_indexless_series():
    dated_prices = pd.Series(
        [100.0, 120.0],
        index=pd.to_datetime(["2025-01-01", "2026-01-01"]),
    )
    plain_prices = pd.Series([100.0, 110.0, 121.0])

    dated = calculate_buy_and_hold(dated_prices, 1000.0)
    plain = calculate_buy_and_hold(plain_prices, 1000.0)

    assert dated["final_value"] == pytest.approx(1200.0)
    assert dated["return_pct"] == pytest.approx(0.2)
    assert dated["cagr"] > 0
    assert plain["final_value"] == pytest.approx(1210.0)
    assert plain["return_pct"] == pytest.approx(0.21)
    assert plain["cagr"] > plain["return_pct"]


def test_alpha_and_correlation_cover_edge_cases():
    assert calculate_alpha(0.25, 0.1) == pytest.approx(0.15)

    strategy = pd.Series([0.01, 0.02, 0.03], index=[1, 2, 3])
    benchmark = pd.Series([0.01, 0.02, 0.04], index=[1, 2, 3])
    constant = pd.Series([0.01, 0.01, 0.01], index=[1, 2, 3])

    assert calculate_correlation(pd.Series([0.1]), pd.Series([0.2])) == 0.0
    assert calculate_correlation(strategy, benchmark) > 0.9
    assert calculate_correlation(constant, constant) == 0.0


def test_evaluate_go_nogo_returns_go_with_positive_reasons_and_warnings():
    metrics = {
        "max_drawdown": 0.32,
        "sharpe_ratio": 1.2,
        "trade_concentration": 0.5,
        "cagr": 0.28,
        "benchmark": {"cagr": 0.18},
        "calmar_ratio": 1.2,
        "profit_factor": 2.1,
        "expectancy": 15.0,
        "total_trades": 180,
    }

    result = evaluate_go_nogo(metrics)

    assert result.status == "GO"
    assert any("Supera Buy & Hold" in reason for reason in result.reasons)
    assert any("Drawdown aceitável" in reason for reason in result.reasons)
    assert any("Calmar Ratio aceitável" in warning for warning in result.warnings)
    assert any("Max Drawdown próximo ao limite" in warning for warning in result.warnings)


def test_evaluate_go_nogo_returns_no_go_when_critical_metrics_fail():
    metrics = {
        "max_drawdown": 0.5,
        "sharpe_ratio": 0.2,
        "trade_concentration": 0.9,
        "cagr": 0.05,
        "benchmark": {"cagr": 0.12},
        "calmar_ratio": 0.3,
        "profit_factor": 1.0,
        "expectancy": -2.0,
        "total_trades": 20,
    }

    result = evaluate_go_nogo(metrics)

    assert result.status == "NO-GO"
    assert any("Max Drawdown crítico" in reason for reason in result.reasons)
    assert any("Sharpe Ratio muito baixo" in reason for reason in result.reasons)
    assert any("Lucro concentrado em poucos trades" in reason for reason in result.reasons)
    assert any("CAGR não supera Buy & Hold" in reason for reason in result.reasons)


def test_calculate_avg_indicators_handles_empty_and_present_columns():
    empty = pd.DataFrame()
    populated = pd.DataFrame({"ATR_14": [1.0, 2.0, 3.0], "ADX_14": [10.0, 20.0, 30.0]})

    assert calculate_avg_indicators(empty) == {"avg_atr": 0.0, "avg_adx": 0.0}
    assert calculate_avg_indicators(populated) == {"avg_atr": 2.0, "avg_adx": 20.0}


def test_calculate_cagr_validates_inputs_and_supports_both_index_modes():
    with pytest.raises(ValueError, match="pelo menos 2 pontos"):
        calculate_cagr(pd.Series([100.0]))

    with pytest.raises(ValueError, match="Valor inicial deve ser positivo"):
        calculate_cagr(pd.Series([0.0, 110.0]))

    dated = pd.Series([100.0, 125.0], index=pd.to_datetime(["2025-01-01", "2026-01-01"]))
    plain = pd.Series([100.0, 130.0, 160.0])

    assert calculate_cagr(dated) > 0
    assert calculate_cagr(plain) > 0


def test_calculate_monthly_return_handles_resample_fallback_and_validation():
    with pytest.raises(ValueError, match="DatetimeIndex"):
        calculate_monthly_return(pd.Series([100.0, 110.0], index=[1, 2]))

    with pytest.raises(ValueError, match="pelo menos 2 pontos"):
        calculate_monthly_return(pd.Series([100.0], index=pd.to_datetime(["2025-01-01"])))

    short_period = pd.Series(
        [100.0, 115.0],
        index=pd.to_datetime(["2025-01-01", "2025-01-20"]),
    )
    monthly = pd.Series(
        [100.0, 110.0, 121.0],
        index=pd.to_datetime(["2025-01-31", "2025-02-28", "2025-03-31"]),
    )
    flat = pd.Series(
        [100.0, 100.0, 100.0],
        index=pd.to_datetime(["2025-01-31", "2025-02-28", "2025-03-31"]),
    )

    assert calculate_monthly_return(short_period) > 0
    assert calculate_monthly_return(monthly) == pytest.approx(0.1)
    assert calculate_monthly_return(flat) == pytest.approx(0.0)


def test_regime_classification_handles_empty_frames_and_missing_sma_column():
    empty = pd.DataFrame()
    source = pd.DataFrame({"close": [100.0, 200.0, 90.0]})

    assert calculate_regime_classification(empty).empty

    derived = calculate_regime_classification(source, sma_period=2)
    with_sma = calculate_regime_classification(
        pd.DataFrame({"close": [100.0, 90.0], "SMA_2": [95.0, 95.0]}),
        sma_period=2,
    )

    assert "regime" in derived.columns
    assert list(with_sma["regime"]) == ["Bull", "Bear"]


def test_risk_functions_cover_drawdown_duration_and_recovery_branches():
    dated = pd.Series(
        [100.0, 120.0, 90.0, 95.0, 130.0],
        index=pd.to_datetime(
            ["2025-01-01", "2025-01-02", "2025-01-05", "2025-01-06", "2025-01-10"]
        ),
    )
    plain = pd.Series([100.0, 90.0, 95.0, 80.0, 110.0], index=[0, 1, 2, 3, 4])

    drawdown = calculate_drawdown_series(dated)

    assert drawdown.iloc[0] == 0.0
    assert drawdown.min() < 0
    assert calculate_avg_drawdown(pd.Series([100.0])) == 0.0
    assert calculate_avg_drawdown(pd.Series([100.0, 110.0])) == 0.0
    assert calculate_avg_drawdown(dated) > 0
    assert calculate_max_dd_duration(pd.Series([100.0])) == 0
    assert calculate_max_dd_duration(pd.Series([100.0, 110.0])) == 0
    assert calculate_max_dd_duration(dated) >= 1
    assert calculate_max_dd_duration(plain) >= 1
    assert math.isinf(calculate_recovery_factor(0.5, 0.0))
    assert calculate_recovery_factor(0.0, 0.0) == 0.0
    assert calculate_recovery_factor(0.6, 0.2) == pytest.approx(3.0)


def test_risk_adjusted_metrics_cover_short_zero_downside_and_standard_case():
    assert calculate_sortino_ratio(pd.Series([0.01])) == 0.0

    positive_only = pd.Series([0.02, 0.03, 0.01])
    identical_negative = pd.Series([-0.01, -0.01, -0.01])
    mixed = pd.Series([0.02, -0.01, 0.03, -0.02])

    assert math.isinf(calculate_sortino_ratio(positive_only))
    assert calculate_sortino_ratio(identical_negative) == 0.0
    assert calculate_sortino_ratio(mixed) != 0.0
    assert math.isinf(calculate_calmar_ratio(0.2, 0.0))
    assert calculate_calmar_ratio(0.0, 0.0) == 0.0
    assert calculate_calmar_ratio(0.3, 0.15) == pytest.approx(2.0)


def test_trade_statistics_cover_empty_and_ranked_cases():
    trades = [{"pnl": 10.0}, {"pnl": -5.0}, {"pnl": 8.0}, {"pnl": -2.0}, {"pnl": 12.0}]

    assert calculate_expectancy([]) == 0.0
    assert calculate_expectancy(trades) == pytest.approx(4.6)
    assert calculate_max_consecutive_wins([]) == 0
    assert calculate_max_consecutive_wins(trades) == 1
    assert calculate_max_consecutive_losses([]) == 0
    assert calculate_max_consecutive_losses(trades) == 1
    assert calculate_trade_concentration([]) == 0.0
    assert calculate_trade_concentration([{"pnl": -1.0}, {"pnl": 0.0}]) == 0.0
    assert calculate_trade_concentration(trades, top_n=2) == pytest.approx((12.0 + 10.0) / 30.0)
