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

    def run(self, df: pd.DataFrame, strategy: Strategy):
        # Reset state
        self.cash = self.initial_capital
        self.position = 0.0
        self.trades = []
        self.equity_curve = []
        
        # Generate signals
        # We expect the strategy to add a 'signal' column or return a Series
        # But to be safe and clean, let's copy the DF or expect the strategy to return signals
        signals_output = strategy.generate_signals(df)
        
        # Handle different return types (Series vs DataFrame)
        if isinstance(signals_output, pd.DataFrame):
            signals = signals_output['signal']
            # Store the full strategy output (indicators) for visualization
            # We enforce that the index aligns
            if 'signal' not in signals_output.columns:
                 raise ValueError("Strategy DataFrame must contain 'signal' column")
        else:
             signals = signals_output
        
        # Check alignment
        if len(signals) != len(df):
            raise ValueError("Signals length mismatch with DataFrame")

        # Combine for iteration
        # We need to iterate row by row for proper portfolio simulation (path dependent)
        simulation_df = df.copy()
        simulation_df['signal'] = signals
        
        # Merge other strategy columns (indicators) if available
        if isinstance(signals_output, pd.DataFrame):
            # Join everything except signal which we already added (and potentially overwrote if index matched)
            # Actually, just joining everything is fine.
            cols_to_use = signals_output.columns.difference(simulation_df.columns)
            simulation_df = simulation_df.join(signals_output[cols_to_use])
            
        self.simulation_data = simulation_df # Store for later use (e.g. plotting indicators)
        
        # --- Pre-calculate Numpy Arrays (CPU Optimization) ---
        # accessing numpy arrays by index is ~100x faster than iterrows
        timestamps = simulation_df['timestamp_utc'].values
        opens = simulation_df['open'].values
        closes = simulation_df['close'].values
        highs = simulation_df['high'].values
        lows = simulation_df['low'].values
        signals = simulation_df['signal'].to_numpy() # Ensure numpy array
        
        # Entry price variable for SL/TP tracking
        avg_entry_price = 0.0
        current_trade_entry_time = None
        
        n_rows = len(simulation_df)

        for i in range(n_rows):
            timestamp = timestamps[i]
            open_price = opens[i]
            close_price = closes[i]
            high_price = highs[i]
            low_price = lows[i]
            signal = signals[i]
            
            # --- Stop Loss / Take Profit Logic (Intrabar trigger check, exit at Close) ---
            sl_hit = False
            tp_hit = False
            
            if self.position > 0:
                if self.stop_loss_pct:
                    stop_price = avg_entry_price * (1 - self.stop_loss_pct)
                    if low_price < stop_price: # Triggered
                        sl_hit = True
                        
                if self.take_profit_pct:
                    tp_price = avg_entry_price * (1 + self.take_profit_pct)
                    if high_price > tp_price: # Triggered
                        tp_hit = True
            
            # Executing SL/TP
            # If both hit in same candle, simpler to assume SL hit first for conservative backtest, or just exit.
            # We exit at CLOSE price as per requirements.
            if sl_hit or tp_hit:
                # Sell everything
                # Determine exit price based on what hit
                # Priority: SL hit? Exit at Stop Price (or Open if gapped down)
                # TP hit? Exit at Take Profit Price (or Open if gapped up)
                # If both hit? Ambiguous. Assume SL hit first (conservative) => Stop Price.
                
                raw_exit_price = close_price # Default fall through
                
                if sl_hit:
                    # Check for gap down
                    if open_price < stop_price:
                        raw_exit_price = open_price # Gapped down, filled at Open
                    else:
                        raw_exit_price = stop_price # Filled at Stop level
                        
                elif tp_hit:
                    # Check for gap up
                    if open_price > tp_price:
                         raw_exit_price = open_price
                    else:
                         raw_exit_price = tp_price
                
                exit_price = raw_exit_price * (1 - self.slippage)
                revenue = self.position * exit_price
                cost_fee = revenue * self.fee
                
                self.cash += (revenue - cost_fee)
                
                reason = "SL" if sl_hit else "TP"
                if sl_hit and tp_hit: reason = "SL/TP" # Ambiguous
                
                pnl = (exit_price - avg_entry_price) * self.position - cost_fee
                pnl_pct = (exit_price - avg_entry_price) / avg_entry_price if avg_entry_price > 0 else 0

                self.trades.append({
                    'entry_time': current_trade_entry_time,
                    'exit_time': timestamp,
                    'side': 'long',
                    'reason': reason,
                    'entry_price': avg_entry_price,
                    'exit_price': exit_price,
                    'size': self.position,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'commission': cost_fee
                })
                
                self.position = 0.0
                avg_entry_price = 0.0
                current_trade_entry_time = None
                
                # If we exited due to SL/TP, we ignore the strategy signal for THIS candle?
                # Usually yes, we are out.
                # However, if signal is BUY, do we re-enter? 
                # Let's assume SL/TP forces flat for this candle.
                
            # --- Strategy Signals (if not just exited) ---
            elif signal == 1: # BUY
                # Calculate max buy amount
                # Position Sizing: % of CURRENT equity (Cash + Value)? Or % of Cash?
                # "percent_of_cash (default 20% por entrada)" -> implies % of available CASH.
                
                amount_to_invest = self.cash * self.position_size_pct
                # Fee buffer? 
                # If we invest X, we pay X.
                # Fee is additional or included? usually additional.
                # But if X is % of cash, we have X available.
                
                if amount_to_invest > 10: # Min trade size 10 USDT
                     # Execute at Close
                     entry_exec_price = close_price * (1 + self.slippage)
                     
                     # Can we afford it?
                     cost_with_fee = amount_to_invest * (1 + self.fee)
                     if cost_with_fee > self.cash:
                         # Adjust to max possible
                         amount_to_invest = self.cash / (1 + self.fee)
                         cost_with_fee = self.cash # Float precision?
                    
                     quantity = amount_to_invest / entry_exec_price
                     commission = amount_to_invest * self.fee
                     
                     # Update avg entry price (weighted avg if adding to position)
                     if self.position > 0:
                         total_val = (self.position * avg_entry_price) + (quantity * entry_exec_price)
                         avg_entry_price = total_val / (self.position + quantity)
                     else:
                         avg_entry_price = entry_exec_price
                         current_trade_entry_time = timestamp

                     self.cash -= (quantity * entry_exec_price + commission)
                     self.position += quantity
                     
                     # Determine trade entry time if this is a new position
                     if current_trade_entry_time is None:
                         current_trade_entry_time = timestamp

            elif signal == -1: # SELL
                if self.position > 0:
                    exit_price = close_price * (1 - self.slippage)
                    revenue = self.position * exit_price
                    commission = revenue * self.fee
                    
                    self.cash += (revenue - commission)
                    
                    pnl = (exit_price - avg_entry_price) * self.position - commission
                    pnl_pct = (exit_price - avg_entry_price) / avg_entry_price if avg_entry_price > 0 else 0
                    
                    self.trades.append({
                        'entry_time': current_trade_entry_time,
                        'exit_time': timestamp,
                        'side': 'long', # It was a long position
                        'reason': 'Signal',
                        'entry_price': avg_entry_price,
                        'exit_price': exit_price,
                        'size': self.position,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'commission': commission
                    })
                    
                    self.position = 0.0
                    avg_entry_price = 0.0
                    current_trade_entry_time = None

            # --- Tracking ---
            equity = self.cash + (self.position * close_price)
            self.equity_curve.append({'timestamp': timestamp, 'equity': equity})

        # End of loop: Force close position if exists
        if self.position > 0:
            # Use last element of arrays instead of iloc
            last_price = closes[-1]
            last_ts = timestamps[-1]
            
            exit_price = last_price * (1 - self.slippage)
            revenue = self.position * exit_price
            commission = revenue * self.fee
            
            self.cash += (revenue - commission)
            
            pnl = (exit_price - avg_entry_price) * self.position - commission
            pnl_pct = (exit_price - avg_entry_price) / avg_entry_price if avg_entry_price > 0 else 0
            
            self.trades.append({
                'entry_time': current_trade_entry_time,
                'exit_time': last_ts,
                'side': 'long',
                'reason': 'Force Close',
                'entry_price': avg_entry_price,
                'exit_price': exit_price,
                'size': self.position,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'commission': commission
            })
            self.position = 0.0
            
            self.equity_curve[-1]['equity'] = self.cash

        return pd.DataFrame(self.equity_curve)
