"""
Combo Strategy Optimizer

Adapts SequentialOptimizer for combo strategies with multiple indicators.
Handles parameter naming, stage generation, and optimization execution.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.services.sequential_optimizer import SequentialOptimizer
from app.services.combo_service import ComboService
from app.services.backtest_service import BacktestService
from src.data.incremental_loader import IncrementalLoader


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
        
        stages = []
        stage_num = 1
        
        # Stage 1: Timeframe optimization (if not fixed)
        if not fixed_timeframe:
            stages.append({
                "stage_num": stage_num,
                "stage_name": "Timeframe",
                "parameter": "timeframe",
                "values": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
                "locked_params": {},
                "description": "Optimize trading timeframe"
            })
            stage_num += 1
            
        # Get optimization schema from database (if available)
        schema = metadata.get('optimization_schema')
                
        if schema:
            # Use explicit schema from database
            for param_name, config in schema.items():
                # Check for custom range override
                if custom_ranges and param_name in custom_ranges:
                    custom = custom_ranges[param_name]
                    values = self._generate_values_from_range(
                        custom.get('min', config['min']),
                        custom.get('max', config['max']),
                        custom.get('step', config['step'])
                    )
                else:
                    values = self._generate_values_from_range(
                        config['min'],
                        config['max'],
                        config['step']
                    )
                
                stages.append({
                    "stage_num": stage_num,
                    "stage_name": f"Optimize {param_name}",
                    "parameter": param_name,
                    "values": values,
                    "locked_params": {},
                    "description": f"Optimize {param_name}"
                })
                stage_num += 1
                
        else:
            # Fallback: Infer from indicators metadata (Legacy behavior for templates without schema)
            # Stages 2 to N: Indicator parameters
            for indicator in metadata['indicators']:
                ind_type = indicator['type']
                ind_alias = indicator.get('alias', ind_type)
                ind_params = indicator.get('params', {})
                
                # Get optimization ranges from indicator config or use defaults
                opt_range = indicator.get('optimization_range', {})
                
                for param_name, param_value in ind_params.items():
                    # Create full parameter name (e.g., "ema_fast_length")
                    full_param_name = f"{ind_alias}_{param_name}"
                    
                    # Check if custom range is provided
                    if custom_ranges and full_param_name in custom_ranges:
                        custom = custom_ranges[full_param_name]
                        values = self._generate_values_from_range(
                            custom.get('min', param_value),
                            custom.get('max', param_value * 2),
                            custom.get('step', 1)
                        )
                    elif param_name in opt_range:
                        # Use optimization range from template
                        range_config = opt_range[param_name]
                        values = self._generate_values_from_range(
                            range_config.get('min', param_value),
                            range_config.get('max', param_value * 2),
                            range_config.get('step', 1)
                        )
                    else:
                        # Default range: ±50% of default value
                        min_val = max(1, int(param_value * 0.5))
                        max_val = int(param_value * 1.5)
                        step = max(1, int((max_val - min_val) / 10))
                        values = self._generate_values_from_range(min_val, max_val, step)
                    
                    stages.append({
                        "stage_num": stage_num,
                        "stage_name": f"{ind_alias.upper()} {param_name}",
                        "parameter": full_param_name,
                        "values": values,
                        "locked_params": {},
                        "description": f"Optimize {ind_alias} {param_name}"
                    })
                    stage_num += 1
        
        return stages
    
    def _generate_values_from_range(self, min_val: float, max_val: float, step: float) -> List[float]:
        """Generate list of values from min to max with step."""
        values = []
        current = min_val
        while current <= max_val:
            values.append(current)
            current += step
        return values
    
    def run_optimization(
        self,
        template_name: str,
        symbol: str,
        timeframe: str = "1h",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        custom_ranges: Optional[Dict[str, Any]] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run optimization for a combo strategy.
        
        Args:
            template_name: Name of combo template
            symbol: Trading symbol
            timeframe: Fixed timeframe or None for optimization
            start_date: Start date for backtest
            end_date: End date for backtest
            custom_ranges: Custom parameter ranges
            job_id: Optional job ID for tracking
            
        Returns:
            Optimization results with best parameters and metrics
        """
        # Generate stages
        fixed_timeframe = timeframe if timeframe else None
        stages = self.generate_stages(
            template_name=template_name,
            symbol=symbol,
            fixed_timeframe=fixed_timeframe,
            custom_ranges=custom_ranges
        )
        
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
        best_sharpe = float('-inf')
        
        # Run optimization stages sequentially
        for stage in stages:
            stage_param = stage['parameter']
            stage_values = stage['values']
            
            logging.info(f"Stage {stage['stage_num']}: Optimizing {stage_param}")
            
            stage_best_value = None
            stage_best_sharpe = float('-inf')
            
            for value in stage_values:
                # Build parameters for this test
                test_params = best_params.copy()
                
                # Handle timeframe parameter separately
                if stage_param == 'timeframe':
                    test_timeframe = value
                    # Reload data with new timeframe
                    df = self.loader.fetch_data(
                        symbol=symbol,
                        timeframe=test_timeframe,
                        since_str=start_date,
                        until_str=end_date
                    )
                else:
                    test_params[stage_param] = value
                    test_timeframe = timeframe
                
                # Run backtest
                try:
                    # Create strategy with current parameters
                    strategy = self.combo_service.create_strategy(
                        template_name=template_name,
                        parameters=test_params
                    )
                    
                    # Generate signals
                    df_with_signals = strategy.generate_signals(df.copy())
                    
                    # Extract trades from signals
                    trades = []
                    position = None
                    
                    for idx, row in df_with_signals.iterrows():
                        if row['signal'] == 1 and position is None:
                            # Buy signal
                            position = {
                                'entry_time': idx,
                                'entry_price': row['close'],
                                'type': 'long'
                            }
                        elif row['signal'] == -1 and position is not None:
                            # Sell signal
                            position['exit_time'] = idx
                            position['exit_price'] = row['close']
                            position['profit'] = (position['exit_price'] - position['entry_price']) / position['entry_price']
                            trades.append(position)
                            position = None
                    
                    # Calculate metrics
                    if len(trades) > 0:
                        total_trades = len(trades)
                        winning_trades = sum(1 for t in trades if t['profit'] > 0)
                        win_rate = winning_trades / total_trades
                        total_return = sum(t['profit'] for t in trades)
                        avg_profit = total_return / total_trades
                        
                        # Simple Sharpe approximation
                        returns = [t['profit'] for t in trades]
                        import numpy as np
                        sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
                        
                        metrics = {
                            'total_trades': total_trades,
                            'win_rate': win_rate,
                            'total_return': total_return,
                            'avg_profit': avg_profit,
                            'sharpe_ratio': sharpe
                        }
                    else:
                        metrics = {
                            'total_trades': 0,
                            'win_rate': 0,
                            'total_return': 0,
                            'avg_profit': 0,
                            'sharpe_ratio': 0
                        }
                    
                    # Check if this is the best
                    sharpe = metrics.get('sharpe_ratio', 0)
                    if sharpe > stage_best_sharpe:
                        stage_best_sharpe = sharpe
                        stage_best_value = value
                        
                        if sharpe > best_sharpe:
                            best_sharpe = sharpe
                            best_metrics = metrics
                
                except Exception as e:
                    logging.warning(f"Backtest failed for {stage_param}={value}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Lock in best value for this stage
            if stage_best_value is not None:
                if stage_param == 'timeframe':
                    timeframe = stage_best_value
                else:
                    best_params[stage_param] = stage_best_value
                logging.info(f"Stage {stage['stage_num']} complete: {stage_param}={stage_best_value} (Sharpe: {stage_best_sharpe:.3f})")
        
        return {
            "job_id": job_id or "combo_opt_" + str(hash(template_name + symbol)),
            "template_name": template_name,
            "symbol": symbol,
            "stages": stages,
            "best_parameters": best_params,
            "best_metrics": best_metrics or {},
            "total_stages": len(stages)
        }
