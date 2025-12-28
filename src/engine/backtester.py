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
        signals = strategy.generate_signals(df)
        
        # Check alignment
        if len(signals) != len(df):
            raise ValueError("Signals length mismatch with DataFrame")

        # Combine for iteration
        # We need to iterate row by row for proper portfolio simulation (path dependent)
        simulation_df = df.copy()
        simulation_df['signal'] = signals
        
        # Entry price variable for SL/TP tracking
        avg_entry_price = 0.0

        for i, row in simulation_df.iterrows():
            timestamp = row['timestamp_utc']
            open_price = row['open']
            close_price = row['close']
            high_price = row['high']
            low_price = row['low']
            signal = row['signal']
            
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
                exit_price = close_price * (1 - self.slippage)
                revenue = self.position * exit_price
                cost_fee = revenue * self.fee
                
                self.cash += (revenue - cost_fee)
                
                reason = "SL" if sl_hit else "TP"
                if sl_hit and tp_hit: reason = "SL/TP" # Ambiguous
                
                self.trades.append({
                    'entry_time': current_trade_entry_time,
                    'exit_time': timestamp,
                    'symbol': 'BTC/USDT', # TODO: Pass symbol
                    'side': 'SELL',
                    'reason': reason,
                    'price': exit_price,
                    'size': self.position,
                    'pnl': (exit_price - avg_entry_price) * self.position - cost_fee, # Approx
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
                     
                     self.trades.append({
                        'entry_time': timestamp,
                        'exit_time': None,
                        'side': 'BUY',
                        'price': entry_exec_price,
                        'size': quantity,
                        'commission': commission
                     })

            elif signal == -1: # SELL
                if self.position > 0:
                    # Sell ALL? "só vende se tiver posição".
                    # Strategies like SMA cross usually imply flip or full exit.
                    # Simplest is Full Exit on signal.
                    
                    exit_price = close_price * (1 - self.slippage)
                    revenue = self.position * exit_price
                    commission = revenue * self.fee
                    
                    self.cash += (revenue - commission)
                    
                    self.trades.append({
                        'entry_time': current_trade_entry_time, # From last full open? 
                        # This logging is tricky with partial scale-ins. 
                        # But for "Swing" usually 1 entry / 1 exit.
                        'exit_time': timestamp,
                        'side': 'SELL',
                        'reason': 'Signal',
                        'price': exit_price,
                        'size': self.position,
                        'pnl': (exit_price - avg_entry_price) * self.position - commission,
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
            last_price = simulation_df.iloc[-1]['close'] # Or use the last close_price from loop
            # Use last timestamp
            last_ts = simulation_df.iloc[-1]['timestamp_utc']
            
            exit_price = last_price * (1 - self.slippage)
            revenue = self.position * exit_price
            commission = revenue * self.fee
            
            self.cash += (revenue - commission)
            
            self.trades.append({
                'entry_time': current_trade_entry_time,
                'exit_time': last_ts,
                'side': 'SELL',
                'reason': 'Force Close',
                'price': exit_price,
                'size': self.position,
                'pnl': (exit_price - avg_entry_price) * self.position - commission,
                'commission': commission
            })
            self.position = 0.0
            
            # Update last point in equity curve to reflect cash only (minus fees)
            # Actually equity curve tracks mark-to-market so it shouldn't change much except for fee
            self.equity_curve[-1]['equity'] = self.cash

        return pd.DataFrame(self.equity_curve)
