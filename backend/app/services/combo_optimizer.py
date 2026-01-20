"""
Combo Strategy Optimizer

Hybrid Grid Optimization Strategy:
Combines Grid Search for correlated parameters with Sequential Optimization for independent ones.

Features:
- Hybrid Stage Generation: Automatically identifies correlated groups (e.g., [media_curta, media_inter, media_longa]) and generates joint Grid Search stages.
- Single Round Execution: Disables iterative refinement (max_rounds=1) when Grid Search is active to avoid local maximum traps.
- Parallel Execution: Uses ProcessPoolExecutor for both Sequential (single parameter) and Grid (multi-parameter) tests.
- Deep Backtesting: Integrated simulation for precision testing using 15m intraday data.
"""

import json
import concurrent.futures
import os
import time
import logging
import itertools  # For Grid Search cartesian product
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd

from app.services.sequential_optimizer import SequentialOptimizer
from app.services.combo_service import ComboService
from app.services.backtest_service import BacktestService
from src.data.incremental_loader import IncrementalLoader
from app.services.deep_backtest import simulate_execution_with_15m

# -----------------------------------------------------------------------------
# SHARED LOGIC HELPER
# -----------------------------------------------------------------------------
def extract_trades_from_signals(df_with_signals, stop_loss: float):
    """
    Extract trades from signals with consistent logic:
    - Intra-candle Stop Loss (Low vs Stop Price)
    - Binance Fees (0.075% per op)
    - Exit at exact Stop Price if triggered
    """
    TRADING_FEE = 0.00075
    trades = []
    position = None
    
    # Pre-calculate stop loss threshold to avoid repeated float casting
    stop_loss_pct = float(stop_loss) if stop_loss is not None else 0.0
    
    for idx, row in df_with_signals.iterrows():
        # Check stop loss if we have an open position
        if position is not None and stop_loss_pct > 0:
            current_low = float(row['low'])
            entry_price = position['entry_price']
            
            # Intra-candle stop check
            # We use (Low - Entry) / Entry for quick check
            # Or simpler: Low <= Entry * (1 - Stop)
            exact_stop_price = entry_price * (1 - stop_loss_pct)
            
            if current_low <= exact_stop_price:
                # Stop loss triggered
                # Keep UTC timezone to match TradingView
                position['exit_time'] = idx.isoformat()
                position['exit_price'] = exact_stop_price
                
                # Calculate Net Profit with Fees
                # ((Exit*(1-fee)) - (Entry*(1+fee))) / (Entry*(1+fee))
                position['profit'] = ((exact_stop_price * (1 - TRADING_FEE)) - (entry_price * (1 + TRADING_FEE))) / (entry_price * (1 + TRADING_FEE))
                
                position['exit_reason'] = 'stop_loss'
                trades.append(position)
                position = None
                continue  # Skip signal check for this candle

        # Check signals
        if row['signal'] == 1 and position is None:
            # Keep UTC timezone to match TradingView
            position = {
                'entry_time': idx.isoformat(),
                'entry_price': float(row['open']), # Execute at OPEN
                'type': 'long'
            }
        elif row['signal'] == -1 and position is not None:
            # Normal exit (Signal) - execute at OPEN
            exit_price = float(row['open'])
            entry_price = position['entry_price']
            
            position['exit_time'] = idx.isoformat()
            position['exit_price'] = exit_price
            
            # Calculate Net Profit with Fees
            position['profit'] = ((exit_price * (1 - TRADING_FEE)) - (entry_price * (1 + TRADING_FEE))) / (entry_price * (1 + TRADING_FEE))
            
            position['exit_reason'] = 'signal'
            trades.append(position)
            position = None
            
    return trades

def extract_trades_with_mode(
    df_with_signals,
    stop_loss: float,
    deep_backtest: bool = False,
    symbol: str = None,
    since_str: str = None,
    until_str: str = None,
    df_15m_cache: Optional[pd.DataFrame] = None
):
    """
    Extract trades using either Fast (daily) or Deep (15m) backtesting mode.
    
    Args:
        df_with_signals: DataFrame with daily signals
        stop_loss: Stop loss percentage
        deep_backtest: If True, use 15m intraday simulation
        symbol: Trading pair (required for deep backtest)
        since_str: Start date (required for deep backtest)
        until_str: End date (required for deep backtest)
        
    Returns:
        List of trades
    """
    if not deep_backtest:
        # Fast mode: use existing daily-only logic
        return extract_trades_from_signals(df_with_signals, stop_loss)
    
    # Deep Backtesting mode: fetch 15m data and simulate execution
    logger = logging.getLogger(__name__)
    # logger.info(f"Deep Backtesting enabled for {symbol}") # Too noisy for grid search
    
    if not symbol or not since_str:
        logger.warning("Deep Backtesting requires symbol and date range. Falling back to fast mode.")
        return extract_trades_from_signals(df_with_signals, stop_loss)
    
    try:
        if df_15m_cache is not None:
            df_15m = df_15m_cache
        else:
            # Fetch 15m data
            loader = IncrementalLoader()
            df_15m = loader.fetch_intraday_data(
                symbol=symbol,
                timeframe='15m',
                since_str=since_str,
                until_str=until_str
            )
        
        if df_15m.empty:
            if df_15m_cache is None: # Only warn if we tried to fetch it
                logger.warning("No 15m data available. Falling back to fast mode.")
            return extract_trades_from_signals(df_with_signals, stop_loss)
        
        if df_15m_cache is None:
            logger.info(f"Fetched {len(df_15m)} 15m candles for deep backtest simulation")
        
        # Run deep backtest simulation
        trades = simulate_execution_with_15m(
            df_daily_signals=df_with_signals,
            df_15m=df_15m,
            stop_loss=stop_loss
        )
        
        return trades
        
    except Exception as e:
        logger.error(f"Error in deep backtest: {e}. Falling back to fast mode.")
        return extract_trades_from_signals(df_with_signals, stop_loss)

