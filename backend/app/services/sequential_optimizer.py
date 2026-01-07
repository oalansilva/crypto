"""
Sequential Optimizer Service

Orchestrates sequential parameter optimization with:
- Dynamic stage generation based on indicator schemas
- Checkpoint system for crash recovery
- Full history backtesting
- State persistence after each test
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from app.schemas.indicator_params import (
    get_indicator_schema,
    calculate_total_stages,
    TIMEFRAME_OPTIONS,
    RISK_MANAGEMENT_SCHEMA
)
from app.services.backtest_service import BacktestService
from src.data.incremental_loader import IncrementalLoader


class SequentialOptimizer:
    """
    Sequential parameter optimization service.
    
    Optimizes one parameter at a time, using best results from previous stages.
    Includes checkpoint system for crash recovery.
    """
    
    def __init__(self, checkpoint_dir: str = "backend/data/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.backtest_service = BacktestService()
    
    def generate_stages(
        self, 
        strategy: str, 
        symbol: str, 
        fixed_timeframe: Optional[str] = None,
        custom_ranges: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate optimization stages dynamically based on indicator schema.
        
        Args:
            strategy: Strategy name (e.g., "macd", "rsi")
            symbol: Trading symbol (e.g., "BTC/USDT")
            fixed_timeframe: If set, skips timeframe optimization stage
            custom_ranges: Optional overrides for parameter ranges
            
        Returns:
            List of stage configurations
        """
        indicator_schema = get_indicator_schema(strategy)
        if not indicator_schema:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        stages = []
        
        # Stage 1: Timeframe optimization (Only if NOT fixed)
        if not fixed_timeframe:
            stages.append({
                "stage_num": 1,
                "stage_name": "Timeframe",
                "parameter": "timeframe",
                "values": TIMEFRAME_OPTIONS,
                "locked_params": {},
                "description": "Optimize trading timeframe"
            })
            stage_offset = 1
        else:
            stage_offset = 0
        
        # Stages 2 to N+1: Indicator parameters
        stage_num = 1 + stage_offset
        for param_name, param_schema in indicator_schema.parameters.items():
            # Check for custom range override
            opt_range = param_schema.optimization_range
            
            if custom_ranges and param_name in custom_ranges:
                custom = custom_ranges[param_name]
                # Format: {min: x, max: y, step: z}
                if isinstance(custom, dict) and 'min' in custom:
                    # Create temporary range object or list of values
                    values = []
                    current = float(custom['min'])
                    end = float(custom['max'])
                    step = float(custom.get('step', 1.0))
                    
                    if step <= 0: step = 1.0 # Prevent infinite loop
                    
                    while current <= end + (step * 0.1): # Float tolerance
                        if param_schema.type == "int":
                            values.append(int(current))
                        else:
                            values.append(round(current, 4))
                        current += step
                else:
                    # Fallback or direct list
                    values = [custom] if not isinstance(custom, list) else custom
            
            elif opt_range:
                # Use default schema range
                values = []
                current = opt_range.min
                while current <= opt_range.max:
                    values.append(current)
                    current += opt_range.step
            else:
                continue # No optimization for this param

            if values:
                stages.append({
                    "stage_num": stage_num,
                    "stage_name": param_name.replace("_", " ").title(),
                    "parameter": param_name,
                    "values": values,
                    "locked_params": {},  # Will be filled during execution
                    "description": param_schema.description,
                    "market_standard": param_schema.market_standard
                })
                stage_num += 1
        
        # Stage N+2: Stop-loss optimization
        sl_param = RISK_MANAGEMENT_SCHEMA["stop_loss"]
        sl_range = sl_param.optimization_range
        sl_values = []
        current = sl_range.min
        while current <= sl_range.max:
            sl_values.append(round(current, 4))
            current += sl_range.step
        
        stages.append({
            "stage_num": stage_num,
            "stage_name": "Stop-Loss",
            "parameter": "stop_loss",
            "values": sl_values,
            "locked_params": {},
            "description": sl_param.description,
            "market_standard": sl_param.market_standard
        })
        stage_num += 1
        
        # Stage N+3: Stop-gain optimization
        sg_param = RISK_MANAGEMENT_SCHEMA["stop_gain"]
        stages.append({
            "stage_num": stage_num,
            "stage_name": "Stop-Gain",
            "parameter": "stop_gain",
            "values": sg_param.options,
            "locked_params": {},
            "description": sg_param.description,
            "market_standard": sg_param.market_standard
        })
        
        return stages
    
    def get_full_history_dates(self, symbol: str) -> Tuple[str, str]:
        """
        Auto-detect full available history for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Tuple of (start_date, end_date) as ISO strings
        """
    def get_full_history_dates(self, symbol: str) -> Tuple[str, str]:
        """
        Auto-detect full available history for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Tuple of (start_date, end_date) as ISO strings
        """
        # Fix: IncrementalLoader defaults to binance, doesn't take symbol in init
        loader = IncrementalLoader() 
        
        # Load data ensuring full history (start from 2017)
        # timeframe="1d" is sufficient for determining range
        df = loader.fetch_data(symbol=symbol, timeframe="1d", since_str="2017-01-01")
        
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
            
        # Ensure index is datetime if it's not already (fetch_data returns default index usually)
        # fetch_data returns 'timestamp_utc' column
        if 'timestamp_utc' in df.columns:
            start_date = df['timestamp_utc'].min().isoformat()
            end_date = df['timestamp_utc'].max().isoformat()
        else:
            # Fallback
            start_date = df.index.min().isoformat()
            end_date = df.index.max().isoformat()
        
        return start_date, end_date
    
    def create_checkpoint(self, job_id: str, state: Dict[str, Any]) -> None:
        """
        Save checkpoint after each test completion.
        
        Args:
            job_id: Unique job identifier
            state: Current optimization state
        """
        checkpoint_file = self.checkpoint_dir / f"{job_id}.json"
        
        state["timestamp"] = datetime.utcnow().isoformat()
        state["status"] = "in_progress"
        
        with open(checkpoint_file, "w") as f:
            json.dump(state, f, indent=2)
    
    def load_checkpoint(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint state for recovery.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Checkpoint state if exists, None otherwise
        """
        checkpoint_file = self.checkpoint_dir / f"{job_id}.json"
        
        if not checkpoint_file.exists():
            return None
        
        with open(checkpoint_file, "r") as f:
            return json.load(f)
    
    def delete_checkpoint(self, job_id: str) -> None:
        """
        Delete checkpoint after successful completion.
        
        Args:
            job_id: Unique job identifier
        """
        checkpoint_file = self.checkpoint_dir / f"{job_id}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
    
    def find_incomplete_jobs(self) -> List[Dict[str, Any]]:
        """
        Find all incomplete optimization jobs.
        
        Returns:
            List of incomplete job states
        """
        incomplete = []
        
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            with open(checkpoint_file, "r") as f:
                state = json.load(f)
                if state.get("status") == "in_progress":
                    incomplete.append(state)
        
        return incomplete
    
    async def run_stage(
        self,
        job_id: str,
        stage_config: Dict[str, Any],
        symbol: str,
        strategy: str,
        locked_params: Dict[str, Any],
        start_from_test: int = 0
    ) -> Dict[str, Any]:
        """
        Execute a single optimization stage.
        
        Args:
            job_id: Unique job identifier
            stage_config: Stage configuration
            symbol: Trading symbol
            strategy: Strategy name
            locked_params: Parameters locked from previous stages
            start_from_test: Resume from this test index (for recovery)
            
        Returns:
            Stage results with best value
        """
        stage_num = stage_config["stage_num"]
        parameter = stage_config["parameter"]
        values = stage_config["values"]
        
        # Get full history dates
        start_date, end_date = self.get_full_history_dates(symbol)
        
        results = []
        best_result = None
        best_value = None
        
        # Resume from checkpoint if needed
        for i, value in enumerate(values):
            if i < start_from_test:
                continue  # Skip already completed tests
            
            # Build test parameters
            test_params = locked_params.copy()
            test_params[parameter] = value
            
            # Run backtest with full history
            # Build config for BacktestService
            config = {
                "exchange": "binance",
                "symbol": symbol,
                "timeframe": test_params.get("timeframe", "1h"),
                "strategies": [strategy],
                "since": start_date,
                "until": end_date,
                "params": {strategy: test_params},
                "mode": "run",
                "cash": 10000
            }

            # Run backtest (synchronous)
            backtest_result = self.backtest_service.run_backtest(config)
            
            # Extract metrics (handle nested structure)
            # Structure: {'results': {'StrategyName': {'metrics': ...}}}
            try:
                # Debug: Print the structure
                print(f"DEBUG: backtest_result keys: {backtest_result.keys()}")
                
                results_dict = backtest_result.get("results", {})
                print(f"DEBUG: results_dict keys: {results_dict.keys() if results_dict else 'None'}")
                
                if results_dict:
                    # Take the first result (we only ran one strategy)
                    strat_result = list(results_dict.values())[0]
                    print(f"DEBUG: strat_result keys: {strat_result.keys() if isinstance(strat_result, dict) else 'Not a dict'}")
                    
                    # Check if there's an error
                    if 'error' in strat_result:
                        print(f"ERROR: Backtest failed: {strat_result['error']}")
                        metrics = {"total_pnl": 0, "error": strat_result['error']}
                    else:
                        metrics = strat_result.get("metrics", {})
                        if not metrics or 'total_pnl' not in metrics:
                            print(f"WARNING: No valid metrics found, using default")
                            metrics = {"total_pnl": 0}
                else:
                    print("WARNING: No results in backtest_result")
                    metrics = {"total_pnl": 0}
            except Exception as e:
                print(f"ERROR extracting metrics: {e}")
                import traceback
                traceback.print_exc()
                metrics = {"total_pnl": 0}

            result = {
                parameter: value,
                "metrics": metrics,
                "test_num": i + 1,
                "total_tests": len(values)
            }
            results.append(result)
            
            # Track best result
            current_pnl = metrics.get("total_pnl", float('-inf'))
            best_pnl = best_result["metrics"].get("total_pnl", float('-inf')) if best_result else float('-inf')
            
            if best_result is None or current_pnl > best_pnl:
                best_result = result
                best_value = value
            
            # Create checkpoint after each test
            checkpoint_state = {
                "job_id": job_id,
                "symbol": symbol,
                "strategy": strategy,
                "current_stage": stage_num,
                "total_stages": None,  # Will be set by caller
                "stage_name": stage_config["stage_name"],
                "tests_completed": i + 1,
                "total_tests_in_stage": len(values),
                "completed_tests": results,
                "best_result": best_result,
                "locked_params": locked_params
            }
            self.create_checkpoint(job_id, checkpoint_state)
        
        return {
            "stage_num": stage_num,
            "stage_name": stage_config["stage_name"],
            "parameter": parameter,
            "results": results,
            "best_value": best_value,
            "best_result": best_result
        }
    
    async def resume_from_checkpoint(self, job_id: str) -> Dict[str, Any]:
        """
        Resume optimization from last checkpoint.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Optimization results
        """
        checkpoint = self.load_checkpoint(job_id)
        if not checkpoint:
            raise ValueError(f"No checkpoint found for job {job_id}")
        
        # Extract state
        symbol = checkpoint["symbol"]
        strategy = checkpoint["strategy"]
        current_stage = checkpoint["current_stage"]
        tests_completed = checkpoint["tests_completed"]
        locked_params = checkpoint["locked_params"]
        
        # Generate stages
        stages = self.generate_stages(strategy, symbol)
        
        # Resume from current stage
        stage_config = stages[current_stage - 1]
        
        return await self.run_stage(
            job_id=job_id,
            stage_config=stage_config,
            symbol=symbol,
            strategy=strategy,
            locked_params=locked_params,
            start_from_test=tests_completed
        )
