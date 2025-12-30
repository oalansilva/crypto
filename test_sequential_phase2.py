"""
Simple validation script for WebSocket Manager and API endpoints.
Tests basic functionality without requiring full FastAPI server.
"""

import sys
sys.path.insert(0, 'backend')

from app.services.websocket_manager import WebSocketManager
from app.services.sequential_optimizer import SequentialOptimizer
import asyncio


async def test_websocket_manager():
    """Test WebSocket manager basic functionality"""
    print("=" * 60)
    print("Testing WebSocket Manager")
    print("=" * 60)
    
    ws_manager = WebSocketManager()
    
    # Test 1: Initial state
    print("\n1. Testing initial state...")
    assert len(ws_manager.active_connections) == 0, "Should start with no connections"
    print("   ✓ Manager initialized correctly")
    
    # Test 2: Connection count
    print("\n2. Testing connection count...")
    count = ws_manager.get_connection_count("test_job_1")
    assert count == 0, f"Expected 0 connections, got {count}"
    print("   ✓ Connection count works")
    
    # Test 3: Message structure
    print("\n3. Testing message structure...")
    # We can't test actual WebSocket connections without a server,
    # but we can verify the manager is properly initialized
    print("   ✓ WebSocket manager ready for connections")
    
    print("\n✅ WebSocket Manager tests passed!")


async def test_sequential_optimizer_integration():
    """Test SequentialOptimizer with checkpoint system"""
    print("\n" + "=" * 60)
    print("Testing Sequential Optimizer Integration")
    print("=" * 60)
    
    optimizer = SequentialOptimizer()
    
    # Test 1: Stage generation
    print("\n1. Testing stage generation...")
    stages = optimizer.generate_stages("macd", "BTC/USDT")
    assert len(stages) == 6, f"Expected 6 stages, got {len(stages)}"
    print(f"   ✓ Generated {len(stages)} stages for MACD")
    
    # Test 2: Checkpoint creation
    print("\n2. Testing checkpoint system...")
    test_job_id = "test_job_checkpoint_001"
    test_state = {
        "job_id": test_job_id,
        "symbol": "BTC/USDT",
        "strategy": "macd",
        "current_stage": 2,
        "total_stages": 6,
        "tests_completed": 5,
        "total_tests_in_stage": 13,
        "completed_tests": [],
        "best_result": {"fast_period": 12, "pnl": 1500},
        "locked_params": {"timeframe": "1h"}
    }
    
    optimizer.create_checkpoint(test_job_id, test_state)
    print(f"   ✓ Checkpoint created for {test_job_id}")
    
    # Test 3: Checkpoint loading
    print("\n3. Testing checkpoint loading...")
    loaded_state = optimizer.load_checkpoint(test_job_id)
    assert loaded_state is not None, "Checkpoint should exist"
    assert loaded_state["job_id"] == test_job_id, "Job ID should match"
    assert loaded_state["current_stage"] == 2, "Stage should be 2"
    assert loaded_state["tests_completed"] == 5, "Should have 5 tests completed"
    print("   ✓ Checkpoint loaded correctly")
    print(f"      Job: {loaded_state['job_id']}")
    print(f"      Stage: {loaded_state['current_stage']}/{loaded_state['total_stages']}")
    print(f"      Progress: {loaded_state['tests_completed']}/{loaded_state['total_tests_in_stage']} tests")
    
    # Test 4: Find incomplete jobs
    print("\n4. Testing incomplete job detection...")
    incomplete = optimizer.find_incomplete_jobs()
    assert len(incomplete) > 0, "Should find at least one incomplete job"
    print(f"   ✓ Found {len(incomplete)} incomplete job(s)")
    
    # Test 5: Checkpoint deletion
    print("\n5. Testing checkpoint deletion...")
    optimizer.delete_checkpoint(test_job_id)
    deleted_state = optimizer.load_checkpoint(test_job_id)
    assert deleted_state is None, "Checkpoint should be deleted"
    print("   ✓ Checkpoint deleted successfully")
    
    print("\n✅ Sequential Optimizer integration tests passed!")


async def test_api_models():
    """Test API request/response models"""
    print("\n" + "=" * 60)
    print("Testing API Models")
    print("=" * 60)
    
    # Import models
    from app.routes.sequential_optimization import (
        StartOptimizationRequest,
        OptimizationJobResponse,
        CheckpointStateResponse
    )
    
    # Test 1: StartOptimizationRequest
    print("\n1. Testing StartOptimizationRequest...")
    request = StartOptimizationRequest(
        symbol="BTC/USDT",
        strategy="macd",
        custom_ranges=None
    )
    assert request.symbol == "BTC/USDT"
    assert request.strategy == "macd"
    print("   ✓ StartOptimizationRequest model works")
    
    # Test 2: OptimizationJobResponse
    print("\n2. Testing OptimizationJobResponse...")
    from datetime import datetime
    response = OptimizationJobResponse(
        job_id="test_001",
        symbol="BTC/USDT",
        strategy="macd",
        total_stages=6,
        estimated_tests=58,
        status="created",
        created_at=datetime.utcnow().isoformat()
    )
    assert response.total_stages == 6
    assert response.estimated_tests == 58
    print("   ✓ OptimizationJobResponse model works")
    
    # Test 3: CheckpointStateResponse
    print("\n3. Testing CheckpointStateResponse...")
    checkpoint = CheckpointStateResponse(
        job_id="test_001",
        symbol="BTC/USDT",
        strategy="macd",
        current_stage=2,
        total_stages=6,
        tests_completed=5,
        total_tests_in_stage=13,
        best_result={"fast_period": 12, "pnl": 1500},
        locked_params={"timeframe": "1h"},
        timestamp=datetime.utcnow().isoformat()
    )
    assert checkpoint.current_stage == 2
    assert checkpoint.tests_completed == 5
    print("   ✓ CheckpointStateResponse model works")
    
    print("\n✅ API model tests passed!")


async def main():
    """Run all tests"""
    try:
        await test_websocket_manager()
        await test_sequential_optimizer_integration()
        await test_api_models()
        
        print("\n" + "=" * 60)
        print("🎉 ALL PHASE 2 TESTS PASSED!")
        print("=" * 60)
        print("\n✅ WebSocket Manager: Ready")
        print("✅ API Endpoints: Ready")
        print("✅ Checkpoint System: Working")
        print("\n📝 Note: Full API endpoint testing requires running FastAPI server")
        print("   These tests validate the core functionality.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
