import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime
from typing import Dict, Optional, List, Any
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class JobManager:
    _instance = None
    _lock = threading.Lock()
    
    # Path to store job files
    DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'jobs'

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
        self.active_jobs: Dict[str, Dict] = {}
        # In-memory flags for signaling pause
        self.pause_signals: Dict[str, bool] = {}
        self._init_database()
        logger.info(f"JobManager initialized. Data dir: {self.DATA_DIR}, DB: {self.db_path}")

    def create_job(self, config: Dict) -> str:
        """Create a new job and return its ID"""
        job_id = str(uuid.uuid4())
        
        job_state = {
            "job_id": job_id,
            "status": "RUNNING",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "config": config,
            "progress": {
                "current_iteration": 0,
                "total_iterations": 0,
                "strategy_index": 0
            },
            "results": []
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
                with open(file_path, 'w') as f:
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
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load job state for {job_id}: {e}")
            return None

    def list_jobs(self) -> List[Dict]:
        """List all jobs found in data directory"""
        jobs = []
        for file_path in self.DATA_DIR.glob("job_*.json"):
            try:
                with open(file_path, 'r') as f:
                    job = json.load(f)
                    # Strip results for lighter listing
                    if 'results' in job:
                        job['result_count'] = len(job['results'])
                        del job['results']
                    jobs.append(job)
            except json.JSONDecodeError as e:
                logger.error(f"Skipping corrupted job file {file_path}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error reading job file {file_path}: {e}")
                continue
                
        # Sort by updated_at desc
        jobs.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return jobs

    def signal_pause(self, job_id: str):
        """Signal a job to pause"""
        logger.info(f"Signaling pause for job {job_id}")
        self.pause_signals[job_id] = True
        
        # Update state on disk to indicate intent (optional, mainly status update)
        state = self.load_state(job_id)
        if state:
            state['status'] = 'PAUSING'
            self.save_state(job_id, state)

    def should_pause(self, job_id: str) -> bool:
        """Check if job has been signaled to pause"""
        return self.pause_signals.get(job_id, False)

    def mark_paused(self, job_id: str, state: Dict):
        """Mark job as fully paused and save final state"""
        state['status'] = 'PAUSED'
        self.save_state(job_id, state)
        # Clear signal
        if job_id in self.pause_signals:
            del self.pause_signals[job_id]
            
    def mark_completed(self, job_id: str, final_results: Any):
        """Mark job as completed"""
        state = self.load_state(job_id) or {}
        state['status'] = 'COMPLETED'
        state['final_results'] = final_results # Optionally store full final report
        self.save_state(job_id, state)

    def get_active_job(self) -> Optional[Dict]:
        """Find the most recently updated RUNNING or PAUSED job"""
        jobs = self.list_jobs()
        for job in jobs:
            if job.get('status') in ['RUNNING', 'PAUSED', 'PAUSING']:
                return job
        return None

    def _init_database(self):
        """Initialize SQLite database with schema for optimization results"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS optimization_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                result_index INTEGER NOT NULL,
                params_json TEXT NOT NULL,
                metrics_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(job_id, result_index)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_job_id ON optimization_results(job_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_job_created ON optimization_results(job_id, created_at DESC)")
        
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.commit()
        conn.close()
        logger.info(f"SQLite database initialized at {self.db_path}")
    
    def save_result(self, job_id: str, result: Dict, index: int):
        """Save a single optimization result to SQLite database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("""
                INSERT OR REPLACE INTO optimization_results 
                (job_id, result_index, params_json, metrics_json)
                VALUES (?, ?, ?, ?)
            """, (
                job_id,
                index,
                json.dumps(result.get('params', {})),
                json.dumps(result.get('metrics', {}))
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to save result {index} for job {job_id}: {e}")
    
    def get_results(self, job_id: str, page: int = 1, limit: int = 50) -> Dict:
        """Get paginated optimization results from SQLite database"""
        offset = (page - 1) * limit
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute("""
                SELECT params_json, metrics_json 
                FROM optimization_results
                WHERE job_id = ?
                ORDER BY result_index
                LIMIT ? OFFSET ?
            """, (job_id, limit, offset))
            
            results = []
            for row in cursor:
                results.append({
                    'params': json.loads(row[0]),
                    'metrics': json.loads(row[1])
                })
            
            # Get total count
            total = conn.execute(
                "SELECT COUNT(*) FROM optimization_results WHERE job_id = ?",
                (job_id,)
            ).fetchone()[0]
            
            conn.close()
            
            return {
                'results': results,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if total > 0 else 0
                }
            }
        except Exception as e:
            logger.error(f"Failed to get results for job {job_id}: {e}")
            # Fallback to reading from old JSON format
            return self._get_results_from_json(job_id, page, limit)
    
    def _get_results_from_json(self, job_id: str, page: int, limit: int) -> Dict:
        """Fallback: Read results from old JSON format for backward compatibility"""
        state = self.load_state(job_id)
        if state and 'results' in state:
            all_results = state['results']
            start = (page - 1) * limit
            end = start + limit
            total = len(all_results)
            
            return {
                'results': all_results[start:end],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if total > 0 else 0
                }
            }
        
        return {
            'results': [],
            'pagination': {'page': page, 'limit': limit, 'total': 0, 'pages': 0}
        }


    def save_results_batch(self, job_id: str, results: List[Dict], start_index: int):
        """Save multiple optimization results in a single transaction for better performance"""
        if not results:
            return
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute('BEGIN TRANSACTION')
            
            batch_data = []
            for i, result in enumerate(results):
                batch_data.append((
                    job_id,
                    start_index + i,
                    json.dumps(result.get('params', {})),
                    json.dumps(result.get('metrics', {}))
                ))
            
            conn.executemany("""
                INSERT OR REPLACE INTO optimization_results 
                (job_id, result_index, params_json, metrics_json)
                VALUES (?, ?, ?, ?)
            """, batch_data)
            
            conn.commit()
            conn.close()
            logger.info(f"Saved batch of {len(results)} results for job {job_id}")
        except Exception as e:
            logger.error(f"Failed to save batch for job {job_id}: {e}")
            if conn:
                conn.rollback()
                conn.close()
