"""
Simplified Parameter Optimization API
No WebSocket, returns complete results when optimization finishes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import os
import json

from app.services.sequential_optimizer import SequentialOptimizer
from app.schemas.indicator_params import get_indicator_schema

router = APIRouter()
optimizer = SequentialOptimizer()

PARAM_ALIASES = {
    'rsi': {'period': 'length', 'rsi_period': 'length'},
    'sma': {'period': 'length'},
    'ema': {'period': 'length'},
    'bbands': {'period': 'length', 'bb_period': 'length', 'std': 'std', 'bb_std': 'std'},
}

def log_debug(message: str):
    """Helper to log to file and console simultaneously"""
    print(message)
    try:
        # Determine path to backend/full_execution_log.txt
        # __file__ is app/routes/parameter_optimization.py
        # We want to go up to backend/
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_path = os.path.join(base_dir, "full_execution_log.txt")
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    except Exception as e:
        print(f" Failed to write to log file: {e}")


class ParameterOptimizationRequest(BaseModel):
    """Request model for parameter optimization"""
    symbol: str
    strategy: str
    timeframe: str
    custom_ranges: Optional[Dict[str, Any]] = None
    strategy_params: Optional[Dict[str, Any]] = None
    fee: Optional[float] = 0.00075  # Default 0.075% (Binance standard)
    slippage: Optional[float] = 0.0005  # Default 0.05%


class ParameterCombinationResult(BaseModel):
    """Single parameter combination result"""
    params: Dict[str, Any]
    metrics: Dict[str, Any]  # Changed from float to Any to handle strings/objects
    trades: Optional[List[Dict[str, Any]]] = None  # Trade details for this combination


class ParameterOptimizationResponse(BaseModel):
    """Response model for parameter optimization"""
    results: List[ParameterCombinationResult]
    best_combination: Dict[str, Any]
    total_tests: int
    execution_time_seconds: float


@router.post("/api/optimize/parameters", response_model=ParameterOptimizationResponse)
async def optimize_parameters(request: ParameterOptimizationRequest):
    """
    Run parameter optimization and return complete results with persistence.
    
    This endpoint runs all optimization stages sequentially and returns
    the complete results when finished. Results are saved to SQLite database.
    
    Args:
        request: Optimization configuration
        
    Returns:
        Complete optimization results with all tested combinations
    """
    from app.services.job_manager import JobManager
    
    start_time = datetime.now()
    log_debug(f" REQUEST RECEIVED: {request.symbol} {request.strategy} {request.timeframe}")
    log_debug(f" Custom Ranges: {request.custom_ranges}")
    log_debug(f" Strategy Params: {request.strategy_params}")
    log_debug(f" Fixed Timeframe: {request.timeframe}")

    # Initialize JobManager and create job for persistence
    job_manager = JobManager()
    job_id = job_manager.create_job({
        "type": "sequential_parameter_optimization",
        "symbol": request.symbol,
        "strategy": request.strategy,
        "timeframe": request.timeframe,
        "custom_ranges": request.custom_ranges,
        "strategy_params": request.strategy_params
    })
    log_debug(f" Created job: {job_id}")

    # Build default parameters for the strategy to ensure incomplete stages have values
    strategy_defaults = {}
    schema = get_indicator_schema(request.strategy)
    
    # Resolve aliases helper
    aliases = PARAM_ALIASES.get(request.strategy.lower(), {})
    
    if schema:
        for param_name, param_schema in schema.parameters.items():
            # Apply alias if exists (e.g. period -> length)
            final_name = aliases.get(param_name, param_name)
            strategy_defaults[final_name] = param_schema.default
            
    # CRITICAL: Override defaults with user provided fixed parameters
    if request.strategy_params:
        # Normalize keys using aliases as well
        for key, value in request.strategy_params.items():
            final_key = aliases.get(key, key)
            strategy_defaults[final_key] = value
            
    # Add fixed timeframe to defaults if present
    if request.timeframe:
        strategy_defaults['timeframe'] = request.timeframe

    log_debug(f" Strategy Defaults (Base): {strategy_defaults}")

    try:
        optimizer = SequentialOptimizer()
        
        # Generate optimization stages for INDICATOR PARAMETERS ONLY
        # Risk parameters (stop_loss, stop_gain) should use /api/optimize/risk instead
        stages = optimizer.generate_stages(
            strategy=request.strategy,
            symbol=request.symbol,
            fixed_timeframe=request.timeframe,  # Lock timeframe to user selection
            custom_ranges=request.custom_ranges,
            include_risk=False  # Always exclude risk - use /api/optimize/risk for that
        )
        
        # Extract all optimization parameter names from stages
        # This ensures consistent params dict structure across all stages for deduplication
        optimization_params = {stage['parameter'] for stage in stages}
        log_debug(f" Optimization parameters across all stages: {optimization_params}")
        
        # Run all stages sequentially
        all_results = []
        
        # CRITICAL FIX: Start with strategy defaults (includes indicator params like fast, slow, signal)
        # Then override with fixed optimization params (timeframe, fee, slippage)
        # This ensures indicator parameters are passed to every backtest
        locked_params = strategy_defaults.copy()
        locked_params.update({
            "timeframe": request.timeframe,
            "fee": request.fee,
            "slippage": request.slippage
        })
        result_index = 0  # Track global result index for database
        
        for i, stage in enumerate(stages):
            log_debug(f" Running stage {i+1}/{len(stages)}: {stage['stage_name']}")
            log_debug(f" Locked params before stage: {locked_params}")
            
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
                log_debug(f" Stage {i+1} complete: {stage['parameter']} = {stage_result['best_value']}")
            
            # DEBUG: Log stage_result structure
            log_debug(f" DEBUG: stage_result keys: {stage_result.keys()}")
            log_debug(f" DEBUG: stage['parameter']: {stage['parameter']}")
            log_debug(f" DEBUG: Number of results: {len(stage_result['results'])}")
            
            # Collect all test results from this stage
            stage_results_batch = []
            for idx, result in enumerate(stage_result["results"]):
                # Extract the actual parameter value
                param_value = result.get(stage["parameter"])
                
                # Start with strategy defaults
                full_params = strategy_defaults.copy()
                
                # Initialize all optimization parameters with None to ensure consistent structure
                # This is critical for deduplication to work across stages
                for opt_param in optimization_params:
                    if opt_param not in full_params:
                        full_params[opt_param] = None
                
                # Apply locked params from previous stages
                full_params.update(locked_params)
                
                # Set the current test parameter value
                full_params[stage['parameter']] = param_value
                
                # Sort trades by entry_time (descending - newest first)
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
            
            # Save this stage's results to database in batch
            if stage_results_batch:
                job_manager.save_results_batch(job_id, stage_results_batch, result_index)
                result_index += len(stage_results_batch)
                log_debug(f" Saved {len(stage_results_batch)} results to database (total: {result_index})")
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        
        # Deduplicate results based on parameters
        # Identical configurations might occur if a subsequent stage re-tests the winning parameter from a previous stage
        seen_params = set()
        unique_results = []
        for res in all_results:
            try:
                # Create a hashable representation of params
                # Sort keys to ensure consistent ordering
                # Convert values to string to handle 0 vs 0.0 consistency if needed, 
                # but standard json dump is usually sufficient for exact matches
                param_key = json.dumps(res['params'], sort_keys=True)
                
                if param_key not in seen_params:
                    seen_params.add(param_key)
                    unique_results.append(res)
            except Exception as e:
                # Fallback in case of serialization error, just keep the result
                log_debug(f"Warning: Failed to serialize params for deduplication: {e}")
                unique_results.append(res)
        
        all_results = unique_results

        # Sort results by Sharpe ratio (descending)
        all_results.sort(key=lambda x: x['metrics'].get('sharpe_ratio', -float('inf')), reverse=True)

        # Select top N results (return all for now, frontend can paginate)
        top_results = all_results  # Return ALL results for client-side pagination

        # CRITICAL FIX: Find the best result that has ALL optimized parameters (from final stage)
        # locked_params contains all the optimized values after all stages complete
        final_stage_results = []
        for result in all_results:
            # Check if this result has all the locked parameters (meaning it's from the final stage)
            has_all_locked = all(
                result['params'].get(param_name) == param_value 
                for param_name, param_value in locked_params.items()
            )
            if has_all_locked:
                final_stage_results.append(result)
        
        # Use the best result from final stage if available, otherwise fall back to global best
        if final_stage_results:
            best_combination = final_stage_results[0]['params']
            log_debug(f" Using best result from FINAL STAGE with all optimized params: {best_combination}")
        else:
            best_combination = all_results[0]['params'] if all_results else {}
            log_debug(f"⚠️ No final stage results found, using global best: {best_combination}")
        
        # Mark job as completed
        job_manager.mark_completed(job_id, {
            "best_combination": best_combination,
            "total_tests": len(all_results),
            "execution_time_seconds": execution_time
        })
        
        log_debug(f" Optimization complete! Tested {len(all_results)} combinations in {execution_time:.1f}s")
        log_debug(f" Job {job_id} completed and saved to database")
        
        # Use final_stage_results[0] for debug logging if available
        debug_result = final_stage_results[0] if final_stage_results else (top_results[0] if top_results else None)
        if debug_result:
            trades_in_response = len(debug_result.get("trades", [])) if debug_result.get("trades") else 0
            log_debug(f" DEBUG: Best result has {trades_in_response} trades")
            log_debug(f" DEBUG: Best Result Params: {debug_result['params']}")
            if trades_in_response > 0:
                log_debug(f" DEBUG: Best Result First Trade: {debug_result['trades'][0]}")

        return ParameterOptimizationResponse(
            results=top_results,
            best_combination=best_combination,
            total_tests=len(all_results),
            execution_time_seconds=execution_time
        )
        
    except ValueError as e:
        log_debug(f" Optimization error: {e}")
        job_manager.save_state(job_id, {"status": "FAILED", "error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        log_debug(f" Optimization error: {str(e)}")
        log_debug(f"Traceback:\n{traceback.format_exc()}")
        job_manager.save_state(job_id, {"status": "FAILED", "error": str(e)})
        raise HTTPException(status_code=500, detail="An unexpected error occurred during optimization.")


@router.get("/api/optimize/parameters/history")
async def get_optimization_history():
    """
    Get list of all parameter optimization jobs.
    
    Returns:
        List of optimization job summaries with metadata
    """
    from app.services.job_manager import JobManager
    
    job_manager = JobManager()
    jobs = job_manager.list_jobs()
    
    # Filter only sequential parameter optimization jobs
    param_opt_jobs = [
        job for job in jobs 
        if job.get('config', {}).get('type') == 'sequential_parameter_optimization'
    ]
    
    return {
        "jobs": param_opt_jobs,
        "total": len(param_opt_jobs)
    }


@router.get("/api/optimize/parameters/history/{job_id}")
async def get_optimization_job(job_id: str, page: int = 1, limit: int = 50):
    """
    Get detailed results for a specific optimization job.
    
    Args:
        job_id: Job identifier
        page: Page number (1-indexed)
        limit: Results per page
        
    Returns:
        Job details with paginated results
    """
    from app.services.job_manager import JobManager
    
    job_manager = JobManager()
    
    # Load job metadata
    job_state = job_manager.load_state(job_id)
    if not job_state:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Get paginated results from database
    results_data = job_manager.get_results(job_id, page=page, limit=limit)
    
    return {
        "job_id": job_id,
        "status": job_state.get("status"),
        "config": job_state.get("config"),
        "created_at": job_state.get("created_at"),
        "updated_at": job_state.get("updated_at"),
        "results": results_data["results"],
        "pagination": results_data["pagination"]
    }

