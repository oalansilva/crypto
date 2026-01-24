
import sys
import os
import asyncio
import logging
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath("backend"))

from app.services.combo_service import ComboService
from app.services.combo_optimizer import extract_trades_with_mode
from src.data.incremental_loader import IncrementalLoader

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

async def compare_strategies():
    print("--- STARTING COMPARISON: ANTIGA vs NOVA (EXACT COMBO LOGIC) ---")
    
    # 1. Initialize Components
    combo_service = ComboService()
    loader = IncrementalLoader()
    
    # Define Strategies
    # Note: Antiga parameters must be mapped to template structure (indicators list)
    # The 'multi_ma_crossover' template expects specific indicator configurations.
    
    # Strategy 1: User Set A
    antiga_params = {
        "short": 20,      # ema_short
        "long": 40,       # sma_long
        "medium": 38,     # sma_medium
        "stop_loss": 0.068
    }

    # Strategy 2: User Set B
    nova_params = {
        "short": 15,      # ema_short
        "long": 47,       # sma_long
        "medium": 33,     # sma_medium
        "stop_loss": 0.069
    }

    strategies = [
        ("STRATEGY_A", antiga_params),
        ("STRATEGY_B", nova_params)
    ]
    
    # 2. Load Data (Once)
    symbol = "BTC/USDT"
    timeframe = "1d"
    # Full history as usually requested for comparisons
    start_date = "2017-01-01"
    end_date = "2026-01-01"
    
    print(f"\nLoading Data for {symbol} {timeframe}...")
    df = loader.fetch_data(symbol, timeframe, start_date, end_date)
    print(f"Loaded {len(df)} candles.")
    if not df.empty:
        print(f"DEBUG: DataFrame Starts: {df.index.min()} Ends: {df.index.max()}")

    results_table = []

    for name, params in strategies:
        print(f"\n--- Running {name} ---")
        print(f"Params: {params}")
        
        try:
            # 3. Create Strategy Instance (Exact production logic)
            # ComboService.create_strategy handles parameter mapping (aliases)
            strategy = combo_service.create_strategy(
                template_name="multi_ma_crossover", # which is 'cruzamentomedias' in backend
                parameters=params
            )
            
            if name == "ANTIGA":
                print(f"DEBUG: ANTIGA Indicators Config: {strategy.indicators}")
            
            # 4. Generate Signals
            df_signals = strategy.generate_signals(df.copy())
            
            # FIX: Shift Signal BACK by 1 (-1) to cancel out double-lag.
            # Strategy generates signal on Day X+1 (to avoid lookahead).
            # Extractor enters on Day Y+1 (next open).
            # Result: Day X Cross -> Signal X+1 -> Entry X+2.
            # We want: Day X Cross -> Entry X+1.
            # So we supply Signal X to extractor.
            if 'signal' in df_signals.columns:
                df_signals['signal'] = df_signals['signal'].shift(-1).fillna(0)
            
            # 5. Extract Trades (Unified Logic)
            # Using extract_trades_with_mode ensures consistency with Optimizer/Backtester
            stop_loss = params.get('stop_loss', 0.0)
            
            trades = extract_trades_with_mode(
                df_with_signals=df_signals,
                stop_loss=stop_loss,
                deep_backtest=True, # Enforcing Deep Backtest as requested
                symbol=symbol,
                since_str=start_date,
                until_str=end_date
            )
            
            # 6. Calculate Metrics (Simple aggregation matching optimizer)
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t['profit'] > 0])
            win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
            total_return = sum([t['profit'] for t in trades])
            
            # Print Trade List for ANTIGA (User Request)
            if name == "ANTIGA":
                print(f"\n>>> LISTA DE TRADES - {name} <<<")
                print(f"{'Entry Time':<25} | {'Type':<6} | {'Entry Price':<12} | {'Exit Time':<25} | {'Exit Price':<12} | {'Profit %':<10} | {'Reason'}")
                print("-" * 115)
                for i, t in enumerate(trades):
                    ent_time = t['entry_time']
                    ext_time = t.get('exit_time', 'Open')
                    ent_price = f"{t['entry_price']:.2f}"
                    ext_price = f"{t.get('exit_price', 0):.2f}"
                    profit = f"{t.get('profit', 0)*100:+.2f}%"
                    reason = t.get('exit_reason', '-')
                    type_ = t.get('type', 'long').upper()
                    
                    print(f"{ent_time:<25} | {type_:<6} | {ent_price:<12} | {ext_time:<25} | {ext_price:<12} | {profit:<10} | {reason}")
                print("-" * 115)
                print(f">>> FIM DA LISTA ({len(trades)} trades) <<<\n")

                # DEBUG: Inspect Data around the discrepancy (Sep 2025 - Oct 2025)
                print("\n>>> DEBUG: DADOS DETALHADOS (Set/Out 2025) <<<")
                
                df_debug = None
                if hasattr(strategy, 'simulation_data'):
                    df_debug = strategy.simulation_data
                elif hasattr(strategy, '_indicator_cache') and 'calculated' in strategy._indicator_cache:
                    df_debug = strategy._indicator_cache['calculated']
                
                if df_debug is not None:
                    # Fallback matching: Just take the last 365 days (covers 2025)
                    df_zoom = df_debug.iloc[-365:]
                    print(f"DEBUG: Showing last {len(df_zoom)} rows (Index Type: {type(df_debug.index)})")
                    print(f"DEBUG: Columns: {df_zoom.columns.tolist()}")

                    # Attempt to find standard column names or aliases
                    # Found via debug: ['short', 'medium', 'long']
                    c_close = 'close'
                    c_ema3 = 'short' 
                    c_sma37 = 'long'
                    c_sma32 = 'medium'
                    
                    print(f"{'Date':<12} | {'Close':<10} | {'EMA 3':<10} | {'SMA 37':<10} | {'SMA 32':<10} | {'Signal'}")
                    print("-" * 100)
                    for idx, row in df_zoom.iterrows():
                        date_str = idx.strftime('%Y-%m-%d')
                        close = f"{row.get(c_close, 0):.2f}"
                        ema3 = f"{row.get(c_ema3, 0):.2f}"
                        sma37 = f"{row.get(c_sma37, 0):.2f}"
                        sma32 = f"{row.get(c_sma32, 0):.2f}"
                        
                        sig = 0
                        if idx in df_signals.index:
                            sig = df_signals.loc[idx, 'signal'] if 'signal' in df_signals.columns else 0
                        
                        # Print relevant range for deep debug (Feb 2025)
                        if "2025-02" in date_str: 
                             print(f"{date_str:<12} | {close:<10} | {ema3:<10} | {sma37:<10} | {sma32:<10} | {sig}")
                    
                    # Also print the specific range around Sep 30
                    print("...")
            # Reconstruct equity curve for MDD (simplified)
            equity = 10000.0
            peak = equity
            max_dd = 0.0
            
            for t in trades:
                equity *= (1 + t['profit'])
                if equity > peak:
                    peak = equity
                dd = (peak - equity) / peak
                if dd > max_dd:
                    max_dd = dd
            
            # Sharpe (Simple)
            returns = [t['profit'] for t in trades]
            if returns:
                std_dev = np.std(returns)
                sharpe = np.mean(returns) / std_dev if std_dev > 0 else 0
            else:
                sharpe = 0

            results_table.append({
                "Strategy": name,
                "Net Profit %": f"{total_return * 100:.2f}%",
                "Total Return (Cmp)": f"{(equity - 10000)/10000 * 100:.2f}%", # Compound Diff check
                "Sharpe": f"{sharpe:.3f}",
                "Win Rate %": f"{win_rate * 100:.2f}%",
                "Trades": total_trades,
                "Max DD %": f"{max_dd * 100:.2f}%"
            })
            
        except Exception as e:
            print(f"Error running {name}: {e}")
            import traceback
            traceback.print_exc()

    # 7. Print Comparison
    if results_table:
        df_res = pd.DataFrame(results_table)
        print("\n\n=== FINAL COMPARISON RESULTS (Exact Combo Logic) ===")
        print(df_res.to_string(index=False))
        print("====================================================")

if __name__ == "__main__":
    asyncio.run(compare_strategies())
