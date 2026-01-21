
import sys
import os
import pandas as pd
import logging
from app.services.combo_optimizer import extract_trades_with_mode
from src.data.incremental_loader import IncrementalLoader
from app.strategies.combos.combo_strategy import ComboStrategy
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_test():
    symbol = "ETH/USDT"
    timeframe = "1d"
    start_date = "2017-01-01"
    end_date = "2026-01-21"
    
    # 1. Fetch Data
    loader = IncrementalLoader()
    df = loader.fetch_data(symbol, timeframe, start_date, end_date)
    logger.info(f"Loaded {len(df)} rows for {symbol} {timeframe}")

    # Strategies to test
    strategies = {
        "OLD_BEST (Double Lag?)": {"ema_short": 15, "sma_medium": 36, "sma_long": 55, "stop_loss": 0.066},
        "NEW_BEST (Single Lag)":  {"ema_short": 8, "sma_medium": 17, "sma_long": 33, "stop_loss": 0.068},
    }

    results = []

    for name, params in strategies.items():
        logger.info(f"--- Testing {name} ---")
        
        # 2. Config Indicators
        indicators = [
            {"type": "ema", "alias": "ema_short", "params": {"length": params['ema_short']}},
            {"type": "sma", "alias": "sma_medium", "params": {"length": params['sma_medium']}},
            {"type": "sma", "alias": "sma_long", "params": {"length": params['sma_long']}}
        ]
        
        entry_logic = "(close > ema_short) and (ema_short > sma_medium) and (sma_medium > sma_long)"
        exit_logic = "(close < sma_medium)" # Standard exit for this type? Or checks crossover?
        # WAIT! The Multi MA Crossover logic in template is usually:
        # Entry: Short > Medium > Long
        # Exit: Short < Medium  (CrossUnder)
        # I need to be sure about the logic used by the user. 
        # Assuming standard "Cruzamento Medias" template logic for now.
        
        # Checking template logic from backend would be safer, but let's assume standard Trend Following:
        # Entry: All aligned.
        # Exit: Short crosses under Medium (or something similar).
        
        # Let's use the standard "Cruzamento" logic from the template if possible.
        # But for this script I'll mimic the likely logic:
        # Entry: fast > medium > slow
        # Exit: fast < medium
        
        # 2A. STATE-BASED LOGIC (Re-entry allowed)
        # entry_logic = "(ema_short > sma_medium) & (sma_medium > sma_long)"
        # exit_logic = "(ema_short < sma_medium)"
        
        strategy = ComboStrategy(
            indicators=indicators,
            entry_logic="(ema_short > sma_medium) & (sma_medium > sma_long)",
            exit_logic="(ema_short < sma_medium)",
            stop_loss=params['stop_loss']
        )
        
        df_signals_state = strategy.generate_signals(df.copy())

        # 2B. CROSSOVER-BASED LOGIC (TradingView Style - Event Only)
        # Convert State signals (1, 1, 1...) to Event signals (1, 0, 0...)
        # We only take the FIRST '1' in a sequence.
        df_signals_event = df_signals_state.copy()
        
        # Identify Rising Edge: Current is 1 (Buy), Previous was not 1
        # Signal column has 1 (Buy), -1 (Sell), 0 (Neutral)
        # Note: generate_signals output has 1s on ALL bars where condition was met AND trade was active?
        # NO! generate_signals returns 1 ONLY on the bar where 'pending_entry' became active.
        # Wait, let's check generate_signals loop again.
        
        # ComboStrategy.generate_signals loop:
        # if pending_entry and not in_position: signals[i] = 1; in_position = True
        
        # It ONLY puts '1' on the bar OF ENTRY. It does NOT put '1' on subsequent bars while holding.
        # However, if it Stopped Out (-1), in_position becomes False.
        # Next bar: if entry_bits[i] is True (State still valid), it sets pending_entry = True.
        # Next bar: signals[i+1] = 1. RE-ENTRY!
        
        # So to simulate TradingView (No Re-entry), we need to filter `entry_bits` BEFORE the loop.
        # We cannot easily filter post-generation because the loop logic couples Entry/Exit/Stop.
        
        # Solution: We must subclass/mock ComboStrategy locally to Enforce Rising Edge on `entry_bits`.
        
        # Extract the boolean masks first
        df = strategy.calculate_indicators(df)
        entry_mask = strategy._evaluate_logic_vectorized(df, strategy.entry_logic)
        exit_mask = strategy._evaluate_logic_vectorized(df, strategy.exit_logic)
        
        # Force Rising Edge Only on Entry Mask
        # Entry Event = Entry State AND (NOT Previous Entry State)
        entry_mask_series = pd.Series(entry_mask, index=df.index)
        entry_event_mask = entry_mask_series & (~entry_mask_series.shift(1).fillna(False))
        
        # Now run strategy with this NEW mask (hack: replace _evaluate_logic_vectorized)
        
        # We will create a custom class inheriting from ComboStrategy
        class CrossoverComboStrategy(ComboStrategy):
            def _evaluate_logic_vectorized(self, df, logic):
                mask = super()._evaluate_logic_vectorized(df, logic)
                if logic == self.entry_logic:
                     # Force Rising Edge
                     mask_series = pd.Series(mask, index=df.index)
                     return (mask_series & (~mask_series.shift(1).fillna(False)))
                return mask
                
        strategy_crossover = CrossoverComboStrategy(
            indicators=indicators,
            entry_logic="(ema_short > sma_medium) & (sma_medium > sma_long)",
            exit_logic="(ema_short < sma_medium)",
            stop_loss=params['stop_loss']
        )
        
        df_signals = strategy_crossover.generate_signals(df.copy())
        
        # 3. Test with CURRENT Logic (Single Lag)
        logger.info("  > Simulating CURRENT LOGIC (Single Lag / Day+1)")
        try:
            trades_current = extract_trades_with_mode(
                df_signals.copy(),
                params['stop_loss'],
                deep_backtest=True, # Force Deep
                symbol=symbol,
                since_str=start_date,
                until_str=end_date
            )
            metrics_current = calculate_metrics(trades_current)
        except Exception as e:
            import traceback
            traceback.print_exc()
            metrics_current = {"total_return_pct": 0, "total_trades": 0}
        
        # 4. Test with OLD BUG LOGIC (Double Lag / Day+2)
        logger.info("  > Simulating OLD BUG LOGIC (Double Lag / Day+2)")
        try:
            df_signals_bug = df_signals.copy()
            df_signals_bug['signal'] = df_signals_bug['signal'].shift(1).fillna(0) # Re-introduce the bug
            
            trades_bug = extract_trades_with_mode(
                df_signals_bug,
                params['stop_loss'],
                deep_backtest=True,
                symbol=symbol,
                since_str=start_date,
                until_str=end_date
            )
            metrics_bug = calculate_metrics(trades_bug)
        except Exception as e:
            import traceback
            traceback.print_exc()
            metrics_bug = {"total_return_pct": 0, "total_trades": 0}
        
        results.append({
            "Strategy": name,
            "Mode": "CURRENT (Day+1)",
            "Return %": metrics_current['total_return_pct'],
            "Trades": metrics_current['total_trades']
        })
        results.append({
            "Strategy": name,
            "Mode": "OLD (Day+2)",
            "Return %": metrics_bug['total_return_pct'],
            "Trades": metrics_bug['total_trades']
        })

    print("\n=== FINAL ANALYSIS ===")
    df_res = pd.DataFrame(results)
    print(df_res)

def calculate_metrics(trades):
    if not trades:
        return {"total_return_pct": 0, "total_trades": 0}
    
    # Calculate compounded return
    capital = 100.0
    for t in trades:
        gain = t['profit'] # This is percentage e.g. 0.05
        capital = capital * (1 + gain)
    
    total_return = (capital - 100.0)
    return {"total_return_pct": total_return, "total_trades": len(trades)}

if __name__ == "__main__":
    run_test()