# -----------------------------------------------------------------------------
# WORKER FUNCTION (Top-level for ProcessPoolExecutor)
# -----------------------------------------------------------------------------
def _run_backtest_logic(template_data, params, df, deep_backtest, symbol, since_str, until_str, df_15m_cache=None):
    """Core backtest logic shared by single and batch workers."""
    try:
        # Reconstruct strategy logic locally to avoid DB connection in worker
        indicators = template_data["indicators"]
        entry_logic = template_data["entry_logic"]
        exit_logic = template_data["exit_logic"]
        stop_loss = template_data.get("stop_loss", 0.015)
        
        # Handle stop_loss if it's a dict with 'default' key
        if isinstance(stop_loss, dict):
            stop_loss = stop_loss.get("default", 0.015)
            
        # Apply parameter overrides
        import copy
        indicators = copy.deepcopy(indicators)
        
        if params:
            for param_key, param_value in params.items():
                if param_key == "stop_loss":
                    stop_loss = param_value
                    continue
                
                if param_key == "timeframe":
                    continue

                matched = False
                for indicator in indicators:
                    alias = indicator.get("alias", "")
                    type_ = indicator.get("type", "")
                    
                    # 1. Try "alias_param" format (e.g., "short_length") - Generated by auto-schema
                    if alias and param_key.startswith(f"{alias}_"):
                        target_field = param_key[len(alias)+1:]
                        if "params" not in indicator: indicator["params"] = {}
                        indicator["params"][target_field] = param_value
                        matched = True
                        break
                    
                    # 2. Try "type_alias" format (e.g., "sma_short") - Used in multi_ma_crossover
                    # Default to 'length' or 'period' if not specified
                    if alias and type_ and param_key == f"{type_}_{alias}":
                        if "params" not in indicator: indicator["params"] = {}
                        # Try to find which param to update: length, period, or default to length
                        if "length" in indicator["params"]:
                            indicator["params"]["length"] = param_value
                        elif "period" in indicator["params"]:
                            indicator["params"]["period"] = param_value
                        else:
                            indicator["params"]["length"] = param_value # Fallback
                        matched = True
                        break

                    # 3. Try exact alias match (e.g. "short")
                    if alias and param_key == alias:
                        if "params" not in indicator: indicator["params"] = {}
                        if "length" in indicator["params"]:
                            indicator["params"]["length"] = param_value
                        elif "period" in indicator["params"]:
                            indicator["params"]["period"] = param_value
                        else:
                            indicator["params"]["length"] = param_value
                        matched = True
                        break

        # Create strategy instance
        from app.strategies.combos import ComboStrategy
        strategy = ComboStrategy(
            indicators=indicators,
            entry_logic=entry_logic,
            exit_logic=exit_logic,
            stop_loss=stop_loss
        )
        
        # Generate signals
        df_with_signals = strategy.generate_signals(df.copy())


        
        # Extract trades from signals WITH STOP LOSS using Deep or Fast mode
        trades = extract_trades_with_mode(
            df_with_signals, 
            stop_loss,
            deep_backtest=deep_backtest,
            symbol=symbol,
            since_str=since_str,
            until_str=until_str,
            df_15m_cache=df_15m_cache
        )


        
        # Calculate metrics
        metrics = {
            'total_trades': 0,
            'win_rate': 0,
            'total_return': 0,
            'avg_profit': 0,
            'sharpe_ratio': 0
        }

        if len(trades) > 0:
            total_trades = len(trades)
            winning_trades = sum(1 for t in trades if t['profit'] > 0)
            metrics['total_trades'] = total_trades
            metrics['win_rate'] = winning_trades / total_trades
            metrics['total_return'] = sum(t['profit'] for t in trades)
            metrics['avg_profit'] = metrics['total_return'] / total_trades
            
            # Simple Sharpe approximation
            returns = [t['profit'] for t in trades]
            import numpy as np
            std_dev = np.std(returns)
            metrics['sharpe_ratio'] = np.mean(returns) / std_dev if std_dev > 0 else 0
        
        # Construct full effective parameters for logging
        full_params = {}
        for ind in indicators:
            p_prefix = ind.get("alias") or ind.get("type")
            for pk, pv in ind.get("params", {}).items():
                full_params[f"{p_prefix}_{pk}"] = pv
        
        full_params['stop_loss'] = stop_loss
        
        return metrics, full_params
        
    except Exception as e:
        # Return empty metrics on failure
        return {
            'total_trades': 0,
            'win_rate': 0,
            'total_return': 0,
            'avg_profit': 0,
            'sharpe_ratio': 0,
            'error': str(e)
        }, params

def _worker_run_backtest(args):
    """Legacy worker for single execution (Sequential Mode)."""
    template_data, params, df, stage_param, value, deep_backtest, symbol, since_str, until_str = args
    # Silence loggers
    logging.getLogger('src.data.incremental_loader').setLevel(logging.WARNING)
    logging.getLogger('app.services.deep_backtest').setLevel(logging.WARNING)
    logging.getLogger('app.services.combo_optimizer').setLevel(logging.WARNING)
    
    metrics, full_params = _run_backtest_logic(template_data, params, df, deep_backtest, symbol, since_str, until_str)

    if 'error' in metrics:
        return {
            'value': value,
            'error': metrics['error'],
            'success': False
        }
    else:
        return {
            'value': value,
            'params': params,  # Input overrides
            'full_params': full_params, # Complete effective state
            'metrics': metrics,
            'trades_count': metrics['total_trades'],
            'success': True
        }
        



