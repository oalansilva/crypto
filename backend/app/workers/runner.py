# file: backend/app/workers/runner.py
import asyncio
from uuid import UUID
from typing import Dict
from app.services.backtest_service import BacktestService
from app.services.run_repository import RunRepository
from app.services.job_manager import JobManager
from app.database import SessionLocal

# Global registry of running jobs
running_jobs: Dict[str, asyncio.Task] = {}

async def execute_backtest(run_id: UUID, config: dict, resume: bool = False):
    """Background worker to execute backtest"""
    # Create a new DB session for this thread
    db = SessionLocal()
    repo = RunRepository(db)
    service = BacktestService()
    job_manager = JobManager()
    
    # Register job in JobManager if new
    job_id = str(run_id)
    if not resume:
        job_manager.create_job(config)
        # Verify it persisted? job_manager.active_jobs[job_id]...
    
    try:
        # Update status
        repo.update_run_status(run_id, "RUNNING")
        
        # Execute backtest (blocking operation)
        loop = asyncio.get_event_loop()
        
        from app.globals import RUN_PROGRESS
        
        def progress_updater(msg, progress=None):
            run_id_str = str(run_id)
            
            # Update global store
            if run_id_str not in RUN_PROGRESS:
                RUN_PROGRESS[run_id_str] = {'progress': 0, 'step': ''}
            
            RUN_PROGRESS[run_id_str]['step'] = msg
            if progress is not None:
                RUN_PROGRESS[run_id_str]['progress'] = progress
            
            # Optional: Persist to DB occasionally or just error check
            # For now we rely on memory for speed

        # Pass job_id and resume flag
        result = await loop.run_in_executor(None, lambda: service.run_backtest(config, progress_updater, job_id=job_id, resume=resume))
        
        # Extract metrics summary
        # Extract metrics summary
        metrics_summary = {}
        if 'optimization_results' in result:
             # For optimization, we can use the best result or just a summary
             if result.get('best_result'):
                 metrics_summary['best_result'] = {
                     'total_return_pct': result['best_result']['metrics']['total_pnl_pct'],
                     'win_rate': result['best_result']['metrics']['win_rate'],
                     # Optimization metrics might differ slightly from standard
                     'num_trades': result['best_result']['metrics']['total_trades']
                 }
        elif 'results' in result:
             for strategy_name, strategy_result in result['results'].items():
                 # Handle potential missing keys if error occurred
                 if 'metrics' not in strategy_result:
                     continue
                     
                 metrics = strategy_result['metrics']
                 metrics_summary[strategy_name] = {
                    'total_return_pct': metrics.get('total_pnl_pct', 0),
                    'max_drawdown_pct': metrics.get('max_drawdown', 0),
                    'sharpe': metrics.get('sharpe', 0),
                    'num_trades': metrics.get('total_trades', 0),
                    'win_rate': metrics.get('win_rate', 0)
                }
        
        # Save result
        repo.update_progress(run_id, "Saving results...")
        repo.save_result(run_id, result, metrics_summary)
        
        # Update status
        # Check actual status in case it was PAUSED
        final_run_state = job_manager.load_state(job_id)
        if final_run_state and final_run_state.get('status') == 'PAUSED':
             repo.update_run_status(run_id, "PAUSED")
             print(f"Backtest {run_id} PAUSED.")
        else:
             repo.update_run_status(run_id, "DONE")
        
    except Exception as e:
        error_msg = str(e)
        print(f"Backtest {run_id} failed: {error_msg}")
        repo.update_run_status(run_id, "FAILED", error_msg)
    
    finally:
        # Close DB session
        db.close()
        
        # Remove from running jobs
        if str(run_id) in running_jobs:
            del running_jobs[str(run_id)]

def start_backtest_job(run_id: UUID, config: dict, resume: bool = False):
    """Start backtest in background"""
    run_id_str = str(run_id)
    
    # Prevent duplicate execution
    if run_id_str in running_jobs and not running_jobs[run_id_str].done():
        print(f"Job {run_id_str} is already running. Considering request as idempotent.")
        return running_jobs[run_id_str]

    task = asyncio.create_task(execute_backtest(run_id, config, resume))
    running_jobs[run_id_str] = task
    return task
