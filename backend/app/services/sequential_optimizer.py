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
    
    def generate_stages(self, strategy: str, symbol: str) -> List[Dict[str, Any]]:
        """
        Generate optimization stages dynamically based on indicator schema.
        
        Args:
            strategy: Strategy name (e.g., "macd", "rsi")
            symbol: Trading symbol (e.g., "BTC/USDT")
            
        Returns:
            List of stage configurations
        """
        indicator_schema = get_indicator_schema(strategy)
        if not indicator_schema:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        stages = []
        
        # Stage 1: Timeframe optimization
        stages.append({
            "stage_num": 1,
            "stage_name": "Timeframe",
            "parameter": "timeframe",
            "values": TIMEFRAME_OPTIONS,
            "locked_params": {},
            "description": "Optimize trading timeframe"
        })
        
        # Stages 2 to N+1: Indicator parameters
        stage_num = 2
        for param_name, param_schema in indicator_schema.parameters.items():
            if param_schema.optimization_range:
                opt_range = param_schema.optimization_range
                values = []
                current = opt_range.min
                while current <= opt_range.max:
                    values.append(current)
                    current += opt_range.step
                
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
        loader = IncrementalLoader(symbol=symbol, timeframe="1d")
        df = loader.load()
        
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        
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
            backtest_result = await self.backtest_service.run_backtest(
                symbol=symbol,
                strategy=strategy,
                timeframe=test_params.get("timeframe", "1h"),
                start_date=start_date,
                end_date=end_date,
                params=test_params
            )
            
            result = {
                parameter: value,
                "metrics": backtest_result["metrics"],
                "test_num": i + 1,
                "total_tests": len(values)
            }
            results.append(result)
            
            # Track best result
            if best_result is None or backtest_result["metrics"]["total_pnl"] > best_result["metrics"]["total_pnl"]:
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
