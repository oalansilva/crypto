import pandas as pd

def compare_results(results: list, sort_by='score'):
    """
    results: List of dicts, each containing metrics + 'strategy_name', 'timeframe', etc.
    """
    df = pd.DataFrame(results)
    
    # Calculate Score: Return - 0.5 * MaxDD (MaxDD is negative, so Return + 0.5 * |MaxDD| ?)
    # MaxDD from metrics is usually negative (e.g. -0.20).
    # "score = return - k*drawdown" -> if drawdown is positive number?
    # Usually DD is represented as positive % decline or negative value.
    # In my metrics: 'max_drawdown_pct' is negative (e.g., -0.15 for 15% drop).
    # So: Return - 0.5 * (-0.15) = Return + 0.075 -> Rewards higher drawdown? No.
    # We want to PENALIZE drawdown.
    # Score = Return - 0.5 * abs(Drawdown)
    # OR Score = Return + (Drawdown is negative) -> Return + Drawdown? No.
    # If DD is -0.15, we want to penalize 0.15.
    # Score = Return - 0.5 * 0.15
    # Score = Return + 0.5 * Drawdown (since DD is negative).
    
    k = 0.5
    df['score'] = df['total_return_pct'] + (k * df['max_drawdown_pct'])
    
    if sort_by == 'score':
        df.sort_values('score', ascending=False, inplace=True)
    else:
        if sort_by in df.columns:
            df.sort_values(sort_by, ascending=False, inplace=True)
            
    return df
