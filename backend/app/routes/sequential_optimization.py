"""
API Routes for Sequential Optimization

Provides endpoints for:
- Starting sequential optimization
- Monitoring progress via WebSocket
- Controlling optimization (pause, resume, skip)
- Recovering from checkpoints
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

from app.services.sequential_optimizer import SequentialOptimizer
from app.services.websocket_manager import ws_manager
from app.schemas.indicator_params import TIMEFRAME_OPTIONS


router = APIRouter(prefix="/api/optimize/sequential", tags=["sequential-optimization"])
optimizer = SequentialOptimizer()


# Request/Response Models
class StartOptimizationRequest(BaseModel):
    symbol: str
    strategy: str
    custom_ranges: Optional[Dict[str, Any]] = None  # User can override default ranges


class TimeframeOptimizationRequest(BaseModel):
    """Request model for timeframe optimization only"""
    symbol: str
    strategy: str
    fee: Optional[float] = 0.00075  # Default 0.075% (Binance standard)
    slippage: Optional[float] = 0.0005  # Default 0.05%


class TimeframeOptimizationResponse(BaseModel):
    """Response for timeframe optimization"""
    best_timeframe: str
    best_pnl: float
    all_results: List[Dict[str, Any]]


class OptimizationJobResponse(BaseModel):
    job_id: str
    symbol: str
    strategy: str
    total_stages: int
    estimated_tests: int
    status: str
    created_at: str


class CheckpointStateResponse(BaseModel):
    job_id: str
    symbol: str
    strategy: str
    current_stage: int
    total_stages: int
    tests_completed: int
    total_tests_in_stage: int
    best_result: Optional[Dict[str, Any]]
    locked_params: Dict[str, Any]
    timestamp: str


# Endpoints

@router.post("/timeframe", response_model=TimeframeOptimizationResponse)
async def optimize_timeframe(request: TimeframeOptimizationRequest):
    """
    Run a quick optimization just for timeframe stage.
    Returns the best timeframe based on PnL.
    """
    # Create a temporary job ID for this isolated run
    job_id = f"timeframe_opt_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Manually construct stage config for timeframe
    stage_config = {
        "stage_num": 1,
        "stage_name": "Timeframe",
        "parameter": "timeframe",
        "values": TIMEFRAME_OPTIONS,
        "locked_params": {},
        "description": "Optimize trading timeframe"
    }
    
    try:
        # Prepare config params
        config_params = {
            'fee': request.fee,
            'slippage': request.slippage
        }
        
        # Run timeframe stage
        result = await optimizer.run_stage(
            job_id=job_id,
            stage_config=stage_config,
            symbol=request.symbol,
            strategy=request.strategy,
            locked_params=config_params,
            start_from_test=0
        )
        
        # Cleanup temporary checkpoint
        optimizer.delete_checkpoint(job_id)
        
        return TimeframeOptimizationResponse(
            best_timeframe=result["best_value"],
            best_pnl=result["best_result"]["metrics"]["total_pnl"],
            all_results=result["results"]
        )
        
    except Exception as e:
        # Ensure cleanup even on error
        optimizer.delete_checkpoint(job_id)
        raise HTTPException(status_code=500, detail=f"Timeframe optimization failed: {str(e)}")


@router.post("/start", response_model=OptimizationJobResponse)
async def start_sequential_optimization(request: StartOptimizationRequest):
    """
    Start a new sequential optimization job.
    
    Returns job_id and estimated test count.
    Client should connect to WebSocket for real-time updates.
    """
    # Generate unique job ID
    job_id = f"seq_opt_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Generate stages
    try:
        stages = optimizer.generate_stages(request.strategy, request.symbol)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Calculate estimated tests
    from app.schemas.indicator_params import get_indicator_schema, estimate_total_tests
    indicator_schema = get_indicator_schema(request.strategy)
    estimated_tests = estimate_total_tests(indicator_schema)
    
    # Create initial checkpoint
    initial_state = {
        "job_id": job_id,
        "symbol": request.strategy,
        "strategy": request.strategy,
        "current_stage": 0,
        "total_stages": len(stages),
        "tests_completed": 0,
        "total_tests_in_stage": 0,
        "completed_tests": [],
        "best_result": None,
        "locked_params": {},
        "status": "created"
    }
    optimizer.create_checkpoint(job_id, initial_state)
    
    return OptimizationJobResponse(
        job_id=job_id,
        symbol=request.symbol,
        strategy=request.strategy,
        total_stages=len(stages),
        estimated_tests=estimated_tests,
        status="created",
        created_at=datetime.utcnow().isoformat()
    )


@router.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time optimization updates.
    
    Clients connect here to receive:
    - test_complete events
    - stage_complete events
    - progress_update events
    - error events
    - state_sync events (on reconnect)
    """
    await ws_manager.connect(websocket, job_id)
    
    try:
        # Send current state on connection (for reconnects)
        checkpoint = optimizer.load_checkpoint(job_id)
        if checkpoint:
            await ws_manager.broadcast_reconnect_state(job_id, checkpoint)
        
        # Keep connection alive and listen for client messages
        while True:
            data = await websocket.receive_text()
            # Client can send ping to keep alive
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, job_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await ws_manager.disconnect(websocket, job_id)


