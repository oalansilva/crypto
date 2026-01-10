"""
Risk Management Optimization API
Dedicated endpoint for optimizing stop_loss and stop_gain parameters.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from app.services.sequential_optimizer import SequentialOptimizer
from app.schemas.indicator_params import get_indicator_schema

router = APIRouter()
optimizer = SequentialOptimizer()


def log_debug(message: str):
    """Helper to log to file and console simultaneously"""
    print(message)
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_path = os.path.join(base_dir, "full_execution_log.txt")
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    except Exception as e:
        print(f"⚠ Failed to write to log file: {e}")


class RiskOptimizationRequest(BaseModel):
    """Request model for risk management optimization"""
    symbol: str
    strategy: str
    timeframe: str
    strategy_params: Dict[str, Any]  # Fixed indicator parameters (already optimized)
    custom_ranges: Optional[Dict[str, Any]] = None  # Custom ranges for stop_loss, stop_gain
    fee: Optional[float] = 0.00075
    slippage: Optional[float] = 0.0005


class RiskCombinationResult(BaseModel):
    """Single risk parameter combination result"""
    params: Dict[str, Any]
    metrics: Dict[str, Any]
    trades: Optional[List[Dict[str, Any]]] = None


class RiskOptimizationResponse(BaseModel):
    """Response model for risk optimization"""
    results: List[RiskCombinationResult]
    best_combination: Dict[str, Any]
    total_tests: int
    execution_time_seconds: float


@router.post("/api/optimize/risk", response_model=RiskOptimizationResponse)
async def optimize_risk(request: RiskOptimizationRequest):
    """
    Optimize Risk Management parameters (stop_loss, stop_gain).
    
    This endpoint assumes indicator parameters have already been optimized
    and are provided in strategy_params.
    
    Args:
        request: Risk optimization configuration
        
    Returns:
        Complete optimization results with all tested combinations
    """
    from app.services.job_manager import JobManager
    
    start_time = datetime.now()
    log_debug(f"🎯 RISK OPTIMIZATION REQUEST: {request.symbol} {request.strategy} {request.timeframe}")
    log_debug(f"   Strategy Params (Fixed): {request.strategy_params}")
    log_debug(f"   Custom Ranges: {request.custom_ranges}")
    
    # Initialize JobManager
    job_manager = JobManager()
    job_id = job_manager.create_job({
        "type": "risk_management_optimization",
        "symbol": request.symbol,
        "strategy": request.strategy,
        "timeframe": request.timeframe,
        "strategy_params": request.strategy_params,
        "custom_ranges": request.custom_ranges
    })
    log_debug(f"   Created job: {job_id}")
    
    try:
        # Build locked parameters (indicator params + fixed values)
        locked_params = {
            **request.strategy_params,  # Fixed indicator parameters
            "timeframe": request.timeframe,
            "fee": request.fee,
            "slippage": request.slippage
        }
        
        log_debug(f"   Locked params: {locked_params}")
        
        # Generate ONLY risk management stages
        stages = optimizer.generate_stages(
            strategy=request.strategy,
            symbol=request.symbol,
            fixed_timeframe=request.timeframe,
            custom_ranges=request.custom_ranges,
            include_risk=True  # ONLY include risk parameters
        )
        
        log_debug(f"   Generated {len(stages)} risk optimization stages")
        
        # Validate that we only have risk parameters
        risk_params = {'stop_loss', 'stop_gain'}
        for stage in stages:
            if stage['parameter'] not in risk_params:
                raise ValueError(
                    f"Invalid stage '{stage['parameter']}' in risk optimization. "
                    f"Only {risk_params} are allowed. "
                    f"Indicator parameters should be passed in strategy_params."
                )
        
        # Run all risk stages sequentially
        all_results = []
        result_index = 0
        
        for i, stage in enumerate(stages):
            log_debug(f"   Running stage {i+1}/{len(stages)}: {stage['stage_name']}")
            
            # Run this stage
            stage_result = await optimizer.run_stage(
                job_id=job_id,
                stage_config=stage,
                symbol=request.symbol,
                strategy=request.strategy,
                locked_params=locked_params.copy(),
                start_from_test=0
            )
            
            # Lock best value for next stage
            if stage_result["best_value"] is not None:
                locked_params[stage["parameter"]] = stage_result["best_value"]
                log_debug(f"   Stage {i+1} complete: {stage['parameter']} = {stage_result['best_value']}")
            
            # Collect results
            stage_results_batch = []
            for result in stage_result["results"]:
                param_value = result.get(stage["parameter"])
                
                # Build full params
                full_params = locked_params.copy()
                full_params[stage['parameter']] = param_value
                
                # Sort trades
                trades = result.get("trades", [])
                if trades:
                    trades.sort(key=lambda t: t.get('entry_time', ''), reverse=True)
                
                result_data = {
                    "params": full_params,
                    "metrics": result["metrics"],
                    "trades": trades
                }
                
                all_results.append(result_data)
                stage_results_batch.append(result_data)
            
            # Save to database
            if stage_results_batch:
                job_manager.save_results_batch(job_id, stage_results_batch, result_index)
                result_index += len(stage_results_batch)
                log_debug(f"   Saved {len(stage_results_batch)} results (total: {result_index})")
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Sort by Sharpe ratio
        all_results.sort(key=lambda x: x['metrics'].get('sharpe_ratio', -float('inf')), reverse=True)
        
        # Get best combination (from final stage with all optimized params)
        best_combination = locked_params if all_results else {}
        
        # Mark job as completed
        job_manager.mark_completed(job_id, {
            "best_combination": best_combination,
            "total_tests": len(all_results),
            "execution_time_seconds": execution_time
        })
        
        log_debug(f"✅ Risk optimization complete! Tested {len(all_results)} combinations in {execution_time:.1f}s")
        log_debug(f"   Best combination: {best_combination}")
        
        return RiskOptimizationResponse(
            results=all_results,  # Return ALL results for client-side pagination
            best_combination=best_combination,
            total_tests=len(all_results),
            execution_time_seconds=execution_time
        )
        
    except ValueError as e:
        log_debug(f"❌ Risk optimization error: {e}")
        job_manager.save_state(job_id, {"status": "FAILED", "error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        log_debug(f"❌ Risk optimization error: {str(e)}")
        log_debug(f"Traceback:\n{traceback.format_exc()}")
        job_manager.save_state(job_id, {"status": "FAILED", "error": str(e)})
        raise HTTPException(status_code=500, detail="An unexpected error occurred during risk optimization.")
