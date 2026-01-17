# file: backend/app/api.py
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from app.schemas.backtest import (
    BacktestRunCreate,
    BacktestRunResponse,
    BacktestStatusResponse,
    BacktestRunListItem,
    PresetResponse
)
from app.services.run_repository import RunRepository
from app.services.preset_service import get_presets
from app.services.job_manager import JobManager
from app.workers.runner import start_backtest_job
from app.database import get_db
from app.services.pandas_ta_inspector import get_all_indicators_metadata

router = APIRouter(prefix="/api")

def get_repository(db: Session = Depends(get_db)) -> RunRepository:
    return RunRepository(db)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "crypto-backtester-api"}

@router.get("/presets", response_model=List[PresetResponse])
async def list_presets():
    """Get predefined backtest presets for Playground"""
    return get_presets()

@router.get("/exchanges/binance/symbols")
async def get_binance_symbols():
    """Get all available USDT trading pairs from Binance."""
    from app.services.exchange_service import ExchangeService
    
    service = ExchangeService()
    symbols = service.fetch_binance_symbols()
    
    return {
        "symbols": symbols,
        "count": len(symbols)
    }




@router.post("/backtest/optimize", response_model=BacktestRunResponse)
async def create_optimization(
    request: BacktestRunCreate,
    repo: RunRepository = Depends(get_repository)
):
    """Create and start a strategy optimization (Grid Search)"""
    if request.mode != "optimize":
        raise HTTPException(400, "Use mode 'optimize' for this endpoint")
    
    # Validation: Ensure ranges are present? Or allow scalar (1 run optimization).
    # Allowed.
    
    # DEBUG: Print request to see what we're receiving
    print(f"DEBUG: Received optimization request:")
    print(f"  timeframe type: {type(request.timeframe)}")
    print(f"  timeframe value: {request.timeframe}")
    
    run_data = request.model_dump()
    run_data["status"] = "PENDING"
    
    try:
        run = repo.create_run(run_data)
        run_id = UUID(run['id'])
        
        # Start background job
        config = request.model_dump()
        start_backtest_job(run_id, config)
        
        return BacktestRunResponse(
            run_id=run_id,
            status="PENDING",
            message="Optimization started"
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(500, f"Error starting optimization: {str(e)}")

@router.post("/backtest/compare", response_model=BacktestRunResponse)
async def create_compare(
    request: BacktestRunCreate,
    repo: RunRepository = Depends(get_repository)
):
    """Create and start a comparison backtest"""
    if request.mode != "compare":
        raise HTTPException(400, "Use mode 'compare' for this endpoint")
    
    if len(request.strategies) < 2 or len(request.strategies) > 3:
        raise HTTPException(400, "Compare mode requires 2-3 strategies")
    
    run_data = request.model_dump()
    run_data["status"] = "PENDING"
    
    try:
        run = repo.create_run(run_data)
        run_id = UUID(run['id'])
        
        # Start background job
        config = request.model_dump()
        start_backtest_job(run_id, config)
        
        return BacktestRunResponse(
            run_id=run_id,
            status="PENDING",
            message=f"Comparing {len(request.strategies)} strategies"
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(500, f"Error starting compare: {str(e)}")

from app.globals import RUN_PROGRESS

@router.get("/backtest/status/{run_id}", response_model=BacktestStatusResponse)
async def get_status(
    run_id: UUID,
    repo: RunRepository = Depends(get_repository)
):
    """Get backtest execution status"""
    run = repo.get_run(run_id)
    
    if not run:
        raise HTTPException(404, "Run not found")
        
    # Get ephemeral progress if running
    run_id_str = str(run_id)
    progress_info = RUN_PROGRESS.get(run_id_str, {})
    
    return BacktestStatusResponse(
        run_id=run_id,
        status=run['status'],
        created_at=run['created_at'],
        error_message=run.get('error_message'),
        progress=progress_info.get('progress', 0.0),
        current_step=progress_info.get('step')
    )

@router.get("/backtest/result/{run_id}")
async def get_result(
    run_id: UUID,
    repo: RunRepository = Depends(get_repository)
):
    """Get complete backtest result"""
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    
    if run['status'] != 'DONE':
        raise HTTPException(400, f"Run status is {run['status']}, not DONE")
    
    result = repo.get_result(run_id)
    if not result:
        raise HTTPException(404, "Result not found")
    
    return {
        "run_id": run_id,
        "mode": run['mode'],
        "created_at": run['created_at'],
        **result['result_json']
    }
    
@router.post("/backtest/pause/{run_id}")
async def pause_run(
    run_id: UUID,
    repo: RunRepository = Depends(get_repository)
):
    """Signal a running backtest to pause"""
    job_manager = JobManager()
    run_id_str = str(run_id)
    
    # Check if actually running or optimization
    run = repo.get_run(run_id)
    if not run:
         raise HTTPException(404, "Run not found")
         
    if run['status'] not in ['RUNNING', 'PENDING']:
         raise HTTPException(400, f"Cannot pause run with status {run['status']}")
    
    # Signal Pause
    job_manager.signal_pause(run_id_str)
    
    # Optimistically update status to PAUSING
    repo.update_run_status(run_id, "PAUSING")
    
    return {"status": "PAUSING", "message": "Pause signal sent"}

@router.post("/backtest/resume/{run_id}")
async def resume_run(
    run_id: UUID,
    repo: RunRepository = Depends(get_repository)
):
    """Resume a paused backtest"""
    job_manager = JobManager()
    run_id_str = str(run_id)
    
    run = repo.get_run(run_id)
    if not run:
         raise HTTPException(404, "Run not found")

    # Double check job file validity
    state = job_manager.load_state(run_id_str)
    if not state:
         raise HTTPException(404, "Job state file not found on disk")
         
    # Restart worker with resume=True
    config = state['config'] # Use config from saved state to be safe
    
    try:
        start_backtest_job(run_id, config, resume=True)
        return {"status": "RUNNING", "message": "Resuming backtest..."}
    except Exception as e:
        raise HTTPException(500, f"Failed to resume: {e}")

@router.get("/backtest/jobs")
async def list_jobs_manager():
    """List jobs from Job Manager (Disk State)"""
    job_manager = JobManager()
    return job_manager.list_jobs()

@router.get("/backtest/runs", response_model=List[BacktestRunListItem])
async def list_runs(
    limit: int = 50,
    offset: int = 0,
    repo: RunRepository = Depends(get_repository)
):
    """List recent backtest runs"""
    runs = repo.list_runs(limit, offset)
    result = []
    
    for run in runs:
        item = BacktestRunListItem(**run)
        
        # Inject ephemeral progress if running
        if item.status in ['RUNNING', 'PENDING']:
            prog = RUN_PROGRESS.get(str(item.id))
            if prog:
                item.progress = prog.get('progress', 0.0)
                if prog.get('step'):
                    item.message = prog.get('step') # Update message with current step
        
        result.append(item)
        
    return result

@router.delete("/backtest/runs/{run_id}")
async def delete_run(
    run_id: UUID,
    repo: RunRepository = Depends(get_repository)
):
    """Delete a backtest run"""
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    
    repo.delete_run(run_id)
    return {"message": "Run deleted"}

@router.get("/strategies/metadata")
async def get_strategies_metadata():
    """Get metadata for all available pandas-ta indicators + custom strategies"""
    print(" GET /strategies/metadata called")
    try:
        result = get_all_indicators_metadata()
        
        # Add CRUZAMENTOMEDIAS as a custom strategy
        if 'custom' not in result:
            result['custom'] = []
        
        result['custom'].append({
            "id": "cruzamentomedias",
            "name": "CRUZAMENTOMEDIAS",
            "category": "custom",
            "description": "Moving Average Crossover Strategy (EMA + SMA)",
            "params": [
                {
                    "name": "media_curta",
                    "type": "int",
                    "default": 6
                },
                {
                    "name": "media_longa",
                    "type": "int",
                    "default": 38
                },
                {
                    "name": "media_inter",
                    "type": "int",
                    "default": 21
                }
            ]
        })
        
        # Add EMA_RSI_VOLUME as a custom strategy
        result['custom'].append({
            "id": "emarsivolume",
            "name": "EMA 50/200 + RSI + Volume",
            "category": "custom",
            "description": "Most popular BTC strategy: Trend following with EMA 200 filter, EMA 50 entries, and RSI confirmation",
            "params": [
                {
                    "name": "ema_fast",
                    "type": "int",
                    "default": 50
                },
                {
                    "name": "ema_slow",
                    "type": "int",
                    "default": 200
                },
                {
                    "name": "rsi_period",
                    "type": "int",
                    "default": 14
                },
                {
                    "name": "rsi_min",
                    "type": "int",
                    "default": 40
                },
                {
                    "name": "rsi_max",
                    "type": "int",
                    "default": 50
                }
            ]
        })
        
        # Add FIBONACCI_EMA as a custom strategy
        result['custom'].append({
            "id": "fibonacciema",
            "name": "Fibonacci (0.5 / 0.618) + EMA 200",
            "category": "custom",
            "description": "Institutional pullback strategy: Fibonacci retracement levels (0.5 and 0.618) with EMA 200 trend filter",
            "params": [
                {"name": "ema_period", "type": "int", "default": 200},
                {"name": "swing_lookback", "type": "int", "default": 20},
                {"name": "fib_level_1", "type": "float", "default": 0.5},
                {"name": "fib_level_2", "type": "float", "default": 0.618},
                {"name": "level_tolerance", "type": "float", "default": 0.005}
            ]
        })
        
        print(f" Returning {len(result)} categories")
        return result
    except Exception as e:
        print(f" Error: {e}")
        raise HTTPException(500, f"Error getting metadata: {str(e)}")

@router.get("/indicator/{strategy_name}/schema")
async def get_indicator_schema_endpoint(strategy_name: str):
    """Get parameter schema for a specific indicator - dynamically generated from pandas_ta"""
    from app.schemas.dynamic_schema_generator import get_dynamic_indicator_schema
    
    # Generate schema dynamically from pandas_ta
    schema = get_dynamic_indicator_schema(strategy_name)
    
    if not schema:
        raise HTTPException(
            status_code=404, 
            detail=f"Indicator '{strategy_name}' not found in pandas_ta library"
        )
    
    return schema
