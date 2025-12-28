import pandas as pd
import numpy as np

def calculate_metrics(equity_curve: pd.DataFrame, trades: list, initial_capital=10000) -> dict:
    if equity_curve.empty:
        return {}

    # Equity Curve Metrics
    equity_series = equity_curve['equity']
    final_equity = equity_series.iloc[-1]
    total_return_pct = (final_equity - initial_capital) / initial_capital
    
    # Drawdown
    rolling_max = equity_series.cummax()
    drawdown = (equity_series - rolling_max) / rolling_max
    max_drawdown_pct = drawdown.min()
    
    # CAGR
    start_time = equity_curve['timestamp'].iloc[0]
    end_time = equity_curve['timestamp'].iloc[-1]
    duration_days = (end_time - start_time).days
    
    if duration_days > 30:
        cagr = (final_equity / initial_capital) ** (365 / duration_days) - 1
    else:
        cagr = 0.0 # Not meaningful
        
    # Trade Metrics
    df_trades = pd.DataFrame(trades)
    if not df_trades.empty and 'pnl' in df_trades.columns:
        # PnL only exists for closed trades (SELLs)
        closed_trades = df_trades[df_trades['side'] == 'SELL']
        if not closed_trades.empty:
            num_trades = len(closed_trades)
            winners = closed_trades[closed_trades['pnl'] > 0]
            win_rate = len(winners) / num_trades
            
            gross_profit = closed_trades[closed_trades['pnl'] > 0]['pnl'].sum()
            gross_loss = abs(closed_trades[closed_trades['pnl'] < 0]['pnl'].sum())
            
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
            avg_trade_return = closed_trades['pnl'].mean()
        else:
            num_trades = 0
            win_rate = 0.0
            profit_factor = 0.0
            avg_trade_return = 0.0
    else:
        num_trades = 0
        win_rate = 0.0
        profit_factor = 0.0
        avg_trade_return = 0.0
        
    # Periodic Returns for Sharpe
    # Resample to common timeframe? Or just pct_change of equity curve?
    # Equity curve is per candle.
    equity_curve['returns'] = equity_series.pct_change().dropna()
    mean_ret = equity_curve['returns'].mean()
    std_ret = equity_curve['returns'].std()
    
    sharpe = mean_ret / std_ret if std_ret > 0 else 0.0
    
    return {
        'total_return_pct': total_return_pct,
        'max_drawdown_pct': max_drawdown_pct,
        'cagr': cagr,
        'num_trades': num_trades,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'avg_trade_return': avg_trade_return,
        'sharpe': sharpe,
        'final_equity': final_equity,
        'duration_days': duration_days
    }
