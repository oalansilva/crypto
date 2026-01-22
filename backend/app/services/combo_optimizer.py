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
    # FIX: DO NOT Shift signals manually here.
    # ComboStrategy already places the signal on the execution candle (Day+1).
    # If we shift again, we create a double lag (Day+2).
    df_exec = df_with_signals.copy()
    # df_exec['signal'] = df_exec['signal'].shift(1).fillna(0) # REMOVED REDUNDANT SHIFT
    
    if not deep_backtest:
        # Fast mode: use existing daily-only logic
        return extract_trades_from_signals(df_exec, stop_loss)
    
    # Deep Backtesting mode: fetch 15m data and simulate execution
    logger = logging.getLogger(__name__)
    # logger.info(f"Deep Backtesting enabled for {symbol}") # Too noisy for grid search
    
    if not symbol or not since_str:
        logger.warning("Deep Backtesting requires symbol and date range. Falling back to fast mode.")
        return extract_trades_from_signals(df_exec, stop_loss)
    
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
            return extract_trades_from_signals(df_exec, stop_loss)
        
        if df_15m_cache is None:
            logger.info(f"Fetched {len(df_15m)} 15m candles for deep backtest simulation")
        
        # Run deep backtest simulation
        trades = simulate_execution_with_15m(
            df_daily_signals=df_exec,
            df_15m=df_15m,
            stop_loss=stop_loss
        )
        
        return trades
        
    except Exception as e:
        logger.error(f"Error in deep backtest: {e}. Falling back to fast mode.")
        return extract_trades_from_signals(df_exec, stop_loss)

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
            'sharpe_ratio': 0,
            'profit_factor': 0,
            'sortino_ratio': 0,
            'max_loss': 0,
            'expectancy': 0,
            'max_consecutive_losses': 0,
            'max_drawdown': 0
        }

        if len(trades) > 0:
            total_trades = len(trades)
            winning_trades = sum(1 for t in trades if t['profit'] > 0)
            metrics['total_trades'] = total_trades
            metrics['win_rate'] = winning_trades / total_trades
            
            # Compounded Return
            compounded_capital = 1.0
            for t in trades:
                compounded_capital *= (1.0 + t['profit'])
            metrics['total_return'] = (compounded_capital - 1.0) * 100.0
            
            metrics['avg_profit'] = (metrics['total_return'] / total_trades) if total_trades > 0 else 0
            
            # Sharpe Ratio
            returns = [t['profit'] for t in trades]
            import numpy as np
            std_dev = np.std(returns)
            metrics['sharpe_ratio'] = np.mean(returns) / std_dev if std_dev > 0 else 0
            
            # Profit Factor
            gross_profit = sum([t['profit'] for t in trades if t['profit'] > 0])
            gross_loss = abs(sum([t['profit'] for t in trades if t['profit'] < 0]))
            metrics['profit_factor'] = gross_profit / gross_loss if gross_loss > 0 else (999 if gross_profit > 0 else 0)
            
            # Sortino Ratio (downside deviation)
            downside_returns = [r for r in returns if r < 0]
            if len(downside_returns) > 1:
                downside_std = np.std(downside_returns)
                metrics['sortino_ratio'] = np.mean(returns) / downside_std if downside_std > 0 else 0
            else:
                metrics['sortino_ratio'] = metrics['sharpe_ratio']  # Fallback to Sharpe if no downside
            
            # Max Loss (worst single trade)
            metrics['max_loss'] = min(returns) if returns else 0
            
            # Expectancy (average profit per trade in dollars, assuming $10k capital)
            # Convert from percentage to dollar value
            ASSUMED_CAPITAL = 10000
            expectancy_pct = np.mean(returns) if returns else 0
            metrics['expectancy'] = expectancy_pct * ASSUMED_CAPITAL
            
            # Max Consecutive Losses
            consecutive_losses = 0
            max_consecutive = 0
            for t in trades:
                if t['profit'] < 0:
                    consecutive_losses += 1
                    max_consecutive = max(max_consecutive, consecutive_losses)
                else:
                    consecutive_losses = 0
            metrics['max_consecutive_losses'] = max_consecutive
            
            # Max Drawdown (from equity curve)
            equity = 1.0
            peak = 1.0
            max_dd = 0
            for t in trades:
                equity *= (1.0 + t['profit'])
                if equity > peak:
                    peak = equity
                drawdown = (peak - equity) / peak
                max_dd = max(max_dd, drawdown)
            metrics['max_drawdown'] = max_dd * 100.0  # Convert to percentage
            
            # --- Regime Metrics (Simplified/Moved) ---
            # Heavy calculation (Win Rate Bull/Bear) removed from inner loop for performance.
            # Avg ATR/ADX is fast (vectorized mostly), so we keep if cols exist (simple mean).
            
            atr_col = next((c for c in df.columns if c.startswith('ATR')), None)
            adx_col = next((c for c in df.columns if c.startswith('ADX')), None)
            
            metrics['avg_atr'] = df[atr_col].mean() if atr_col else 0
            metrics['avg_adx'] = df[adx_col].mean() if adx_col else 0

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

                # FORCE STOP LOSS STEP to 0.001 if user intent is strict 0.5% in Round 1
                if param_name == 'stop_loss' and target_step == 0.002:
                    target_step = 0.001

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
                if val_range <= 5: return 1 
                
                # Integer Logic: Strictly respect Target Step * 4 (Round 1) - USER REQUEST CHANGE 5->4
                # If target_step provided (usually 1 for periods), use 4x.
                if target_step:
                     return int(target_step) * 4
                
                # Fallback if no target step: Just use 4 as default coarse step
                return 4
            
            # Float/Decimal logic
            # If target_step provided, jump 5x target (Generic Round 1 Logic)
            if target_step:
                # STRICT USER RULE: Round 1 = Step 5 (Integers) or 0.50 (Decimais)
                # For Stop Loss, user explicitly wants 0.5% (0.005).
                # This implies Base Unit is 0.001 (0.1%).
                # We enforce this if we detect 'stop_loss' context, purely for compliance.
                # Since this method doesn't know param name easily without signature change,
                # we rely on the caller fixing target_step OR we make a best effort here.
                # Actually, best is to just trust target_step * 5.
                # If target_step for stop_loss is 0.002, we get 0.01.
                # To get 0.005, target must be 0.001. 
                # I will handle the 0.001 enforcement in generate_stages instead.
                
                return float(target_step) * 5.0
            
            # No target step, guess based on range magnitude
            if val_range < 0.1: return val_range / 4.0  # e.g. 0.08 -> 0.02
            if val_range < 1.0: return 0.1
            if val_range < 10.0: return 1.0
            return 5.0
            
        except Exception:
            # Fallback to safe default
            return 1 if isinstance(start, int) else 0.1

    def _refine_stage_values(self, stage: Dict, best_params: Dict, round_num: int = 1) -> None:
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
            
            # --- CALCULATE NEW STEP BASED ON ROUND ---
            if target_step:
                tgt = float(target_step)
                if round_num == 2: multiplier = 3.0
                elif round_num == 3: multiplier = 2.0
                elif round_num >= 4: multiplier = 1.0
                else: multiplier = 5.0 
                
                new_step = tgt * multiplier
            else:
                 new_step = float(current_step) / 2.0
            
            # Ensure Integer Constraint
            is_int = (isinstance(best_val, int) or float(best_val).is_integer()) and \
                     (target_step is None or isinstance(target_step, int) or float(target_step).is_integer())
            
            if is_int:
                new_step = max(1, int(new_step))
            
            # Update meta for next round
            meta['current_step'] = new_step

            # --- CALCULATE NEW RANGE ---
            # Radius = Previous Step size (roughly).
            if target_step:
                tgt = float(target_step)
                
                # Determine Previous Multiplier based on Type
                round1_mult = 4.0 if is_int else 5.0 # Integers start at 4x now, Decimals keep 5x (0.5%)

                if round_num == 2: prev_mult = round1_mult
                elif round_num == 3: prev_mult = 3.0
                elif round_num == 4: prev_mult = 2.0
                else: prev_mult = round1_mult
                
                radius_step = tgt * prev_mult
            else:
                radius_step = current_step
            
            if is_int: radius_step = int(radius_step)

            global_min = meta.get('min')
            global_max = meta.get('max')
            
            range_min = best_val - radius_step
            range_max = best_val + radius_step
            
            if global_min is not None: range_min = max(range_min, global_min)
            if global_max is not None: range_max = min(range_max, global_max)
            
            new_vals = self._generate_range_values(range_min, range_max, new_step)
            new_vals = sorted(list(set(new_vals)))
            new_value_lists.append(new_vals)
            
            logging.info(f"    Refining {param_name}: Best={best_val}, Step={new_step} (Round {round_num}), Range [{range_min}, {range_max}]")

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



    def _select_top_candidates(self, candidates: List[Dict], top_k: int = 3, min_dist: float = 0.5) -> List[Dict]:
        """
        Select Top K DISTINCT candidates based on Euclidean distance of parameters.
        Prevents selecting neighbors in the same local maximum.
        """
        if not candidates:
            return []
            
        # Sort by score descending
        sorted_candidates = sorted(candidates, key=lambda x: x['score'], reverse=True)
        
        selected = []
        selected.append(sorted_candidates[0]) # Always take the absolute best
        
        # Helper to calculate normalized distance
        def calc_distance(p1, p2):
            dist = 0
            keys = set(p1.keys()) | set(p2.keys())
            for k in keys:
                v1 = p1.get(k, 0)
                v2 = p2.get(k, 0)
                # Simple Euclidean distance
                if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                    dist += (v1 - v2) ** 2
            return dist ** 0.5
            
        # Greedy selection of next candidates that are "far enough"
        for cand in sorted_candidates[1:]:
            if len(selected) >= top_k:
                break
                
            # Check distance against all currently selected
            is_distinct = True
            for sel in selected:
                dist = calc_distance(cand['params'], sel['params'])
                
                # STRICT FILTER: min_dist default 0.5.
                # Integer params usually change by 1.0 or more.
                # If dist < 0.5, it implies only Stop Loss changed (e.g. 0.01 change).
                # We want structural diversity (Moving Averages must differ).
                if dist < min_dist: 
                    is_distinct = False
                    break
            
            if is_distinct:
                selected.append(cand)
                
        return selected

    def _execute_opt_stages(self, stages, initial_params, round_num, max_workers, 
                          template_name, symbol, timeframe, fixed_timeframe, start_date, end_date, deep_backtest, template_metadata, df,
                          return_top_n: int = 1):
        """
        Execute all stages for a specific branch/candidate.
        Returns: 
             If return_top_n > 1 (Grid Mode): List of dicts [{'params':..., 'metrics':...}]
             If return_top_n = 1 (Sequential): (best_params, best_metrics)
        """
        best_params = initial_params.copy()
        best_metrics = None
        
        # Enrich DF with Regime/Context Metrics (if not present) to enable Worker Logic
        if df is not None and not df.empty and 'regime' not in df.columns:
            try:
                import pandas_ta as ta
                import numpy as np
                df = df.copy()
                
                # Check/Calc SMA (200) for Regime
                if 'SMA_200' not in df.columns:
                    df.ta.sma(length=200, append=True)
                
                # ATR/ADX for Avg Metrics
                if not any(c.startswith('ATR') for c in df.columns):
                    df.ta.atr(length=14, append=True)
                if not any(c.startswith('ADX') for c in df.columns):
                    df.ta.adx(length=14, append=True)

                # Regime Classification
                sma_col = 'SMA_200'
                if sma_col in df.columns:
                    conditions = [(df['close'] > df[sma_col]), (df['close'] < df[sma_col])]
                    choices = ['Bull', 'Bear']
                    df['regime'] = np.select(conditions, choices, default='Unknown')
            except Exception as e:
                logging.warning(f"Failed to enrich DF with regime metrics: {e}")
        
        # -----------------------------------------------------------
        # NOTE: For Multi-Focus Grid (Round 1), we typically have ONE stage (the 4D Grid).
        # We need to collect ALL results from that stage and return top N.
        # For Refinement (Sequential params), we follow the standard greedy path.
        # -----------------------------------------------------------
        
        collected_candidates = [] 

        for stage in stages:
            stage_param = stage['parameter']
            stage_values = stage['values']
            is_grid_mode = stage.get('grid_mode', False)
            
            start_time = time.time()
            stage_best_value = None
            stage_best_sharpe = float('-inf')
            
            worker_args = []
            
            if is_grid_mode:
                param_names = stage_param
                value_lists = stage_values
                for combo in itertools.product(*value_lists):
                    test_params = best_params.copy()
                    
                    # --- HEURISTIC FILTER: Multi MA Logic ---
                    # Optimization: Skip combinations where Short >= Inter or Inter >= Long
                    # This dramatically reduces search space for "Cruzamento Medias" strategy.
                    
                    # 1. Identify params by common aliases
                    p_short = None
                    p_inter = None
                    p_long = None
                    
                    # Map loop values to temp dict for checking
                    # If param not in loop (grid), check best_params (fixed context)
                    current_combo = dict(zip(param_names, combo))
                    full_context = {**best_params, **current_combo}
                    
                    for k, v in full_context.items():
                        k_lower = k.lower()
                        # Check aliases (suffix match to handle prefixes like 'ema_short')
                        if k_lower.endswith('media_curta') or k_lower.endswith('ema_short') or k_lower.endswith('sma_short'):
                             p_short = v
                        elif k_lower.endswith('media_inter') or k_lower.endswith('sma_medium'):
                             p_inter = v
                        elif k_lower.endswith('media_longa') or k_lower.endswith('sma_long'):
                             p_long = v
                    
                    # 2. Check Logical Constraint if all 3 are present
                    if p_short is not None and p_inter is not None and p_long is not None:
                        # Ensure values are comparable numbers
                        try:
                            if not (float(p_short) < float(p_inter) < float(p_long)):
                                continue # SKIP INVALID COMBINATION
                        except (ValueError, TypeError):
                            pass # customized params might be non-numeric, ignore filter
                            
                    # ----------------------------------------

                    for pname, pval in zip(param_names, combo):
                        test_params[pname] = pval
                    combo_dict = dict(zip(param_names, combo))
                    worker_args.append((template_metadata, test_params, df, param_names, combo_dict, deep_backtest, symbol, start_date, end_date))
            else:
                for value in stage_values:
                    test_params = best_params.copy()
                    if stage_param != 'timeframe':
                        test_params[stage_param] = value
                        worker_args.append((template_metadata, test_params, df, stage_param, value, deep_backtest, symbol, start_date, end_date))
            
            if not worker_args:
                continue

            results = []
            BATCH_SIZE = 200
            worker_batches = [worker_args[i:i + BATCH_SIZE] for i in range(0, len(worker_args), BATCH_SIZE)]
            
            import concurrent.futures
            with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(_worker_run_batch, batch) for batch in worker_batches]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        results.extend(future.result())
                    except Exception:
                        pass
            
            valid_results = [r for r in results if r['success']]
            
            if valid_results:
                sharpes = [r['metrics']['sharpe_ratio'] for r in valid_results]
                returns = [r['metrics']['total_return'] for r in valid_results]
                min_s, max_s = min(sharpes), max(sharpes)
                min_r, max_r = min(returns), max(returns)
                range_s = max_s - min_s
                range_r = max_r - min_r
                
                # Score all results
                scored_results = []
                for res in valid_results:
                    m = res['metrics']
                    s = m['sharpe_ratio']
                    r = m['total_return']
                    ns = (s - min_s) / range_s if range_s > 0 else 0
                    nr = (r - min_r) / range_r if range_r > 0 else 0
                    score = (0.7 * ns) + (0.3 * nr)
                    
                    # Construct full params for this result
                    result_params = best_params.copy()
                    if is_grid_mode:
                        result_params.update(res['value'])
                    else:
                        result_params[stage_param] = res['value']
                        
                    scored_results.append({
                        'params': result_params,
                        'metrics': m,
                        'score': score
                    })

                # Sort by score
                scored_results.sort(key=lambda x: x['score'], reverse=True)
                
                # If we are in Grid Mode and collecting candidates for branching
                if is_grid_mode and return_top_n > 1:
                    collected_candidates.extend(scored_results[:return_top_n*2]) # Keep a few more for distance filtering
                
                # Update best for standard greedy flow
                top = scored_results[0]
                stage_best_value = top['params'][stage_param] if not is_grid_mode else {k: top['params'][k] for k in stage_param}
                best_metrics = top['metrics']
                
                # Greedily update best_params for NEXT stage in this loop
                best_params = top['params']

        if return_top_n > 1 and collected_candidates:
            # Sort all collected candidates (if multiple grid stages existed, unlikely for 4D)
            collected_candidates.sort(key=lambda x: x['score'], reverse=True)
            return collected_candidates[:return_top_n*2] 
            
        return best_params, best_metrics


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
        
        # Default Sequential Mode vars
        max_rounds = 5
        round_num = 1
        converged = False
        
        if has_grid_search and has_adaptive:
             # -------------------------------------------------------------
             # 4D ADAPTIVE OPTIMIZATION (MULTI-BRANCH)
             # -------------------------------------------------------------
            max_rounds = 4
            logging.info("=" * 60)
            logging.info("Adaptive Grid Search detected - activating 4D Coarse-to-Fine Optimization")
            logging.info("=" * 60)
            
            # Candidates list (starts with single 'root' candidate which covers the whole space)
            # Structure: {'params': dict, 'meta': dict, 'round': 1, 'score': float}
            candidates = [{'params': best_params.copy(), 'meta': {}, 'round': 1, 'score': float('-inf')}]
            
            final_best_candidates = []
            
            for round_num in range(1, max_rounds + 1):
                logging.info(f"--- STARTING ROUND {round_num} OF ADAPTIVE OPTIMIZATION ---")
                logging.info(f"Candidates (Branches) to process: {len(candidates)}")
                
                next_round_candidates = []
                
                for idx, candidate in enumerate(candidates):
                    logging.info(f"Processing Branch {idx+1}/{len(candidates)} based on: {candidate['params']}")
                    
                    # 1. Setup stages for this candidate
                    if round_num == 1:
                        current_stages = stages # Use initial coarse stages
                    else:
                        # Clone stages to avoid polluting other branches
                        import copy
                        current_stages = copy.deepcopy(stages)
                        # Refine based on THIS candidate's best params
                        for stage in current_stages:
                             if stage.get('adaptive_meta'):
                                 self._refine_stage_values(stage, candidate['params'], round_num=round_num)
                    
                    
                    # 2. Execute Optimization for this branch
                    # For Round 1 (Grid), we want multiple candidates to feed the logical branches.
                    # For Round > 1, we just want the best refinement for this specific branch.
                    return_n = 10 if round_num == 1 else 1
                    
                    execution_result = self._execute_opt_stages(
                       current_stages, 
                       candidate['params'], 
                       round_num, 
                       max_workers,
                       template_name,
                       symbol,
                       timeframe, 
                       fixed_timeframe,
                       start_date,
                       end_date,
                       deep_backtest,
                       template_metadata,
                       df,
                       return_top_n=return_n
                    )
                    
                    if round_num == 1:
                        # Reviewing multiple candidates from Grid
                        branch_candidates = execution_result # It's a list
                        for cand in branch_candidates:
                             result_candidate = {
                                'params': cand['params'],
                                'meta': candidate['meta'], 
                                'round': round_num + 1,
                                'score': cand['score'],
                                'metrics': cand['metrics']
                            }
                             next_round_candidates.append(result_candidate)
                    else:
                        # Standard single result
                        branch_best_params, branch_best_metrics = execution_result
                        
                        # 3. Score this branch result
                        score = branch_best_metrics.get('sharpe_ratio', -999) if branch_best_metrics else -999
                        
                        result_candidate = {
                            'params': branch_best_params,
                            'meta': candidate['meta'], 
                            'round': round_num + 1,
                            'score': score,
                            'metrics': branch_best_metrics
                        }
                        
                        next_round_candidates.append(result_candidate)
                
                # SELECTION LOGIC (End of Round)
                if round_num < max_rounds:
                    # Select Top 10 Distinct Candidates for next round - USER REQUEST CHANGE 3 -> 10
                    # If Round 1 produced 20 candidates, we pick top 10 distinct ones here.
                    candidates = self._select_top_candidates(next_round_candidates, top_k=10)
                    logging.info(f"Selected {len(candidates)} candidates for Round {round_num + 1}")
                else:
                    # Final round - collect all results
                    final_best_candidates = next_round_candidates

            # Find absolute best from final candidates
            if final_best_candidates:
                # Sort by score descending
                final_best_candidates.sort(key=lambda x: x['score'], reverse=True)
                best_candidate = final_best_candidates[0]
                
                best_params = best_candidate['params']
                best_metrics = best_candidate['metrics']
                
                # Log details about the winner
                logging.info(f"Global Best Found from {len(final_best_candidates)} final branches")
                
            converged = True # Mark as done so we skip legacy loop logic
            
        else:
            # -------------------------------------------------------------
            # LEGACY SEQUENTIAL / SIMPLE GRID (Backup)
            # -------------------------------------------------------------
            if has_grid_search:
                max_rounds = 1
                logging.info("=" * 60)
                logging.info("Grid Search (Non-Adaptive) detected - running single round")
                logging.info("=" * 60)
            else:
                max_rounds = 5
                logging.info("Sequential optimization - using iterative refinement (5 rounds)")
            
            while not converged and round_num <= max_rounds:
                logging.info(f"--- STARTING ROUND {round_num} OF REFINE ---")
    
                # Refine stages for rounds > 1 (Adaptive Zoom)
                if round_num > 1:
                     logging.info(f"Refining search grid around best result: {best_params}")
                     for stage in stages:
                         if stage.get('adaptive_meta'):
                             self._refine_stage_values(stage, best_params)
                
                # Execute stages using shared helper (single branch)
                current_metrics = best_metrics
                best_params, best_metrics = self._execute_opt_stages(
                       stages, 
                       best_params, 
                       round_num, 
                       max_workers,
                       template_name,
                       symbol,
                       timeframe, 
                       fixed_timeframe,
                       start_date,
                       end_date,
                       deep_backtest,
                       template_metadata,
                       df
                )
                
                # End of Round Analysis
                # Simple loose check for convergence
                params_changed = True # (Simplify logic: always refine if rounds left in legacy mode unless strictly identical)
                
                if round_num < max_rounds:
                    logging.info(f"--- ROUND {round_num} COMPLETE: Parameters changed. Refining... ---")
                    round_num += 1
                else:
                    converged = True

                
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
            
            # Enrich df_final with regime for heavy metrics calculation
            if 'regime' not in df_final.columns:
                try:
                    import pandas_ta as ta
                    import numpy as np
                    
                    if 'SMA_200' not in df_final.columns:
                        df_final.ta.sma(length=200, append=True)
                    
                    if not any(c.startswith('ATR') for c in df_final.columns):
                        df_final.ta.atr(length=14, append=True)
                    if not any(c.startswith('ADX') for c in df_final.columns):
                        df_final.ta.adx(length=14, append=True)
                    
                    sma_col = 'SMA_200'
                    if sma_col in df_final.columns:
                        conditions = [(df_final['close'] > df_final[sma_col]), (df_final['close'] < df_final[sma_col])]
                        choices = ['Bull', 'Bear']
                        df_final['regime'] = np.select(conditions, choices, default='Unknown')
                except Exception as e:
                    logging.warning(f"Failed to enrich final DF with regime: {e}")
            
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
            
            # Post-Process Heavy Metrics (Only for best result)
            try:
                heavy = _calculate_heavy_metrics(df_with_signals, trades)
                if best_metrics:
                    best_metrics.update(heavy)
                    logging.info(f"Heavy metrics calculated: {heavy}")
            except Exception as e:
                logging.error(f"Failed to calculate heavy metrics: {e}")
                import traceback
                traceback.print_exc()
            
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



def _calculate_heavy_metrics(df, trades):
    metrics = {}
    try:
        if 'regime' in df.columns and trades:
            bull_wins = 0; bull_count = 0
            bear_wins = 0; bear_count = 0
            import pandas as pd
            for t in trades:
                et = t.get('entry_time')
                if et:
                    try:
                        if isinstance(et, str): et = pd.to_datetime(et)
                        idx_match = df.index.asof(et)
                        if idx_match is not None:
                            r_val = df.loc[idx_match]['regime']
                            if isinstance(r_val, pd.Series): r_val = r_val.iloc[0]
                            is_win = t.get('profit', 0) > 0
                            if r_val == 'Bull':
                                bull_count += 1
                                if is_win: bull_wins += 1
                            elif r_val == 'Bear':
                                bear_count += 1
                                if is_win: bear_wins += 1
                    except Exception: pass
            metrics['win_rate_bull'] = (bull_wins / bull_count) if bull_count > 0 else 0
            metrics['win_rate_bear'] = (bear_wins / bear_count) if bear_count > 0 else 0
    except Exception as e: pass
    return metrics
