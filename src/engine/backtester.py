import pandas as pd
import numpy as np
from src.strategy.base import Strategy

class Backtester:
    def __init__(self, initial_capital=10000, fee=0.001, slippage=0.0005, position_size_pct=0.2, stop_loss_pct=None, take_profit_pct=None):
        self.initial_capital = initial_capital
        self.fee = fee
        self.slippage = slippage
        self.position_size_pct = position_size_pct
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        
        # State
        self.cash = initial_capital
        self.position = 0.0 # Asset amount
        self.trades = []
        self.equity_curve = []

    def run(self, df: pd.DataFrame, strategy: Strategy, record_force_close: bool = False):
        # Reset state
        self.cash = self.initial_capital
        self.position = 0.0
        self.trades = []
        self.equity_curve = []
        
        # Generate signals
        # We expect the strategy to add a 'signal' column or return a Series
        signals_output = strategy.generate_signals(df)
        
        # Handle different return types (Series vs DataFrame)
        if isinstance(signals_output, pd.DataFrame):
            signals = signals_output['signal']
            if 'signal' not in signals_output.columns:
                 raise ValueError("Strategy DataFrame must contain 'signal' column")
        else:
             signals = signals_output
        
        # Check alignment
        if len(signals) != len(df):
            raise ValueError("Signals length mismatch with DataFrame")

        # Combine for iteration
        simulation_df = df.copy()
        # Use .values to ignore index mismatch
        simulation_df['signal'] = signals.values if hasattr(signals, 'values') else signals
        
        if isinstance(signals_output, pd.DataFrame):
            cols_to_use = signals_output.columns.difference(simulation_df.columns)
            simulation_df = simulation_df.join(signals_output[cols_to_use])
            
        accumulated_commission = 0.0
        entry_equity = 0.0
        
        # --- 3. Simulation Loop ---
        self.simulation_data = simulation_df 
        
        # --- Pre-calculate Numpy Arrays (CPU Optimization) ---
        if 'timestamp_utc' in simulation_df.columns:
            timestamps = simulation_df['timestamp_utc'].values
        elif 'timestamp' in simulation_df.columns:
            timestamps = simulation_df['timestamp'].values
        elif isinstance(simulation_df.index, pd.DatetimeIndex):
            timestamps = simulation_df.index.values
        else:
            timestamps = np.array([i for i in range(len(simulation_df))])

        opens = simulation_df['open'].values
        closes = simulation_df['close'].values
        highs = simulation_df['high'].values
        lows = simulation_df['low'].values
        signals = simulation_df['signal'].to_numpy() 
        
        avg_entry_price = 0.0
        current_trade_entry_time = None
        
        n_rows = len(simulation_df)
        
        
        # Pre-calculate Buy Signals for fast jumping
        buy_indices = np.where(signals == 1)[0]
        
        # Initial Equity Record
        self.equity_curve.append({'timestamp': timestamps[0], 'equity': self.cash})
        
        i = 0
        while i < n_rows:
            # Current candle data
            # timestamp = timestamps[i] # Accessed only if needed
            
            if self.position == 0:
                # Flat: Search for next BUY signal
                if i < n_rows:
                    # Find first index where signal == 1 AND index >= i
                    # Note: We need a buy signal at 'k', to execute at 'k+1'
                    next_buy_ptr = np.searchsorted(buy_indices, i)
                    
                    if next_buy_ptr >= len(buy_indices):
                        break # No more buys
                        
                    next_buy_idx = buy_indices[next_buy_ptr]
                    
                    # Execution happens at Open of NEXT candle
                    execution_idx = next_buy_idx + 1
                    
                    if execution_idx >= n_rows:
                        # Signal on last candle, cannot enter
                        break
                    
                    # Jump to execution candle
                    i = execution_idx
                    
                    # Execute BUY at Open
                    open_price = opens[i]
                    timestamp = timestamps[i]
                    
                    if self.cash <= 0:
                        break
                    
                    allocated_cash = self.cash * self.position_size_pct
                    entry_exec_price = open_price * (1 + self.slippage)
                    
                    quantity = allocated_cash / (entry_exec_price * (1 + self.fee))
                    
                    if quantity * entry_exec_price > 10: 
                        commission = (quantity * entry_exec_price) * self.fee
                        
                        avg_entry_price = entry_exec_price
                        current_trade_entry_time = timestamp
                        accumulated_commission = commission
                        entry_equity = self.cash 
                        
                        self.cash -= (quantity * entry_exec_price + commission)
                        self.position += quantity
                        
                        # Record Equity at Entry
                        # We are at 'i' (execution day). We hold position.
                        # Equity will be recorded at the end of this iteration loop (or next?)
                        # Strictly, if we buy at Open, we are exposed to 'i' close.
                        # We should let the loop continue to process 'i' as holding.
                    
                    # Do NOT increment i here. 
                    # We want to process candle 'i' in the 'else' block (Checking SL/TP/Close)
                    # changing state to position > 0 will make next iteration go to 'else'
                    # But we need to force next iteration on SAME 'i'
                    continue 
                else:
                    break

            else:
                # Long: Step-by-step logic
                timestamp = timestamps[i]
                open_price = opens[i]
                close_price = closes[i]
                high_price = highs[i]
                low_price = lows[i]
                signal = signals[i]
                prev_signal = signals[i-1] if i > 0 else 0
                
                # Check Exits
                exit_candidates = []
                
                # 0. Pending Signal Exit (From Previous Close) - HIGHEST PRIORITY (Market Open)
                # If we had a sell signal yesterday, we exit TODAY at Open.
                if prev_signal == -1:
                    # Execute Exit at OPEN
                    exit_price = open_price * (1 - self.slippage)
                    revenue = self.position * exit_price
                    exit_commission = revenue * self.fee
                    total_commission = accumulated_commission + exit_commission
                    
                    pnl_gross = (exit_price - avg_entry_price) * self.position
                    pnl = pnl_gross - total_commission
                    pnl_pct = (exit_price - avg_entry_price) / avg_entry_price if avg_entry_price > 0 else 0
                    
                    self.cash += (revenue - exit_commission)
                    current_equity = self.cash
                    
                    self.trades.append({
                        'entry_time': current_trade_entry_time,
                        'exit_time': timestamp,
                        'side': 'long',
                        'reason': 'Signal',
                        'entry_price': avg_entry_price,
                        'exit_price': exit_price,
                        'size': self.position,
                        'pnl_gross': pnl_gross,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'commission': total_commission,
                        'initial_capital': entry_equity,
                        'final_capital': current_equity
                    })
                    
                    self.position = 0.0
                    accumulated_commission = 0.0
                    self.equity_curve.append({'timestamp': timestamp, 'equity': self.cash})
                    
                    # We exited at Open. We are Flat for the rest of 'i'.
                    # Should we check for Buy Signal at 'i'?
                    # If 'signal[i] == 1', we would buy at 'i+1'. 
                    # So we can just continue to next iteration 'i' (as Flat).
                    # But if we don't increment, we process 'i' again as Flat.
                    # Correct.
                    continue

                # 1. Stop Loss (Intra-bar)
                if self.stop_loss_pct:
                    stop_price = avg_entry_price * (1 - self.stop_loss_pct)
                    if low_price < stop_price:
                        exit_candidates.append(('sl', 0, stop_price))

                # 2. Take Profit (Intra-bar)
                if self.take_profit_pct:
                    tp_price = avg_entry_price * (1 + self.take_profit_pct)
                    if high_price > tp_price:
                        exit_candidates.append(('tp', 0, tp_price))
                
                if not exit_candidates:
                    # No SL/TP hit.
                    # Check current signal for NEXT DAY exit
                    # If signal == -1, we DO NOTHING now. We wait for next Open (handled by Prev Signal check above)
                    
                    # Mark-to-Market Equity Check
                    equity_val = self.cash + (self.position * close_price)
                    self.equity_curve.append({'timestamp': timestamp, 'equity': equity_val})
                    
                    i += 1
                    continue
                
                # Handle SL/TP Execution (Intra-bar)
                sl_hit = any(x[0] == 'sl' for x in exit_candidates)
                tp_hit = any(x[0] == 'tp' for x in exit_candidates)
                
                event_type = 'sl' if sl_hit else 'tp'
                
                # Determine Price
                if sl_hit:
                    stop_price = avg_entry_price * (1 - self.stop_loss_pct)
                    best_exit_price = min(open_price, stop_price) # Pessimistic: Gap handling? 
                    # Realistically: If Open < Stop, we execute at Open (Gap Down)
                    if open_price < stop_price: best_exit_price = open_price
                    else: best_exit_price = stop_price
                else: # TP
                    tp_price = avg_entry_price * (1 + self.take_profit_pct)
                    # If Open > TP, we execute at Open (Gap Up)
                    if open_price > tp_price: best_exit_price = open_price
                    else: best_exit_price = tp_price

                # Execute Exit
                raw_exit_price = best_exit_price
                exit_reason = "SL" if sl_hit else "TP"
                
                exit_price = raw_exit_price * (1 - self.slippage)
                revenue = self.position * exit_price
                exit_commission = revenue * self.fee
                total_commission = accumulated_commission + exit_commission
                
                self.cash += (revenue - exit_commission)
                
                pnl_gross = (exit_price - avg_entry_price) * self.position
                pnl = pnl_gross - total_commission
                pnl_pct = (exit_price - avg_entry_price) / avg_entry_price if avg_entry_price > 0 else 0
                
                current_equity = self.cash
                
                self.trades.append({
                    'entry_time': current_trade_entry_time,
                    'exit_time': timestamp,
                    'side': 'long',
                    'reason': exit_reason,
                    'entry_price': avg_entry_price,
                    'exit_price': exit_price,
                    'size': self.position,
                    'pnl_gross': pnl_gross,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'commission': total_commission,
                    'initial_capital': entry_equity,
                    'final_capital': current_equity
                })
                
                self.position = 0.0
                accumulated_commission = 0.0
                
                self.equity_curve.append({'timestamp': timestamp, 'equity': self.cash})
                
                i += 1


        # End of loop: Force close position if exists (for Equity Curve only)
        # Note: We do NOT append to self.trades as user requested to ignore force close
        if self.position > 0:
            last_price = closes[-1]
            last_ts = timestamps[-1]
            # Mark to Market
            equity_val = self.cash + (self.position * last_price)
            self.equity_curve.append({'timestamp': last_ts, 'equity': equity_val})
            
            if record_force_close:
                # Force Exit Logic
                raw_exit_price = last_price
                exit_reason = "Force Close"
                
                exit_price = raw_exit_price * (1 - self.slippage) # Still apply slippage on hypothetical exit? Yes.
                revenue = self.position * exit_price
                exit_commission = revenue * self.fee
                total_commission = accumulated_commission + exit_commission
                
                # Update cash for final theoretical state (optional, but consistent with trade record)
                final_cash = self.cash + (revenue - exit_commission) 
                
                pnl_gross = (exit_price - avg_entry_price) * self.position
                pnl = pnl_gross - total_commission
                pnl_pct = (exit_price - avg_entry_price) / avg_entry_price if avg_entry_price > 0 else 0
                
                self.trades.append({
                    'entry_time': current_trade_entry_time,
                    'exit_time': last_ts,
                    'side': 'long',
                    'reason': exit_reason,
                    'entry_price': avg_entry_price,
                    'exit_price': exit_price,
                    'size': self.position,
                    'pnl_gross': pnl_gross,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'commission': total_commission,
                    'initial_capital': entry_equity,
                    'final_capital': final_cash
                })

        df_result = pd.DataFrame(self.equity_curve)
        if not df_result.empty:
             # Ensure timestamp is datetime
             df_result['timestamp'] = pd.to_datetime(df_result['timestamp'])
             df_result.set_index('timestamp', inplace=True, drop=False)
             
        return df_result
