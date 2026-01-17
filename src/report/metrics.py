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
    sharpe = 0.0  # Initialize sharpe here
    stop_loss_count = 0  # Initialize stop loss count
    
    if not df_trades.empty and 'pnl' in df_trades.columns:
        # PnL only exists for closed trades
        # We look for rows where 'pnl' is not null (NaN)
        closed_trades = df_trades[df_trades['pnl'].notna()]
        if not closed_trades.empty:
            num_trades = len(closed_trades)
            winners = closed_trades[closed_trades['pnl'] > 0]
            win_rate = len(winners) / num_trades
            
            # Count stop losses
            if 'reason' in closed_trades.columns:
                stop_loss_count = len(closed_trades[closed_trades['reason'] == 'Stop Loss'])
            
            gross_profit = closed_trades[closed_trades['pnl'] > 0]['pnl'].sum()
            gross_loss = abs(closed_trades[closed_trades['pnl'] < 0]['pnl'].sum())
            
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
            avg_trade_return = closed_trades['pnl'].mean()
            
            # Sharpe Ratio - Calculate from trade returns, not daily equity changes
            # For low-frequency strategies, daily returns are mostly zero which gives Sharpe ≈ 0
            if len(closed_trades) > 1:
                # Calculate returns as percentage of capital per trade
                trade_returns = closed_trades['pnl'] / initial_capital
                mean_trade_return = trade_returns.mean()
                std_trade_return = trade_returns.std()
                
                if std_trade_return > 0:
                    # Sharpe Ratio = (Mean Return - Risk Free Rate) / Std Dev
                    # Assuming risk-free rate = 0 for crypto
                    # Annualize: multiply by sqrt(trades_per_year)
                    # Estimate trades per year based on duration
                    trades_per_year = (num_trades / duration_days) * 365 if duration_days > 0 else num_trades
                    sharpe = (mean_trade_return / std_trade_return) * np.sqrt(trades_per_year)
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
    
    return {
        'total_return_pct': total_return_pct,
        'total_pnl_pct': total_return_pct, # Alias
        'total_pnl': final_equity - initial_capital, # Added
        'max_drawdown_pct': max_drawdown_pct,
        'max_drawdown': max_drawdown_pct, # Alias
        'cagr': cagr,
        'num_trades': num_trades,
        'total_trades': num_trades, # Alias
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'avg_trade_return': avg_trade_return,
        'sharpe': sharpe,
        'sharpe_ratio': sharpe, # Alias for consistency
        'final_equity': final_equity,
        'duration_days': duration_days,
        'stop_loss_count': stop_loss_count  # Quantidade de stops acionados
    }
