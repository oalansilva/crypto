"""
WebSocket Manager for Sequential Optimization

Manages WebSocket connections and broadcasts real-time updates during optimization.
Supports multiple concurrent optimization jobs with isolated channels.
"""

from typing import Dict, Set, Any
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime


class WebSocketManager:
    """
    Manages WebSocket connections for real-time optimization updates.
    
    Each optimization job has its own set of connected clients.
    """
    
    def __init__(self):
        # job_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, job_id: str):
        """
        Accept a new WebSocket connection for a job.
        
        Args:
            websocket: The WebSocket connection
            job_id: Optimization job identifier
        """
        await websocket.accept()
        
        async with self._lock:
            if job_id not in self.active_connections:
                self.active_connections[job_id] = set()
            self.active_connections[job_id].add(websocket)
        
        print(f"WebSocket connected for job {job_id}. Total connections: {len(self.active_connections[job_id])}")
    
    async def disconnect(self, websocket: WebSocket, job_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: The WebSocket connection
            job_id: Optimization job identifier
        """
        async with self._lock:
            if job_id in self.active_connections:
                self.active_connections[job_id].discard(websocket)
                
                # Clean up empty job entries
                if not self.active_connections[job_id]:
                    del self.active_connections[job_id]
        
        print(f"WebSocket disconnected for job {job_id}")
    
    async def broadcast_test_complete(
        self,
        job_id: str,
        stage: int,
        test_number: int,
        total_tests: int,
        params: Dict[str, Any],
        metrics: Dict[str, float]
    ):
        """
        Broadcast test completion event to all connected clients.
        
        Args:
            job_id: Optimization job identifier
            stage: Current stage number
            test_number: Test number within stage
            total_tests: Total tests in stage
            params: Test parameters
            metrics: Test results (PnL, win rate, etc.)
        """
        message = {
            "event": "test_complete",
            "timestamp": datetime.utcnow().isoformat(),
            "job_id": job_id,
            "stage": stage,
            "test_number": test_number,
            "total_tests": total_tests,
            "progress": round((test_number / total_tests) * 100, 2),
            "params": params,
            "metrics": metrics
        }
        
        await self._broadcast(job_id, message)
    
    async def broadcast_stage_complete(
        self,
        job_id: str,
        stage: int,
        stage_name: str,
        best_value: Any,
        best_metrics: Dict[str, float],
        all_results: list
    ):
        """
        Broadcast stage completion event.
        
        Args:
            job_id: Optimization job identifier
            stage: Stage number
            stage_name: Stage name
            best_value: Best parameter value found
            best_metrics: Metrics for best value
            all_results: All test results from stage
        """
        message = {
            "event": "stage_complete",
            "timestamp": datetime.utcnow().isoformat(),
            "job_id": job_id,
            "stage": stage,
            "stage_name": stage_name,
            "best_value": best_value,
            "best_metrics": best_metrics,
            "all_results": all_results
        }
        
        await self._broadcast(job_id, message)
    
    async def broadcast_progress_update(
        self,
        job_id: str,
        current_stage: int,
        total_stages: int,
        overall_progress: float,
        status: str = "running"
    ):
        """
        Broadcast overall progress update.
        
        Args:
            job_id: Optimization job identifier
            current_stage: Current stage number
            total_stages: Total number of stages
            overall_progress: Overall progress percentage (0-100)
            status: Current status (running, paused, complete, error)
        """
        message = {
            "event": "progress_update",
            "timestamp": datetime.utcnow().isoformat(),
            "job_id": job_id,
            "current_stage": current_stage,
            "total_stages": total_stages,
            "overall_progress": round(overall_progress, 2),
            "status": status
        }
        
        await self._broadcast(job_id, message)
    
    async def broadcast_error(
        self,
        job_id: str,
        error_message: str,
        stage: int = None
    ):
        """
        Broadcast error event.
        
        Args:
            job_id: Optimization job identifier
            error_message: Error description
            stage: Stage where error occurred (optional)
        """
        message = {
            "event": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "job_id": job_id,
            "error": error_message,
            "stage": stage
        }
        
        await self._broadcast(job_id, message)
    
    async def broadcast_reconnect_state(
        self,
        job_id: str,
        state: Dict[str, Any]
    ):
        """
        Broadcast current state to newly connected client (for reconnection).
        
        Args:
            job_id: Optimization job identifier
            state: Current optimization state
        """
        message = {
            "event": "state_sync",
            "timestamp": datetime.utcnow().isoformat(),
            "job_id": job_id,
            "state": state
        }
        
        await self._broadcast(job_id, message)
    
    async def _broadcast(self, job_id: str, message: dict):
        """
        Send message to all connected clients for a job.
        
        Args:
            job_id: Optimization job identifier
            message: Message to broadcast
        """
        if job_id not in self.active_connections:
            return
        
        # Create a copy of connections to avoid modification during iteration
        connections = list(self.active_connections[job_id])
        
        disconnected = []
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error sending to WebSocket: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        if disconnected:
            async with self._lock:
                for ws in disconnected:
                    self.active_connections[job_id].discard(ws)
    
    def get_connection_count(self, job_id: str) -> int:
        """
        Get number of active connections for a job.
        
        Args:
            job_id: Optimization job identifier
            
        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(job_id, set()))


# Global WebSocket manager instance
ws_manager = WebSocketManager()