def _worker_run_batch(batch_args):
    """
    Optimized worker for Grid Search BATCH execution.
    Loads 15m data ONCE per batch to eliminate redundant I/O.
    """
    if not batch_args:
        return []

    # Silence loggers
    logging.getLogger('src.data.incremental_loader').setLevel(logging.WARNING)
    logging.getLogger('app.services.deep_backtest').setLevel(logging.WARNING)
    logging.getLogger('app.services.combo_optimizer').setLevel(logging.WARNING)

    results = []
    
    # 1. Initialize Optimization Cache (Load 15m data once)
    df_15m_cache = None
    first_arg = batch_args[0]
    # unpacking args structure: 
    # template_data, params, df, stage_param, value, deep_backtest, symbol, since_str, until_str
    deep_backtest = first_arg[5]
    symbol = first_arg[6]
    since_str = first_arg[7]
    until_str = first_arg[8]
    
    if deep_backtest:
        try:
            loader = IncrementalLoader()
            df_15m_cache = loader.fetch_intraday_data(
                symbol=symbol,
                timeframe='15m',
                since_str=since_str,
                until_str=until_str
            )


        except Exception as e:
            # proceed without cache
            pass

    # 2. Iterate through batch
    for args in batch_args:
        template_data, params, df, stage_param, value, deep_backtest, _, _, _ = args
        
        metrics, full_params = _run_backtest_logic(
            template_data, 
            params, 
            df, 
            deep_backtest, 
            symbol, 
            since_str, 
            until_str,
            df_15m_cache # Pass the cached data
        )
        
        # Wrap result to match single worker structure
        if 'error' in metrics:
            results.append({
                'value': value,
                'error': metrics['error'],
                'success': False
            })
        else:
            results.append({
                'value': value,
                'params': params,
                'full_params': full_params,
                'metrics': metrics,
                'trades_count': metrics['total_trades'],
                'success': True
            })
        
    return results


