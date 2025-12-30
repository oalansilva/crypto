
import sys
import os
import functools
import traceback
import logging
from typing import Dict, Any, List, Tuple, Union
import pandas as pd

# Add project root to path to ensure imports work
# We need to add:
# 1. Project Root (absolute/path/to/project) -> for 'src' imports
# 2. Backend Root (absolute/path/to/project/backend) -> for 'app' imports (if run from project root)
# Actually, if we are in backend/app/workers, project root is ../../../
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
backend_root = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_root)
sys.path.insert(0, project_root)

# Import core modules
# We wrap imports in try-except to debug path issues if they occur
try:
    from src.engine.backtester import Backtester
    from app.strategies.dynamic_strategy import DynamicStrategy
    from src.report.metrics import calculate_metrics
    from app.metrics import (
        calculate_cagr, calculate_sortino_ratio, calculate_calmar_ratio
    )
except ImportError as e:
    logging.error(f"Failed to import modules in worker: {e}")
    # We don't raise here to allow inspection, but it will fail later
    pass

# Global variable to hold shared data in the worker process
_worker_data_cache: Dict[str, pd.DataFrame] = {}

def init_worker(data_map: Dict[str, pd.DataFrame]):
    """
    Initialize the worker process.
    This runs once per process when the pool starts.
    """
    global _worker_data_cache
    _worker_data_cache = data_map
    
    # Clear lru cache to ensure clean state
    _get_signals_for_params.cache_clear()
    
    # Configure logging for worker
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(processName)s - %(message)s'
    )

class CachedStrategy:
    """
    A wrapper strategy that returns pre-calculated signals.
    Used to bypass redundant indicator calculation in Backtester.
    """
    def __init__(self, df_with_signals: pd.DataFrame):
        self.df = df_with_signals

    def generate_signals(self, df: pd.DataFrame):
        # We ignore the input df because we know it matches self.df 
        # (or at least shares the same index/length)
        return self.df

@functools.lru_cache(maxsize=128)
def _get_signals_for_params(strategy_name: str, params_tuple: Tuple[Tuple[str, Any]], timeframe: str) -> pd.DataFrame:
    """
    Generate indicators/signals and return the DataFrame.
    Cached to reuse results when only execution params change.
    """
    if timeframe not in _worker_data_cache:
        raise ValueError(f"Timeframe '{timeframe}' not found in worker cache")
        
    df = _worker_data_cache[timeframe].copy()
    params = dict(params_tuple)
    
    try:
        # Instantiate the strategy
        # We assume DynamicStrategy for versatility as per current service usage
        # DynamicStrategy expects a single config dict {name: ..., param: ...}
        strat_init_config = {'name': strategy_name}
        strat_init_config.update(params)
        strategy = DynamicStrategy(strat_init_config)
        
        # Generate signals (modifies df or returns new one)
        output = strategy.generate_signals(df)
        
        if isinstance(output, pd.DataFrame):
            return output
        # If it returns Series (shouldn't happen for DynamicStrategy usually, but handle it)
        df['signal'] = output
        return df
        
    except Exception as e:
        logging.error(f"Error generating signals for {strategy_name}: {e}")
        raise e

def evaluate_combination(config: Dict, combination: Tuple, keys: List[str]) -> Dict:
    """
    Execute a single backtest for a parameter combination.
    """
    try:
        # 1. Parse Combination
        params_dict = dict(zip(keys, combination))
        
        # Separate Strategy Params vs Global/Execution Params
        # We identify execution params by name
        execution_keys = {'stop_pct', 'take_pct', 'timeframe', 'cash', 'fee', 'slippage'}
        
        global_params = {k: v for k, v in params_dict.items() if k in execution_keys}
        strat_params = {k: v for k, v in params_dict.items() if k not in execution_keys}
        
        # Determine timeframe
        # Priority: Param > Config > Default
        timeframe = global_params.get('timeframe', config.get('timeframe'))
        # Handle list case in config (should be resolved by now but safe check)
        if isinstance(timeframe, list):
            timeframe = timeframe[0]
            
        # 2. Get Cached Data (Indicators)
        # Create hashable tuple for cache key
        strat_params_tuple = tuple(sorted(strat_params.items()))
        strategy_config = config['strategies'][0]
        strategy_name = strategy_config if isinstance(strategy_config, str) else strategy_config.get('name', 'Strategy')
        
        # This call is CACHED
        df_with_signals = _get_signals_for_params(str(strategy_name), strat_params_tuple, str(timeframe))
        
        # 3. Setup Backtester
        # Use simple params if not in global_params (defaults)
        stop_loss = global_params.get('stop_pct', config.get('stop_pct'))
        take_profit = global_params.get('take_pct', config.get('take_pct'))
        
        backtester = Backtester(
            initial_capital=config.get('cash', 10000),
            fee=config.get('fee', 0.001),
            slippage=config.get('slippage', 0.0005),
            position_size_pct=0.2,
            stop_loss_pct=stop_loss,
            take_profit_pct=take_profit
        )
        
        # 4. Run Backtest
        # Pass CachedStrategy to skip indicator calculation
        cached_strat = CachedStrategy(df_with_signals)
        equity_curve = backtester.run(df_with_signals, cached_strat)
        
        if equity_curve is None or equity_curve.empty:
            return None

        # 5. Calculate Metrics
        trades = backtester.trades
        if not trades:
            # Handle no trades case gracefully
            total_pnl = 0.0
            metrics = {
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'total_trades': 0,
                'sharpe_ratio': 0.0,
                'drawdown': 0.0
            }
        else:
            metrics = calculate_metrics(equity_curve, trades, backtester.initial_capital)
            
            # Enhanced Metrics
            # We can invoke app.metrics if needed, replicating backtest_service logic
            try:
                metrics['cagr'] = calculate_cagr(equity_curve['equity'], len(df_with_signals)) # approx
                metrics['sortino_ratio'] = calculate_sortino_ratio(equity_curve['equity'])
                metrics['calmar_ratio'] = calculate_calmar_ratio(equity_curve['equity'])
            except:
                pass

        # 6. Format Result
        result = {
            'strategy': strategy_name,
            'params': {**global_params, **strat_params},
            'metrics': metrics,
            'timeframe': timeframe
        }
        
        return result

    except Exception as e:
        # Catch-all to prevent worker crash
        # logging.error(f"Worker Exception: {e}")
        # traceback.print_exc()
        # Try to construct params if possible for debugging
        try:
             params_dict = dict(zip(keys, combination))
        except:
             params_dict = {'raw': combination}
        return {'error': str(e), 'params': params_dict}

def evaluate_chunk(config: Dict, combinations: List[Tuple], keys: List[str]) -> List[Dict]:
    """
    Evaluate a batch of combinations.
    Reduces IPC overhead by sending/receiving data in chunks.
    """
    results = []
    for comb in combinations:
        res = evaluate_combination(config, comb, keys)
        if res:
            results.append(res)
    return results