@router.get("/checkpoint/{job_id}", response_model=CheckpointStateResponse)
async def get_checkpoint(job_id: str):
    """
    Get current checkpoint state for a job.
    
    Used for:
    - Checking if job exists
    - Getting current progress
    - Resuming after disconnect
    """
    checkpoint = optimizer.load_checkpoint(job_id)
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail=f"No checkpoint found for job {job_id}")
    
    return CheckpointStateResponse(**checkpoint)


@router.post("/recover/{job_id}")
async def recover_from_checkpoint(job_id: str):
    """
    Resume optimization from last checkpoint.
    
    Used when:
    - Power failure
    - Server restart
    - Network disconnection
    """
    checkpoint = optimizer.load_checkpoint(job_id)
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail=f"No checkpoint found for job {job_id}")
    
    if checkpoint.get("status") != "in_progress":
        raise HTTPException(
            status_code=400,
            detail=f"Job status is '{checkpoint.get('status')}', cannot resume"
        )
    
    # Resume optimization (this would be handled by background task in real implementation)
    return {
        "message": "Optimization resumed from checkpoint",
        "job_id": job_id,
        "resume_from_stage": checkpoint["current_stage"],
        "resume_from_test": checkpoint["tests_completed"]
    }


@router.get("/incomplete")
async def list_incomplete_jobs():
    """
    List all incomplete optimization jobs.
    
    Used on app startup to detect crashed jobs.
    """
    incomplete = optimizer.find_incomplete_jobs()
    return {
        "count": len(incomplete),
        "jobs": incomplete
    }


@router.post("/pause/{job_id}")
async def pause_optimization(job_id: str):
    """
    Pause current optimization.
    
    Note: Current test will complete before pausing.
    """
    checkpoint = optimizer.load_checkpoint(job_id)
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Update status to paused
    checkpoint["status"] = "paused"
    optimizer.create_checkpoint(job_id, checkpoint)
    
    await ws_manager.broadcast_progress_update(
        job_id=job_id,
        current_stage=checkpoint["current_stage"],
        total_stages=checkpoint["total_stages"],
        overall_progress=0,  # Calculate properly
        status="paused"
    )
    
    return {"message": "Optimization paused", "job_id": job_id}


@router.post("/resume/{job_id}")
async def resume_optimization(job_id: str):
    """
    Resume paused optimization.
    """
    checkpoint = optimizer.load_checkpoint(job_id)
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if checkpoint.get("status") != "paused":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not paused (status: {checkpoint.get('status')})"
        )
    
    # Update status to running
    checkpoint["status"] = "in_progress"
    optimizer.create_checkpoint(job_id, checkpoint)
    
    await ws_manager.broadcast_progress_update(
        job_id=job_id,
        current_stage=checkpoint["current_stage"],
        total_stages=checkpoint["total_stages"],
        overall_progress=0,  # Calculate properly
        status="running"
    )
    
    return {"message": "Optimization resumed", "job_id": job_id}


@router.post("/skip/{job_id}/stage/{stage_num}")
async def skip_stage(job_id: str, stage_num: int, default_value: Any):
    """
    Skip a stage and use default value.
    
    Useful when user wants to skip optimization of a specific parameter.
    """
    checkpoint = optimizer.load_checkpoint(job_id)
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Mark stage as skipped and set default value
    # This would be implemented in the actual optimization loop
    
    return {
        "message": f"Stage {stage_num} skipped",
        "job_id": job_id,
        "default_value": default_value
    }


@router.delete("/cancel/{job_id}")
async def cancel_optimization(job_id: str):
    """
    Cancel optimization and delete checkpoint.
    """
    checkpoint = optimizer.load_checkpoint(job_id)
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Delete checkpoint
    optimizer.delete_checkpoint(job_id)
    
    await ws_manager.broadcast_error(
        job_id=job_id,
        error_message="Optimization cancelled by user"
    )
    
    return {"message": "Optimization cancelled", "job_id": job_id}