class ComboOptimizer:
    """
    Optimizer for combo strategies.
    
    Extends SequentialOptimizer logic to handle multiple indicators
    and their parameters in combo strategies.
    """
    
    def __init__(self, checkpoint_dir: str = "backend/data/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.combo_service = ComboService()
        self.backtest_service = BacktestService()
        self.loader = IncrementalLoader()
    
    def generate_stages(
        self,
        template_name: str,
        symbol: str,
        fixed_timeframe: Optional[str] = None,
        custom_ranges: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate optimization stages for a combo strategy.
        Supports Grid Search for correlated parameters.
        
        Args:
            template_name: Name of combo template
            symbol: Trading symbol
            fixed_timeframe: If set, skips timeframe optimization
            custom_ranges: Custom parameter ranges
            
        Returns:
            List of stage configurations
        """
        # Get template metadata
        metadata = self.combo_service.get_template_metadata(template_name)
        
        # Validate correlation metadata if present
        self._validate_correlation_metadata(metadata)
        
        stages = []
        stage_num = 1
        
        # Get optimization schema from database (if available)
        optimization_schema = metadata.get('optimization_schema', {})
        correlated_groups = optimization_schema.get('correlated_groups', [])
        parameters = optimization_schema.get('parameters', {})
        
        # Fallback for Flat Schema (historical data support)
        if not parameters and optimization_schema and not optimization_schema.get('correlated_groups'):
            # Heuristic: If values are dicts with 'min'/'max', assume flat parameters
            first_key = next(iter(optimization_schema), None)
            if first_key:
                first_val = optimization_schema[first_key]
                if isinstance(first_val, dict) and ('min' in first_val or 'start' in first_val):
                     parameters = optimization_schema
        
        # Track which parameters have been added to stages
        processed_params = set()
        
        # PHASE 1: Create Grid Search stages for correlated groups
        for group in correlated_groups:
            # Generate value lists for each parameter in the group
            value_lists = []
            param_names = []
            
            for param_name in group:
                if param_name not in parameters:
                    continue  # Skip if parameter not found (validation should have caught this)
                
                config = parameters[param_name]
                
                # Check for custom range override
                if custom_ranges and param_name in custom_ranges:
                    custom = custom_ranges[param_name]
                    values = self._generate_range_values(
                        custom.get('min', config.get('min')),
                        custom.get('max', config.get('max')),
                        custom.get('step', config.get('step'))
                    )
                else:
                    values = self._generate_range_values(
                        config.get('min'),
                        config.get('max'),
                        config.get('step')
                    )
                
                value_lists.append(values)
        # PHASE 1: Create Grid Search stages for correlated groups
        for group in correlated_groups:
            # Generate value lists for each parameter in the group
            value_lists = []
            param_names = []
            adaptive_meta = {}
            
            for param_name in group:
                if param_name not in parameters:
                    continue  # Skip if parameter not found (validation should have caught this)
                
                config = parameters[param_name]
                
                # Check for custom range override
                if custom_ranges and param_name in custom_ranges:
                    custom = custom_ranges[param_name]
                    p_min = custom.get('min', config.get('min'))
                    p_max = custom.get('max', config.get('max'))
                    target_step = custom.get('step', config.get('step'))
                else:
                    p_min = config.get('min')
                    p_max = config.get('max')
                    target_step = config.get('step')

                # Calculate Coarse Step for Round 1
                coarse_step = self._calculate_coarse_step(p_min, p_max, target_step)
                
                values = self._generate_range_values(p_min, p_max, coarse_step)
                
                value_lists.append(values)
                param_names.append(param_name)
                processed_params.add(param_name)
                
                # Store metadata for adaptive refinement
                adaptive_meta[param_name] = {
                    'target_step': target_step,
                    'current_step': coarse_step,
                    'min': p_min,
                    'max': p_max
                }
            
            # Create Grid Search stage
            if param_names:
                stage = {
                    "stage_num": stage_num,
                    "stage_name": f"Grid Search: {', '.join(param_names)}",
                    "parameter": param_names,  # List of parameters (Grid mode)
                    "values": value_lists,  # List of value lists
                    "locked_params": {},
                    "grid_mode": True,  # Flag for Grid Search
                    "description": f"Joint optimization of {', '.join(param_names)}",
                    "adaptive_meta": adaptive_meta
                }
                
                # Calculate and log grid size
                grid_size = self._calculate_grid_size(stage)
                logging.info(f"Stage {stage_num}: Grid Search with {grid_size} combinations")
                
                stages.append(stage)
                stage_num += 1
        
        # PHASE 2: Create Sequential stages for independent parameters
        for param_name, config in parameters.items():
            # Skip if already processed in a correlated group
            if param_name in processed_params:
                continue
            
            # Check for custom range override
            if custom_ranges and param_name in custom_ranges:
                custom = custom_ranges[param_name]
                p_min = custom.get('min', config.get('min'))
                p_max = custom.get('max', config.get('max'))
                target_step = custom.get('step', config.get('step'))
            else:
                p_min = config.get('min')
                p_max = config.get('max')
                target_step = config.get('step')
            
            # Coarse Step for Round 1
            coarse_step = self._calculate_coarse_step(p_min, p_max, target_step)
            values = self._generate_range_values(p_min, p_max, coarse_step)
            
            adaptive_meta = {
                param_name: {
                    'target_step': target_step,
                    'current_step': coarse_step,
                    'min': p_min,
                    'max': p_max
                }
            }
            
            stages.append({
                "stage_num": stage_num,
                "stage_name": f"Grid Search: {param_name}",
                "parameter": [param_name],  # List for Grid
                "values": [values],      # List of lists for Grid
                "locked_params": {},
                "grid_mode": True,       # Explicit Grid Mode
                "description": f"Grid Search verification of {param_name}",
                "adaptive_meta": adaptive_meta
            })
            stage_num += 1
        
        # FALLBACK: If no optimization_schema, use legacy behavior
        if not parameters:
            logging.warning(f"No optimization_schema found for {template_name} - using legacy stage generation")
            
            # Legacy: Infer from indicators metadata
            # Legacy: Infer from indicators metadata
            
            # Step 1: Collect indicator parameters for Grid Search
            grid_param_names = []
            grid_value_lists = []
            
            for indicator in metadata.get('indicators', []):
                ind_type = indicator['type']
                ind_alias = indicator.get('alias', ind_type)
                ind_params = indicator.get('params', {})
                
                # Get optimization ranges from indicator config or use defaults
                opt_range = indicator.get('optimization_range', {})
                
                for param_name, param_value in ind_params.items():
                    # Create full parameter name (e.g., "ema_fast_length")
                    full_param_name = f"{ind_alias}_{param_name}"
                    
                    # Determine range values
                    if custom_ranges and full_param_name in custom_ranges:
                        custom = custom_ranges[full_param_name]
                        values = self._generate_range_values(
                            custom.get('min', param_value),
                            custom.get('max', param_value * 2),
                            custom.get('step', 1)
                        )
                    elif param_name in opt_range:
                        # Use optimization range from template
                        range_config = opt_range[param_name]
                        values = self._generate_range_values(
                            range_config.get('min', param_value),
                            range_config.get('max', param_value * 2),
                            range_config.get('step', 1)
                        )
                    else:
                        # Default range: ±50% of default value
                        min_val = max(1, int(param_value * 0.5))
                        max_val = int(param_value * 1.5)
                        step = max(1, int((max_val - min_val) / 10))
                        values = self._generate_range_values(min_val, max_val, step)
                    
                    grid_param_names.append(full_param_name)
                    grid_value_lists.append(values)
            
            # Create Grid Search Stage (Stage 1)
            if grid_param_names:
                stage = {
                    "stage_num": stage_num,
                    "stage_name": f"Grid Search: {', '.join(grid_param_names)}",
                    "parameter": grid_param_names,
                    "values": grid_value_lists,
                    "locked_params": {},
                    "grid_mode": True,
                    "description": f"Joint optimization of {', '.join(grid_param_names)}"
                }
                
                # Check grid size safety
                grid_size = self._calculate_grid_size(stage)
                logging.info(f"Implicit Grid Stage generated with {grid_size} combinations")
                
                stages.append(stage)
                stage_num += 1

            # Step 2: Check for orphan parameters in custom_ranges (e.g. stop_loss)
            if custom_ranges:
                existing_params = set(grid_param_names) # Use list of names from grid
                for s in stages: # Also check other stages if any
                     if isinstance(s['parameter'], list):
                         existing_params.update(s['parameter'])
                     else:
                         existing_params.add(s['parameter'])

                for param, range_config in custom_ranges.items():
                    if param not in existing_params:
                        values = self._generate_range_values(
                            range_config.get('min'),
                            range_config.get('max'),
                            range_config.get('step')
                        )
                        # Force Grid Mode for orphans too (1D Grid), as requested
                        stages.append({
                            "stage_num": stage_num,
                            "stage_name": f"Grid Search: {param}",
                            "parameter": [param], # List for Grid
                            "values": [values],   # List of lists for Grid
                            "locked_params": {},
                            "grid_mode": True,    # Explicit Grid Mode
                            "description": f"Grid Search verification of {param}"
                        })
                        stage_num += 1
        
        logging.info(f"Generated {len(stages)} stages for {template_name}")
        return stages
    
    def _generate_values_from_range(self, min_val: float, max_val: float, step: float) -> List[float]:
        """Generate list of values from min to max with step."""
        values = []
        current = min_val
        while current <= max_val:
            values.append(current)
            current += step
        return values
    
    # -------------------------------------------------------------------------
    # GRID SEARCH HELPER METHODS (Phase 1)
    # -------------------------------------------------------------------------
    
    def _validate_correlation_metadata(self, template_metadata: Dict[str, Any]) -> None:
        """
        Validate correlated_groups against available parameters.
        
        Raises:
            ValueError: If validation fails
        """
        optimization_schema = template_metadata.get("optimization_schema", {})
        correlated_groups = optimization_schema.get("correlated_groups", [])
        parameters = optimization_schema.get("parameters", {})
        
        if not correlated_groups:
            return  # No validation needed (backward compatible)
        
        all_correlated_params = set()
        
        for group in correlated_groups:
            for param in group:
                # Check if parameter exists
                if param not in parameters:
                    raise ValueError(
                        f"Invalid correlated_groups: parameter '{param}' not found in parameters. "
                        f"Available: {list(parameters.keys())}"
                    )
                
                # Check for duplicates
                if param in all_correlated_params:
                    raise ValueError(
                        f"Invalid correlated_groups: parameter '{param}' appears in multiple groups"
                    )
                all_correlated_params.add(param)
    
    def _calculate_coarse_step(self, start: Any, end: Any, target_step: Any = None) -> Any:
        """
        Calculate a coarse step for Round 1 to cover the range efficiently.
        Heuristic: Try to cover range in ~4-6 distinct values.
        """
        try:
            # Check if all inputs are effectively integers
            is_int = (isinstance(start, int) or float(start).is_integer()) and \
                     (isinstance(end, int) or float(end).is_integer()) and \
                     (target_step is None or isinstance(target_step, int) or float(target_step).is_integer())
            
            val_range = float(end) - float(start)
            
            if is_int:
                val_range = int(val_range)
                if val_range <= 5: return 1 # Small range, just do step 1
                
                # Target ~4 steps (Range/4)
                # Ensure step is at least 1
                coarse = max(1, int(val_range // 4))
                
                # Make coarse step cleaner (e.g. 5, 10, etc) if possible, but raw division is fine for now
                return coarse
            
            # Float/Decimal logic
            # If target_step provided, jump 5x target
            if target_step:
                # e.g. Target 0.01 -> Coarse 0.05
                # e.g. Target 1 -> Coarse 5
                # But maximize with range/4 to mostly ensure we don't have 100 steps
                return max(float(target_step) * 5, val_range / 4.0)
            
            # No target step, guess based on range magnitude
            if val_range < 0.1: return val_range / 4.0  # e.g. 0.08 -> 0.02
            if val_range < 1.0: return 0.1
            if val_range < 10.0: return 1.0
            return 5.0
            
        except Exception:
            # Fallback to safe default
            return 1 if isinstance(start, int) else 0.1

    def _refine_stage_values(self, stage: Dict, best_params: Dict) -> None:
        """
        Refine the search grid for the next round based on best results.
        Updates stage['values'] in-place.
        """
        adaptive_meta = stage.get('adaptive_meta')
        if not adaptive_meta: return

        new_value_lists = []
        param_names = stage['parameter'] # List for grid
        
        # Iterate over parameters in this stage
        for i, param_name in enumerate(param_names):
            meta = adaptive_meta.get(param_name)
            if not meta:
                # Should not happen if structured correctly, but fallback
                new_value_lists.append(stage['values'][i])
                continue
                
            best_val = best_params.get(param_name)
            if best_val is None:
                # Fallback
                new_value_lists.append(stage['values'][i])
                continue

            current_step = meta['current_step']
            target_step = meta.get('target_step')
            
            # --- CALCULATE NEW STEP ---
            # Heuristic: Halve the step until we hit target
            
            is_int = (isinstance(best_val, int) or float(best_val).is_integer()) and \
                     (target_step is None or isinstance(target_step, int) or float(target_step).is_integer())
            
            if is_int:
                # Integer refinement (e.g. 5 -> 2 -> 1)
                current_step_int = int(current_step)
                if current_step_int > 1:
                    new_step = max(1, int(current_step_int // 2)) 
                    # Prefer simple steps: 5->2, 4->2, 3->1, 2->1
                else:
                    new_step = 1
            else:
                # Float refinement
                if target_step:
                     new_step = max(float(target_step), float(current_step) / 2.0)
                else:
                     new_step = float(current_step) / 2.0
            
            # Update meta for next round
            meta['current_step'] = new_step
            
            # --- CALCULATE NEW RANGE ---
            # Smart Bounds: [Best - OldStep, Best + OldStep]
            # This covers the "neighbors" we just tested
            
            global_min = meta.get('min')
            global_max = meta.get('max')
            
            range_min = best_val - current_step
            range_max = best_val + current_step
            
            # Clamp to globals if exist
            if global_min is not None: range_min = max(range_min, global_min)
            if global_max is not None: range_max = min(range_max, global_max)
            
            # Generate new values
            new_vals = self._generate_range_values(range_min, range_max, new_step)
            
            # Deduplicate and Sort
            new_vals = sorted(list(set(new_vals)))
            new_value_lists.append(new_vals)
            
            logging.info(f"    Refining {param_name}: Best={best_val}, Step {current_step}->{new_step}, Range [{range_min}, {range_max}]")

        # Update stage values
        stage['values'] = new_value_lists

    def _generate_range_values(self, start: Any, end: Any, step: Any) -> List[Any]:
        """
        Generate inclusive range supporting floats and integers.
        
        Args:
            start: Start value
            end: End value (inclusive)
            step: Step size
            
        Returns:
            List of values from start to end (inclusive)
            
        Examples:
            _generate_range_values(10, 20, 5) -> [10, 15, 20]
            _generate_range_values(0.1, 0.3, 0.1) -> [0.1, 0.2, 0.3]
        """
        values = []
        current = start
        
        # Use small epsilon for float comparison
        epsilon = step / 1000.0 if isinstance(step, float) else 0
        
        while current <= end + epsilon:
            # Round floats to avoid precision issues (e.g., 0.30000000004)
            if isinstance(current, float):
                # Determine decimal places from step
                if step >= 1:
                    decimal_places = 0
                elif step >= 0.1:
                    decimal_places = 1
                elif step >= 0.01:
                    decimal_places = 2
                elif step >= 0.001:
                    decimal_places = 3
                else:
                    decimal_places = 4
                current = round(current, decimal_places)
            
            values.append(current)
            current += step
        
        return values
    
    def _calculate_grid_size(self, stage: Dict[str, Any]) -> int:
        """
        Calculate total grid size for a stage.
        
        Args:
            stage: Stage configuration
            
        Returns:
            Total number of combinations
        """
        if not stage.get('grid_mode'):
            return len(stage.get('values', []))
        
        # Calculate product of all value list sizes
        grid_size = 1
        for value_list in stage['values']:
            grid_size *= len(value_list)
        
        # Validate against limit
        MAX_GRID_SIZE = 1000
        if grid_size > MAX_GRID_SIZE:
            logging.warning(
                f"Grid size ({grid_size:,}) exceeds recommended limit ({MAX_GRID_SIZE:,}). "
                f"Estimated time: ~{grid_size * 2 / 3600:.1f} hours. "
                f"Consider increasing step size or reducing range."
            )
        
        return grid_size
    
    def _is_correlated_group(self, template_metadata: Dict[str, Any], param_names: List[str]) -> bool:
        """
        Check if given parameters form a correlated group.
        
        Args:
            template_metadata: Template metadata
            param_names: List of parameter names to check
            
        Returns:
            True if params are in a correlated group
        """
        optimization_schema = template_metadata.get("optimization_schema", {})
        correlated_groups = optimization_schema.get("correlated_groups", [])
        
        param_set = set(param_names)
        for group in correlated_groups:
            if set(group) == param_set:
                return True
        
        return False


    def run_optimization(
        self,
        template_name: str,
        symbol: str,
        timeframe: str = "1h",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        custom_ranges: Optional[Dict[str, Any]] = None,
        deep_backtest: bool = True,  # Default to Deep Backtesting
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        
        # Generate stages
        fixed_timeframe = timeframe if timeframe else None
        stages = self.generate_stages(
            template_name=template_name,
            symbol=symbol,
            fixed_timeframe=fixed_timeframe,
            custom_ranges=custom_ranges
        )
        
        # Get template metadata ONCE for workers
        template_metadata = self.combo_service.get_template_metadata(template_name)
        
        # Ensure we have date ranges for Deep Backtesting
        # If not provided, use full period (2017-present for comprehensive testing)
        if not start_date:
            start_date = "2017-01-01"  # Full crypto history (works for most major assets)
        if not end_date:
            from datetime import datetime
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Load data
        df = self.loader.fetch_data(
            symbol=symbol,
            timeframe=timeframe,
            since_str=start_date,
            until_str=end_date
        )
        
        # Initialize best parameters
        best_params = {}
        best_metrics = None
        
        # Use ProcessPoolExecutor for parallel execution
        # Use max_workers = CPU count - 1 to leave one for the OS/Backend
        max_workers = max(1, (os.cpu_count() or 2) - 1)
        
        # PHASE 2: Detect Grid Search and allow refinement
        # Grid Search finds the best "coarse" region, then we refine it.
        has_grid_search = any(stage.get('grid_mode', False) for stage in stages)
        has_adaptive = any(stage.get('adaptive_meta') for stage in stages)
        
        if has_grid_search:
            if has_adaptive:
                max_rounds = 4
                logging.info("=" * 60)
                logging.info("Adaptive Grid Search detected - 4 Rounds (Coarse -> Fine)")
                logging.info("=" * 60)
            else:
                max_rounds = 1
                logging.info("=" * 60)
                logging.info("Grid Search detected - running single round (no refinement)")
                logging.info("Grid Search guarantees global maximum within search space")
                logging.info("=" * 60)
        else:
            max_rounds = 5
            logging.info("Sequential optimization - using iterative refinement (5 rounds)")
        
        round_num = 1
        converged = False
        
        while not converged and round_num <= max_rounds:
            logging.info(f"--- STARTING ROUND {round_num} OF REFINE ---")

            # Refine stages for rounds > 1 (Adaptive Zoom)
            if round_num > 1:
                 # Check if we should refine based on adaptive meta
                 logging.info(f"Refining search grid around best result: {best_params}")
                 for stage in stages:
                     if stage.get('adaptive_meta'):
                         self._refine_stage_values(stage, best_params)
            
            params_at_start = best_params.copy()
            
            for stage in stages:
                stage_param = stage['parameter']
                stage_values = stage['values']
                is_grid_mode = stage.get('grid_mode', False)
                
                # Log stage start
                if is_grid_mode:
                    # Calculate grid size for logging
                    grid_size = 1
                    for value_list in stage_values:
                        grid_size *= len(value_list)
                    logging.info(f"Round {round_num} - Stage {stage['stage_num']}: Grid Search {stage_param} ({grid_size} combinations) with {max_workers} workers")
                else:
                    logging.info(f"Round {round_num} - Stage {stage['stage_num']}: Optimizing {stage_param} ({len(stage_values)} tests) with {max_workers} workers")
                
                start_time = time.time()
                stage_best_value = None
                stage_best_sharpe = float('-inf')
                
                # PHASE 3: Prepare arguments for parallel execution
                worker_args = []
                
                if is_grid_mode:
                    # Grid Search: Generate all combinations using itertools.product
                    param_names = stage_param  # List of parameter names
                    value_lists = stage_values  # List of value lists
                    
                    # Generate cartesian product
                    for combo in itertools.product(*value_lists):
                        # Build parameters for this combination
                        test_params = best_params.copy()
                        
                        # Set all parameters in the combination
                        for param_name, param_value in zip(param_names, combo):
                            test_params[param_name] = param_value
                        
                        # Worker args: (metadata, params, df, param_name, value, deep_backtest, symbol, start, end)
                        # For Grid mode, we pass the full combo as "value" for logging
                        combo_dict = dict(zip(param_names, combo))
                        worker_args.append((template_metadata, test_params, df, param_names, combo_dict, deep_backtest, symbol, start_date, end_date))
                    
                    logging.info(f"  Generated {len(worker_args)} Grid combinations")
                
                else:
                    # Sequential: Test single parameter
                    for value in stage_values:
                        # Build parameters for this test
                        test_params = best_params.copy()
                        
                        if stage_param == 'timeframe':
                            # Timeframe optimization changes the DATA itself. 
                            # Complex to parallelize efficiently without reloading data in every worker.
                            # Separate logic.
                            continue
                        else:
                            test_params[stage_param] = value
                            worker_args.append((template_metadata, test_params, df, stage_param, value, deep_backtest, symbol, start_date, end_date))
                
                if stage_param == 'timeframe':
                    # Sequential fallback for timeframe
                    for value in stage_values:
                        # Reload data with new timeframe
                        sub_df = self.loader.fetch_data(
                            symbol=symbol,
                            timeframe=value,
                            since_str=start_date,
                            until_str=end_date
                        )
                         # Synchronous execution for timeframe
                        worker_args_tf = (template_metadata, test_params, sub_df, stage_param, value, deep_backtest, symbol, start_date, end_date)
                        res = _worker_run_backtest(worker_args_tf)
                        
                        value_res = res['value']
                        if res['success']:
                            metrics = res['metrics']
                            trades_count = res['trades_count']
                            sharpe = metrics['sharpe_ratio']
                            
                            logging.info(f"  Tested {stage_param}={value_res} -> Sharpe: {sharpe:.3f}, Trades: {trades_count}")
                            
                            if sharpe > stage_best_sharpe:
                                stage_best_sharpe = sharpe
                                stage_best_value = value_res
                                best_metrics = metrics
                        else:
                            logging.error(f"  Failed {stage_param}={value_res}: {res.get('error')}")
                
                else:
                    # Parallel execution for indicator parameters
                    total_tests = len(worker_args)
                    logging.info(f"  Starting parallel execution of {total_tests} tests...")
                    
                    results = []
                    
                    # BATCH PROCESSING OPTIMIZATION
                    # Group tasks into batches to reduce I/O and Process overhead
                    BATCH_SIZE = 200 # 200 tests per worker task
                    worker_batches = [worker_args[i:i + BATCH_SIZE] for i in range(0, len(worker_args), BATCH_SIZE)]
                    
                    logging.info(f"  Optimized: {len(worker_batches)} batches of up to {BATCH_SIZE} tests")

                    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
                        # Submit batches
                        futures = [executor.submit(_worker_run_batch, batch) for batch in worker_batches]
                        
                        completed_tests = 0
                        
                        # Process as batches complete
                        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                            try:
                                batch_results = future.result()
                                results.extend(batch_results)
                                completed_tests += len(batch_results)
                                
                                # Log progress
                                elapsed = time.time() - start_time
                                avg_time_per_test = elapsed / completed_tests if completed_tests > 0 else 0
                                remaining = (total_tests - completed_tests) * avg_time_per_test
                                
                                logging.info(f"  Progress: {completed_tests}/{total_tests} ({completed_tests/total_tests:.1%}) - Elapsed: {elapsed:.1f}s - ETA: {remaining:.1f}s")

                            except Exception as exc:
                                logging.error(f"  Worker Batch exception: {exc}")
                    
                    # Sort results to maintain deterministic order if needed (though scoring handles it)
                    # results.sort(key=lambda x: x.get('value', 0) if isinstance(x.get('value'), (int, float)) else str(x.get('value')))
                    
                    # Process results with Weighted Composite Score
                    valid_results = []
                    test_num = 0
                    progress_interval = max(50, total_tests // 10)  # Every 10% or 50 tests
                    
                    for res in results:
                        test_num += 1
                        
                        # Progress logging
                        if test_num % progress_interval == 0 or test_num == total_tests:
                            progress_pct = (test_num / total_tests) * 100
                            elapsed = time.time() - start_time
                            eta = (elapsed / test_num) * (total_tests - test_num) if test_num > 0 else 0
                            logging.info(f"  Progress: {test_num}/{total_tests} ({progress_pct:.1f}%) - Elapsed: {elapsed:.1f}s - ETA: {eta:.1f}s")
                        
                        if res['success']:
                            valid_results.append(res)
                        else:
                            logging.error(f"  Failed {stage_param}={res['value']}: {res.get('error')}")

                    if valid_results:
                        # Calculate min/max for normalization
                        sharpes = [r['metrics']['sharpe_ratio'] for r in valid_results]
                        returns = [r['metrics']['total_return'] for r in valid_results]
                        
                        min_sharpe, max_sharpe = min(sharpes), max(sharpes)
                        min_return, max_return = min(returns), max(returns)
                        
                        range_sharpe = max_sharpe - min_sharpe
                        range_return = max_return - min_return
                        
                        best_score = float('-inf')
                        new_best_found = False

                        for res in valid_results:
                            metrics = res['metrics']
                            sharpe = metrics['sharpe_ratio']
                            total_return = metrics['total_return']
                            
                            # Normalize inputs (0 to 1 scale)
                            norm_sharpe = (sharpe - min_sharpe) / range_sharpe if range_sharpe > 0 else 0
                            norm_return = (total_return - min_return) / range_return if range_return > 0 else 0
                            
                            # Weighted Score: 70% Sharpe, 30% Total Return
                            score = (0.7 * norm_sharpe) + (0.3 * norm_return)
                            
                            # Tie-breaker: If scores exact, prefer higher Sharpe
                            if score > best_score:
                                best_score = score
                                stage_best_value = res['value']
                                best_metrics = metrics
                                stage_best_sharpe = sharpe # Still track for logging
                                new_best_found = True
                                
                                # NEW BEST indicator
                                logging.info(f"  🌟 NEW BEST: {stage_param}={res['value']} -> Sharpe: {sharpe:.3f}, Return: {total_return:.3f} (Score: {score:.3f})")

                            # Format full params for logging
                            full_params_str = str(res.get('full_params', {}))
                            
                            logging.info(f"  Tested {stage_param}={res['value']} | State={full_params_str} -> Sharpe: {sharpe:.3f}, Return: {total_return:.3f} (Score: {score:.3f})")

                        # Summary of stage results
                        if new_best_found:
                            logging.info(f"  ✓ Stage complete: Found improvement with Sharpe {stage_best_sharpe:.3f}")
                        else:
                            logging.info(f"  ✓ Stage complete: No improvement found")

                # Update best params for next stage (immediate update for greedy refinement within round)
                if stage_best_value is not None:
                    if is_grid_mode:
                        # Grid mode: Update all parameters in the combination
                        best_params.update(stage_best_value)
                        param_str = ", ".join([f"{k}={v}" for k, v in stage_best_value.items()])
                        logging.info(f"Round {round_num} - Stage {stage['stage_num']} complete: {param_str} (Sharpe: {stage_best_sharpe:.3f})")
                    else:
                        # Sequential mode: Update single parameter
                        best_params[stage_param] = stage_best_value
                        logging.info(f"Round {round_num} - Stage {stage['stage_num']} complete: {stage_param}={stage_best_value} (Sharpe: {stage_best_sharpe:.3f})")
                else:
                    logging.warning(f"Round {round_num} - Stage {stage['stage_num']} failed to find improvements.")
                    if not is_grid_mode and stage_values and stage_param not in best_params:
                        best_params[stage_param] = stage_values[0]

                logging.info(f"Stage time: {time.time() - start_time:.2f}s")
            
            # End of Round Analysis
            if best_params == params_at_start:
                converged = True
                logging.info(f"--- CONVERGENCE ACHIEVED IN ROUND {round_num} ---")
            else:
                logging.info(f"--- ROUND {round_num} COMPLETE: Parameters changed. Refining... ---")
                round_num += 1
                
        if not converged:
             logging.warning(f"Optimization stopped after max rounds ({max_rounds}) without full convergence.")

        # COMPLETION SUMMARY
        total_optimization_time = time.time() - start_time if 'start_time' in locals() else 0
        rounds_display = round_num if converged else round_num - 1
        
        logging.info("=" * 80)
        logging.info("🎯 OPTIMIZATION COMPLETE")
        logging.info("=" * 80)
        logging.info(f"Rounds completed: {rounds_display}/{max_rounds}")
        logging.info(f"Total execution time: {total_optimization_time:.1f}s ({total_optimization_time/60:.1f} minutes)")
        logging.info(f"Convergence: {'Yes' if converged else 'No'}")
        logging.info(f"\nFinal Configuration:")
        for param, value in best_params.items():
            logging.info(f"  {param}: {value}")
        if best_metrics:
            logging.info(f"\nFinal Metrics:")
            logging.info(f"  Sharpe Ratio: {best_metrics.get('sharpe_ratio', 0):.3f}")
            logging.info(f"  Total Return: {best_metrics.get('total_return', 0):.3f}")
            logging.info(f"  Max Drawdown: {best_metrics.get('max_drawdown', 0):.3f}")
        logging.info("=" * 80)

        # Run final backtest with best parameters to get complete data
        logging.info(f"Running final backtest with best parameters: {best_params}")
        
        try:
            # Reload data with best timeframe
            df_final = self.loader.fetch_data(
                symbol=symbol,
                timeframe=timeframe,
                since_str=start_date,
                until_str=end_date
            )
            
            # Create strategy with best parameters
            strategy = self.combo_service.create_strategy(
                template_name=template_name,
                parameters=best_params
            )
            
            # Generate signals
            df_with_signals = strategy.generate_signals(df_final.copy())
            
            # Extract trades
            # Extract trades with exact logic matching worker (Stop Loss + Fees)
            stop_loss = best_params.get('stop_loss', 0.0)
            trades = extract_trades_from_signals(df_with_signals, stop_loss)
            
            # Prepare candles data
            candles = []
            
            # Prepare candles data
            candles = []
            for idx, row in df_final.iterrows():
                candles.append({
                    'timestamp_utc': str(idx),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume'])
                })
            
            # Extract indicator data
            indicator_data = {}
            for col in df_with_signals.columns:
                if col not in ['open', 'high', 'low', 'close', 'volume', 'signal']:
                    indicator_data[col] = df_with_signals[col].fillna(0).tolist()
            
        except Exception as e:
            logging.error(f"Final backtest failed: {e}")
            trades = []
            candles = []
            indicator_data = {}
        
        return {
            "job_id": job_id or "combo_opt_" + str(hash(template_name + symbol)),
            "template_name": template_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "stages": stages,
            "best_parameters": best_params,
            "best_metrics": best_metrics or {},
            "total_stages": len(stages),
            # Add complete backtest data
            "trades": trades,
            "candles": candles,
            "indicator_data": indicator_data,
            "parameters": best_params  # For compatibility with ComboResultsPage
        }

