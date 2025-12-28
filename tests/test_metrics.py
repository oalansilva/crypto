import pytest
import pandas as pd
from src.report.metrics import calculate_metrics

def test_max_drawdown_calculation():
    # Equity curve: 100 -> 110 -> 120 -> 90 -> 100
    # Peak: 100, 110, 120, 120, 120
    # DD: 0, 0, 0, (90-120)/120=-0.25, (100-120)/120=-0.16
    # Max DD: -0.25
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2023-01-01', periods=5),
        'equity': [100, 110, 120, 90, 100]
    })
    
    metrics = calculate_metrics(df, [], initial_capital=100)
    assert metrics['max_drawdown_pct'] == -0.25
