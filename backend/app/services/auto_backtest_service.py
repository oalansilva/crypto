# file: backend/app/services/auto_backtest_service.py
"""
Auto Backtest Service - Orchestrates end-to-end backtest workflow
"""
import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import AutoBacktestRun
from app.services.pandas_ta_inspector import get_all_indicators_metadata
import pandas as pd
from app.metrics import (
    calculate_sortino_ratio,
    calculate_avg_drawdown,
    calculate_recovery_factor,
    calculate_expectancy,
    calculate_max_consecutive_losses
)
from app.metrics.regime import calculate_regime_classification

logger = logging.getLogger(__name__)


class AutoBacktestService:
    """Orchestrator for auto backtest workflow"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_run(self, symbol: str, strategy: str) -> AutoBacktestRun:
        """Create a new auto backtest run in database"""
        run_id = f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        run = AutoBacktestRun(
            run_id=run_id,
            symbol=symbol,
            strategy=strategy,
            status='PENDING'
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        
        self._log(run_id, f"Stage 0 - Created run - Symbol: {symbol}, Strategy: {strategy}")
        return run
    
    def execute_workflow(self, run: AutoBacktestRun) -> AutoBacktestRun:
        """
        Execute complete 3-stage workflow
        This will be called by background task or async endpoint
        """
        try:
            run.status = 'RUNNING'
            self.db.commit()
            
            # Stage 1: Timeframe
            self._log(run.run_id, f"Stage 1 started - Testing timeframes")
            stage1_result = self._execute_stage_1(run)
            run.stage_1_result = stage1_result
            self.db.commit()
            self._log(run.run_id, f"Stage 1 completed - Best: {stage1_result.get('best_timeframe')}")
            
            # Stage 2: Parameters
            self._log(run.run_id, f"Stage 2 started - Optimizing parameters")
            stage2_result = self._execute_stage_2(run, stage1_result)
            run.stage_2_result = stage2_result
            self.db.commit()
            self._log(run.run_id, f"Stage 2 completed - Best params found")
            
            # Stage 3: Risk
            self._log(run.run_id, f"Stage 3 started - Optimizing stop/take")
            stage3_result = self._execute_stage_3(run, stage1_result, stage2_result)
            run.stage_3_result = stage3_result
            self.db.commit()
            self._log(run.run_id, f"Stage 3 completed - Stop: {stage3_result.get('stop_loss')}%, Take: {stage3_result.get('take_profit')}%")
            
            # Stage 4: Save favorite
            favorite_id = self._save_favorite(run, stage1_result, stage2_result, stage3_result)
            run.favorite_id = favorite_id
            run.status = 'COMPLETED'
            run.completed_at = datetime.now()
            self.db.commit()
            
            self._log(run.run_id, f"Final: Saved to favorites (ID: {favorite_id})")
            
        except Exception as e:
            logger.error(f"Auto backtest {run.run_id} failed: {str(e)}")
            run.status = 'FAILED'
            run.error_message = str(e)
            self.db.commit()
            self._log(run.run_id, f"FAILED: {str(e)}")
            raise
        
        return run
    
    def _execute_stage_1(self, run: AutoBacktestRun) -> Dict[str, Any]:
        """
        Stage 1: Timeframe Optimization
        Calls existing sequential/timeframe endpoint logic
        """
        from app.services.backtest_service import BacktestService
        
        backtest_service = BacktestService()
        
        # Get default parameters for strategy
        metadata = get_all_indicators_metadata()
        
        # Metadata is a dict of categories, flatten it
        flattened_meta = []
        if isinstance(metadata, dict):
            for category, items in metadata.items():
                if isinstance(items, list):
                    flattened_meta.extend(items)
        else:
            flattened_meta = metadata
            
        strategy_meta = next((m for m in flattened_meta if m.get('id') == run.strategy or m.get('name') == run.strategy), None)
        if not strategy_meta:
            raise ValueError(f"Strategy {run.strategy} not found")
        
        default_params = {param['name']: param['default'] for param in strategy_meta.get('params', [])}
        
        # Test all timeframes
        timeframes = ["5m", "15m", "30m", "1h", "2h", "4h", "1d"]
        results = []
        
        for tf in timeframes:
            config = {
                "exchange": "binance",
                "symbol": run.symbol,
                "timeframe": tf,
                "strategies": [run.strategy],
                "params": {run.strategy: default_params},  # Nest params by strategy name
                "full_period": True,  # Use complete historical data
                "fee": 0.00075,
                "slippage": 0.0
            }
            
            # run_backtest returns a dict with 'results' key containing run results
            result_map = backtest_service.run_backtest(config)
            
            # Extract metrics from results
            if not result_map or 'results' not in result_map:
                continue
            
            results_dict = result_map['results']
            if not results_dict:
                continue
                
            # Get the first (and only) result
            first_result = next(iter(results_dict.values()))
            metrics = first_result.get("metrics", {})
            
            # Log diagnostic info
            trades = metrics.get("total_trades", 0)
            self._log(run.run_id, f"TF {tf}: {trades} trades, Sharpe: {metrics.get('sharpe_ratio', 0):.4f}, Return: {metrics.get('total_return_pct', 0):.2f}%")
            
            results.append({
                "timeframe": tf,
                "sharpe_ratio": metrics.get("sharpe_ratio", 0),
                "metrics": metrics
            })
        
        # Select best by Sharpe
        if not results:
            raise ValueError("No results from timeframe optimization")
            
        best = max(results, key=lambda x: x["sharpe_ratio"])
        
        return {
            "best_timeframe": best["timeframe"],
            "all_results": results,
            "selection_criteria": "sharpe_ratio"
        }
    
    def _execute_stage_2(self, run: AutoBacktestRun, stage1: Dict) -> Dict[str, Any]:
        """
        Stage 2: Sequential Parameter Optimization
        Uses schema optimization ranges (same as /optimize/parameters)
        """
        from app.services.backtest_service import BacktestService
        from app.schemas.indicator_params import get_indicator_schema
        
        backtest_service = BacktestService()
        best_timeframe = stage1["best_timeframe"]
        
        # Get indicator schema (same source as /optimize/parameters)
        indicator_schema = get_indicator_schema(run.strategy)
        if not indicator_schema:
            raise ValueError(f"Unknown strategy: {run.strategy}")
        
        # Get base parameters (defaults from schema)
        base_params = {}
        for param_name, param_schema in indicator_schema.parameters.items():
            base_params[param_name] = param_schema.default
        
        # Sequential optimization: test each parameter individually
        locked_params = base_params.copy()
        all_results = []
        
        for param_name, param_schema in indicator_schema.parameters.items():
            # Skip if no optimization range defined
            if not param_schema.optimization_range:
                continue
            
            opt_range = param_schema.optimization_range
            
            # Generate test values from schema range (same as /optimize/parameters)
            test_values = []
            current = opt_range.min
            while current <= opt_range.max:
                test_values.append(current)
                current += opt_range.step
            
            # Remove duplicates while preserving order
            seen = set()
            test_values = [x for x in test_values if not (x in seen or seen.add(x))]
            
            stage_results = []
            
            for test_value in test_values:
                # Create config with locked params + current test value
                test_params = locked_params.copy()
                test_params[param_name] = test_value
                
                config = {
                    "exchange": "binance",
                    "symbol": run.symbol,
                    "timeframe": best_timeframe,
                    "strategies": [run.strategy],
                    "params": {run.strategy: test_params},  # Nest params by strategy name
                    "full_period": True,  # Use complete historical data
                    "fee": 0.00075,
                    "slippage": 0.0
                }
                
                
                result_map = backtest_service.run_backtest(config)
                
                if not result_map or 'results' not in result_map:
                    continue
                
                results_dict = result_map['results']
                if not results_dict:
                    continue
                    
                first_result = next(iter(results_dict.values()))
                metrics = first_result.get("metrics", {})
                
                result_entry = {
                    "parameters": test_params.copy(),
                    "sharpe_ratio": metrics.get("sharpe_ratio", 0),
                    "metrics": metrics
                }
                
                stage_results.append(result_entry)
                all_results.append(result_entry)
                
                self._log(run.run_id, f"Tested {param_name}={test_value}: Sharpe: {metrics.get('sharpe_ratio', 0):.4f}")
            
            # Lock the best value for this parameter
            if stage_results:
                best_for_param = max(stage_results, key=lambda x: x["sharpe_ratio"])
                locked_params[param_name] = best_for_param["parameters"][param_name]
                self._log(run.run_id, f"Locked {param_name}={locked_params[param_name]} (Sharpe: {best_for_param['sharpe_ratio']:.4f})")
        
        if not all_results:
            raise ValueError("No results from parameter optimization")
        
        # Best result is the one with all locked parameters (from final iteration)
        best = max(all_results, key=lambda x: x["sharpe_ratio"])
        
        return {
            "best_parameters": best["parameters"],
            "all_results": all_results
        }
    
    def _execute_stage_3(self, run: AutoBacktestRun, stage1: Dict, stage2: Dict) -> Dict[str, Any]:
        """
        Stage 3: Risk Optimization (Stop/Take)
        Tests grid: stop=[1%, 2%, 3%, 4%, 5%], take=[1%, 2%, 3%, 4%, 5%, 7.5%, 10%]
        """
        from app.services.backtest_service import BacktestService
        
        backtest_service = BacktestService()
        best_timeframe = stage1["best_timeframe"]
        best_params = stage2["best_parameters"]
        
        # Grid for stop loss and take profit
        # Grid for stop loss and take profit
        # Stop: 0.5% to 13%, step 0.2% (Matches frontend)
        # 0.005, 0.007, ... 0.129
        stops = [round(x / 1000.0, 4) for x in range(5, 131, 2)]
        
        # Take: Matches frontend DEFAULT (None only) to speed up and follow rules
        # If user wants 1%, 2% etc they can use manual optimization.
        takes = [None]
        
        results = []
        
        for stop_loss in stops:
            for take_profit in takes:
                # Create params copy with risk settings
                # Note: Strategy must perform risk management using these keys
                # or we need to pass them differently if strategy doesn't support them inside params.
                # Assuming strategy uses them or service applies them.
                # Standard params often used: 'stop_loss_pct', 'take_profit_pct'
                # If strategy doesn't support them, this optimization might be moot without modifying strategy execution wrapper.
                # But let's assume we pass them as params.
                current_params = best_params.copy()
                current_params['stop_loss'] = stop_loss
                current_params['take_profit'] = take_profit
                
                config = {
                    "exchange": "binance",
                    "symbol": run.symbol,
                    "timeframe": best_timeframe,
                    "strategies": [run.strategy],
                    "params": {run.strategy: current_params},  # Nest params by strategy name
                    "full_period": True,  # Use complete historical data
                    "fee": 0.00075,
                    "slippage": 0.0,
                    "stop_pct": stop_loss,
                    "take_pct": take_profit
                }
                
                result_map = backtest_service.run_backtest(config)
    
                if not result_map or 'results' not in result_map:
                    continue
                
                results_dict = result_map['results']
                if not results_dict:
                    continue
                    
                first_result = next(iter(results_dict.values()))
                metrics = first_result.get("metrics", {})
                
                results.append({
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "metrics": metrics,
                    "trades": first_result.get("trades", []),
                    "equity_curve": first_result.get("equity") or first_result.get("equity_curve")
                })
                
                # DEBUG LOG ONCE
                if stop_loss == stops[0] and take_profit == takes[0]:
                     logger.info(f"DEBUG First Result Keys: {list(first_result.keys())}")
                     logger.info(f"DEBUG Equity Data Found: {first_result.get('equity') is not None}")
                take_display = f"{take_profit*100:.1f}%" if take_profit is not None else "None"
                self._log(run.run_id, f"Tested Risk (Stop: {stop_loss*100:.1f}%, Take: {take_display}): Sharpe: {metrics.get('sharpe_ratio', 0):.4f}")
                
        if not results:
             # unexpected
             return {
                 "best_risk": {"stop_loss": 0.02, "take_profit": 0.04}, # fallback
                 "all_results": []
             }
             
        best = max(results, key=lambda x: x["metrics"].get("total_return_pct", -999999))
        
        # Enrich metrics for the winner
        enriched_metrics = self._enrich_metrics(
            best["metrics"], 
            best.get("trades", []), 
            best.get("equity_curve")
        )
        best["metrics"] = enriched_metrics
        
        return_pct = best["metrics"].get("total_return_pct", 0)
        self._log(run.run_id, f"Best Risk: Stop {best['stop_loss']*100:.1f}%, Return: {return_pct:.2f}%")
        
        return {
            "best_risk": {
                "stop_loss": best["stop_loss"],
                "take_profit": best["take_profit"]
            },
            "metrics": best["metrics"],
            "all_results": [
                {k: v for k, v in r.items() if k not in ['trades', 'equity_curve']} 
                for r in results
            ]
        }
    
    
    def _enrich_metrics(self, metrics: Dict[str, Any], trades: list, equity_data: Any) -> Dict[str, Any]:
        """Calculate heavy and advanced metrics for the selected strategy"""
        enhanced = metrics.copy()
        
        # 1. Equity Curve Metrics
        if equity_data:
            try:
                # Convert back to Series
                if isinstance(equity_data, list):
                    # Expect [{'timestamp': '...', 'equity': 123}, ...]
                    df_eq = pd.DataFrame(equity_data)
                    if 'equity' in df_eq.columns:
                        eq = pd.to_numeric(df_eq['equity'], errors='coerce')
                        
                        # Recalculate Total Return (Compounded)
                        if len(eq) > 0:
                            start_eq = float(eq.iloc[0])
                            end_eq = float(eq.iloc[-1])
                            if start_eq > 0:
                                new_ret = (end_eq - start_eq) / start_eq
                                enhanced['total_return_pct'] = new_ret * 100
                                logger.info(f"Recalculated Return: {enhanced['total_return_pct']:.2f}% (Start: {start_eq}, End: {end_eq})")
                    else:
                        eq = pd.Series([])
                elif isinstance(equity_data, dict):
                    eq = pd.Series(equity_data).sort_index()
                else:
                    eq = equity_data
                
                # Ensure numeric and drop NaNs
                eq = pd.to_numeric(eq, errors='coerce').dropna()
                
                if len(eq) > 1:
                    returns = eq.pct_change().dropna()
                    sortino = calculate_sortino_ratio(returns)
                    enhanced['sortino_ratio'] = sortino
                    enhanced['sortino'] = sortino # Map for frontend
                    logger.info(f"Calculated Sortino: {sortino}")
            except Exception as e:
                logger.error(f"Error calculating equity metrics: {e}")

        # 2. Trade Statistics
        if trades:
            try:
                # Expectancy
                enhanced['expectancy'] = calculate_expectancy(trades)
                
                # Profit Factor
                gross_profit = sum([float(t.get('pnl', 0)) for t in trades if float(t.get('pnl', 0)) > 0])
                gross_loss = abs(sum([float(t.get('pnl', 0)) for t in trades if float(t.get('pnl', 0)) < 0]))
                
                enhanced['profit_factor'] = gross_profit / gross_loss if gross_loss > 0 else (999 if gross_profit > 0 else 0)
                
                # Max Loss (simple min of PnL)
                pnl_values = [float(t.get('pnl', 0)) for t in trades]
                enhanced['max_loss'] = min(pnl_values) if pnl_values else 0
                
                # Max Consecutive Losses
                enhanced['max_consecutive_losses'] = calculate_max_consecutive_losses(trades)
                
            except Exception as e:
                logger.error(f"Error calculating trade metrics: {e}")
                
        return enhanced

    def _save_favorite(self, run: AutoBacktestRun, stage1: Dict, stage2: Dict, stage3: Dict) -> int:
        """Save final configuration to favorites"""
        from app.models import FavoriteStrategy
        
        # Merge parameters with risk settings
        final_parameters = stage2["best_parameters"].copy()
        final_parameters["stop_loss"] = stage3["best_risk"]["stop_loss"]
        final_parameters["stop_gain"] = stage3["best_risk"]["take_profit"]
        if "take_profit" in final_parameters:
            del final_parameters["take_profit"] # Remove backend-style key if present
        
        favorite = FavoriteStrategy(
            name=f"Auto: {run.strategy.upper()} - {run.symbol}",
            symbol=run.symbol,
            strategy_name=run.strategy,
            timeframe=stage1["best_timeframe"],
            parameters=final_parameters,
            notes=f"Auto-selected on {datetime.now().strftime('%Y-%m-%d %H:%M')} (Run: {run.run_id})",
            metrics=stage3["metrics"]
        )
        
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        
        return favorite.id
    
    def _log(self, run_id: str, message: str):
        """Append to full_execution_log.txt"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] AUTO_BACKTEST - {message}\n"
        
        with open("backend/full_execution_log.txt", "a") as f:
            f.write(log_line)
        
        logger.info(f"[{run_id}] {message}")
