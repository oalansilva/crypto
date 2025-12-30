# file: backend/app/services/run_repository.py
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from app.models import BacktestRun, BacktestResult
from datetime import datetime
import json

class RunRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_run(self, data: dict) -> dict:
        """Create a new backtest run"""
        # Data filtering/conversion for model
        # For 'since'/'until' which might be strings in Pydantic but handled as strings in SQLite model
        model_data = data.copy()
        
        # Remove keys that are not in the model but might be in the request (e.g., timeframes)
        if 'timeframes' in model_data:
            model_data.pop('timeframes')
        
        # Serialize timeframe if it's a list (for SQLite compatibility)
        if isinstance(model_data.get('timeframe'), list):
            model_data['timeframe'] = json.dumps(model_data['timeframe'])
            
        # Ensure strategies is list (API sends list) or JSON dump?
        # Our custom JSONType handles list -> json string automatically.
        
        # Ensure UUID
        if 'id' not in model_data:
            import uuid
            model_data['id'] = uuid.uuid4()
            
        # Ensure dates are iso strings for SQLite if passed as datetime objects
        if isinstance(model_data.get('since'), datetime):
            model_data['since'] = model_data['since'].isoformat()
        if isinstance(model_data.get('until'), datetime):
             model_data['until'] = model_data['until'].isoformat()
        
        model_data['created_at'] = datetime.utcnow()
            
        run = BacktestRun(**model_data)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return {
            "id": str(run.id),
            "status": run.status,
            "created_at": run.created_at
        }
    
    def _parse_timeframe(self, tf_value):
        """Helper to parse timeframe that might be JSON list"""
        if not tf_value:
            return tf_value
        try:
            # If it starts with [, it might be a JSON list
            if isinstance(tf_value, str) and tf_value.startswith('['):
                return json.loads(tf_value)
        except:
            pass
        return tf_value
    
    def get_run(self, run_id: UUID) -> Optional[dict]:
        """Get run by ID"""
        run = self.db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
        if not run:
            return None
        
        return {
            "id": str(run.id),
            "status": run.status,
            "mode": run.mode,
            "created_at": run.created_at,
            "error_message": run.error_message,
            "symbol": run.symbol,
            "timeframe": self._parse_timeframe(run.timeframe),
            "strategies": run.strategies
        }
    
    
    def update_progress(self, run_id: UUID, message: str):
        """Update run progress message while keeping RUNNING status"""
        self.update_run_status(run_id, "RUNNING", message)

    def update_run_status(self, run_id: UUID, status: str, error_message: Optional[str] = None):
        """Update run status"""
        run = self.db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
        if run:
            run.status = status
            # Only update error_message if provided (allows clearing it if None passed? No, usually allows setting it)
            # If status is RUNNING, we use error_message as progress message
            if error_message is not None:
                run.error_message = error_message
            self.db.commit()
    
    def save_result(self, run_id: UUID, result_json: dict, metrics_summary: dict):
        """Save backtest result"""
        existing = self.db.query(BacktestResult).filter(BacktestResult.run_id == run_id).first()
        
        if existing:
            existing.result_json = result_json
            existing.metrics_summary = metrics_summary
            existing.updated_at = datetime.utcnow()
        else:
            result = BacktestResult(
                run_id=run_id,
                result_json=result_json,
                metrics_summary=metrics_summary,
                updated_at=datetime.utcnow()
            )
            self.db.add(result)
            
        self.db.commit()
    
    def get_result(self, run_id: UUID) -> Optional[dict]:
        """Get result by run_id"""
        result = self.db.query(BacktestResult).filter(BacktestResult.run_id == run_id).first()
        if not result:
            return None
            
        return {
            "run_id": str(result.run_id),
            "result_json": result.result_json,
            "metrics_summary": result.metrics_summary,
            "updated_at": result.updated_at
        }
    
    def list_runs(self, limit: int = 50, offset: int = 0) -> list[dict]:
        """List recent runs"""
        runs = self.db.query(BacktestRun)\
            .order_by(BacktestRun.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
            
        return [{
            "id": run.id,
            "created_at": run.created_at,
            "status": run.status,
            "mode": run.mode,
            "symbol": run.symbol,
            "timeframe": self._parse_timeframe(run.timeframe),
            "strategies": run.strategies,
            "message": run.error_message # Return progress or error message
        } for run in runs]
    
    def delete_run(self, run_id: UUID):
        """Delete run"""
        self.db.query(BacktestRun).filter(BacktestRun.id == run_id).delete()
        self.db.query(BacktestResult).filter(BacktestResult.run_id == run_id).delete()
        self.db.commit()
