import json
import threading
import uuid
from datetime import datetime
from typing import Dict, Optional, List, Any
import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import DB_URL
from app.models import Base, OptimizationResult

# Configure logging
logger = logging.getLogger(__name__)


class JobManager:
    _instance = None
    _lock = threading.Lock()

    # Path to store job files
    DATA_DIR = Path(__file__).parent.parent.parent / "data" / "jobs"

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(JobManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.db_path = self.DATA_DIR / "results.db"
        self.engine = create_engine(DB_URL, pool_pre_ping=True)
        self._session_factory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.active_jobs: Dict[str, Dict] = {}
        # In-memory flags for signaling pause
        self.pause_signals: Dict[str, bool] = {}
        self._init_database()
        logger.info(f"JobManager initialized. Data dir: {self.DATA_DIR}, DB URL: {self.engine.url}")

    def create_job(self, config: Dict) -> str:
        """Create a new job and return its ID"""
        job_id = str(uuid.uuid4())

        job_state = {
            "job_id": job_id,
            "status": "RUNNING",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "config": config,
            "progress": {"current_iteration": 0, "total_iterations": 0, "strategy_index": 0},
            "results": [],
        }

        self.save_state(job_id, job_state)
        self.active_jobs[job_id] = job_state
        return job_id

    def save_state(self, job_id: str, state: Dict):
        """Persist job state to disk"""
        state["updated_at"] = datetime.now().isoformat()
        file_path = self.DATA_DIR / f"job_{job_id}.json"

        try:
            # Atomic write pattern could be used, but simple write for now
            # Use lock to prevent race conditions between API threads and background workers
            with self._lock:
                with open(file_path, "w") as f:
                    json.dump(state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save job state for {job_id}: {e}")

    def load_state(self, job_id: str) -> Optional[Dict]:
        """Load job state from disk"""
        file_path = self.DATA_DIR / f"job_{job_id}.json"

        if not file_path.exists():
            return None

        try:
            with self._lock:
                with open(file_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load job state for {job_id}: {e}")
            return None

    def list_jobs(self) -> List[Dict]:
        """List all jobs found in data directory"""
        jobs = []
        for file_path in self.DATA_DIR.glob("job_*.json"):
            try:
                with open(file_path, "r") as f:
                    job = json.load(f)
                    # Strip results for lighter listing
                    if "results" in job:
                        job["result_count"] = len(job["results"])
                        del job["results"]
                    jobs.append(job)
            except json.JSONDecodeError as e:
                logger.error(f"Skipping corrupted job file {file_path}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error reading job file {file_path}: {e}")
                continue

        # Sort by updated_at desc
        jobs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return jobs

    def signal_pause(self, job_id: str):
        """Signal a job to pause"""
        logger.info(f"Signaling pause for job {job_id}")
        self.pause_signals[job_id] = True

        # Update state on disk to indicate intent (optional, mainly status update)
        state = self.load_state(job_id)
        if state:
            state["status"] = "PAUSING"
            self.save_state(job_id, state)

    def should_pause(self, job_id: str) -> bool:
        """Check if job has been signaled to pause"""
        return self.pause_signals.get(job_id, False)

    def mark_paused(self, job_id: str, state: Dict):
        """Mark job as fully paused and save final state"""
        state["status"] = "PAUSED"
        self.save_state(job_id, state)
        # Clear signal
        if job_id in self.pause_signals:
            del self.pause_signals[job_id]

    def mark_completed(self, job_id: str, final_results: Any):
        """Mark job as completed"""
        state = self.load_state(job_id) or {}
        state["status"] = "COMPLETED"
        state["final_results"] = final_results  # Optionally store full final report
        self.save_state(job_id, state)

    def get_active_job(self) -> Optional[Dict]:
        """Find the most recently updated RUNNING or PAUSED job"""
        jobs = self.list_jobs()
        for job in jobs:
            if job.get("status") in ["RUNNING", "PAUSED", "PAUSING"]:
                return job
        return None

    def _init_database(self):
        """Initialize optimization results table in the main app database."""
        Base.metadata.create_all(bind=self.engine, tables=[OptimizationResult.__table__])
        logger.info("Optimization results table initialized on %s", self.engine.url)

    def save_result(self, job_id: str, result: Dict, index: int):
        """Save a single optimization result to the main database."""
        try:
            with self._session_factory() as db:
                row = (
                    db.query(OptimizationResult)
                    .filter(
                        OptimizationResult.job_id == job_id,
                        OptimizationResult.result_index == index,
                    )
                    .first()
                )
                if row is None:
                    row = OptimizationResult(job_id=job_id, result_index=index)
                    db.add(row)
                row.params_json = result.get("params", {})
                row.metrics_json = result.get("metrics", {})
                db.commit()
        except Exception as e:
            logger.error(f"Failed to save result {index} for job {job_id}: {e}")

    def get_results(self, job_id: str, page: int = 1, limit: int = 50) -> Dict:
        """Get paginated optimization results from the main database."""
        offset = (page - 1) * limit

        try:
            with self._session_factory() as db:
                rows = (
                    db.query(OptimizationResult)
                    .filter(OptimizationResult.job_id == job_id)
                    .order_by(OptimizationResult.result_index.asc())
                    .offset(offset)
                    .limit(limit)
                    .all()
                )
                total = (
                    db.query(OptimizationResult).filter(OptimizationResult.job_id == job_id).count()
                )

            results = [
                {
                    "params": row.params_json or {},
                    "metrics": row.metrics_json or {},
                }
                for row in rows
            ]

            return {
                "results": results,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit if total > 0 else 0,
                },
            }
        except Exception as e:
            logger.error(f"Failed to get results for job {job_id}: {e}")
            # Fallback to reading from old JSON format
            return self._get_results_from_json(job_id, page, limit)

    def _get_results_from_json(self, job_id: str, page: int, limit: int) -> Dict:
        """Fallback: Read results from old JSON format for backward compatibility"""
        state = self.load_state(job_id)
        if state and "results" in state:
            all_results = state["results"]
            start = (page - 1) * limit
            end = start + limit
            total = len(all_results)

            return {
                "results": all_results[start:end],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit if total > 0 else 0,
                },
            }

        return {"results": [], "pagination": {"page": page, "limit": limit, "total": 0, "pages": 0}}

    def save_results_batch(self, job_id: str, results: List[Dict], start_index: int):
        """Save multiple optimization results in a single transaction for better performance"""
        if not results:
            return

        try:
            with self._session_factory() as db:
                indexes = [start_index + i for i in range(len(results))]
                existing_rows = (
                    db.query(OptimizationResult)
                    .filter(
                        OptimizationResult.job_id == job_id,
                        OptimizationResult.result_index.in_(indexes),
                    )
                    .all()
                )
                existing_by_index = {row.result_index: row for row in existing_rows}

                for i, result in enumerate(results):
                    idx = start_index + i
                    row = existing_by_index.get(idx)
                    if row is None:
                        row = OptimizationResult(job_id=job_id, result_index=idx)
                        db.add(row)
                    row.params_json = result.get("params", {})
                    row.metrics_json = result.get("metrics", {})

                db.commit()
            logger.info(f"Saved batch of {len(results)} results for job {job_id}")
        except Exception as e:
            logger.error(f"Failed to save batch for job {job_id}: {e}")
